---
title: Unstick a CDI DataVolume import, upload or clone (Pending, ErrClaimNotValid, ImportInProgress forever, CloneInProgress, host-assisted fallback, scratch space)
type: runbook
area: kubevirt
teams: [storage]
tags: [kubevirt, cdi, datavolume, import, clone, upload, storageprofile, errclaimnotvalid, scratch-space, importer, waitforfirstconsumer]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/containerized-data-importer doc/{datavolumes,storageprofile,efficient-cloning,scratch-space,debug,waitforfirstconsumer-storage-handling}.md and pkg/controller/datavolume/util.go
---

# DataVolume import / clone stuck

**When to use:** VM `Provisioning`/`DataVolumeError`, DV not reaching `Succeeded`, golden image (DataImportCron) not
updating (`CDIDataImportCronOutdated`).
**Impact while running:** read-only until step 6.
**Prerequisites:** `oc`. Background: `knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md`.

## Pre-checks

```bash
oc get dv -n <namespace>                                     # PHASE, PROGRESS
oc describe dv <dv> -n <namespace> | sed -n '/Status/,$p'
oc get pvc -n <namespace> | grep <dv>
oc get pods -n <namespace> | grep -E 'importer|cdi-upload|clone'
oc get storageprofile <storageclass> -o jsonpath='{.status}' | jq
```

## Procedure

1. **`Pending` + event `ErrClaimNotValid`** — read the message:
   `DataVolume.storage spec is missing accessMode and cannot get access mode from StorageProfile <sc>` → the StorageProfile
   is empty (unknown provisioner, or a Trident class without `backendType`). Either give the DV explicit
   `accessModes`/`volumeMode`, or (better, with the storage team) fill the StorageProfile:
   ```bash
   oc patch storageprofile <sc> --type=merge -p '{"spec":{"claimPropertySets":[{"accessModes":["ReadWriteMany"],"volumeMode":"Block"}]}}'
   ```
   (values from `interfaces/virtualization-storage-kubevirt-vm-disks.md`, not guesses). `ContentType Archive cannot have block volumeMode`
   → archive imports need Filesystem.
2. **`WaitForFirstConsumer`** — normal for WFFC StorageClasses until a VM using it is scheduled. For an image no VM uses
   yet, annotate `cdi.kubevirt.io/storage.bind.immediate.requested: "true"`.
3. **PVC `Pending`** — a CSI/provisioner problem, not CDI: `oc describe pvc` events → the backend
   (`interfaces/ocp-storage-netapp-trident.md`, `interfaces/ocp-storage-dell-csm.md`).
4. **Import in progress forever / failing** — importer pod logs:
   ```bash
   oc logs -n <namespace> importer-<dv>          # or the pod listed above
   ```
   Source URL not reachable from the cluster (air gap: only our mirrors/registries), TLS (`certConfigMap`), checksum,
   registry auth (`secretRef`). If the pod is gone, recreate with annotation `cdi.kubevirt.io/storage.pod.retainAfterCompletion: "true"`
   to keep its logs. **Scratch space**: registry imports and uploads need a Filesystem RWO scratch PVC — on a Block-only
   class set `scratchSpaceStorageClass` (HyperConverged `spec.storage`) to a Filesystem class.
5. **Clone slow** — check what CDI chose: `oc get pvc <target> -o yaml | grep cdi.kubevirt.io/clone` —
   `cloneType: copy` with `cloneFallbackReason` means host-assisted copy (different StorageClass or volumeMode, no
   VolumeSnapshotClass, source in use). Align class/mode or set the right `cloneStrategy` on the StorageProfile.
6. **Restart** — delete and recreate the DV (or the VM's dataVolumeTemplate DV) after fixing; a VM with
   `dataVolumeTemplates` recreates it.

## Verification

```bash
oc get dv <dv> -n <namespace>           # Succeeded, 100.0%
oc get pvc <dv> -n <namespace>          # Bound
```

## Rollback

StorageProfile patches: `oc patch storageprofile <sc> --type=json -p '[{"op":"remove","path":"/spec/claimPropertySets"}]'`.

## History

- 2026-11-02: created
