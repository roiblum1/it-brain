---
title: Start, watch and steer a Redbull Workflows run — trigger API (202/409), GET /workflows/runs/{id}, bulk routes, upgrade decisions, cancelling in Temporal
type: runbook
area: temporal
tags: [temporal, redbull-workflows, operations, trigger-api, status, workflow-id, bulk, cancel, decisions]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# Start, watch and steer a workflow run

**When to use:** you need to run one of the orchestrator's workflows by hand, or find out what a run is doing.
**Impact while running:** depends on the workflow — install/uninstall/provision touch real hardware and clusters; read
the workflow's page first (`knowledge/temporal/README.md` lists them).
**Prerequisites:** network access to `workflows-orchestrator-api` (`<workflows-api-url>`; Swagger at `/docs`); for the
Temporal UI, access to the Temporal server on the hub. The trigger API has **no auth of its own** — be deliberate.

## Pre-checks

- Read the workflow's page for its body, workflow id scheme and what it writes.
- Is a run already open for the same thing? Its id is deterministic, so compute it and check:

```bash
API=<workflows-api-url>
curl -sS "$API/workflows/runs/<workflow-id>"      # 200 = known run (any state), 404 = never started
```

## Procedure

1. **Start** — always async; the reply is the id to poll.
   ```bash
   curl -sS -X POST "$API/workflows/<domain>/<workflow>" -H 'Content-Type: application/json' -d @body.json
   # 202 {"workflow_id": "...", "run_id": "..."}   started
   # 409                                          a run with that id is in flight — poll it instead of retrying
   # 422                                          body rejected (unknown field, missing field, bad value)
   ```
   Many items: use the `/bulk` route where one exists (initialize-segment, provision-dell-server) — one run per item,
   202 with a per-item report (`started`, `already_running`, `rejected`/`failed`). install-server and uninstall-server take a
   list in `server_names` (and install-server `count`) on their normal route. install-server pool requests are **not**
   retry-safe: sending `count: N` twice starts 2N installs.
2. **Watch** — poll the domain-agnostic status route.
   ```bash
   curl -sS "$API/workflows/runs/<workflow-id>" | jq '{status, progress, result, error}'
   ```
   `status` RUNNING / COMPLETED / FAILED / CANCELED / TERMINATED. While RUNNING read `progress.phase` and, by workflow,
   `waiting_on` (provision), `activity_queue` (server-lifecycle), `waiting_for` (upgrade — what a person must do next).
   Temporary pages: `/ui/server-lifecycle`, `/ui/cluster-upgrade`. The Temporal UI shows every step, its input and result.
3. **Steer** (upgrade-cluster only) — decisions are Temporal Updates:
   ```bash
   curl -sS -X POST "$API/workflows/cluster-upgrade/upgrade-cluster/<workflow-id>/approve" \
     -H 'Content-Type: application/json' -d '{"by": "<you>", "reason": "<why>"}'
   # 200 taken · 409 not waiting for that (detail says what it waits for) · 504 brain worker not answering
   ```
   Decisions: `approve`, `approve-admin-ack`, `continue`, `confirm-day2`, `pause`, `resume`, `abort`, `retry`,
   `actions/<id>/approve|reject` (`knowledge/temporal/upgrade-cluster-workflow.md`). To stop an upgrade use `abort`, never a
   Temporal cancel/terminate: abort commits `pausedUntil` and syncs, a cancel does not.
4. **Stop another workflow** — the trigger API has no cancel route; cancel from the Temporal UI or the standard Temporal
   CLI (generic Temporal usage, not described in the workflows docs; namespace from `TEMPORAL_NAMESPACE`):
   ```bash
   temporal workflow describe --workflow-id <workflow-id> --namespace <namespace>
   temporal workflow cancel   --workflow-id <workflow-id> --namespace <namespace>
   ```
   There is **no compensating rollback**: a cancelled install-server leaves its resources on the MCE (so you can see how
   far it got) and the server-scan lock expires on its own; a cancelled uninstall leaves a deleted Machine deleted.
   A re-run converges from where it stopped.

## Verification

`status: COMPLETED` and a `result` matching the workflow page's result description (e.g. allocate-segment
`values_updated`, install-server `agent_name`, release-segment `released`).

## Rollback

Workflows here don't roll back. Undo is the inverse workflow (allocate ↔ release-segment, install ↔ uninstall-server)
or a hand fix described on the workflow's page. A FAILED run's message says what to fix; after fixing, start again with
the same body (same id → a fresh run once the old one is closed).

## History

- 2026-11-02: created from the Redbull Workflows docs site v1.0.61 (HTTP surface sections of every workflow page)
