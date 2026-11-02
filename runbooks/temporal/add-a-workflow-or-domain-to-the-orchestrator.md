---
title: Add a new workflow to an existing domain, or a whole new domain, in the Redbull Workflows orchestrator (models, interfaces, consts, worker registration, router, limb image, chart)
type: runbook
area: temporal
tags: [temporal, redbull-workflows, development, new-workflow, new-domain, task-queue, worker, activity, chart]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# Add a workflow or a domain

**When to use:** a new long-lived operation should run in `team-redbull/workflows`.
**Impact while running:** none until deployed; deploying a brain that calls activities no limb registers leaves runs waiting.
**Prerequisites:** the repo, Python 3.12, `temporal` CLI for a dev server. Read the repo's `CLAUDE.md` (authoritative)
and `knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`.

## Pre-checks — workflow or domain?

A new **domain** is needed only for a new *credential / dependency set* (= one limb deployment and one activity queue).
Otherwise add a workflow to the domain whose credentials it uses. Naming test: could a sibling reuse it unchanged →
domain name; otherwise workflow name (`knowledge/temporal/redbull-workflows-orchestrator-architecture.md`).

## Procedure — a workflow in an existing domain

1. `shared/models/<domain>.py`: one `<Workflow>RunArgs` (input + resume state — `run()` takes exactly this one argument),
   plus `Progress` and `Result`.
2. New activity signatures in `shared/interfaces/<domain>.py` (bodies `...`); implement them in
   `activities/<domain>/activities.py`. Make every activity idempotent; classify permanent errors in `shared/exceptions.py`.
3. Queue name `<workflow>-workflow` in `shared/consts.py`; id builder in `shared/workflow_ids.py` (**include the workflow name**).
4. `workflow_domains/<domain>/<workflow>.py`: import `shared` under `workflow.unsafe.imports_passed_through()`; pass
   `task_queue=<DOMAIN>_ACTIVITY_QUEUE` on every `execute_activity`; a `progress` query with a `phase`.
5. Register the workflow in `workflow_domains/main_worker_init.py`; add a route under the existing `/workflows/<domain>`
   prefix in that domain's `router.py`.
6. Register new activities in `activities/<domain>/worker_init.py`.
7. Tests: workflow on the time-skipping env, activities with mocked HTTP, the contract test.
   No new deployment, chart or credentials.

## Procedure — a whole new domain (everything above, plus)

1. `shared/models|interfaces/<domain>.py` and a domain activity-queue constant (append `-<mce>` only if it must write to
   a specific cluster — then one worker per cluster, see the per-MCE exception).
2. `activities/<domain>/` with its own `requirements.txt`, `Dockerfile`, `worker_init.py`.
3. A settings group in `shared/settings.py` (endpoints, credentials — fail fast at start).
4. `workflow_domains/<domain>/` with its workflows and `router.py`, included in `workflow_domains/api.py`.
5. A build job in `.github/workflows/build.yml` and a `gitops/charts/<domain>-worker/` chart in `redbull-platform`
   (Argo CD deploys on push to `main`). The brain is already deployed; the domain registers against it.

## Local run

```bash
pip install -r requirements-dev.txt
temporal server start-dev                                   # UI on :8233
PYTHONPATH=. python -m workflow_domains.main_worker_init     # brain
PYTHONPATH=. python -m activities.<domain>.worker_init       # limb
PYTHONPATH=. uvicorn workflow_domains.api:app --port 8080    # trigger API, Swagger at /docs
pytest -q
```

Config comes from `.env` (see `.env.example`).

## Verification

A local end-to-end run reaches COMPLETED; `pytest -q` passes; the new workflow appears in the docs site catalogue
(`assets/nav.js` — one entry plus its page).

## Rollback

Deploy order on the way out matters too: stop triggering the route before removing activities a running workflow still
calls. Reshaping an existing workflow breaks replay of in-flight runs — check what is running first.

## History

- 2026-11-02: created from the "Adding your own" recipes of the Redbull Workflows docs site v1.0.61
