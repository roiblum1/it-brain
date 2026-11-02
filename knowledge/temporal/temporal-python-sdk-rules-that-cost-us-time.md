---
title: Temporal Python SDK gotchas — run stuck RUNNING instead of FAILED, plain exception in workflow, non_retryable_error_types, sandbox imports, pydantic_data_converter, one RunArgs argument, missing task_queue
type: knowledge
area: temporal
tags: [temporal, temporalio, python-sdk, determinism, applicationerror, retry-policy, non-retryable, sandbox, pydantic, data-converter, task-queue, continue-as-new, replay, gotchas]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# Temporal Python SDK rules that cost the workflows team time

Learned building `team-redbull/workflows` (`knowledge/temporal/redbull-workflows-orchestrator-architecture.md`).
Each failure mode looks like something else. They apply to any `temporalio` Python code.

## Symptom → rule

| Symptom | Cause | Rule |
|---|---|---|
| Run hangs in **RUNNING**, workflow task retrying forever, never FAILED | A plain Python exception raised **in workflow code** fails the *workflow task*, which Temporal retries forever | Deterministic failures in workflow code must be `ApplicationError`. In **activity** code ordinary exceptions are fine (converted, class name = error type) |
| Run RUNNING with one activity failing every minute, forever | Activities retry without attempt limit; a permanent error not classified non-retryable retries forever | List it in `non_retryable_error_types` or raise a non-retryable `ApplicationError`. **Fix by classifying, never by adding a deadline** |
| A "non-retryable" error still retries | Error type list written as string literals with a typo — Temporal matches on type *name* | Build the list from the exception classes (`Cls.__name__`), so a wrong name is an ImportError at worker start |
| Worker / sandbox crash on importing models | Our model modules are re-imported inside the workflow sandbox (the docs blame Pydantic's C extensions; in newer SDKs, e.g. 1.35.0, `pydantic` / `pydantic_core` are already passed through by default, and it is our own `shared/` modules that need it — `knowledge/python/pydantic-with-temporal-data-converter-sandbox-model-evolution.md`) | In workflow modules import `shared/` under `with workflow.unsafe.imports_passed_through():`. Entrypoints import normally. Never import settings in workflow code |
| Payloads fail to (de)serialize at one boundary | One `Client.connect(...)` without the Pydantic converter | Pass `pydantic_data_converter` on **every** client: every worker and the API |
| Workflow gets a raw `dict` instead of its model, no error | Typed conversion is skipped silently when payload count ≠ declared parameters | Give `run()` exactly **one** Pydantic argument: a `RunArgs` wrapping input + internal resume state |
| Activity never starts; run sits forever | `execute_activity` without `task_queue=` goes to the workflow's own queue, which no limb polls | Always pass `task_queue=` from `shared/consts.py` |
| Activity reaped by Temporal while an HTTP call hangs | No client timeout, or one above the activity timeout | HTTP client timeout below `start_to_close_timeout` (60 s vs 90 s there); create the client inside the activity so tokens never leak across runs |
| In-flight runs break after a deploy | Workflow code changed shape (steps reordered, activity renamed) — replay no longer matches history | Changing workflow code is a compatibility question: additions and new workflows are fine, reshaping an existing flow needs a look at what is running |
| Old runs fail to decode after a model change | Run input models are decoded **from history on replay** | Keep the shape of `…Input` / `RunArgs` models stable (install-server never puts `count` into the run model for this reason) |
| Activities queue up unseen on a per-host queue | No worker polls that queue | A 5-min **schedule-to-start** timeout on activities for host-specific queues (per-MCE) makes it visible in history; expose the queue in the `progress` query |

## Determinism (why most of the above exist)

Workflows are replayed from history, so workflow code must make the same decisions on every replay.

| Fine in a workflow | Must be an activity |
|---|---|
| branching, loops, arithmetic on own state | any HTTP / DB / filesystem call |
| `await workflow.execute_activity(...)`, `asyncio.gather` over activity handles | `datetime.now()`, `random`, `uuid4` |
| `workflow.now()`, `workflow.sleep()` (durable timer — never `time.sleep`), `workflow.logger` | reading env vars or settings |
| | anything whose answer could change between runs |

Corollary seen in provision-dell-server: a lookup table (iDRAC prefix → region) is resolved **at the edge** (the API
router) and passed in as input; a lookup inside the workflow would change behaviour of in-flight runs on replay.

## Other patterns used across the repo

- **Deterministic workflow ids** derived from the input (with the workflow name in them) → duplicate triggers are a
  409 from the server, not a race in our code. `/bulk` routes start one workflow per item, never a batch workflow.
- **Retry policy:** 1 s initial, ×2, capped at 1 min, unlimited attempts; permanent errors listed explicitly.
- **`continue_as_new`** every N cycles (a poll loop every 48 h; upgrade-cluster after every step) keeps history bounded
  — a week-long wait costs the same as an hour.
- **Human waits** are `workflow.wait_condition` on a flag set by a Temporal **Update** (upgrade-cluster): no timer, no
  polling, nothing added to history while waiting. Updates answer the caller at once (200 / 409 "not waiting for that").
- **Queries** (`@workflow.query def progress`) feed the status endpoint; keep `phase` + "what it is waiting for" there.
- **Child workflows** with `ParentClosePolicy.ABANDON` where cutting the child off mid-way is dangerous (remove-server
  between power-off and deletes; a control-plane step mid-upgrade). Drive children by signals, not cancellation.
- **Heartbeating activity** for long watches (upgrade's control-plane watch polls every 30 s).
- **No secrets in history.** Inputs, results and error messages are stored verbatim and readable by anyone with
  Temporal UI access. Pass a *reference* (provision-dell-server passes credential index `0`, `1`, …, resolved by the
  limb from its Secret at call time); scrub tokens from git errors; never put kubeconfig material in errors or logs.
- Tests run on the SDK's **time-skipping test environment** (no server needed); activity tests mock HTTP; a contract test
  keeps signatures and implementations in step; replay tests of saved histories (upgrade-cluster).

## History

- 2026-11-02: created from the "SDK rules that cost us time" and design sections of the Redbull Workflows docs site v1.0.61
- 2026-11-02: sandbox-import cause refined from the Temporal Python SDK source (see the python area)
