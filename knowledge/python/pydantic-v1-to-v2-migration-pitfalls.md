---
title: Pydantic v1 → v2 migration pitfalls — parse_obj → model_validate, dict() → model_dump, class Config → model_config, @validator → @field_validator, __root__ → RootModel, orm_mode → from_attributes, Optional now required, float→int, unions keep str
type: knowledge
area: python
tags: [pydantic, migration, pydantic-v1, pydantic-v2, bump-pydantic, model-validate, model-dump, configdict, rootmodel, from-attributes, json-encoders, pydantic-settings]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic docs/migration.md (577aa83); temporalio/sdk-python README "Pydantic Support"
---

# Pydantic v1 → v2: what breaks

Source: the upstream migration guide (`docs/migration.md`). Our tools (server-scan, Redbull Workflows) are already on
v2; this page is for old scripts, vendored helpers and anything copied from older examples. The Temporal SDK's
Pydantic converter **does not support v1 at all** (`temporalio/sdk-python` README).

## Renamed methods (old ones still exist, deprecated, warn)

| v1 | v2 |
|---|---|
| `Model.parse_obj(d)` | `Model.model_validate(d)` |
| `Model.parse_raw(s)` | `Model.model_validate_json(s)` |
| `Model.from_orm(o)` | `Model.model_validate(o)` with `from_attributes=True` |
| `m.dict()` | `m.model_dump()` |
| `m.json()` | `m.model_dump_json()` (passing `indent`/`ensure_ascii` to the old `.json()` gives confusing errors) |
| `m.copy()` | `m.model_copy()` |
| `Model.construct()` | `Model.model_construct()` |
| `Model.schema()` | `Model.model_json_schema()` |
| `Model.__fields__` | `Model.model_fields` |
| `Model.update_forward_refs()` | `Model.model_rebuild()` |

## Config

`class Config:` inside the model → `model_config = ConfigDict(...)`. Renamed keys:

| v1 | v2 |
|---|---|
| `orm_mode` | `from_attributes` |
| `allow_population_by_field_name` | `populate_by_name` (`validate_by_name` from 2.11) |
| `anystr_strip_whitespace` / `anystr_lower` | `str_strip_whitespace` / `str_to_lower` |
| `max_anystr_length` / `min_anystr_length` | `str_max_length` / `str_min_length` |
| `validate_all` | `validate_default` |
| `schema_extra` | `json_schema_extra` |
| `allow_mutation = False` | `frozen = True` (inverse) |

Removed: `fields`, `smart_union` (smart is now the default), `json_loads`, `json_dumps`, `copy_on_model_validation`,
`underscore_attrs_are_private` (always on), `error_msg_templates`, `getter_dict`. `json_encoders` still works but is
deprecated — use `@field_serializer` (`knowledge/python/pydantic-serialization-model-dump-json-mode-alias-secretstr.md`).

## Validators

| v1 | v2 |
|---|---|
| `@validator("x")` | `@field_validator("x")` + `@classmethod` |
| `@validator("x", pre=True)` | `@field_validator("x", mode="before")` |
| `@validator(..., each_item=True)` | annotate the item type instead (`list[Annotated[int, AfterValidator(f)]]`) |
| `@root_validator(pre=True)` | `@model_validator(mode="before")` |
| `@root_validator` | `@model_validator(mode="after")` — gets the **instance**, returns it |
| `values` argument | `info: ValidationInfo` → `info.data` |
| `@validate_arguments` | `@validate_call` |
| `allow_reuse=True` | no longer needed |

A `TypeError` raised in a validator is no longer turned into a `ValidationError` — it propagates
(`knowledge/python/pydantic-validators-field-model-before-after-wrap.md`).

## Behaviour changes that pass tests and break production

| Change | v1 | v2 |
|---|---|---|
| `Optional[str]` without default | optional, default `None` | **required**, may be `None` |
| `5.5` → `int` | truncated to `5` | error `int_from_float` |
| number → `str` | coerced | error `string_type` (opt-in `coerce_numbers_to_str`) |
| `x: int \| str` with `"1"` | `1` (first type that fits) | `"1"` (input type preserved; `union_mode='left_to_right'` reverts) |
| iterable of pairs → `dict` | coerced | error |
| model equality | equal to a dict with the same data | only equal to models of the same type, incl. private attrs |
| nested subclass instance dumped | all subclass fields | only the declared type's fields |
| regex `pattern` | Python `re` | Rust regex: **no look-arounds or backreferences** (`regex_engine='python-re'` to keep them) |
| `__root__` field | custom root | `RootModel[T]` |
| `BaseSettings` | in `pydantic` | separate package `pydantic-settings` (`knowledge/python/pydantic-settings-env-prefix-dotenv-secrets-precedence-nodecode.md`) |
| `GenericModel` | `pydantic.generics.GenericModel` | plain `BaseModel` + `Generic[T]` |
| URL types | subclasses of `str` | not `str` — `str(url)` where a string is needed |

## Tools

- `bump-pydantic <package>` (PyPI `bump-pydantic`, beta) rewrites most of the renames mechanically — review the diff.
- `from pydantic import v1` gives the old API inside v2 while migrating file by file; it is not compatible with
  the Temporal Pydantic converter.

## Procedure

`runbooks/python/migrate-a-pydantic-v1-model-to-v2-safely.md`.

## History

- 2026-11-02: created
