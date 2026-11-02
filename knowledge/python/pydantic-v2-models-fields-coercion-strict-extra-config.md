---
title: Pydantic v2 models — required vs Optional, defaults, lax coercion ("120" becomes 120) vs strict, extra fields ignored, frozen, validate_assignment, aliases and populate_by_name
type: knowledge
area: python
tags: [pydantic, basemodel, configdict, coercion, strict, extra-forbid, alias, populate-by-name, frozen, validate-assignment, from-attributes]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic docs/concepts/models.md, fields.md, strict_mode.md, config.md, alias.md, migration.md (577aa83); reproduced with pydantic 2.13.4
---

# Pydantic v2 models: what is required, what gets coerced, what gets dropped

Every example below was run on 2026-11-02 in a scratch venv with **pydantic 2.13.4** (the version pinned in
server-scan's `pyproject.toml` at `08d284c`). The behaviour is v2-wide unless a line says otherwise.

## Required, optional, nullable

| Declaration | Required? | `None` allowed? |
|---|---|---|
| `a: str` | yes | no |
| `a: str = "x"` | no (default `"x"`) | no |
| `a: str \| None` (or `Optional[str]`) | **yes** | yes |
| `a: str \| None = None` | no | yes |
| `a: Any` | yes | yes |

`Optional[...]` does **not** mean "has a default" in v2 — that was v1 behaviour (`knowledge/python/pydantic-v1-to-v2-migration-pitfalls.md`).
Omitting such a field gives `Field required [type=missing, input_value={}, input_type=dict]`.

Mutable defaults are safe: `items: list[int] = []` gives each instance its own copy (checked: appending on one
instance leaves the next instance's list empty). `Field(default_factory=...)` is still the clearer way for
anything computed.

## Lax mode (the default): Pydantic converts when it can

| Input → field type | Result |
|---|---|
| `"120"` → `int` | `120` |
| `5.0` → `int` | `5` |
| `5.5` → `int` | error `int_from_float` (v1 silently truncated) |
| `True` → `int` | `1` |
| `"12.5"` → `int` | error `int_parsing` |
| `5` → `str` | error `string_type` (numbers are **not** turned into strings unless `coerce_numbers_to_str=True`) |
| `"yes"` → `bool` | `True` |

The full table is `docs/concepts/conversion_table.md` upstream. JSON input (`model_validate_json`) is a bit
stricter than Python input for some types — validate the way the data actually arrives.

## Strict mode

`model_config = ConfigDict(strict=True)` (or `Field(strict=True)` on one field, or `model_validate(..., strict=True)`)
turns coercion off: `"120"` → `int` fails with `Input should be a valid integer [type=int_type, ...]`. Use it on
inputs where a string number means a bug upstream (e.g. VLAN ids coming from another service).

## Extra keys

| `extra=` | Unknown key in input |
|---|---|
| `"ignore"` (**default**) | silently dropped |
| `"forbid"` | error `Extra inputs are not permitted [type=extra_forbidden, ...]` |
| `"allow"` | kept, readable as an attribute and dumped back |

Default `ignore` hides typos in input (`vlanid` instead of `vlan_id` → field missing or default used). `forbid`
catches them — but also rejects **old payloads that still carry a removed field**, which matters for Temporal
history (`knowledge/python/pydantic-with-temporal-data-converter-sandbox-model-evolution.md`). server-scan's
`Settings` uses `extra="ignore"` so unrelated environment entries don't break start-up
(`knowledge/python/pydantic-settings-env-prefix-dotenv-secrets-precedence-nodecode.md`).

## Assignment after construction

- By default attributes are **not** re-validated on assignment: `m.a = "not-an-int"` is accepted and stays a string.
- `validate_assignment=True` validates (and coerces) on every assignment.
- `frozen=True` refuses assignment: `Instance is frozen [type=frozen_instance, ...]`, and makes instances hashable.

## Aliases (external names ≠ Python names)

`vlan_id: int = Field(alias="vlanId")`:

| Operation | Default behaviour |
|---|---|
| Validate `{"vlanId": 5}` | works |
| Validate `{"vlan_id": 5}` | **fails** `Field required` on `vlanId` — unless `populate_by_name=True` (v2.11+: `validate_by_name=True`) |
| `model_dump()` | `{"vlan_id": 5}` — by **name** |
| `model_dump(by_alias=True)` | `{"vlanId": 5}` |
| `pydantic_core.to_json(model)` | `{"vlanId":5}` — by **alias** (this is what the Temporal converter uses) |

So `Model.model_validate(m.model_dump())` fails for an aliased model without `populate_by_name` — reproduced. server-scan
sets `populate_by_name: True` on every model that maps Mongo's `_id` to `id` (`Field(alias="_id")`, e.g.
`team-redbull/server-scan:backend/app/domain/models/site.py`) for exactly this reason.

`AliasChoices` / `validation_alias` / `serialization_alias` exist for accepting several names or using different
names in and out (`docs/concepts/alias.md`).

## Reading from objects

`from_attributes=True` (v1: `orm_mode`) lets `model_validate(obj)` read attributes instead of dict keys — for ORM
rows or SDK objects.

## Config is inherited

`model_config` on a base class applies to subclasses; with multiple bases the settings merge and the later base
wins (`docs/migration.md`, "Changes to config"). A shared base model is the simplest way to apply `extra`,
`populate_by_name` or `strict` everywhere.

## Related

Validators: `knowledge/python/pydantic-validators-field-model-before-after-wrap.md`. Output side:
`knowledge/python/pydantic-serialization-model-dump-json-mode-alias-secretstr.md`. Error text:
`knowledge/python/pydantic-validationerror-reading-error-types-in-logs.md`.

## History

- 2026-11-02: created
