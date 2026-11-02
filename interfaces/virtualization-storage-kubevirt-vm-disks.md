---
title: Virtualization ↔ Storage — what KubeVirt VM disks need from arrays and CSI drivers (RWX Block for live migration, snapshots, CSI clone, thin capacity, StorageProfiles) per backend (Trident, PowerFlex, PowerMax, PowerScale, ODF, Portworx)
type: interface
area: kubevirt
teams: [virtualization, storage, ocp]
tags: [kubevirt, vm-disks, rwx, block, csi-clone, volumesnapshotclass, storageprofile, trident, ontap-san, ontap-nas, powerflex, powermax, powerscale, odf, ceph-rbd, portworx, copy-offload]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization, storage]
source: it-brain-design; CDI pkg/storagecapabilities/storagecapabilities.go for the defaults quoted
---

# Virtualization ↔ Storage: VM disks

> **Draft contract.** The column "CDI assumes" is read from CDI's code (observed); everything the array must really do
> is for the storage team to confirm. Fill the `<…>` cells in an MR approved by all three teams.

## Parties

| Side | Team | Systems |
|---|---|---|
| consumer | `virtualization` | VMs, DataVolumes, golden images (DataSources), CDI, MTV storage maps, VM snapshots/backup |
| platform | `ocp` | CSI drivers, StorageClasses, VolumeSnapshotClasses, StorageProfiles on each cluster |
| provider | `storage` | arrays: ONTAP, PowerFlex, PowerMax, PowerScale, Ceph/ODF; capacity, multi-attach, snapshots, clones |

## What crosses the boundary

VM disks are PVCs, so everything in `interfaces/ocp-storage-netapp-trident.md` and `interfaces/ocp-storage-dell-csm.md`
applies — plus what VMs need on top:

1. **RWX** on every disk for **live migration** (node drains, OCP upgrades, workload updates) — preferably **Block**
   (`knowledge/kubevirt/kubevirt-live-migration-requirements-limits-policies-failures.md`).
2. **VolumeSnapshotClass** per driver for VM snapshots, smart clone and OADP backup.
3. **CSI clone** for fast golden-image cloning (otherwise CDI copies through pods).
4. A **correct StorageProfile** per StorageClass (`knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md`).
5. Capacity planning for **thin** disks that grow, preallocation where performance needs it, and `discard`/`fstrim` passing through.

## Per backend

| Backend | CDI assumes | Array/driver must provide (storage confirms) | Open |
|---|---|---|---|
| Trident ontap-san | RWX Block only; StorageClass needs `backendType: ontap-san` | multi-attach LUNs to all workers; igroups for new nodes | `<…>` |
| Trident ontap-nas | RWX/RWO Filesystem | export policy covering every worker | NFS performance for VM disks `<…>` |
| PowerFlex | RWX/RWO Block, RWO FS; csi-clone | multi-attach; SDC on every worker | `<…>` |
| PowerMax | RWX/RWO Block, RWO FS; csi-clone | masking for all workers | `<…>` |
| PowerScale | RWX/RWO FS; csi-clone | export clients | `<…>` |
| ODF / Ceph RBD | RWX/RWO Block, RWO FS | Windows VMs: StorageClass with `krbd:rxbounce` | `<…>` |
| Portworx | RWX/RWO Block and FS | — | `<…>` |

## Who provides what

| Item | Provided by | Requested how | Lead time |
|---|---|---|---|
| StorageClass(es) for VM disks, one marked `storageclass.kubevirt.io/is-default-virt-class` | ocp, with storage | day2 GitOps | — |
| VolumeSnapshotClass per driver | ocp | day2 GitOps | — |
| StorageProfile overrides where CDI has no defaults | ocp + virtualization | day2 GitOps | — |
| Capacity for VM disk growth and snapshots | storage | `<ticket queue>` | `<…>` |
| Copy offload for MTV (array credentials, SVM) | storage | `<…>` | `<…>` |

## How each side checks its half (read-only)

```bash
oc get storageprofile -o custom-columns=NAME:.metadata.name,MODES:.status.claimPropertySets,CLONE:.status.cloneStrategy
oc get volumesnapshotclass
oc get vmi -A -o wide | awk '$NF=="False"'            # VMs that cannot migrate
```

Storage side: multi-attach sessions per LUN/volume, snapshot reserve usage, clone counts.

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| `DisksNotLiveMigratable`, drains block (virtualization/ocp) | StorageClass gives RWO | StorageProfile and SC parameters |
| DV `ErrClaimNotValid … cannot get access mode from StorageProfile` (virtualization) | ocp: empty StorageProfile | SC parameters (Trident `backendType`) |
| Clones slow, `cloneType: copy` (virtualization) | ocp/storage: no CSI clone / snapshot class | PVC `cloneFallbackReason` |
| VM I/O errors after array failover (virtualization) | storage / network path | `interfaces/storage-network-data-paths.md` |
| VM snapshot `Failed` after 5 min (virtualization) | storage: slow array snapshots | VolumeSnapshot status |

## Open questions

- Which StorageClass is the default for VMs per cluster, and is it RWX Block?
- Do we need preallocation for some VMs (databases)?
- MTV copy offload: which arrays, who holds the credentials?

## History

- 2026-11-02: drafted with the KubeVirt deep dive (`knowledge/kubevirt/README.md`)
