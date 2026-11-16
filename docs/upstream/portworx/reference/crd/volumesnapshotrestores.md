# VolumeSnapshotRestore CRD reference

Source: https://docs.portworx.com/portworx-enterprise/reference/crd/volumesnapshotrestores (Portworx Enterprise latest)

VolumeSnapshotRestore CRD reference | Portworx Enterprise Documentation

VolumeSnapshotRestore crd spec for in-place restore of volume.

## VolumeSnapshotRestore​

FieldDescriptionType

`apiVersion`APIVersion defines the versioned schema of this representation of an object.
Servers should convert recognized schemas to the latest internal value, and
may reject unrecognized values.
More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources`string`

`kind`Kind is a string value representing the REST resource this object represents.
Servers may infer this from the endpoint the client submits requests to.
Cannot be updated.
In CamelCase.
More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds`string`

`spec`VolumeSnapshotRestoreSpec for in-place volume restore`object`

`status`VolumeSnapshotRestoreStatus of volume`object`

### `spec` fields​

FieldDescriptionType

`spec.groupSnapshot`GroupSnapshot true if snapshot volumegroupsnapshot`boolean`

`spec.pvcs`DestinationPVC list to restore snapshot`object`

`spec.sourceName`SourceName of snapshot`string`

`spec.sourceNamespace`SourceNameSpace is snapshot namespace`string`

### `status` fields​

FieldDescriptionType

`status.cleanupDone`CleanupDone is set once the driver has successfully cleaned up the
temporary in-place restore objects for a Failed restore. Without it the
controller cannot tell a first cleanup from a repeat one and re-invokes
the driver on every reconcile, forever.`boolean`

`status.reason`Reason is the reason the restore terminally failed. The per-volume
Reason in Volumes[] is only populated once that list exists, so a
failure before then (e.g. the source snapshot not being found at the
Initial stage) has nowhere else to record why.`string`

`status.status`Status of volume restore`string`

`status.volumes`Volumes list of volume restore information`array`

`status.volumes.status`VolumeSnapshotRestoreStatusType is the status of volume in-place restore`string`

In this topic:
