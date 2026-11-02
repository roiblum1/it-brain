---
title: KubeVirt live migration — what makes a VM LiveMigratable (RWX, masquerade, no host devices), limits and timeouts, MigrationPolicies, post-copy and auto-converge, dedicated migration network, reading VMIM phases and failure messages
type: knowledge
area: kubevirt
teams: [network, storage]
tags: [kubevirt, live-migration, vmim, livemigratable, disksnotlivemigratable, interfacenotlivemigratable, migrationpolicy, post-copy, auto-converge, completiontimeoutpergib, progresstimeout, migration-network, host-model]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/user-guide docs/compute/live_migration.md, docs/cluster_admin/migration_policies.md; kubevirt/kubevirt staging/src/kubevirt.io/api/core/v1/types.go, pkg/virt-controller/watch/migration/migration.go; kubevirt/hyperconverged-cluster-operator docs/cluster-configuration.md
---

# Live migration

A migration moves a running VMI to another node: a **target virt-launcher pod** is scheduled, prepared, and the guest
state (RAM, plus non-shared disks for block migration) is streamed from the source. Triggered by a
`VirtualMachineInstanceMigration` (`virtctl migrate <vm>`), by evictions (node drain — see
`knowledge/kubevirt/kubevirt-node-drain-eviction-strategy-and-pdbs.md`), by workload updates after an upgrade, and by
volume updates (`updateVolumesStrategy: Migration`). Cancel: delete the VMIM or `virtctl migrate-cancel <vm>`.

## Is the VM migratable?

At start, KubeVirt computes the VMI condition `LiveMigratable` (`oc get vmi -o wide` → `LIVE-MIGRATABLE`) and the
`migrationMethod` (`LiveMigration` = memory only; `BlockMigration` = some disks are copied too). Migrating a
non-migratable VMI is rejected. Reasons (`reason` on the condition, from the API):

| Reason | Means | Usual fix |
|---|---|---|
| `DisksNotLiveMigratable` | a PVC is not **ReadWriteMany** (and cannot be block-migrated) | RWX StorageClass (`knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md`) |
| `InterfaceNotLiveMigratable` | e.g. `bridge` binding on the pod network — message `cannot migrate VMI which does not use masquerade to connect to the pod network` | masquerade on the pod network |
| `HotplugNotLiveMigratable` | hotplug volumes in use | |
| `CPUModeLiveMigratable` | CPU mode prevents it (e.g. `host-passthrough`) | `host-model` or a named model |
| `VirtIOFSNotLiveMigratable` | virtiofs filesystem shares | |
| `HostDeviceNotLiveMigratable` | PCI host devices (GPU passthrough…) | — (vGPU has its own limits) |
| `SEVNotLiveMigratable`, `TDXNotLiveMigratable`, `SecureExecutionNotLiveMigratable` | confidential computing | — |
| `PersistentReservationNotLiveMigratable` | SCSI persistent reservation requested | |
| `SnapshotOverlaysNotLiveMigratable`, `CPUDRANotLiveMigratable`, `VirtualMachineStateNotLiveMigratable`, `HypervPassthroughNotLiveMigratable`, `NoTSCFrequencyNotLiveMigratable` | newer, rarer cases | read the condition message |
| `NotMigratable` | generic, details in the message | |

Other documented requirements: ports **49152, 49153** free in the virt-launcher pod (don't list them in masquerade
`ports`); the launcher's primary interface has the same name on source and target; post-copy needs extra node
permissions (`vm.unprivileged_userfaultfd=1` — set by MCO on supported OpenShift — plus seccomp/SELinux allowances).

`host-model` CPU VMs can only go to nodes whose CPU supports the same host model; the controller logs
`cannot get nodes to migrate VMI with host-model CPU` / `unable to locate host cpu model, does not contain label …` —
mixed hardware generations in one cluster are the classic cause
(`knowledge/kubevirt/kubevirt-scheduling-performance-cpu-model-dedicated-cpus-hugepages-numa.md`).

## Limits and timeouts

| Setting (KubeVirt CR `spec.configuration.migrations`; HCO: `spec.virtualization.liveMigrationConfig`, older `spec.liveMigrationConfig`) | Means |
|---|---|
| `parallelMigrationsPerCluster` | concurrent migrations in the cluster (5 in both docs) |
| `parallelOutboundMigrationsPerNode` | concurrent outbound per node (user guide: 2; HCO default: 1) — lower converges better, higher drains faster |
| `bandwidthPerMigration` | per-migration cap (user guide: 64Mi/s; HCO: unset) |
| `completionTimeoutPerGiB` | allowed seconds per GiB of guest RAM + migrated disks before abort / switch to post-copy (user guide: 150 → 8 GiB = 1200 s; HCO guide lists 20 with an 800 example) |
| `progressTimeout` | abort if remaining bytes make no progress for this long (150 s) — only catches completely stuck migrations |
| `allowAutoConverge` | throttle guest CPU so pre-copy converges |
| `allowPostCopy` | switch to post-copy at the completion timeout — converges anything, but a network/node failure during post-copy **crashes the VM** |
| `allowWorkloadDisruption` | at the completion timeout: post-copy if allowed, else **pause the VM** until done; unset = same as `allowPostCopy` |
| `network` | a NAD (in the KubeVirt namespace) for a **dedicated migration network**; changing it restarts virt-handler |
| `disableTLS`, `unsafeMigrationOverride`, `nodeDrainTaintKey` | rarely changed |

**Defaults differ between documents and versions** — read the effective values:
`oc get kubevirt -n openshift-cnv -o jsonpath='{.items[0].spec.configuration.migrations}'`, and set them in the
HyperConverged CR (HCO reverts edits to the KubeVirt CR). VMs with explicit CPU limits use single-threaded migration.

Target pod pending: the migration controller deletes a target pod that stays **unschedulable for 5 minutes**
(`unschedulable pod … timeout period exceeded`) or **pending for 15 minutes** for any reason
(`pending pod … timeout period exceeded`); the migration then fails. Per-migration annotations can change both.

## MigrationPolicies

`migrations.kubevirt.io/v1alpha1` `MigrationPolicy` refines the cluster settings for a group of VMs selected by
`namespaceSelector` and/or `virtualMachineInstanceSelector` labels: `allowAutoConverge`, `bandwidthPerMigration`,
`completionTimeoutPerGiB`, `allowPostCopy` (fields left out fall back to the cluster config). Use it for busy
databases (auto-converge / post-copy) without changing every VM.

## Strategies

- **Pre-copy** (default): guest keeps running on the source while memory is copied; safest, cancellable, multithreaded.
  Fails to converge when the guest dirties memory faster than the link copies it.
- **Auto-converge**: pre-copy plus increasing CPU throttling.
- **Post-copy**: guest runs on the target at once, missing pages fetched on demand; no single source of truth — a
  failure loses the VM. Use only when draining matters more than the VM.
- **Stall detection** (alpha, `MigrationStallDetection` gate, v1.9): switches over near a local minimum of remaining bytes.

## Reading a migration

VMIM phases: `Pending` → `Scheduling` → `Scheduled` → `PreparingTarget` → `TargetReady` → `Running` → `Succeeded` /
`Failed` (plus `WaitingForSync`/`Synchronizing` for decentralized migrations). The VMI's `status.migrationState` has
`sourceNode`, `targetNode`, `targetPod`, `completed`, `failed`, `abortRequested`, `abortStatus`, and the effective
`migrationConfiguration`.

Failure events from the migration controller (exact strings): `Migration failed because target pod shutdown during migration`,
`Migration failed vmi shutdown during migration.`, `Migration failed due to being canceled`,
`Migration target pod was removed during active migration.`, `VMI is not eligible for migration because another migration job is in progress.`,
`source node reported migration failed`, `failed to create target pod for vmi <ns>/<vm>, it needs a privileged namespace to run: …`,
`Migration target pod for VMI [<ns>/<vm>] is currently unschedulable.`

```bash
oc get vmim -n <namespace>                                   # phase per migration
oc get vmi <vm> -n <namespace> -o jsonpath='{.status.migrationState}' | jq
oc describe vmim <name> -n <namespace>                       # events
oc get pods -n <namespace> -l kubevirt.io/created-by=<vmi-uid> -o wide   # source + target launcher pods
```

Procedure: `runbooks/kubevirt/live-migration-fails-or-stuck.md`. Alert `KubeVirtVMIExcessiveMigrations`: a VMI
migrated more than 12 times in 24 h — look for node pressure or network trouble.

## Cross-team

- Migration traffic goes between **nodes** (pod network, or the dedicated migration NAD); bandwidth and MTU on that
  path are the network team's — `interfaces/virtualization-network-kubevirt-vm-networks.md`.
- RWX Block per array — `interfaces/virtualization-storage-kubevirt-vm-disks.md`.

## Scope & caveats

Upstream KubeVirt `main` (2026-11) plus HCO docs; defaults quoted where the docs disagree. Check RHOKP for the CNV
version's defaults.

## History

- 2026-11-02: created
