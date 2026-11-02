---
title: KubeVirt VM disks — DataVolumes, StorageProfiles, CDI clone strategies (csi-clone, snapshot, copy), Block vs Filesystem, RWX for live migration, filesystem overhead, per backend (Trident, Dell PowerFlex/PowerMax/PowerScale, ODF RBD, Portworx)
type: knowledge
area: kubevirt
teams: [storage, ocp]
tags: [kubevirt, cdi, datavolume, storageprofile, clone, csi-clone, smart-clone, host-assisted, rwx, block, filesystem-overhead, scratch-space, trident, powerflex, powermax, powerscale, odf, ceph-rbd, portworx, preallocation]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/containerized-data-importer doc/{datavolumes,storageprofile,efficient-cloning,scratch-space,waitforfirstconsumer-storage-handling,preallocation}.md and pkg/storagecapabilities/storagecapabilities.go; kubevirt/user-guide docs/storage/*; kubevirt/hyperconverged-cluster-operator docs/cluster-configuration.md
---

# VM disks: DataVolumes, StorageProfiles and our backends

## The pieces

- **PVC** — what the disk really is. `volumeMode: Block` → the PV is passed as a raw device; `Filesystem` → KubeVirt
  stores a `disk.img` file on the volume.
- **DataVolume (DV)** — a CDI object that creates a PVC *and fills it* (import from HTTP/S3/registry/VDDK/ImageIO,
  upload, clone from a PVC or VolumeSnapshot, or blank). VMs normally use `spec.dataVolumeTemplates`, so the DV
  lives and dies with the VM.
- **DataSource / DataImportCron** — named "golden image" pointers and the cron that keeps them fresh from a registry
  (in an air gap the registry is our mirror — `knowledge/registry-mirroring/README.md`).
- **StorageProfile** — CDI creates **one per StorageClass**; it holds the recommended `accessModes`/`volumeMode`
  (`claimPropertySets`, ordered by preference) and the `cloneStrategy`. DataVolumes that use `spec.storage` (not
  `spec.pvc`) fill missing fields from it.

DV phases (`cdi` `doc/datavolumes.md`): `Pending`, `WaitForFirstConsumer`, `PVCBound`, `ImportScheduled`/
`CloneScheduled`/`UploadScheduled`, `ImportInProgress`/`CloneInProgress`/`UploadInProgress`,
`SnapshotForSmartClone`/`SmartClonePVCInProgress`, `CSICloneInProgress`, `CloneFromSnapshotSourceInProgress`,
`Paused` (multi-stage import), `Succeeded`, `Failed`, `Unknown`. Conditions: `Ready`, `Bound`, `Running`.

## StorageProfiles decide most of it

CDI ships recommended capabilities for known provisioners; an **unknown provisioner gets an empty profile**
(`spec: {}`), and then any DV that leaves out `accessModes` fails with the event
`ErrClaimNotValid … DataVolume.storage spec is missing accessMode and cannot get access mode from StorageProfile <sc>`
(or `PVC spec is missing accessMode and no storageClass to choose profile` when there is no StorageClass at all).
The alert for this is `CDIStorageProfilesIncomplete`. Fix: set `spec.claimPropertySets` on the StorageProfile
(when you set `volumeMode` you must also set `accessModes`). Priority order: CDI CR overrides → the DataVolume →
user values in StorageProfile `spec` → CDI's built-in defaults → Kubernetes defaults.

CDI's preferences: **Block over Filesystem** (fewer layers), **RWX over RWO** (live migration).

`cloneStrategy` ∈ `csi-clone` (CSI volume clone — preferred, offloads to the array), `snapshot` (temporary
VolumeSnapshot + restore = "smart clone"), `copy` (host-assisted: a source pod streams data to a target pod — slowest).
Unset → `snapshot` if possible, else `copy`. A StorageClass can force it with the annotation
`cdi.kubevirt.io/clone-strategy: copy|snapshot|csi-clone`.

Efficient cloning needs **same StorageClass and same volumeMode** for source and target, permission on
`datavolumes/source` in the source namespace, and the source not in use; otherwise CDI falls back to host-assisted
copy and says why on the PVC (`cdi.kubevirt.io/cloneFallbackReason: The volume modes of source and target are incompatible`,
event `IncompatibleVolumeModes`). Smart clone additionally needs a VolumeSnapshotClass for the driver.

## Built-in defaults for the backends we have

From CDI's `pkg/storagecapabilities/storagecapabilities.go` (upstream `main`, 2026-11). "Key" is how CDI identifies the
StorageClass — for some drivers it reads StorageClass parameters.

| Backend | CDI key (how detected) | Capabilities CDI assumes | Clone strategy CDI advises | DataImportCron source format |
|---|---|---|---|---|
| Trident ontap-nas | `csi.trident.netapp.io/ontap-nas` (StorageClass parameter `backendType` starts with `ontap-nas`) | RWX file, RWO file | — (default: snapshot if a VolumeSnapshotClass exists) | snapshot |
| Trident ontap-san | `csi.trident.netapp.io/ontap-san` (`backendType` starts with `ontap-san`) | **RWX block only** | — | snapshot |
| Trident, no/other `backendType` | `UNKNOWN` → **empty StorageProfile** | none — DVs without accessModes fail | — | — |
| Dell PowerFlex | `csi-vxflexos.dellemc.com` (`/nfs` variant when fsType is nfs) | RWX block, RWO block, RWO file, ROX block, ROX file | `csi-clone` | — |
| Dell PowerMax | `csi-powermax.dellemc.com` (`/nfs` variant) | RWX block, RWO block, RWO file, ROX block | `csi-clone` | — |
| Dell PowerScale | `csi-isilon.dellemc.com` | RWX file, RWO file, ROX file | `csi-clone` | — |
| ODF / Ceph RBD | `openshift-storage.rbd.csi.ceph.com` (also `rbd.csi.ceph.com`, `rook-ceph.…`) | RWX block, RWO block, RWO file | — | snapshot |
| ODF CephFS | `openshift-storage.cephfs.csi.ceph.com` | RWX file, RWO file | — | — |
| Portworx CSI | `pxd.portworx.com` (`/nfs` when the class is a sharedv4 NFS one) | RWX block, RWX file, RWO block, RWO file | — | — |
| vSphere CSI | `csi.vsphere.vmware.com` | RWO block, RWO file (RWX file only for the `/nfs` variant) | — | — |

Consequences worth knowing:

- **Trident StorageClasses must carry `backendType`** (e.g. `ontap-san`), or CDI cannot recognise them and the
  StorageProfile stays empty. With ontap-san the only default is RWX **Block** — good for live migration; a VM that
  asks for Filesystem on it gets nothing from the profile. With ontap-nas, VM disks are files on NFS (RWX, migratable)
  and the NFS export policy rules from `interfaces/ocp-storage-netapp-trident.md` apply to every node that may run the VM.
- **Dell PowerFlex / PowerMax**: RWX Block is in the defaults and `csi-clone` is advised — the array clones, so
  golden-image clones are fast; PowerFlex still needs the SDC on every node (`interfaces/ocp-storage-dell-csm.md`).
- **ODF RBD**: RWX Block → migratable. For Windows guests on RBD, OpenShift Virtualization warns with
  `VMStorageClassWarning` unless the StorageClass maps with `krbd:rxbounce` (bad crc/signature errors can saturate
  the network); ODF provides `ocs-storagecluster-ceph-rbd-virtualization` with it.
- Whatever CDI assumes, the **driver and array must really support it** (RWX block needs multi-attach on the array
  side): the storage team confirms per backend in `interfaces/virtualization-storage-kubevirt-vm-disks.md`.

Check what a cluster actually has:

```bash
oc get storageprofile                                      # one per StorageClass
oc get storageprofile <sc> -o jsonpath='{.status}' | jq    # claimPropertySets, cloneStrategy, provisioner
oc get sc <sc> -o jsonpath='{.parameters}{"\n"}'           # e.g. backendType for Trident
oc get volumesnapshotclass                                 # driver must match the StorageClass provisioner
```

## Default virtualization StorageClass

If a DV gives no `storageClassName`, CDI prefers the StorageClass annotated
`storageclass.kubevirt.io/is-default-virt-class: "true"` over the cluster default. Alerts:
`CDINoDefaultStorageClass`, `CDIMultipleDefaultVirtStorageClasses`, `CDIDefaultStorageClassDegraded`.

## Sizes: filesystem overhead

With `spec.storage` and a Filesystem volume, CDI requests a PVC of `size × (1 + overhead)` so the image fits next to
the filesystem metadata; with `spec.pvc` the PVC is created as requested and the image ends up about
`size / (1 + overhead)`. The default overhead is documented as **0.06** in CDI's `doc/datavolumes.md` and as
**5.5 %** in HCO's configuration guide — read the effective value from the CDI CR
(`oc get cdi -o jsonpath='{.items[0].status}'` / `spec.config.filesystemOverhead`). Set it in the HyperConverged CR,
globally or per StorageClass (`spec.storage.filesystemOverhead.global`, `.storageClass.<sc>`). Block volumes have no
overhead. MTV's `Unable to resize disk image to required size` (EXT4 on block) is the same family of problem
(`knowledge/kubevirt/kubevirt-mtv-forklift-migrating-vms-from-vmware.md`).

## Scratch space

Registry imports, uploads, some HTTP imports and some others need a temporary PVC. CDI uses
`scratchSpaceStorageClass` (CDI config / HyperConverged `spec.storage.scratchSpaceStorageClass`) if set, else the
StorageClass of the target PVC. Scratch PVCs are **always Filesystem + RWO** — so a Block-only StorageClass (e.g.
Trident ontap-san) cannot provide scratch space: set a Filesystem StorageClass as scratch class.

## WaitForFirstConsumer

With a `volumeBindingMode: WaitForFirstConsumer` StorageClass, CDI does not start the importer until the PVC binds;
the DV sits in phase `WaitForFirstConsumer` and KubeVirt triggers binding when the VM is scheduled. Annotation
`cdi.kubevirt.io/storage.bind.immediate.requested` forces immediate binding (useful for golden images). Feature gate
`HonorWaitForFirstConsumer` is on in the released CDI CR.

## Thin, thick, preallocation, discard

Every disk is passed with `discard=unmap` so `fstrim` in the guest returns space to thin storage. Preallocated
(`spec.preallocation: true` on the DV — CDI annotates the PVC `cdi.kubevirt.io/storage.preallocation: true`) or
annotated thick volumes (`…/storage.thick-provisioned: "true"`) have discard disabled. Disk expansion works when the
StorageClass allows volume expansion; the guest sees the new size, and Filesystem images are grown.

## Hotplug and moving disks between arrays

- Hotplug disks/LUNs into a running VM (feature gate `DeclarativeHotplugVolumes`; `scsi` bus for many disks; few
  VirtIO ports: 3 for ≤ 2 GiB guests, 6 above). Hotplugged volumes can block live migration (`HotplugNotLiveMigratable`).
- **Storage live migration**: set `spec.updateVolumesStrategy: Migration` and point the VM's volumes at new
  PVCs/DVs (any class, Block↔Filesystem allowed, same size or larger) — KubeVirt copies the disks while the VM runs.
  Requires `LiveMigrate` in `workloadUpdateMethods`; follow progress with
  `oc get vmim -l kubevirt.io/volume-update-in-progress=<vm> -w`. This is the tool for moving VMs off one array.

## Debugging CDI

- Keep transfer pods for their logs: DV annotation `cdi.kubevirt.io/storage.pod.retainAfterCompletion: "true"`.
- Verbosity: CDI CR `spec.config.logVerbosity: 4` (restarts CDI components).
- Importer pod names start with `importer-`, cloner `cdi-clone-source…`/`…-source-pod`; events on the DV and PVC tell
  the phase. Procedure: `runbooks/kubevirt/datavolume-import-or-clone-stuck.md`.

## Scope & caveats

Capability table read from CDI `main` on 2026-11-02; older CDI releases may lack entries (check the CDI version in
the installed CNV). CDI's defaults are *recommendations*; the array's real abilities and our StorageClass parameters
win. Confirm per backend with the storage team before relying on RWX Block.

## History

- 2026-11-02: created
