---
title: Diagnose a Temporal workflow run stuck in RUNNING — waiting on a person, unpolled per-MCE activity queue, unclassified permanent error retrying forever, limb older than brain, missing task_queue
type: runbook
area: temporal
tags: [temporal, redbull-workflows, troubleshooting, stuck, running, task-queue, schedule-to-start, retry, non-retryable, worker, mce]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# Diagnose a run stuck in RUNNING

**When to use:** `GET /workflows/runs/<id>` says RUNNING for longer than the workflow page's "normal duration".
**Impact while running:** read-only diagnosis.
**Prerequisites:** the trigger API (`<workflows-api-url>`), Temporal UI access, `oc` access to the hub and the MCE concerned.

First rule: **do not add a deadline and do not terminate the run** to "fix" slowness. Runs that wait on people have no
timeout by design (`knowledge/temporal/redbull-workflows-orchestrator-architecture.md`).

## Pre-checks

```bash
curl -sS "<workflows-api-url>/workflows/runs/<workflow-id>" | jq '.progress'
```

## Procedure — match the symptom

1. **`progress` says it is waiting for a person** (`awaiting-approval`, `awaiting-continue`, `awaiting-day2-confirm`,
   `awaiting-admin-ack`, `needs-human`; `waiting_for` set). Working as designed → send the decision
   (`runbooks/temporal/start-watch-and-steer-a-redbull-workflow-run.md`).
2. **Phase never advances and `progress.activity_queue` is a per-MCE queue** (`server-lifecycle-activity-<mce>`,
   `cluster-upgrade-activity-<mce>` …). Nothing polls it. History shows repeated **schedule-to-start timeouts** (5 min).
   ```bash
   oc --context <mce> -n <worker-ns> get deploy,pods -l app.kubernetes.io/name=server-lifecycle-worker   # label may differ
   oc --context <mce> -n <worker-ns> logs deploy/server-lifecycle-worker --tail=100
   ```
   Causes: no worker on that MCE; worker can't reach Temporal; worker's `MCE_CLUSTER` ≠ the `mce_cluster` callers send
   (queue names differ). Fix: `runbooks/temporal/deploy-server-lifecycle-worker-on-an-mce.md`.
3. **An activity fails and retries every minute (Temporal UI: attempt count climbing, same error).** Either a real
   outage being out-waited (Segments Manager, DHCP API, git remote, OME, server-scan, a hosted API) — fix the dependency
   and the run continues by itself — or a **permanent error nobody classified as non-retryable**. Then the fix is a code
   change adding it to `non_retryable_error_types` (`knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`).
   Typical permanent-looking errors: 401/403 from a service (rotated token in the worker's Secret), RBAC 403 on the MCE.
4. **Workflow task failing (UI shows workflow task failures, not activity failures).** A plain exception in workflow code,
   or non-determinism after a deploy that reshaped the workflow. Code fix; in-flight runs may need a reviewed decision.
5. **Run sits right after a brain deploy, in an early phase** (e.g. uninstall-server in `checking-inventory`). The brain
   calls an activity the old limb doesn't register. CI ships the brain first → **upgrade the limb** (and its ClusterRole) on each MCE.
6. **Activity scheduled but never picked up, on the workflow's own queue name.** `task_queue=` missing in
   `execute_activity` — code fix.
7. **Long but legitimate machine waits** (each has a deadline and will fail by name): install-server `awaiting-agent`
   ≤ 1 h per candidate, uninstall-server `unbinding` ≤ 1 h, provision-dell-server `deploying-template` ≤ 2 h,
   upgrade `control-plane-step` ≤ 3 h, release-segment held in `removing-dhcp-scope` while the DHCP API is down.

## Verification

The phase advances (poll again), or the run reaches FAILED with a named error you can act on.

## Rollback

Nothing to roll back — diagnosis only.

## History

- 2026-11-02: created from the Redbull Workflows docs site v1.0.61
