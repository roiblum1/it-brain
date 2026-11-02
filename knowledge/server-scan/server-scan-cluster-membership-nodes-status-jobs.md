---
title: server-scan cluster membership — nodes-status CronJobs per cluster mark servers INSTALLED or free them, refuse empty reads, fall back to SSH serial
type: knowledge
area: server-scan
tags: [server-scan, nodes-status, openshift, membership, installed, available, installed-to-inventory, agents, mce, cronjob, argocd, ssh, serial]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (ADR-0024/0036/0041, deploy/helm/nodes-status/README.md, tools/collect_openshift.py)
---

# Cluster membership: the `nodes-status` jobs

Vendor managers know hardware, not workloads — to UCS, a blade running production and an idle blade are both
`associated`. Only the cluster knows, so each cluster reports for itself (ADR-0024). Field meaning:
`knowledge/server-scan/server-scan-inventory-data-model-site-vendor-classification-health.md`.

## What runs where

A separate chart, `deploy/helm/nodes-status`, **one release per cluster** deployed by Argo CD (only a few values
differ). Both jobs run `tools/collect_openshift.py` from the API image with an in-cluster ServiceAccount and write
straight to the same MongoDB (`db.dbName` must match the platform's).

| Job | Values | Runs on | Reads | Writes |
|---|---|---|---|---|
| `openshift-nodes` | `nodes.enabled`, `nodes.clusterName` (required) | every cluster, incl. an MCE hub's own hardware | its worker nodes | `INSTALLED` + cluster name |
| `openshift-agents` | `agents.enabled` (off by default), `agents.mceName` (required) | MCE hubs only | Agent CRs | `INSTALLED` + hosted cluster, or `INSTALLED_TO_INVENTORY` (unbound Agent) |

Default schedule `*/15 * * * *`. `agents.enabled` is off by default because a cluster without the Agent CRD would
fail every 15 minutes. Hostnames containing any of `excludeNameParts` (default `infra,control-plane,master`) are
dropped — this is the **only** filter (the worker role label was unreliable across clusters).

## A reconcile, scoped to its own cluster

Nothing in Kubernetes reports a removal, so each run reconciles **the servers already naming its cluster** (or MCE):
claims what it sees, frees (`AVAILABLE`) what it no longer sees, never touches other clusters' servers. A broken job
in one cluster cannot free another's machines.

Two refusals: a **failed** API read exits non-zero and writes nothing, and a **successful read returning nothing**
also refuses (more likely a broken selector, RBAC change or upgrade blip than an empty cluster).

Exit codes (same as `run_collector`): 0 complete, 1 total failure, 2 not configured, 3 partial (some hosts matched
nothing). A cluster host that matches no inventory server is reported and skipped — only vendor collectors may say a
server exists. Every real run writes a `MembershipRun` document, exported as a fleet gauge — the only way a
zero-match job becomes visible (`knowledge/server-scan/server-scan-observability-alerts-and-fleet-gauges.md`).

## Matching nodes to servers

By hostname first. When the hostname is **not a unique match** (miss, or two servers share it) it falls back to the
**hardware serial**: over SSH for a node (`SshSerialReader`, `nodes.ssh.*`, user `core`, key from a Secret — off by
default), from the Agent's inventory for an agent (ADR-0036). A renamed server stays `INSTALLED`; the cluster's name
for it lands in `OpenShiftLifecycle.reported_name`. An unreadable serial holds back only its own candidates, not the
whole run (one unreachable node once froze a cluster's releases).

A server two jobs keep flipping between within an hour is flagged `contested_with` (ADR-0041: log, gauge, "Duplicate
Server" in the inventory) — detection only; a single move is never flagged.

## Symptoms

| Symptom | Likely cause |
|---|---|
| A server in use shows `AVAILABLE` | its cluster has no `nodes-status` release, the job fails (check exit code 1/2), or its hostname matched nothing and SSH serial fallback is off |
| Every server of a cluster stays `INSTALLED` after decommission | the job stopped running (no reconcile = no release) |
| A freshly installed MCE server is drawn again after 24 h | that MCE lacks the agents job (`INSTALLED_TO_INVENTORY` never written) |
| Two clusters claim one server | hostname reuse or a real double install — see `contested_with` and the reservation lock (`knowledge/server-scan/server-scan-available-servers-and-install-reservation-lock.md`) |

## Scope & caveats

From docs/code at `08d284c`; topology terms (hub, MCE, hosted, UPI) as in
`knowledge/openshift/fleet-topology-hub-mce-hosted.md`. The real per-cluster values live in the GitOps repo, not here.

## How we know

`team-redbull/server-scan:deploy/helm/nodes-status/README.md`, `:deploy/helm/nodes-status/values.yaml`,
`:tools/collect_openshift.py`, `:docs/adr/0024-openshift-cluster-membership.md`, `:docs/adr/0036-openshift-membership-serial-fallback.md`.

## History

- 2026-11-02: created
