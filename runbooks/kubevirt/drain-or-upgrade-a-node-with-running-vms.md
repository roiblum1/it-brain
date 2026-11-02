---
title: Drain a node or run an OCP / OpenShift Virtualization upgrade on a cluster with running VMs without getting stuck (VMCannotBeEvicted, MCP rollout blocked)
type: runbook
area: kubevirt
teams: [ocp]
tags: [kubevirt, drain, upgrade, mco, machineconfigpool, eviction, vmcannotbeevicted, live-migration, maintenance, capacity]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/kubevirt docs/handling-eviction-requests.md, docs/updates.md; kubevirt/user-guide docs/cluster_admin/node_maintenance.md; openshift/runbooks VMCannotBeEvicted, OutdatedVirtualMachineInstanceWorkloads
---

# Drain / upgrade with running VMs

**When to use:** node maintenance, OCP upgrade (MCO drains every node), OpenShift Virtualization upgrade.
**Impact while running:** VMs live-migrate (brief pause at switchover); non-migratable VMs restart if you allow it.
**Prerequisites:** cluster-admin; an agreed window with VM owners; no CNV upgrade and OCP upgrade at the same time.
Background: `knowledge/kubevirt/kubevirt-node-drain-eviction-strategy-and-pdbs.md`,
`knowledge/kubevirt/kubevirt-upgrades-hco-workload-updates-outdated-launchers.md`.

## Pre-checks

```bash
oc get hyperconverged -n openshift-cnv -o jsonpath='{.items[0].spec.virtualization.evictionStrategy}{"\n"}'   # v1 API; older: .spec.evictionStrategy
oc get vmi -A -o wide | awk 'NR==1 || $NF=="False"'          # not live-migratable
oc get vmi -A -o json | jq -r '.items[] | "\(.metadata.namespace)/\(.metadata.name) \(.spec.evictionStrategy // "cluster-default")"'
oc adm top nodes                                             # spare memory for one node's VMs
oc get vmim -A | grep -vE 'Succeeded|Failed'                 # nothing in flight
oc get pdb -A | awk '$4==0'                                  # PDBs allowing 0 disruptions (own PDBs with maxUnavailable?)
```

## Procedure

1. **Handle every non-migratable VM** found above, with its owner: fix the cause, or set its `evictionStrategy` to
   `LiveMigrateIfPossible`/`None` (it will be shut down and restarted elsewhere), or stop it for the window. Otherwise
   the drain — and the MCP rollout — stops on its node (`VMCannotBeEvicted`).
2. **Capacity** — the remaining nodes must hold the drained node's VMs (memory is not overcommitted). Consider lowering
   MCP `maxUnavailable` to 1 on VM-heavy pools.
3. **Drain** (manual maintenance):
   ```bash
   oc adm cordon <node>
   oc adm drain <node> --ignore-daemonsets --delete-emptydir-data --force --timeout=30m
   ```
   429 / PDB messages while migrations run are expected. Watch: `oc get vmim -A -w`.
   For an OCP upgrade, MCO does this per node; watch `oc get mcp` and the VMIMs.
4. **If a node stays `SchedulingDisabled` with launcher pods** — find which VM: `oc get pods -A -o wide --field-selector spec.nodeName=<node> | grep virt-launcher`,
   then `runbooks/kubevirt/live-migration-fails-or-stuck.md`.
5. **After a CNV upgrade** — outdated launchers: `oc get vmi -A -l kubevirt.io/outdatedLauncherImage`; with
   `workloadUpdateMethods: [LiveMigrate]` they migrate by themselves; non-migratable ones need a planned restart.
6. `oc adm uncordon <node>` when done (manual maintenance).

## Verification

```bash
oc get nodes                                   # all Ready, schedulable
oc get vm -A | grep -v Running                 # only VMs that should be stopped
oc get vmi -A -l kubevirt.io/outdatedLauncherImage   # empty after a CNV upgrade
```

## Rollback

Uncordon the node. VMs that were stopped or switched to `None` for the window: restore their evictionStrategy / start them.

## History

- 2026-11-02: created
