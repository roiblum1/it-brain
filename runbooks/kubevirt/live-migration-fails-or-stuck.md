---
title: Diagnose a KubeVirt live migration that fails, is rejected, or never finishes (VMIM Pending/Scheduling forever, not converging, target pod unschedulable)
type: runbook
area: kubevirt
tags: [kubevirt, live-migration, vmim, troubleshooting, livemigratable, converge, post-copy, migration-network, target-pod]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/user-guide docs/compute/live_migration.md; kubevirt/kubevirt pkg/virt-controller/watch/migration/migration.go
---

# Live migration fails or is stuck

**When to use:** a `virtctl migrate` or drain-triggered migration fails or hangs; drains blocked; alert
`KubeVirtVMIExcessiveMigrations`.
**Impact while running:** read-only until "Remediation". Cancelling a migration leaves the VM running on the source.
**Prerequisites:** `oc`/`virtctl` on the cluster. Background: `knowledge/kubevirt/kubevirt-live-migration-requirements-limits-policies-failures.md`.

## Pre-checks

```bash
oc get vmi <vm> -n <namespace> -o wide                               # LIVE-MIGRATABLE
oc get vmi <vm> -n <namespace> -o jsonpath='{.status.conditions[?(@.type=="LiveMigratable")]}{"\n"}'
oc get vmim -n <namespace> --sort-by=.metadata.creationTimestamp
oc get vmi <vm> -n <namespace> -o jsonpath='{.status.migrationState}' | jq
oc get kubevirt -n openshift-cnv -o jsonpath='{.items[0].spec.configuration.migrations}{"\n"}'
```

## Procedure

1. **Rejected at once / `LiveMigratable=False`** — read `reason`/`message` on the condition and fix the cause
   (RWO disk → `DisksNotLiveMigratable`; bridge on pod network → `InterfaceNotLiveMigratable`; host device; CPU mode…).
   These cannot be fixed by retrying.
2. **VMIM stuck in `Pending`** — another migration of this VMI runs (`VMI is not eligible for migration because another
   migration job is in progress.`) or the cluster/node limits (`parallelMigrationsPerCluster`,
   `parallelOutboundMigrationsPerNode`) are saturated — count running VMIMs: `oc get vmim -A | grep -v Succeeded`.
3. **`Scheduling` / target pod `Pending`** — the target virt-launcher cannot be placed:
   ```bash
   oc get pods -n <namespace> -l kubevirt.io/created-by=$(oc get vmi <vm> -n <namespace> -o jsonpath='{.metadata.uid}') -o wide
   oc describe vmim <vmim> -n <namespace> | sed -n '/Events/,$p'
   ```
   Event `Migration target pod for VMI [...] is currently unschedulable.` — free memory on other nodes, matching CPU model
   (`cannot get nodes to migrate VMI with host-model CPU`), affinity, devices. After 5 min unschedulable (15 min pending)
   the controller deletes the target pod and the migration fails.
4. **`Running` for a long time, then `Failed`** — not converging (busy guest, slow link). Look at the progress in
   `migrationState` and the source launcher log (`oc logs <source-launcher> -c compute | grep -i migrat`). Check the
   migration path: pod network or dedicated migration NAD, its bandwidth and MTU
   (`interfaces/virtualization-network-kubevirt-vm-networks.md`), `bandwidthPerMigration`.
5. **Failed with a controller message** — map it: `Migration failed because target pod shutdown during migration`
   (target evicted/OOM — check target node), `source node reported migration failed` (source launcher log has QEMU's
   reason), `Migration failed due to being canceled` (someone deleted the VMIM), in-flight migrations also fail during a
   CNV upgrade (`knowledge/kubevirt/kubevirt-upgrades-hco-workload-updates-outdated-launchers.md`).

## Remediation (with approval)

- Busy VM that never converges: a `MigrationPolicy` matching it with `allowAutoConverge: true` (or `allowPostCopy: true`
  if losing the VM on a failure is acceptable), or retry when the guest is quieter. Configure via GitOps / HyperConverged,
  not by editing the KubeVirt CR (HCO reverts it).
- Cancel a hung migration: `virtctl migrate-cancel <vm> -n <namespace>` (or delete the VMIM).

## Verification

```bash
oc get vmim -n <namespace>                    # Succeeded
oc get vmi <vm> -n <namespace> -o wide        # new node
```

## Rollback

Cancelling returns to the source; MigrationPolicy changes are reverted by removing the policy.

## History

- 2026-11-02: created
