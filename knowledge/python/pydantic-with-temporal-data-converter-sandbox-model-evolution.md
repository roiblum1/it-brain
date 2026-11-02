---
title: Pydantic with Temporal — pydantic_data_converter on every client, how payloads are encoded (to_json by alias) and decoded (TypeAdapter.validate_json), sandbox passthrough of pydantic, datetime.date, model changes that break replay of in-flight runs
type: knowledge
area: python
tags: [pydantic, temporal, temporalio, data-converter, pydantic-data-converter, sandbox, passthrough, replay, model-evolution, payload, runargs]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: temporalio/sdk-python README "Data Conversion" / "Pydantic Support" / sandbox sections, temporalio/contrib/pydantic.py, temporalio/worker/workflow_sandbox/_restrictions.py (d488ff5, SDK 1.35.0); decode cases reproduced with pydantic 2.13.4
---

# Pydantic with Temporal (Python SDK)

The orchestrator's own rules are in `knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md` (one
`RunArgs` argument, the converter on every client, imports passed through). This page explains the Pydantic side
of those rules.

## Why a special converter

The SDK's default converter handles JSON types, dataclasses, `datetime.datetime`, `UUID`, str/int enums, sets — but
**not Pydantic model instances**, and `datetime.date` / `datetime.time` only work with the Pydantic converter
(SDK README). Set it on every `Client`:

```python
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

client = await Client.connect("<temporal-frontend>:7233", namespace="<namespace>",
                              data_converter=pydantic_data_converter)
```

Every worker, the API that starts runs, and any script that queries or signals must use it — the encoding side and
the decoding side must agree. Pydantic **v1 is not supported** by this converter.

## What it does

From `temporalio/contrib/pydantic.py` (SDK 1.35.0):

| Direction | Implementation | Consequence |
|---|---|---|
| encode (`to_payload`) | `pydantic_core.to_json(value)`, encoding `json/plain` | models are written **by alias** (reproduced: `{"vlanId":5}`); `SecretStr` is written as `"**********"` |
| decode (`from_payload`) | `TypeAdapter(type_hint).validate_json(payload.data)` (adapters cached, LRU 1024) | full Pydantic validation on the way in — a payload that doesn't match the **current** model raises `ValidationError` |
| no type hint | `TypeAdapter(Any)` | you get plain `dict`/`list` back — the "workflow got a raw dict" symptom |

Encode-by-alias and decode-by-alias match, so aliased models round-trip **through Temporal** without
`populate_by_name` (reproduced). They do **not** round-trip through your own `model_dump()` (by name) — see
`knowledge/python/pydantic-v2-models-fields-coercion-strict-extra-config.md`.

`ToJsonOptions(exclude_unset=True)` exists for smaller payloads; it is off by default.

## The sandbox

Workflow files are re-imported into a sandbox on every run and replay. Third-party modules are re-imported too
unless passed through, and modules full of Pydantic models are expensive to import. The SDK README recommends
passing through **all deterministic modules, explicitly including modules containing Pydantic models**:

```python
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from shared.models.segments import AllocateSegmentRunArgs   # our model modules
```

or `SandboxRestrictions.default.with_passthrough_modules("shared")` on the worker. In SDK 1.35.0, `pydantic`,
`pydantic_core` and `annotated_types` themselves are already in the default passthrough set
(`_restrictions.py`: "Due to how Pydantic is importing lazily inside of some classes, we choose to always pass it
through"); our own `shared/` model modules are not, which is why the orchestrator imports them passed-through.

## Model changes vs in-flight runs

Workflow inputs, activity inputs/results, signals and queries are stored in **history** and decoded again with the
**current** model on replay or when a pending activity result is read. Reproduced with a payload
`{"cluster":"c1","count":3}` written by old code:

| Change to the model | Old payload decodes? |
|---|---|
| add a field **with a default** | yes |
| add a **required** field | no — `missing` |
| remove a field (default `extra="ignore"`) | yes, the old key is dropped |
| remove a field with `extra="forbid"` | no — `extra_forbidden` |
| rename a field | no — `missing` (keep the old name as an alias, or `AliasChoices("old", "new")`) |
| change a field's type (`int` → `str`) | no — `string_type` (lax mode does not turn numbers into strings) |
| make validation stricter (new validator, `strict=True`) | maybe not — the old value is re-validated |

So: **add with defaults, never rename or retype in place, don't use `extra="forbid"` on history models**, and check
what is running before deploying a model change (the orchestrator's rule "keep `RunArgs` stable",
`knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`). Single-model parameters are what make the
"add with a default" path possible (SDK README).

## Also

- Generic models are not resolved by the converter ("Classes with generics may not have the generics properly
  resolved… use concrete types", SDK README) — `knowledge/python/pydantic-typeadapter-discriminated-unions-generics-performance.md`.
- Payloads have size limits on the Temporal server; keep big blobs (inventories, logs) out of inputs and pass ids.
- Never put credentials into a model that goes through Temporal: `SecretStr` would arrive masked, and a plain `str`
  would sit in history.

## History

- 2026-11-02: created
