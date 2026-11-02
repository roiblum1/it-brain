---
title: KubeVirt node drain — evictionStrategy (LiveMigrate, LiveMigrateIfPossible, None, External), the virt-api eviction webhook, PDBs, VMCannotBeEvicted, and why a drain or MCO rollout blocks on a non-migratable VM
type: knowledge
area: kubevirt
teams: [ocp]
tags: [kubevirt, drain, eviction, evictionstrategy, livemigrate, pdb, poddisruptionbudget, vmcannotbeevicted, mco, machineconfig, node-maintenance, 429]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/kubevirt docs/handling-eviction-requests.md; kubevirt/user-guide docs/cluster_admin/node_maintenance.md; kubevirt/hyperconverged-cluster-operator docs/cluster-configuration.md; openshift/runbooks alerts/openshift-virtualization-operator/VMCannotBeEvicted.md
---

# Node drain and eviction with VMs

Every drain — `oc adm drain`, an MCO rollout during an OCP upgrade, a NodePool replace, the descheduler — evicts
virt-launcher pods. What happens to the VM is decided by its **evictionStrategy**.

## evictionStrategy

Set per VMI (`spec.template.spec.evictionStrategy`) or cluster-wide (HyperConverged `spec.virtualization.evictionStrategy`;
the VMI value wins). HCO default: **`LiveMigrate` on clusters with several workers, `None` on single-worker clusters**.

| Strategy | On eviction |
|---|---|
| `None` | no protection: the pod is evicted; the VM restarts elsewhere or stays off according to its runStrategy |
| `LiveMigrate` | the VM is migrated instead; **a non-migratable VM blocks the drain** until someone acts |
| `LiveMigrateIfPossible` | migrate if `LiveMigratable`, otherwise behave like `None` (VM is shut down and restarted elsewhere) |
| `External` | block the drain, set `vmi.status.evacuationNodeName`, let an external controller act (used by cluster-api-provider-kubevirt) |

## How it works (why `oc adm drain` says "429")

1. `virt-api` runs a **validating webhook on all eviction requests** in the cluster (`virt-api-validator`).
   For a virt-launcher pod with `LiveMigrate`/`LiveMigrateIfPossible` (migratable) or `External`, it marks the VMI for
   evacuation (`status.evacuationNodeName`) and **denies the eviction with 429** ("evacuation was triggered");
   `LiveMigrate` + not migratable → plain 429 deny; `None`, or `LiveMigrateIfPossible` + not migratable → 200, evicted.
2. The evacuation controller creates the migration; when it completes, the source pod goes away and drain proceeds.
3. Because the webhook is "fail open" (ignored if virt-api is down), virt-controller also puts **PDBs** on the
   launcher pods that must not be evicted; with virt-api down, VMs stay protected by the PDB but are **not** migrated —
   the drain just hangs.

So "drain keeps retrying with `Cannot evict pod as it would violate the pod's disruption budget`" or 429s is normal
while migrations run — and permanent if a VM can never migrate.

## The classic blocker

`LiveMigrate` + a VM that is not migratable (RWO disk, bridge on pod network, host device…) → alert
**`VMCannotBeEvicted`**, drain and therefore the **MachineConfigPool rollout of an OCP upgrade stops on that node**.
Find them before a maintenance:

```bash
oc get vmi -A -o wide | awk 'NR==1 || $NF=="False"'          # LIVE-MIGRATABLE False
oc get vmi -A -o json | jq -r '.items[] | select(.status.conditions[]? | select(.type=="LiveMigratable" and .status=="False")) | "\(.metadata.namespace)/\(.metadata.name)"'
```

Options: fix the reason (`knowledge/kubevirt/kubevirt-live-migration-requirements-limits-policies-failures.md`), set
that VM's `evictionStrategy` to `None`/`LiveMigrateIfPossible` (accepting a restart), or stop the VM for the window.
Procedure: `runbooks/kubevirt/drain-or-upgrade-a-node-with-running-vms.md`.

## Manual drain flags

The KubeVirt guide uses `--delete-emptydir-data` (old name `--delete-local-data`; launcher pods have emptyDirs),
`--ignore-daemonsets` (virt-handler), `--force` (launcher pods have no ReplicaSet), optionally
`--pod-selector=kubevirt.io=virt-launcher` to move only VMs. The `kubevirt.io/drain` taint of old releases is obsolete.

## Your own PDBs for VM groups

For a PDB over several VMs (e.g. a VirtualMachinePool) use an **absolute `minAvailable`**. `maxUnavailable` or a
percentage `minAvailable` fails because a VMI has no `/scale` subresource: event `CalculateExpectedPodCountFailed …
virtualmachineinstances.kubevirt.io does not implement the scale subresource`, `ALLOWED DISRUPTIONS 0`, and every drain
blocks.

## Scope & caveats

Upstream docs (main, 2026-11) and the OpenShift Virtualization runbook. Behaviour of hosted-cluster NodePools whose
workers are themselves VMs: `knowledge/kubevirt/kubevirt-hypershift-kubevirt-platform-hosted-clusters-on-vms.md`.

## History

- 2026-11-02: created
