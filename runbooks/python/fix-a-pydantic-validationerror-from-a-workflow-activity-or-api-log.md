---
title: Fix a Pydantic ValidationError seen in a Temporal workflow / activity failure, a worker log or a FastAPI 422 — find the field, the input, the side that changed, and the fix
type: runbook
area: python
tags: [pydantic, validationerror, troubleshooting, temporal, activity-failure, fastapi, 422, server-scan, redbull-workflows]
applies_to: [pydantic-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic docs/errors/validation_errors.md; temporalio/contrib/pydantic.py; error texts reproduced with pydantic 2.13.4
---

# Fix a Pydantic ValidationError from a workflow, activity or API log

## When to use

A log line, Temporal failure or HTTP 422 contains `validation error(s) for <Model>`, or a worker fails to start with
`SettingsError: error parsing value for field ...`.

## Pre-checks

- Read access to the logs or the Temporal Web UI / `temporal` CLI for the namespace (`knowledge/temporal/README.md`).
- The repo of the service at the deployed commit (image tag → commit).
- Redact `input_value=…` before pasting anything into a ticket, MR or the brain.

## Procedure

1. **Classify the line.**
   - `N validation error(s) for <Model>` → data didn't match a model. Continue.
   - `SettingsError: error parsing value for field "<f>" from source "EnvSettingsSource"` → an env var for a list/dict
     field isn't JSON. Fix the value (`'["a","b"]'`) or the field (`NoDecode` + a before validator) —
     `knowledge/python/pydantic-settings-env-prefix-dotenv-secrets-precedence-nodecode.md`. Stop here.
   - A bare `TypeError` from a validator → a bug in validator code, not bad data.
2. **Read each error block**: line 1 = `loc` (field path), line 2 = message + `[type=…, input_value=…, input_type=…]`.
   Look the `type` up in `knowledge/python/pydantic-validationerror-reading-error-types-in-logs.md`.
3. **Find where the validation ran**:

   | Where it shows up | What was validated | Who sent it |
   |---|---|---|
   | activity failure, `ApplicationError` wrapping a ValidationError raised in our code | data an activity got from an external API (server-scan, Segments Manager, OME, Kubernetes) | that API |
   | workflow task failure / activity result can't be decoded, right after a deploy | a **payload from history** decoded with the new model | old code — a model change broke in-flight runs |
   | the API that starts runs returns 422 | the HTTP request body | the caller (Navigator, a script, a person) |
   | server-scan logs at ingest | a provider response (Redfish, OME, CIMC…) mapped into a model | the hardware manager |

4. **Check the "after a deploy" case first** if the error appeared when a new image rolled out:
   ```bash
   git -C <service-repo> diff <old-tag> <new-tag> -- shared/models/ backend/app/domain/models/
   ```
   Added required field, renamed or retyped field, `extra="forbid"`, stricter validator → see the table in
   `knowledge/python/pydantic-with-temporal-data-converter-sandbox-model-evolution.md`. Fix by giving the new field a
   default / restoring the old name as an alias (`AliasChoices`), redeploy, and let the stuck runs retry their
   workflow task. Don't terminate runs before that is tried.
5. **Otherwise compare input and model**: take the `input_value` and the model at the deployed commit.
   - `missing` on an aliased field + the input uses the Python name → add `populate_by_name=True` or send the alias.
   - `int_parsing` / `string_type` from an external API → the API changed or returns sentinels (`""`, `"N/A"`):
     handle them in a `mode="before"` validator, don't loosen the type to `Any`.
   - `extra_forbidden` → a typo in the caller or a field the model doesn't know yet.
6. **If the error came from our validator** (`value_error`, a custom type): the rule fired — decide whether the
   input or the rule is wrong. In activities, make it a **non-retryable** error so the run fails instead of retrying
   forever (`knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`).
7. **Reproduce locally** with the redacted input before changing code:
   ```python
   from pydantic import ValidationError
   from <package>.models import <Model>
   try:
       <Model>.model_validate_json('<redacted payload>')
   except ValidationError as e:
       print(e.errors(include_url=False))
   ```
8. **Add a test** with that input (and one with an old-history payload if step 4 applied), then fix.

## Verification

The same input validates in the local reproduction; the stuck runs progress (Temporal UI shows the next event); the
API returns 2xx for the corrected request.

## Rollback

Redeploy the previous image tag; in-flight runs written by the old code decode again with the old model.

## Related

`knowledge/python/pydantic-validationerror-reading-error-types-in-logs.md`,
`runbooks/temporal/diagnose-a-workflow-run-stuck-in-running.md`.

## History

- 2026-11-02: created
