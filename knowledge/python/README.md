# Area `python`

Python as we write it for our platform tools: Pydantic models and settings (v2), validation and serialization, the
Temporal Python SDK's Pydantic data converter, FastAPI in server-scan.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** —
- **Domain:** our own platform tooling (`platform-tools`)

Two of our tools are Pydantic-heavy Python: the Redbull Workflows orchestrator (Temporal Python SDK + Pydantic +
FastAPI, `knowledge/temporal/redbull-workflows-orchestrator-architecture.md`) and server-scan (FastAPI + Pydantic +
pydantic-settings, `knowledge/server-scan/server-scan-architecture-collectors-mongodb-api.md`). Most "the workflow
got a dict", "422 from the API", "settings won't load" and "old runs can't decode" problems are Pydantic behaviour,
so it gets its own area.

## Pages

| Page | What it answers |
|---|---|
| `knowledge/python/pydantic-v2-models-fields-coercion-strict-extra-config.md` | BaseModel, required vs optional, defaults, lax vs strict coercion, `extra`, `frozen`, `validate_assignment`, `from_attributes`, aliases and `populate_by_name` |
| `knowledge/python/pydantic-validators-field-model-before-after-wrap.md` | `field_validator` / `model_validator` modes, order, raising `ValueError` vs `PydanticCustomError`, `TypeError` is not converted |
| `knowledge/python/pydantic-serialization-model-dump-json-mode-alias-secretstr.md` | `model_dump` vs `mode="json"` vs `model_dump_json`, `by_alias`, `exclude_none`, datetime / UUID / Enum / set output, `SecretStr` masking, `field_serializer` |
| `knowledge/python/pydantic-validationerror-reading-error-types-in-logs.md` | the exact `ValidationError` text, `loc` / `type` / `input`, the common error types and what each means |
| `knowledge/python/pydantic-v1-to-v2-migration-pitfalls.md` | renamed methods and config keys, `__root__` → `RootModel`, `json_encoders`, Optional semantics, float→int, unions, `bump-pydantic` |
| `knowledge/python/pydantic-settings-env-prefix-dotenv-secrets-precedence-nodecode.md` | `BaseSettings`, `INVENTORY_` prefix, `.env`, secrets dir, nested `__`, list env vars and `NoDecode`, precedence, never logging secrets |
| `knowledge/python/pydantic-with-temporal-data-converter-sandbox-model-evolution.md` | `pydantic_data_converter`, what it does on encode/decode, sandbox passthrough, `datetime.date`, model changes vs in-flight runs |
| `knowledge/python/pydantic-typeadapter-discriminated-unions-generics-performance.md` | `TypeAdapter`, tagged unions for workflow inputs, generics in Temporal, performance tips |
| `runbooks/python/fix-a-pydantic-validationerror-from-a-workflow-activity-or-api-log.md` | procedure: from a log line to the field, the input and the fix |
| `runbooks/python/migrate-a-pydantic-v1-model-to-v2-safely.md` | procedure: v1 → v2 with tests that pin the wire format |

## Belongs here

How Pydantic, pydantic-settings, the Temporal SDK's data conversion and FastAPI behave in *our* code: coercion,
validation, serialization, settings loading, error messages, migration, performance.

## Not here

Workflow design, task queues, retries and determinism → `temporal` (`knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`).
What server-scan's fields *mean* and how its API behaves → `server-scan`
(`knowledge/server-scan/server-scan-inventory-data-model-site-vendor-classification-health.md`).

## Offline sources

Planned docs-only snapshots (`docs/it-brain/SOURCES-PLAN.md`), none committed yet:

| Name | Repo | Paths | Licence |
|---|---|---|---|
| `pydantic-docs` | `pydantic/pydantic` | `docs/concepts`, `docs/errors`, `docs/migration.md`, `docs/api`, `docs/integrations` | MIT |
| `pydantic-settings-docs` | `pydantic/pydantic-settings` | `docs/index.md` | MIT |
| `temporal-python-sdk` | `temporalio/sdk-python` | `README.md` (data conversion, sandbox, Pydantic support), `temporalio/contrib/pydantic.py` | MIT |

Until then, the pages here quote the relevant behaviour and say where it came from.

## Redact

Settings examples use field and variable **names only**. Never paste a `.env`, a Secret, a connection string with
credentials or a `SecretStr` value; write `<REDACTED>`. `ValidationError` text echoes the input value
(`input_value=…`): redact it before pasting a log line into a page or an MR.

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
