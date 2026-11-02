---
title: Deploy or fix the per-MCE server-lifecycle-worker (MCE_CLUSTER = queue name, server-scan admin token, BMC credentials, Role and ClusterRole) so install-server and uninstall-server runs on that MCE move
type: runbook
area: temporal
tags: [temporal, redbull-workflows, server-lifecycle, server-lifecycle-worker, mce, task-queue, rbac, deployment, install-server, uninstall-server]
applies_to: [hosted-cp]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# Deploy or fix server-lifecycle-worker on an MCE

**When to use:** a new MCE should take install-server / uninstall-server runs, or runs for an MCE sit in a phase that
never advances with `progress.activity_queue: server-lifecycle-activity-<mce>`.
**Impact while running:** none on existing hosts; queued runs for that MCE start moving once the worker polls.
**Prerequisites:** the brain release (`workflows-orchestrator`, global ConfigMap `workflows-orchestrator-config`) already
installed — limbs mount it for `TEMPORAL_*`. The worker chart: `gitops/charts/server-lifecycle-worker/` in
`redbull-platform` (production, via Argo CD) or `deploy/charts/` in the workflows repo. Lasting changes go through GitOps.

## Pre-checks

```bash
oc --context <mce> get infraenv -A                               # the InfraEnvs install-server will fill
oc --context <mce> get agentserviceconfig                        # the Agent stack server-scan's agents job relies on
oc --context <mce> -n <worker-ns> get deploy,cm,secret | grep -i server-lifecycle
```

## Procedure

1. **`server-lifecycle-config`**: `MCE_CLUSTER` = exactly the `mce_cluster` callers send (it builds the queue name
   `server-lifecycle-activity-<MCE_CLUSTER>`); `SERVER_SCAN_URL` including `/api/v1`.
2. **`server-lifecycle-credentials`** (Secret, never in git): `SERVER_SCAN_API_TOKEN` — an **admin** token (the install
   lock uses mutation endpoints; a viewer token fails every run with `ServerScanAuthError`; may be empty only where
   server-scan runs without auth); `{HP,DELL,CISCO,INTERSIGHT}_BMC_USERNAME` / `_PASSWORD` for each vendor the MCE's
   InfraEnvs hold (missing → `BmcCredentialsMissingError`).
3. **Namespaced Role** in the InfraEnv namespace: `secrets` get/create/delete; `metal3.io/baremetalhosts`
   get/create/delete/patch; `agent-install.openshift.io/nmstateconfigs` get/create/delete; `agents` get/list.
4. **ClusterRole** for uninstall-server (`rbac.hostedClusters: true`, the default): machines and agentmachines
   get/list/delete/patch, agents patch, hostedclusters get/list, secrets get (cluster-wide — hosted admin kubeconfigs).
   With it off, any host with an Agent fails uninstall inspection with a 403; use remove-server on such an MCE.
5. **Network**: the worker dials out to Temporal on the hub (no inbound to the MCE needed) and must reach
   server-scan, and for uninstall each `kube-apiserver.<hc-ns>-<hc>.svc:6443` (check NetworkPolicies on HCP namespaces).
6. **Roll the limb out before the brain uses new activities** (CI ships the brain first).

## Verification

```bash
oc --context <mce> -n <worker-ns> logs deploy/server-lifecycle-worker --tail=50   # started, polling its queue
```

A stuck run's phase advances; a new install-server run for this MCE moves past `resolving-vlan`. A missing RBAC verb
shows as a non-retryable `BmhPrerequisiteMissingError`, not a silent loop.

## Rollback

Scale the worker to 0: runs for that MCE wait (visible as schedule-to-start timeouts) instead of acting — safe.

## History

- 2026-11-02: created from the install-server and uninstall-server reference sections of the Redbull Workflows docs site v1.0.61
