---
title: OCP ↔ Virtualization — who owns OpenShift Virtualization on our clusters (HCO operator, HyperConverged CR, nodes and MachineConfig, upgrades, capacity, monitoring) and how VM workloads affect cluster operations
type: interface
area: kubevirt
teams: [ocp, virtualization]
tags: [kubevirt, cnv, openshift-virtualization, hco, hyperconverged, ownership, upgrades, mco, capacity, monitoring, gitops]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp, virtualization]
source: it-brain-design
---

# OCP ↔ Virtualization: the platform under the VMs

> **Draft contract.** OpenShift Virtualization is an operator on clusters the OCP team runs, while VMs and their
> lifecycle belong to the virtualization team. The seam: who changes what, and how cluster operations (upgrades, drains,
> node changes) are coordinated with running VMs.

## Parties

| Side | Team | Systems |
|---|---|---|
| platform | `ocp` | clusters, nodes, MachineConfig/MCO, OLM subscriptions, day1/day2 GitOps, monitoring, upgrades (`knowledge/temporal/upgrade-cluster-workflow.md`) |
| consumer / operator owner | `virtualization` | the HyperConverged CR settings, VMs, templates/instance types, MTV, VM backup |

## Who provides what

| Item | Provided by | Requested how |
|---|---|---|
| OpenShift Virtualization operator subscription and version per cluster | ocp (version agreed with virtualization) | day2 GitOps |
| HyperConverged CR content (migrations, eviction, workload updates, CPU ratio, storage settings, feature gates) | virtualization | day2 GitOps, reviewed by ocp |
| Node prerequisites: hardware virtualization, IOMMU/hugepages/CPU manager where needed (MachineConfig, PerformanceProfile) | ocp | day2 GitOps |
| Capacity headroom for one node's VMs during drains | ocp + virtualization | capacity review `<…>` |
| Upgrade windows and pre-checks for non-migratable VMs | ocp leads, virtualization confirms | `runbooks/kubevirt/drain-or-upgrade-a-node-with-running-vms.md` |
| Alerts routing for `openshift-virtualization-operator` alerts | ocp | Alertmanager config `<…>` |

Rule: configuration goes into the **HyperConverged CR** (HCO reverts manual edits of the KubeVirt/CDI CRs and fires
`KubeVirtCRModified` — `knowledge/kubevirt/kubevirt-architecture-components-virt-launcher-hco-cdi.md`).

## How each side checks its half (read-only)

```bash
oc get csv -n openshift-cnv | grep -i kubevirt          # version
oc get hyperconverged -n openshift-cnv -o jsonpath='{.items[0].status.conditions}' | jq
oc get vmi -A -o wide | awk '$NF=="False"'              # VMs that would block drains
oc get vmi -A -l kubevirt.io/outdatedLauncherImage
```

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| OCP upgrade stuck on one MCP node (ocp) | virtualization: non-migratable VM with `LiveMigrate` | `VMCannotBeEvicted`, launcher pods on the node |
| VMs restarted during maintenance (virtualization) | ocp: drained with VMs not migratable / eviction `None` | evictionStrategy, change log |
| `OutdatedVirtualMachineInstanceWorkloads` days after a CNV update (ocp) | virtualization: VMs not migratable, `Evict` not allowed | `workloadUpdateStrategy` |
| `KubeVirtCRModified` (ocp) | someone edited an operand CR | GitOps vs live HyperConverged CR |

## Open questions

- Which clusters may run VMs at all (dedicated VM clusters vs mixed)?
- Is the CNV version pinned per fleet minor in `knowledge/meta/fleet-versions.md`?
- Does the upgrade-cluster workflow need a "VMs present" pre-check?

## History

- 2026-11-02: drafted with the KubeVirt deep dive (`knowledge/kubevirt/README.md`)
