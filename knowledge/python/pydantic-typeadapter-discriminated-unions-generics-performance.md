---
title: Pydantic TypeAdapter, discriminated (tagged) unions for vendor-specific inputs, RootModel, generics with Temporal, and performance tips (model_validate_json, build TypeAdapter once, tagged unions)
type: knowledge
area: python
tags: [pydantic, typeadapter, discriminated-union, tagged-union, union-tag-invalid, rootmodel, generics, performance, model-validate-json]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic docs/concepts/type_adapter.md, unions.md, models.md, performance.md (577aa83); temporalio/sdk-python README; reproduced with pydantic 2.13.4
---

# TypeAdapter, tagged unions, generics, performance

## TypeAdapter: validation for things that aren't models

```python
from datetime import datetime
from pydantic import TypeAdapter

TypeAdapter(list[int]).validate_python(["1", 2])          # [1, 2]
TypeAdapter(datetime).dump_python(dt_value, mode="json")  # ISO string — server-scan's way to store datetimes
```

server-scan uses exactly that `TypeAdapter(datetime).dump_python(..., mode="json")` in its Mongo repositories
(`team-redbull/server-scan:backend/app/infrastructure/mongodb/server_repository.py`). The Temporal Pydantic converter
decodes every payload with a cached `TypeAdapter(type_hint)` (`knowledge/python/pydantic-with-temporal-data-converter-sandbox-model-evolution.md`).

**Build a TypeAdapter once** (module level) — constructing one builds a validator and serializer each time
(`docs/concepts/performance.md`).

## Discriminated unions: one input type, several vendors

```python
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, TypeAdapter

class Dell(BaseModel):
    vendor: Literal["dell"]
    idrac: str
class Cisco(BaseModel):
    vendor: Literal["cisco"]
    cimc: str

Server = Annotated[Union[Dell, Cisco], Field(discriminator="vendor")]
TypeAdapter(Server).validate_python({"vendor": "cisco", "cimc": "<cimc>"})    # Cisco(...)
```

Reproduced errors — much clearer than a plain union's "tried every member" output:

```text
Input tag 'hpe' found using 'vendor' does not match any of the expected tags: 'dell', 'cisco' [type=union_tag_invalid, ...]
dell.idrac
  Field required [type=missing, input_value={'vendor': 'dell'}, input_type=dict]
```

Good fit for workflow inputs that differ per vendor or per mode: one `RunArgs` field typed as a tagged union keeps
the "exactly one argument" rule (`knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`) and the
error names the branch. Plain unions in v2 run in **smart** mode: they keep the input's type when it already
matches a member (`int | str` with `"1"` stays `"1"`) — see `knowledge/python/pydantic-v1-to-v2-migration-pitfalls.md`.

## RootModel

`class Names(RootModel[list[str]])` wraps a bare list/dict as a model (v1 `__root__`); `Names(["a","b"]).model_dump_json()`
→ `["a","b"]`. Access the value as `.root`.

## Generics

`class Page(BaseModel, Generic[T]): items: list[T]` works in Pydantic, but the Temporal SDK warns that generic
classes may not have their generics resolved by the converter — use **concrete types** (`class ServerPage(Page[Server])`
or a non-generic model) for anything that crosses a workflow or activity boundary.

## Performance tips (from `docs/concepts/performance.md`)

- `Model.model_validate_json(raw)` instead of `Model.model_validate(json.loads(raw))` — one pass in Rust.
- Create `TypeAdapter`s once.
- Tagged unions instead of plain unions for large unions.
- `TypedDict` instead of deeply nested models when you only need validation, not methods.
- Avoid `wrap` validators on hot paths; `Any` when a value needs no validation; `FailFast` to stop at the first
  error in big sequences.

## History

- 2026-11-02: created
