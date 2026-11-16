# Configure FlashArray as a Direct Access volume

Source: https://docs.portworx.com/portworx-enterprise/provision-storage/create-pvcs/pure-flasharray (Portworx Enterprise latest)

Configure FlashArray as a Direct Access volume | Portworx Enterprise Documentation

On-premises users who want to use FlashArray with Portworx on Kubernetes can attach FlashArray as a Direct Access volume. Used in this way, Portworx directly provisions FlashArray volumes, maps them to a user PVC, and mounts them to pods. Once mounted, the application writes data directly onto FlashArray. As a result, this mounting method does not use storage pools.

FlashArray Direct Access volumes support the following CSI operations:

- Basic filesystem operations: create, mount, expand, clone, unmount, delete

- Mount options: Configure file system mount options

- Snapshots

- Quality of service (QoS) settings (requires at least one FlashArray with Purity version 5.3.0 or newer and REST API version 1.17 or newer)

note

- If you enable the FA/FB driver, Portworx Enterprise uses it to provision and manage your FlashArray Direct Access volumes. For more information, see FlashArray and FlashBlade Features.

- Portworx recommends installing Portworx with FlashArray Cloud Drive before using FlashArray Direct Access volumes.

- Portworx supports encryption of FlashArray Direct Access volumes. For more information, see Create encrypted PVCs in FlashArray

- FlashArray Direct Access volumes have the following limitations:

- Raw Block volumes are intended only for the KubeVirt VM use case. For other scenarios, contact support before deployment.

- Volume import and CSI ephemeral volumes are not supported.

- The `kube_datastore_affinity` StorageClass parameter is not supported. FlashArray Direct Access volumes are not placed on Portworx storage pools, so Kube Datastore (KDS) affinity does not apply.

- `CreateOperations` is not honored by Portworx.

Once you’ve configured Portworx to work with your FlashArray, you can create a StorageClass and reference it in any PVCs you create.

## Create a StorageClass​

Depending on your environment, you can create StorageClass with specific parameters to enable secure multi-tenancy, provision volumes on a specific FlashArray, or in a specific FlashArray realm.

### Provision volumes on FlashArray​

Create a StorageClass spec and set `parameters.backend` to `"pure_block"`. For secure multi-tenancy, set the `pure_fa_pod_name` parameter to the FlashArray pod. Here are example StorageClass spec:

- FlashArray without secure multi-tenancy

- FlashArray with secure multi-tenancy

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: sc-portworx-fa-direct-access

provisioner: pxd.portworx.com

parameters:

  backend: "pure_block"

  max_iops: "1000"

  max_bandwidth: "1G"

allowVolumeExpansion: true

```

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: sc-portworx-fa-direct-access

provisioner: pxd.portworx.com

parameters:

  backend: "pure_block"

  max_iops: "1000"

  max_bandwidth: "1G"

  pure_fa_pod_name: "<fa-pod-name>"

allowVolumeExpansion: true

```

### Provision volumes on a specific FlashArray​

By default, Portworx Enterprise selects a FlashArray for each Direct Access volume. If your environment includes multiple FlashArrays, you can provision all volumes created by a `StorageClass` on a specific array by setting the `storage_backend` parameter to the FlashArray name or fully qualified domain name (FQDN). This is useful to place volumes based on performance, capacity, or organizational requirements.

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: sc-portworx-fa-direct-access

provisioner: pxd.portworx.com

parameters:

  backend: "pure_block"

  storage_backend: "<fa-name-or-fqdn>"

allowVolumeExpansion: true

```

Replace `<fa-name-or-fqdn>` with the name or FQDN of the FlashArray you want to use. All PVCs that reference this StorageClass are provisioned on that array.

note

- `storage_backend` selects the target FlashArray, while `pure_fa_pod_name` places volumes in a specific pod for secure multi-tenancy. These parameters address different placement needs.

- If you enable the FA/FB driver, the equivalent capability is provided by the `portworx.io/pure-array-id` StorageClass parameter or PVC annotation. For more information, see Control volume placement using array ID.

### Provision volumes on a specific FlashArray realm​

Prerequisites

- Portworx 3.7.0 or later is installed and running.

- Array-level hosts is shared with the target realm on the FlashArray before deploying workloads that reference this StorageClass.

Create a StorageClass and specify the target realm using the `pure_fa_realm` StorageClass parameter alongside `pure_fa_pod_name`. `pure_fa_realm` requires `pure_fa_pod_name` to also be set.

The following example StorageClass provisions FlashArray Direct Access volumes in a specific realm:

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: fada-realm

parameters:

  backend: "pure_block"

  pure_fa_pod_name: "<pod-name>"

  pure_fa_realm: "<realm-name>"

provisioner: pxd.portworx.com

reclaimPolicy: Delete

volumeBindingMode: WaitForFirstConsumer

```

