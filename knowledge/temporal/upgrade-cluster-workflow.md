---
title: upgrade-cluster workflow — HostedCluster upgrade by day1 mastertag/workertag commits and Argo CD syncs, ladder in upgrade/ladder.yaml, one approval, admin acks, NodePools one at a time, upgrade agent only on failed gates
type: knowledge
area: temporal
tags: [temporal, redbull-workflows, cluster-upgrade, upgrade-cluster, hypershift, hostedcluster, nodepool, mastertag, workertag, day1, day2, argocd, admin-ack, upgrade-ladder, digest, idms, pdb, upgrade-agent]
applies_to: [hosted-cp]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# upgrade-cluster

**Status (docs v1.0.61): built and run end to end on a sandbox HostedCluster, not in production yet.** Not yet built:
the agent's judge and tier-1 tools (every fix is a proposal), the RBAC/admission policies fencing the agent, the three
workers' charts in `redbull-platform` (installed by hand from `deploy/charts/`), fleet waves and their circuit breaker.

| | |
|---|---|
| Trigger | `POST /workflows/cluster-upgrade/upgrade-cluster` — 202, 409 if the cluster has a run, 422 bad body |
| Workflow id | `upgrade-cluster-<cluster>`; child per control-plane step `upgrade-control-plane-<mce>_<n>` (n ≤ `maxConcurrentControlPlanes` = the MCE's slots) |
| Queues | workflows `upgrade-cluster-workflow`, `upgrade-control-plane-workflow`; activities `upgrade-gitops-activity` (hub), `cluster-upgrade-activity-<mce>`, `upgrade-agent-activity-<mce>` |
| Writes | day1 git commits (`mastertag`, `nodepool[<name>].workertag`, `pausedUntil`), Argo CD sync of `Application/<cluster>` in `openshift-gitops` on the MCE, the hosted `openshift-config/admin-acks` ConfigMap |
| Never | patches a HostedCluster, NodePool or IDMS; syncs day2; `force-upgrade-to`; downgrades; reverts a commit |

Background: `mastertag` and day1 layout — `knowledge/gitops/day1-platform-config-values.md`; day2 version layers —
`knowledge/gitops/day2-sites-tree-discovery-and-version-layers.md`; versions — `knowledge/meta/fleet-versions.md`;
architecture — `knowledge/temporal/redbull-workflows-orchestrator-architecture.md`.

## Rules

- **Git is intent, the cluster is truth.** Every change edits one or two lines of the cluster's day1 file, runs the
  day1 validator, pushes to `main` (compare-and-set on the file's blob id — a file someone edited since planning is never
  committed over), then syncs `Application/<cluster>` to exactly that commit; a sync with anything else out of sync is
  refused (someone's change is pending).
- **Temporal owns the upgrade, the agent only advises.** "Continue" and "skip" are never agent verdicts.
- **Control plane through every minor**, never skipping a `must` rung; workers may skip minors but never fall more than
  `maxWorkerSkew` (2; HyperShift allows 3) behind.
- **Digests pinned once**: every tag resolved at planning to the release payload + HyperShift control-plane-operator
  digests; re-resolved right before each commit — a moved tag stops the step ("the mirror changed under the run").
- **The happy path is boring**: all checks are deterministic code; no LLM call when every gate passes.

## The path: a ladder in day1

A disconnected fleet has no upgrade graph to ask, so the path comes from day1 `upgrade/ladder.yaml`: one verified rung
per minor (each consecutive pair an edge in Red Hat's public stable graphs, last-checked date shown to the approver),
plus `maxWorkerSkew`, `release` (the one full mirror and its layout `{imagePath}/openshift/release-images:{version}-x86_64`),
`adminAcks`, `apiUsageIgnoredUsers`. Per MCE `upgrade/mces/<mce>.yaml`: `supportedHostedVersions` (must equal the MCE's
`hypershift/supported-versions`) and `maxConcurrentControlPlanes`. Validator: day1 `scripts/validate_upgrade_rules.py`
(rungs ascending, no minor missing, skew 1–3). Current rungs and the newest reachable minor: `knowledge/meta/fleet-versions.md`.

Next control-plane step: within the target's minor → the target (after any `must` rung); else the own minor's newer
rung; else the next minor's rung (a minor with no rung is refused). Before a step that would leave a NodePool more than
the skew behind, lagging NodePools move to the control plane's current release; `dataPlane: required` rungs roll workers
right after; `workers_to_target` (default true) adds a final worker step. A worker step never goes past the control
plane. A two-minor InPlace NodePool roll was tried on a sandbox (each node drained and rebooted once); `maxWorkerSkew: 1`
rolls every minor instead. Target: `target_version` (in the mirror; may be a non-rung last step) or `target_minor`
(newest release of that minor that is both mirrored and a rung). Refused at planning: downgrade, NodePool newer than its
control plane, NodePool already beyond the skew, a version not `X.Y.Z[-x86_64]`, a repeated rung.

## Lifecycle and phases

`planning` (reads day1 file on the hub — its folder `sites/<site>/mces/<mce>/` is the MCE; rules; the MCE's supported
versions; HostedCluster + NodePools; profile `zoned` if NodePools carry `topology.kubernetes.io/zone`; pins digests; checks
day2 layers) → `preflight` (checks 5–11) → `awaiting-approval` (**the one approval**; also the dry run: start, read the
plan, `abort` → CANCELLED, nothing committed) → per control-plane step: `preflight` → `admin-acks` → `waiting-for-slot`
(slots polled every 2 min) → `control-plane-step` (child: checking-mirror → committing `mastertag: <v>-x86_64` with every
NodePool's `workertag` pinned explicitly → syncing (5 min) → watching (30 s polls; `history[0]` Completed,
`ClusterVersionSucceeding`/`ValidReleaseInfo` True, all ClusterOperators at version; **20 min no change = stall, 3 h
deadline**) → diagnosing → needs-human) → `awaiting-day2-confirm` → per NodePool: `awaiting-continue` → `preflight` →
`nodepool-roll` (watch `status.version`, `UpdatingVersion` False, `AllNodesHealthy` True; stall 30 min, a drain refused by
the eviction API for 10 min is handed over early; deadline `ceil(replicas / maxUnavailable)` × 60 min) → `nodepool-gate`
(nodes Ready + schedulable; zoned: PDBs back to `disruptionsAllowed ≥ 1`, StatefulSets ready; soak 30 min zoned / 0 generic /
`upgrade.soakMinutes`) → `postflight` (drops the top-level `workertag` it added, syncs, reads everything at target) → done.
Also `agent-invocation`, `needs-human`, `paused`, `aborting`, and outcomes done / cancelled / aborted.

Continue-as-new after every control-plane step and every NodePool, carrying the **approved** plan, digests, profile,
order and limits (whatever the rules file says by then). Human waits are `wait_condition`s on Update-set flags: a week
between NodePools costs nothing. The child is `ParentClosePolicy.ABANDON` and driven by signals (`stop`, `hold`, `retry`);
an early end before the sync frees the slot and becomes `needs-human` in the parent.

## Checks

| # | Check | On failure |
|---|---|---|
| 1 | `rules-match-mce` — rules' `supportedHostedVersions` = MCE's, every step's minor in it | Failed |
| 2 | `mirror-has-every-step` — release + CPO tags resolve, payload images exist | Failed: "mirror <v> first" with an ImageSetConfiguration snippet |
| 3 | `day1-file-upgradeable` — parses, NodePools match, all `upgradeType: InPlace`, `imagePath` is the full mirror | Failed |
| 4 | `day2-layers-exist` — each pinned day2 chart has `ocp-versions/<v>/` for every step version | Failed: create the layer first |
| — | `git-matches-cluster`, `auto-approve-wave` | Failed |
| 5 | `argo-app-clean` — Application Synced + Healthy | needs-human |
| 6 | `operators-healthy`, `cluster-version-upgradeable` (no condition counts as True; `AdminAckRequired` alone passes) | needs-human |
| 7 | `control-plane-idle` | re-checked each minute for 30 min, then needs-human |
| 8 | `nodes-healthy` — Nodes Ready, NodePools at replicas, no pending CSRs | needs-human |
| 9 | `pdbs-allow-disruption` — no PDB at `disruptionsAllowed: 0` in scope | needs-human for the PDB owner; never remediated |
| 10 | `webhooks-have-endpoints` — no `failurePolicy: Fail` webhook without endpoints | needs-human |
| 11 | `idms-covers-release` — HostedCluster `imageContentSources`, hosted IDMS and MCE IDMS cover the release repos | Failed (before approval only) |
| 12 | concurrency — one run per cluster, a free slot | 409 / wait |

Before approval a Failed check fails the run; after approval checks only wait for a person. Not checked: backups
(assumed), whether IDMS reached `registries.conf` on nodes; PDB owners aren't notified beyond `waiting_for` and logs.

## Admin acks (before a minor step)

Example gate: from 4.19.15 a 4.19 cluster asks for `ack-4.19-admissionregistration-v1beta1-api-removals-in-4.20`
(admissionregistration `v1beta1` webhooks and ValidatingAdmissionPolicies/bindings are gone in 4.20); until acked the
hosted CVO says `Upgradeable=False` / `AdminAckRequired` and HyperShift refuses a minor change. The run reads
`openshift-config-managed/admin-gates`, `openshift-config/admin-acks`, the CVO message, and each listed API's
**APIRequestCount over 24 h**. Listed gate, no caller → the run acks (merge patch `data.<gate>: "true"`, read back, wait
≤ 10 min for the CVO); listed with callers → `awaiting-admin-ack` (`approve-admin-ack` with a reason, or `retry`);
unlisted → needs-human. `apiUsageIgnoredUsers` (GC, namespace controller, KCM, cluster-policy-controller) don't count.
APIRequestCount can't see idle workloads or external tools — listing a gate is a reviewed team decision.

## Modes and waves

`upgrade.wave` in the day1 cluster file: 0 lab, 1 canary, 2+ (or none) production. `auto_approve: true` and
`nodepool_mode: auto` are allowed only in waves 0–1 (else planning fails). Default production flow stops for `approve` →
`confirm-day2` after **every** control-plane step (the day2 team syncs their layer; skipped only on wave 0 with no day2
Application) → `continue` before each NodePool (the customer's sign-off after their own checks — can take a week).
`workers_to_target: false` = control plane only. `pause` / `resume` / `abort` only by a person; pause holds before the next
commit (what's rolling finishes); abort after approval stops the child, commits `pausedUntil` for the HostedCluster and every
NodePool (rendered by the hostedclusters-setup chart), syncs → ABORTED (observed: committed and synced in 17 s).

## The upgrade agent

`invoke_upgrade_agent` on `upgrade-agent-activity-<mce>`, only on a failed gate or stalled watch. Calls the upgrade agent
service in the MCE (a kubernetes-sigs agent-sandbox `Sandbox`, OpenAI-compatible model, read-only tools under its own
identity). In: evidence bundle ≤ 512 KB (no Secrets), budget 15 min / 40 tool calls / 2 tier-1 actions. Out: diagnosis,
proposals, verdict `retry_gate` | `needs_human` | `abort_recommended`. Malformed or unreachable twice → `needs_human`;
the run never fails because of the agent. Proposals are approved per action (`actions/{id}/approve|reject`) and run with
the workflow's identity. Tiers: 0 read (not Secrets); 1 known-safe pod deletes in `openshift-*` (never OVN/multus, never
`etcd-*`/`kube-apiserver-*` in the HCP namespace) — waves 0–1 only, not built yet; 2 proposals; 3 forbidden by RBAC and
admission policy (workload controllers, PDBs, namespaces, CRDs, webhooks, customer namespaces, exec, impersonate…). Every
answered call is written to "Brain" as an incident (Brain never blocks the run).

Known remediation: a drain stuck on an **OpenShift** PDB whose pods crash-loop on the node being drained (seen on
`openshift-console/downloads`, 35 min; `nodeDrainTimeout` 0 = waits for ever; "Cannot evict pod as it would violate the
pod's disruption budget") → delete the not-Ready pods behind it, then `retry_gate`. Never the PDB, never a Ready pod,
never outside `openshift-*`; a customer's PDB → `needs_human` for its owner.

## Decisions API

`POST …/upgrade-cluster/{workflow_id}/<decision>` with `{by, …}` — `approve`, `approve-admin-ack` (reason required),
`continue` (`nodepool?`), `confirm-day2`, `pause`, `resume`, `abort` (reason required), `retry`,
`actions/{action_id}/approve|reject`. Answers: 200 taken; 409 not waiting for that (detail says what it waits for); 404;
504 no answer in 15 s (brain worker down?); 500. `GET /workflows/cluster-upgrade/upgrade-targets?cluster=<cluster>` is
synchronous (≤ 60 s; 504 = is the upgrade-gitops limb running?). Status: `progress.waiting_for` says in words what a person
must do next; also plan + pinned digests, versions, `pending_actions`, last verdict, last 20 log lines. Page: `/ui/cluster-upgrade`.

## Sandbox evidence (observed by the workflows team)

2026-10-31: a KubeVirt HostedCluster went one minor up in 2.5 h (control plane 74 min, two in-place nodes 64 min); two
pre-flights went to the agent (the lab model didn't answer; a person retried); the run gave the admin ack itself.
2026-11-01: a three-zone cluster went two minors in one wave-0 `auto_approve` run, zones a→b→c each gated and soaked; a
pause during zone b held before zone c. Faults met (stalls under emulation, a CVO guard, the image pruner) all stopped at
a person; on CPU-served models the agent timed out or diagnosed without a usable fix. Design doc: `docs/upgrade/DESIGN.md`
in the Cluster-AutoUpgrade workspace (stall window of 45 min proposed there, still open).

## History

- 2026-11-02: created from the upgrade-cluster page of the Redbull Workflows docs site v1.0.61
