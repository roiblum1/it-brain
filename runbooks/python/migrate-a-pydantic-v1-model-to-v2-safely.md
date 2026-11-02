---
title: Migrate a Pydantic v1 model (or script) to v2 safely — pin the wire format with tests first, bump-pydantic, fix Optional / coercion / validator changes, then compare outputs
type: runbook
area: python
tags: [pydantic, migration, pydantic-v1, pydantic-v2, bump-pydantic, tests, golden-files, model-validate, model-dump]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic docs/migration.md (577aa83)
---

# Migrate a Pydantic v1 model to v2 safely

## When to use

Old automation, a vendored helper or copied example code still uses Pydantic v1 (`class Config`, `.dict()`,
`@validator`, `parse_obj`), or it must be used with the Temporal Pydantic converter (v2 only).

## Pre-checks

- The pitfalls list: `knowledge/python/pydantic-v1-to-v2-migration-pitfalls.md`.
- Real (redacted) sample inputs: API responses, stored documents, workflow payloads.
- A branch; Python ≥ 3.9 with v1 still installable for step 1.

## Procedure

1. **Pin today's behaviour with tests, still on v1.** For each model: validate every sample input and store
   `model.dict()` / `model.json()` output as golden files. Add the edge cases v2 changes:
   - a field declared `Optional[X]` with **no** default, omitted in the input;
   - a float with a fractional part into an `int` field;
   - a number into a `str` field;
   - an `int | str` field given `"1"`;
   - a list/iterable of pairs into a `dict` field;
   - a regex `pattern`/`regex` with look-arounds.
2. **Upgrade** pydantic to v2 (and `pydantic-settings` if `BaseSettings` is used — it moved out).
3. **Run `bump-pydantic <package>`** (PyPI `bump-pydantic`) for the mechanical renames; review the diff. Check by hand:
   - `class Config` → `model_config = ConfigDict(...)` with renamed keys (`orm_mode` → `from_attributes`,
     `allow_population_by_field_name` → `populate_by_name`, …);
   - `@validator` → `@field_validator` + `@classmethod`; `pre=True` → `mode="before"`; `each_item=True` → annotated item type;
   - `@root_validator` → `@model_validator`; the after-mode one takes and **returns the instance**;
   - `__root__` → `RootModel[T]`;
   - `json_encoders` → `@field_serializer`;
   - `GenericModel` → `BaseModel` + `Generic[T]`.
4. **Decide each behaviour change explicitly** where the golden tests fail:
   - `Optional[X]` fields that were really optional → add `= None`;
   - numbers into strings → fix the producer, or `coerce_numbers_to_str=True` if the producer can't change;
   - union results → reorder or `Field(union_mode="left_to_right")`;
   - regex with look-arounds → rewrite, or `regex_engine="python-re"`.
5. **Compare outputs**: `model_dump()` must equal the old `.dict()` golden files; JSON output must parse to the same
   data (v2's compact separators and `str(key)` for non-string keys are expected differences).
6. **If the models cross a Temporal boundary**, switch to `pydantic_data_converter` on every client and check the
   evolution rules before deploying to a namespace with running workflows
   (`knowledge/python/pydantic-with-temporal-data-converter-sandbox-model-evolution.md`).
7. Remove remaining deprecated calls (`.dict()`, `.json()`, `parse_obj`): run the tests with
   `-W error::DeprecationWarning` (or `PYTHONWARNINGS=error::DeprecationWarning`).

## Verification

All golden tests green on v2 with deprecation warnings as errors; a sample of real inputs validates identically.

## Rollback

Revert the branch; nothing persistent changes unless step 6 deployed to a namespace with running workflows.

## History

- 2026-11-02: created
