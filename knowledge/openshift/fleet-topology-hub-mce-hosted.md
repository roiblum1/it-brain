---
title: Fleet topology — hub cluster (Navigator, Temporal, Argo CD) manages MCE clusters that run hosted clusters, plus standalone UPI clusters
type: knowledge
area: openshift
tags: [architecture, topology, hub, mce, hypershift, argocd, navigator, temporal, upi]
applies_to: [ocp-4.16, ocp-4.20, ocp-4.22, hosted-cp]
confidence: observed
last_verified: 2026-11-02
owners: [platform-team]
source: gitops-day2-prod/ARCHITECTURE.md, gitops-day1/platform-config README, ClickCluster-navigator README
---

# Fleet topology

Read this first when a question involves "which cluster manages which". Real region, site and cluster
names are classified and are **never written in this repo** — pages use `<region>`, `<site>`, `<mce>`,
`<cluster>`. The real values live only inside the disconnected network.

## The layers

```
<hub cluster>   (called "prod-hub" in the day2 repo)
  ├─ Cluster Navigator   inventory/UI of clusters; syncs HC + MCE segments from Segments Manager
  ├─ Temporal server     workflow engine for provisioning/automation
  ├─ Argo CD (day2)      top instance: discovers teams, deploys to MCEs, hub charts
  └─ Argo CD "upi"       second instance (namespace openshift-gitops-upi): holds UPI cluster secrets
        │  configures and manages
        ▼
<mce cluster> × many, per <site>/<region>
  ├─ ACM + MCE           cluster lifecycle
  ├─ HyperShift          hosted control planes
  ├─ Metal3              bare-metal hosts (BareMetalHost) for node pools
  ├─ NMState             node network configuration
  ├─ OADP                backup/restore
  └─ Argo CD (own)       deploys day2 charts to the hosted clusters below
        │  hosts control planes of
        ▼
<hosted cluster> × many  (workloads run here; GPU nodes, AKO load balancing, Portworx…)

<upi cluster>   standalone clusters under no MCE; deployed to by the hub's "upi" Argo
```

## What each hub component does

| Component | Role | Notes |
|---|---|---|
| Cluster Navigator | Web UI + API listing clusters by site: console URL, segments (CIDR), load balancer IP (resolved via DNS), CSV/Excel export, availability probes | Syncs `HC`/`MCE` segment types from **Segments Manager** read-only every 5 min; manual entries must be named `ocp4-*`; file-based storage, file lock for multi-replica |
| Temporal server | Runs the provisioning/automation workflows (the Redbull Workflows orchestrator) | allocate-segment is a Temporal workflow whose "brain" runs on the hub — confirmed from the orchestrator's docs (observed, 2026-11-02): `knowledge/temporal/redbull-workflows-orchestrator-architecture.md`, `knowledge/temporal/allocate-segment-workflow.md` |
| Argo CD (day2) | Renders the `groups → mces → clusters → operators → deploy` ApplicationSet chain | See `knowledge/gitops/day2-sites-tree-discovery-and-version-layers.md` |
| Argo CD "upi" | Deploys charts to standalone UPI clusters | The only Argo with UPI cluster secrets |

## Naming (the join key for everything)

- Hosted cluster: `ocp4-<env>-<name>-<site>`; MCE: `ocp4-<env>-mce-<site>-<letter>`; `<env>` ∈ `prod|prep|test`.
- **Folder basename == Argo cluster name** (day2). A hosted cluster's day1 file is `<cluster>.yaml`.
- UPI cluster names are exempt but must never reuse an MCE or hosted-cluster name.
- `in-cluster` means "the cluster this Argo runs on" — a different cluster per Argo.

## Where each fact is written (single source of truth)

| Fact | Lives in |
|---|---|
| OCP version of an MCE / hosted cluster (`mastertag`) | **day1** repo only (`platform-config`) — see `knowledge/gitops/day1-platform-config-values.md` |
| Where charts run (site/env/MCE/cluster) | **day2** team repo folders (`sigs/<team>/sites/...`) |
| Which chart version | pin files in day2 `operators/<chart>/...` |
| VLAN/segment, DHCP scope for a hosted cluster | Segments Manager → day1 `dhcp_values`, written by the allocate-segment flow |
| Cluster inventory, console URLs, LB IPs | Cluster Navigator (derived; not authoritative) |

Version-specific refs for HyperShift/CAPI/etc. follow `knowledge/meta/fleet-versions.md`.

## Open questions (fill in, then raise `confidence`)

- Is there one hub for all regions or one per region? (day2 docs describe a single `prod-hub`.)
- How `<region>` maps to `<site>` in the repos (docs and trees use `<site>`).
- ~~Whether Temporal is what the allocate-segment workflow actually runs on.~~ Yes (2026-11-02, from the orchestrator docs).
- MCE name shape: this page says `ocp4-<env>-mce-<site>-<letter>`; the Redbull Workflows docs' examples use
  `ocp4-mce-<site>-NN` and accept `mce_cluster` with or without the `ocp4-` prefix. Check one real MCE and fix whichever is wrong.

## History

- 2026-10-03: created from the platform team's description plus the day1/day2/Navigator repo docs.
- 2026-11-02: Temporal confirmed for allocate-segment (orchestrator docs); MCE name-shape discrepancy noted
