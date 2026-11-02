---
title: KubeVirt VM snapshots and restore (VirtualMachineSnapshot, guest-agent freeze, 5-minute deadline), Clone API, Export API, and backing up VMs with OADP / Velero and the kubevirt-velero-plugin
type: knowledge
area: kubevirt
teams: [storage, ocp]
tags: [kubevirt, snapshot, virtualmachinesnapshot, restore, clone, virtualmachineclone, export, virtualmachineexport, oadp, velero, kubevirt-velero-plugin, backup, volumesnapshotclass, guest-agent, quiesce]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/user-guide docs/storage/{snapshot_restore_api,clone_api,export_api}.md; kubevirt/kubevirt-velero-plugin README.md
---

# Snapshots, clones, export and backup

## VirtualMachineSnapshot / Restore (`snapshot.kubevirt.io`)

- Needs a **VolumeSnapshotClass whose `driver` equals the StorageClass `provisioner`** of each disk, and the Kubernetes
  snapshot API `v1` (`oc get volumesnapshotclass`). Without one, a snapshot still captures the VM **definition** only.
- Online snapshots: if the **guest agent** runs, KubeVirt freezes the guest filesystems, snapshots, then thaws.
  `status.indications`: `Online`, `GuestAgent` (application-consistent), `NoGuestAgent` (crash-consistent),
  `QuiesceFailed` (retry). Only persistent hotplugged disks are included.
- Phases `InProgress` → `Succeeded`/`Failed`; **default deadline 5 minutes** (`failureDeadline`; 0 = none) — a slow array
  snapshot fails the VM snapshot and thaws the guest. Check `status.readyToUse`, `includedVolumes`, `excludedVolumes`.
- Restore: stop the VM, create a `VirtualMachineRestore`, wait for it; then start.

```bash
oc get vmsnapshot -n <namespace>
oc wait vmsnapshot <snap> -n <namespace> --for condition=Ready
oc get vmsnapshot <snap> -n <namespace> -o jsonpath='{.status.indications}{"\n"}'
```

## Clone API (`clone.kubevirt.io/v1beta1`)

`VirtualMachineClone` copies a VM (or a VirtualMachineSnapshot) to a new VM in the **same namespace**, with
label/annotation filters (template filters keep CNI-injected network annotations, e.g. from OVN-K, off the clone), MAC addresses stripped by default (kubemacpool assigns fresh ones; `newMacAddresses` to set them), an auto-generated SMBIOS serial (`newSMBiosSerial` to set it) and optional JSON `patches`. Built on
snapshot/restore, so the same VolumeSnapshotClass prerequisite applies. Use it for "golden VM" workflows. The MCP
`vm_clone` tool creates exactly this object.

## Export API (`VirtualMachineExport`)

Exports a stopped VM's PVC/DataVolume/MemoryDump volumes (or a VM snapshot, or a PVC) through a dedicated export proxy,
with a token Secret in the namespace; status carries internal and external links. Running the VM terminates active
exports (to avoid inconsistent data). Feature gate `VMExport`. Use to move disks to another cluster/site.

## Backup with OADP (Velero) — kubevirt-velero-plugin

The plugin makes Velero back up VMs consistently: it pulls the VM's whole object graph (DataVolumes/PVCs, instance types,
access credentials, launcher pod for running VMIs) into the backup, marks PVCs so CDI does not re-import on restore
(`cdi.kubevirt.io/storage.prePopulated` / `populatedFor`), skips VMIs owned by a VM and always skips virt-launcher pods on
restore. Documented limits:

- **Cluster-scoped objects and network configuration are not backed up** (NADs in the namespace via templates aside):
  StorageClasses, NNCPs, cluster instance types must exist on the restore cluster.
- Tested backup methods: **CSI volume snapshots** and **CSI snapshot data movement** (DataMover). **File-system backup
  (Kopia/Restic) is not tested** with KubeVirt volumes.
- Plugin ↔ Velero ↔ KubeVirt ↔ CDI compatibility matrix in the plugin README (e.g. plugin v0.9 ↔ Velero 1.18).

In OADP the plugin is enabled in the `DataProtectionApplication` as the `kubevirt` default plugin alongside `csi` —
*hypothesis: confirm the DPA field and supported versions in RHOKP (OADP docs)*. Who owns VM backup and whether
Commvault also protects VMs: `interfaces/ocp-storage-backup.md`; OADP area: `knowledge/oadp/README.md`. VM disks on
Block PVCs need the backend's VolumeSnapshotClass to work — `interfaces/virtualization-storage-kubevirt-vm-disks.md`.

## Scope & caveats

Upstream docs and plugin README (main, 2026-11). Snapshot of running VMs is crash-consistent without the guest agent.

## History

- 2026-11-02: created