Replace `<pod-name>` with the name of the FlashArray pod and `<realm-name>` with the name of the target realm. If `pure_fa_pod_name` is omitted, volume provisioning fails with the following error:

```

StorageClass parameter "pure_fa_realm" requires "pure_fa_pod_name" to be set

```

## Create a PVC​

Create a PersistentVolumeClaim and reference the StorageClass you created by entering the name that you gave your StorageClass in the `spec.storageClassName` field. For example:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

  name: pure-claim-block

  labels:

    app: nginx

spec:

  accessModes:

    - ReadWriteOnce

  resources:

    requests:

      storage: 20Gi

  storageClassName: sc-portworx-fa-direct-access

```

## Mount to a pod​

Create a Pod and reference the PVC you created by entering the name you gave your PVC in the `persistentVolumeClaim.claimName` field. For example:

```

kind: Pod

apiVersion: v1

metadata:

  name: nginx-pod

  labels:

    app: nginx

spec:

  volumes:

  - name: pure-vol

    persistentVolumeClaim:

      claimName: pure-claim-block

  containers:

  - name: nginx

    image: nginx

    volumeMounts:

    - name: pure-vol

      mountPath: /data

    ports:

    - containerPort: 80

```

Once you apply the Pod, you can use `watch kubectl get pods` for Kubernetes and `watch oc get pods` for OpenShift to look for a `STATUS` of `Running`. Once the pod is running, you can see it as a connected host for your volume.

## Clone a PVC​

To clone a PVC, create a PersistentVolumeClaim with `dataSource.kind` set to `PVC` and `dataSource.name` set to the name of the PVC you wish to clone. For example:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

  name: pvc-clone

spec:

  accessModes:

    - ReadWriteOnce

  resources:

    requests:

      storage: 20Gi

  storageClassName: sc-portworx-fa-direct-access

  dataSource:

    kind: PersistentVolumeClaim

    name: pure-claim-block

```

## Take a snapshot​

To take a snapshot, perform the following steps:

-
Create a SnapshotClass with `driver` set to `pxd.portworx.com`. For example:

```

kind: VolumeSnapshotClass

apiVersion: snapshot.storage.k8s.io/v1

metadata:

  name: px-fa-direct-access-snapshotclass

  annotations:

    snapshot.storage.kubernetes.io/is-default-class: "true"

driver: pxd.portworx.com

deletionPolicy: Delete

```

-
Create a VolumeSnapshot where `volumeSnapshotClassName` is set to the name you gave your VolumeSnapshotClass, and `source.persistentVolumeClaimName` is set to the name you gave your volume. For example:

```

kind: VolumeSnapshot

apiVersion: snapshot.storage.k8s.io/v1

metadata:

  name: volumesnapshot-of-pure-claim-block

spec:

  volumeSnapshotClassName: px-fa-direct-access-snapshotclass

  source:

    persistentVolumeClaimName: pure-claim-block

```

Once you have applied the VolumeSnapshot to create a snapshot, you can view the snapshot with `kubectl get volumesnapshot` or in the array UI under Volume Snapshots, where it has the same functions as other types of Pure snapshots.

note

- If you do not see your VolumeSnapshot when you run `kubectl get volumesnapshot`, run `kubectl get crd` to get the full path of the CRD, then use that full path in your `kubectl get` command. For example:

- Kubernetes

- Openshift

```

kubectl get volumesnapshots.snapshot.storage.k8s.io

```

```

oc get volumesnapshots.snapshot.storage.k8s.io

```

- A snapshot of a volume that has not been attached will be completely empty. It will include no filesystem, making it unattachable. If you want an attachable but empty snapshot with a filesystem, attach and detach the volume before taking the snapshot.

## Restore a snapshot​

To restore a snapshot to a new PVC, create a PersistentVolumeClaim with `dataSource.kind` set to `VolumeSnapshot` and `dataSource.name` set to the name of your VolumeSnapshot. For example:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

  name: pvc-restore

spec:

  accessModes:

    - ReadWriteOnce

  resources:

    requests:

      storage: 20Gi

  storageClassName: sc-portworx-fa-direct-access

  dataSource:

    kind: VolumeSnapshot

    name: volumesnapshot-of-pure-claim-block

    apiGroup: snapshot.storage.k8s.io

```

Once you have applied the PersistentVolumeClaim to create a PVC, you can view it with `kubectl get pvc` or in the array UI. The array UI shows under Details that the source of the new PVC is the PVC from which the snapshot was made.

## Expand a PVC​

To expand a PVC of a FlashArray direct access volume, run the command `kubectl edit pvc <pvcName>`, then change the size in the spec.

## Delete a PVC​

To delete a PVC of a FlashArray direct access volume, use the following command:

- Kubernetes

- Openshift

```

kubectl delete pvc <pvcName>

```

```

oc delete pvc <pvcName>

```

## Related topics​

CSI topology for FlashArray and FlashBlade Direct Access volumes

In this topic:
