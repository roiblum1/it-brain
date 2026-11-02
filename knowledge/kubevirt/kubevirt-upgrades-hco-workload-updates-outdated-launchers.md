---
title: OpenShift Virtualization upgrades — control-plane update without VM downtime, workloadUpdateStrategy (LiveMigrate, Evict), outdated virt-launcher pods (OutdatedVirtualMachineInstanceWorkloads), and what an OCP node upgrade does to running VMs
type: knowledge
area: kubevirt
teams: [ocp]
tags: [kubevirt, cnv, upgrade, hco, workloadupdatestrategy, outdated-launcher, outdatedvirtualmachineinstanceworkloads, mco, olm, version-coupling]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/kubevirt docs/updates.md; kubevirt/hyperconverged-cluster-operator docs/cluster-configuration.md (workloadUpdateStrategy); openshift/runbooks alerts/openshift-virtualization-operator/OutdatedVirtualMachineInstanceWorkloads.md
---

# Upgrades and VMs

Two different upgrades touch VMs: the **OpenShift Virtualization operator** (HCO → KubeVirt/CDI/…) and the **OCP
cluster** (MCO drains and reboots every node).

## 1. Upgrading OpenShift Virtualization

KubeVirt control-plane updates are zero-downtime for running VMs (since v0.17): virt-controller and virt-handler are
updated before virt-api; create/delete keep working. Known disruptions: **in-flight migrations fail** (TLS cut when
virt-handler restarts) and **`virtctl console`/`vnc` sessions drop**. So don't run maintenance migrations during a
CNV upgrade.

Running VMs keep their **old virt-launcher image** until they are moved; they then show the label
`kubevirt.io/outdatedLauncherImage`. 24 hours after the control-plane update, alert
**`OutdatedVirtualMachineInstanceWorkloads`** fires: outdated launchers miss new features and security fixes.

### workloadUpdateStrategy (HyperConverged `spec.virtualization.workloadUpdateStrategy`, older `spec.workloadUpdateStrategy`)

| Field | Default | Means |
|---|---|---|
| `workloadUpdateMethods` | `[LiveMigrate]` | how outdated VMs are refreshed; `Evict` (shutdown + restart) is opt-in. With both, migratable VMs migrate and only the rest are evicted. Empty list = no automatic updates |
| `batchEvictionSize` | 10 | VMIs force-updated per interval |
| `batchEvictionInterval` | `1m` | wait between batches |

Non-migratable VMs stay outdated unless `Evict` is allowed or they are restarted by hand:

```bash
oc get vmi -A -l kubevirt.io/outdatedLauncherImage
oc get hyperconverged -n openshift-cnv -o jsonpath='{.items[0].spec.virtualization.workloadUpdateStrategy}{"\n"}'
```

### Version coupling with OCP

OpenShift Virtualization is versioned with the OCP minor (CNV 4.N for OCP 4.N) — *hypothesis from product naming,
not from the offline sources here*; upgrade OCP and CNV in the order Red Hat documents — **check RHOKP for the CNV
version and its update path**. Record
which CNV version each fleet minor runs in `knowledge/meta/fleet-versions.md` (no version numbers here).

## 2. Upgrading OCP with VMs running

Each node is cordoned and drained by MCO. With `evictionStrategy: LiveMigrate` (HCO default on multi-worker clusters),
every VM on the node is live-migrated away first; the speed is governed by `parallelOutboundMigrationsPerNode`,
`parallelMigrationsPerCluster` and bandwidth (`knowledge/kubevirt/kubevirt-live-migration-requirements-limits-policies-failures.md`).
A single non-migratable VM with `LiveMigrate` stops the MCP rollout (`VMCannotBeEvicted`) —
`knowledge/kubevirt/kubevirt-node-drain-eviction-strategy-and-pdbs.md`. Check before the window:
spare capacity for one node's worth of VMs (memory especially — VMs don't shrink), all VMs migratable or explicitly
allowed to restart, and no CNV upgrade running at the same time.

Procedure: `runbooks/kubevirt/drain-or-upgrade-a-node-with-running-vms.md`. Fleet upgrade workflow:
`knowledge/temporal/upgrade-cluster-workflow.md` (it does not know about VMs yet — open question for that page).

## Scope & caveats

Upstream docs and the OpenShift runbook (2026-11). The exact CNV ↔ OCP support and update graph is Red Hat's —
RHOKP wins.

## History

- 2026-11-02: created
