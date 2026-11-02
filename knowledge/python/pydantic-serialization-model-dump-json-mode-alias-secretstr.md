---
title: Pydantic v2 serialization — model_dump vs model_dump(mode="json") vs model_dump_json, by_alias, exclude_none, datetime / UUID / Enum / set output, SecretStr dumps as ********** , field_serializer
type: knowledge
area: python
tags: [pydantic, serialization, model-dump, model-dump-json, mode-json, by-alias, exclude-none, secretstr, datetime, uuid, enum, field-serializer]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic docs/concepts/serialization.md, docs/concepts/types.md (577aa83); reproduced with pydantic 2.13.4
---

# Pydantic v2 serialization

## Three ways out, three different results

For a model with `when: datetime` (UTC), `day: date`, `id: UUID`, `c: Color` (Enum), `s: set[int]`,
`note: str | None = None`, `token: SecretStr`:

| Call | `when` | `day` | `id` | `c` | `s` | `note` | `token` |
|---|---|---|---|---|---|---|---|
| `model_dump()` (python mode) | `datetime(...)` object | `date(...)` | `UUID(...)` | `<Color.RED>` | `{1, 2}` | `None` | `SecretStr('**********')` |
| `model_dump(mode="json")` | `'2026-11-02T09:30:00Z'` | `'2026-11-02'` | `'0000…0001'` | `'red'` | `[1, 2]` | `None` | `'**********'` |
| `model_dump_json()` | same as json mode, as a JSON string | | | | | `null` | `"**********"` |

Rules that follow:
- `model_dump()` is **not JSON-safe**: passing it to `json.dumps`, Mongo or an HTTP client fails or stores objects.
  Use `mode="json"` whenever the result leaves Python. server-scan uses `model_dump(mode="json")` and
  `TypeAdapter(datetime).dump_python(value, mode="json")` for exactly this — which is why every datetime in its Mongo
  is an ISO **string** (`knowledge/server-scan/server-scan-inventory-data-model-site-vendor-classification-health.md`).
- Aware datetimes in UTC serialize with a trailing `Z`; **naive** datetimes serialize without any offset
  (`'2026-01-01T12:00:00'`) — ambiguous once stored. Make datetimes timezone-aware at the edge.
- `exclude_none=True` drops `None` fields; `exclude_unset=True` drops fields the caller never set (handy for PATCH
  bodies); `exclude_defaults=True` drops fields equal to their default.
- `by_alias=True` writes alias names; plain `model_dump()` writes field names — see the alias table in
  `knowledge/python/pydantic-v2-models-fields-coercion-strict-extra-config.md`.

## SecretStr

`SecretStr` prints, `repr`s **and serializes** as `**********` — in python mode, JSON mode, `model_dump_json()` and
`pydantic_core.to_json` (all reproduced). Consequences:

- Good: a settings object or model logged by accident doesn't leak the value.
- Trap: a `SecretStr` field sent through any serializer (an API response, a Temporal payload) arrives as the literal
  string `**********`. Unwrap explicitly with `.get_secret_value()` only at the point of use; server-scan does this
  in one function (`team-redbull/server-scan:backend/app/infrastructure/credentials/env.py`, `_read`) because a naive
  `str(...)` once "logged in" with `**********`.
- Never put credentials in workflow inputs at all — Temporal history is stored and readable
  (`knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`).

## Custom output

```python
from pydantic import BaseModel, field_serializer
import datetime as dt

class Report(BaseModel):
    when: dt.datetime

    @field_serializer("when")
    def day_only(self, v: dt.datetime) -> str:
        return v.strftime("%Y-%m-%d")

Report(when=dt.datetime(2026, 1, 1)).model_dump_json()   # '{"when":"2026-01-01"}'
```

`@model_serializer` replaces the whole output; `@computed_field` adds a derived read-only field to the output.
`json_encoders` in config is the v1 way and is deprecated (`knowledge/python/pydantic-v1-to-v2-migration-pitfalls.md`).

## Subclasses are cut down to the declared type

If a field is declared as `User` and holds a `UserLogin(User)` instance, `model_dump()` only writes `User`'s fields
(v2 change; `docs/concepts/serialization.md`, "Subclasses of model-like types"). Use `SerializeAsAny[User]` or
`serialize_as_any=True` when you really want the subclass fields — and think twice if one of them is a password.

## Related

Temporal payloads are written by `pydantic_core.to_json` (by alias):
`knowledge/python/pydantic-with-temporal-data-converter-sandbox-model-evolution.md`.

## History

- 2026-11-02: created
