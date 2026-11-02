---
title: Pydantic v2 validators — field_validator and model_validator modes before / after / wrap, run order, ValueError vs PydanticCustomError vs assert, TypeError is not a ValidationError
type: knowledge
area: python
tags: [pydantic, field-validator, model-validator, before, after, wrap, value-error, pydanticcustomerror, validation-order]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic docs/concepts/validators.md, docs/migration.md (577aa83); reproduced with pydantic 2.13.4
---

# Pydantic v2 validators

## The four modes

| Mode | Runs | Gets | Use for |
|---|---|---|---|
| `before` | before Pydantic's own parsing | the raw input (any type) | normalising input: split a CSV string, strip, map legacy values |
| `after` (default) | after parsing | a value of the declared type | business rules: range checks, cross-checks on a parsed value |
| `wrap` | around parsing | raw input + a `handler` to call Pydantic | try/fallback logic, catching and re-raising errors |
| `plain` | instead of parsing | raw input; Pydantic does no type check | rarely what you want |

```python
from pydantic import BaseModel, field_validator, model_validator

class Segment(BaseModel):
    name: str
    vlan_id: int

    @field_validator("name", mode="before")
    @classmethod
    def strip(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("vlan_id")          # mode="after"
    @classmethod
    def vlan_range(cls, v: int) -> int:
        if not 1 <= v <= 4094:
            raise ValueError("VLAN must be 1-4094")
        return v

    @model_validator(mode="after")        # whole model, after every field is valid
    def check(self):
        return self
```

Order observed for one field with a `before` and an `after` decorator: `before` (raw `'  ABC '`) → Pydantic's `str`
parsing → `after` (got `'ABC'`) → then `model_validator(mode="after")`. With the annotated pattern
(`Annotated[str, BeforeValidator(f), AfterValidator(g)]`) the docs define the order as: *before* and *wrap*
validators **right to left**, then *after* validators **left to right** (`docs/concepts/validators.md`, "Ordering of validators").

`model_validator(mode="before")` gets the raw input (often a dict) — check its type, it may also be a model
instance or anything else the caller passed. `mode="after"` gets the instance and must **return** it.

## Raising errors

| Raise inside a validator | Becomes |
|---|---|
| `ValueError("VLAN must be 1-4094")` | `Value error, VLAN must be 1-4094 [type=value_error, ...]` |
| `assert v < 4095, "too big"` | `Assertion failed, too big [type=assertion_error, ...]` — and **skipped under `python -O`**, so don't use assert for real checks |
| `PydanticCustomError("vlan_range", "VLAN {vlan} outside 1-4094", {"vlan": v})` | `VLAN 5000 outside 1-4094 [type=vlan_range, ...]` — your own stable `type` string, good for API clients and alerts |
| `TypeError` (e.g. a bug in the validator) | **not** converted: the `TypeError` propagates as-is (v2 change, `docs/migration.md`) |

All of these were reproduced with pydantic 2.13.4. A `ValueError` raised from an activity's input validation is a
deterministic, permanent error — in Temporal code classify it non-retryable
(`knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`).

## Patterns seen in our code

server-scan's `Settings` (`team-redbull/server-scan:backend/app/config/settings.py`) uses:
- a `mode="before"` field validator `_split_csv` that turns `"a,b"` into `["a", "b"]` for a list setting declared
  `Annotated[list[str], NoDecode]` (`knowledge/python/pydantic-settings-env-prefix-dotenv-secrets-precedence-nodecode.md`);
- `field_validator`s for numeric limits (retention days, batch sizes);
- several `model_validator(mode="after")` that check combinations (e.g. production must not run with the dev
  default secrets).

That split is the house style worth copying: **before** = shape the input, **after** = rules, **model after** = cross-field rules.

## Validation context and info

Validators can take a second `info: ValidationInfo` argument: `info.data` holds the already-validated fields
(fields are validated in definition order, so only earlier fields are there), `info.context` carries whatever
was passed as `model_validate(..., context={...})`.

## Related

`knowledge/python/pydantic-v2-models-fields-coercion-strict-extra-config.md`,
`knowledge/python/pydantic-validationerror-reading-error-types-in-logs.md`,
`knowledge/python/pydantic-v1-to-v2-migration-pitfalls.md` (`@validator` / `@root_validator` → these).

## History

- 2026-11-02: created
