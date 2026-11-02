---
title: Reading a Pydantic ValidationError in logs — "N validation errors for Model", loc, type=missing / int_parsing / string_type / extra_forbidden / union_tag_invalid / json_invalid, input_value, errors.pydantic.dev URL
type: knowledge
area: python
tags: [pydantic, validationerror, error-types, missing, int-parsing, string-type, extra-forbidden, json-invalid, union-tag-invalid, logs, fastapi-422]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic docs/errors/validation_errors.md, docs/errors/errors.md (577aa83); messages reproduced with pydantic 2.13.4
---

# Reading a Pydantic ValidationError

## Shape of the text

```text
2 validation errors for Segment                      ← count + model (or "tagged-union[Dell,Cisco]", a TypeAdapter type…)
vlan_id                                              ← loc: the field path, dotted for nesting (ome.timeout, servers.3.mac)
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/int_parsing     ← version of pydantic that raised it
name
  Input should be a valid string [type=string_type, input_value=5, input_type=int]
```

Programmatically, `e.errors()` gives a list of dicts with `type`, `loc` (tuple), `msg`, `input`, optionally `ctx`
and `url`; `e.errors(include_url=False)` drops the URL; `e.json()` gives the same as JSON. FastAPI returns this list
as the body of a **422** response (`detail: [...]`). Pydantic's URL line shows the **pydantic minor** that raised the
error — useful to tell which image produced a log line.

`input_value=` echoes the input. If the input is a dict, the whole dict is printed — **redact it** before pasting a
log into a page, MR or chat (it can carry hostnames, serials or credentials).

## Error types we actually hit

| `type` | Message (v2.13) | Usual cause in our tools |
|---|---|---|
| `missing` | `Field required` | field not sent; **aliased field sent under its Python name** (needs `populate_by_name`); a new required field added while old payloads exist (Temporal history) |
| `int_parsing` | `Input should be a valid integer, unable to parse string as an integer` | `"12.5"`, `""`, `"N/A"` from an upstream API |
| `int_type` | `Input should be a valid integer` | strict mode rejected a string number |
| `int_from_float` | `Input should be a valid integer, got a number with a fractional part` | `5.5` into `int` (v1 truncated silently) |
| `string_type` | `Input should be a valid string` | a number sent where a string is declared (v2 doesn't coerce numbers to str) |
| `extra_forbidden` | `Extra inputs are not permitted` | `extra="forbid"` and a typo, or an old payload with a removed field |
| `value_error` | `Value error, <your message>` | a validator raised `ValueError` |
| `assertion_error` | `Assertion failed, <message>` | a validator used `assert` |
| `<custom>` | your template | a validator raised `PydanticCustomError("<custom>", ...)` |
| `frozen_instance` | `Instance is frozen` | assignment to a `frozen=True` model |
| `json_invalid` | `Invalid JSON: EOF while parsing an object at line 1 column 14` | truncated or non-JSON body / payload |
| `union_tag_invalid` | `Input tag 'hpe' found using 'vendor' does not match any of the expected tags: 'dell', 'cisco'` | discriminated union got an unknown tag (`knowledge/python/pydantic-typeadapter-discriminated-unions-generics-performance.md`) |
| `list_type` | `Input should be a valid list` | a list setting got a plain string (see `NoDecode` in `knowledge/python/pydantic-settings-env-prefix-dotenv-secrets-precedence-nodecode.md`) |

The full catalogue with one example per type is upstream in `docs/errors/validation_errors.md`.

## Not a ValidationError

- `pydantic_settings.exceptions.SettingsError: error parsing value for field "<f>" from source "EnvSettingsSource"` —
  pydantic-settings tried to JSON-decode a complex env var and failed (reproduced with pydantic-settings 2.15.0).
- `PydanticUserError` / `PydanticSchemaGenerationError` at import time — the *model definition* is wrong
  (`docs/errors/usage_errors.md`), not the data.
- A bare `TypeError` from a validator — v2 no longer wraps it.

## Procedure

`runbooks/python/fix-a-pydantic-validationerror-from-a-workflow-activity-or-api-log.md`.

## History

- 2026-11-02: created
