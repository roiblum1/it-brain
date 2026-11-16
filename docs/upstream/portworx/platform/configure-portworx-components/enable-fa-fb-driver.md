# FlashArray/FlashBlade Driver

Source: https://docs.portworx.com/portworx-enterprise/platform/configure-portworx-components/enable-fa-fb-driver (Portworx Enterprise latest)

FlashArray/FlashBlade Driver | Portworx Enterprise Documentation

Portworx Enterprise includes the FlashArray/FlashBlade (FA/FB) driver, a component that provides enhanced storage capabilities for FlashArray Direct Access (FADA), FlashBlade Direct Access (FBDA), and FlashArray File volumes. The driver supports Kubernetes-native provisioning, attachment, snapshots, and other volume lifecycle operations.

Enable the FA/FB driver to use the FlashArray and FlashBlade capabilities described in this topic. For more information, see Enable the FA/FB driver.

note

Some configuration fields and Kubernetes resources use `csi` in their names, such as the `portworx.io/pure-csi-integration` annotation and `px-pure-csi-node` DaemonSet. These names are part of the Portworx Enterprise implementation and do not require a separate product installation.

## Features available with the FA/FB Driver​

- Portworx Enterprise 3.7.0

- Portworx Enterprise 3.7.1

- Portworx Enterprise 3.7.2

When you enable the FA/FB driver, the following FlashArray and FlashBlade features become available in your Portworx cluster:

- Shared NFS volumes from FlashArray File Services with `ReadWriteMany` (RWX) access, directory quotas, and encrypted NFS transport

- Shared raw block FADA volumes with read-write attachment to multiple nodes for KubeVirt VM live migration

- FlashArray File volumes for persistent virtual Trusted Platform Module (vTPM) state and KubeVirt VM live migration

- Static provisioning of existing FlashArray volumes, FlashArray File Services directories, and FlashBlade file systems through Kubernetes PVCs

- FlashArray and FlashBlade snapshots as Kubernetes `VolumeSnapshot` resources, including FlashBlade snapshot policies

- Replication of FADA volume snapshots to another FlashArray and provisioning of volumes from remote snapshots

- FADA volumes in synchronously replicated ActiveCluster pods, with storage paths through both member FlashArrays

- FlashArray volume attachment over iSCSI, Fibre Channel, NVMe/TCP, or NVMe over Fibre Channel, with support for different transports on individual nodes

- Kernel-native NVMe multipathing with stable device paths

- Parallel attachment of multiple Direct Access volumes to reduce attachment time at scale

- Per-node volume attachment limits advertised to Kubernetes

- FlashBlade//EXA file systems with GPUDirect Storage through remote direct memory access (RDMA) NFS

- Prometheus metrics for volume capacity and node storage connectivity, Grafana dashboards, Pure1 diagnostic information, and storage inspection through the `kubectl px csi` CLI

### Provision storage​

FeatureDescriptionReference

FlashArray File ServicesProvisions shared NFS volumes from FlashArray File Services with `ReadWriteMany` (RWX) access. Supports directory quota policies and encrypted NFS transport through `StorageClass` mount options.Dynamic provisioning of FlashArray File Services

FlashArray block volumesProvisions FADA block volumes, including volumes in synchronously replicated ActiveCluster pods.Dynamic provisioning of FlashArray block volumes

FlashBlade file systemsProvisions FBDA NFS file systems, including FlashBlade//EXA file systems associated with a data node group. Supports exports through multi-tenancy servers and Purity realms.Dynamic provisioning of FlashBlade file systems

Static provisioningMakes an existing FlashArray volume, FlashArray File Services directory, or FlashBlade file system available through a Kubernetes PVC without provisioning new storage.Static provisioning

Shared raw block volumes for KubeVirtAllows a FADA volume to be attached as a read-write raw block device to multiple nodes, supporting KubeVirt live migration.Raw block volumes for live migration

FlashArray File for vTPMUses FlashArray File Services volumes to store persistent state for virtual machines that use a virtual Trusted Platform Module (vTPM), supporting VM live migration.FlashArray File for live migration with vTPM

Volume placement by arrayPlaces volumes created from a `StorageClass` on a specific FlashArray by using its array ID.Control volume placement using array ID

CSI topologyRestricts volume provisioning and attachment based on the nodes and zones that can access a storage backend.Enable CSI topology

ActiveClusterProvisions FADA volumes in an ActiveCluster pod and provides paths to the volumes through both member FlashArrays.Use FlashArray ActiveCluster

Subnet-aware iSCSIRestricts iSCSI sessions to subnets accessible from each node.Configure subnet-aware iSCSI

### Manage provisioned storage​

FeatureDescriptionReference

FlashArray snapshotsCreates, deletes, and restores FlashArray snapshots as Kubernetes `VolumeSnapshot` resources. You can also replicate snapshots to another FlashArray, and provision volumes from the remote snapshots.Snapshot a FlashArray volume

FlashBlade snapshotsCreates on-demand snapshots of FBDA file systems, optionally by using a FlashBlade snapshot policy, and restores snapshots to new file systems.Snapshot a FlashBlade volume

PVC cloningCreates a new PVC from an existing Direct Access PVC.Clone a PVC

PVC resizeExpands a Direct Access PVC and its corresponding volume on the storage system.Resize a PVC

PVC deletionDeletes Direct Access PVCs and handles storage-specific dependencies, such as existing snapshots, FlashBlade snapshot policies, and FlashArray File managed directories.Delete a PVC

Backup and restoreRebuilds missing `PureVolume` and `PureSnapshot` custom resources from the storage system to support resource-only backup and restore of Direct Access volumes.Backup and restore

Portworx Enterprise continues to manage FADA CloudSnap backup and restore operations.

### Monitor and troubleshoot​

FeatureDescriptionReference

Volume and storage metricsExports volume usage and capacity metrics for FADA and FBDA volumes and node-level health metrics for storage connectivity to Prometheus.Monitor storage

Grafana dashboardsProvides Grafana dashboards for monitoring FlashArray and FlashBlade storage metrics.Grafana dashboards

Pure1 telemetrySends FA/FB driver logs and diagnostic information to Pure1 through Portworx Enterprise telemetry.Telemetry

CLIProvides cluster status, image, diagnostic, backend credential, volume, and snapshot operations through the `kubectl px csi` command.CLI reference

### Configure storage connectivity​

FeatureDescriptionReference

Storage transportsSupports FlashArray volume attachment over iSCSI, Fibre Channel, NVMe/TCP, and NVMe-oF, with transport configuration available per node.Prepare FlashArray

Native NVMe multipathingSupports kernel-native NVMe multipathing with stable device paths as an alternative to device-mapper multipathing.Prepare FlashArray

Volume attachment limitsAdvertises per-node volume attachment limits to the kubelet.Volume attachment limits

GPUDirect StoragePasses remote direct memory access (RDMA) NFS mount options to FBDA mounts to support GPUDirect Storage.StorageClass reference

In addition to all the features available with Portworx Enterprise 3.7.0 :

- Cross-array snapshots that transfer a FlashArray block volume snapshot asynchronously to a different FlashArray in the same cluster. For more information, see Cross-array snapshot.

note

Creating cross-array snapshots requires Portworx Operator 26.4.0 or later.

### Provision storage​

FeatureDescriptionReference

FlashArray File ServicesProvisions shared NFS volumes from FlashArray File Services with `ReadWriteMany` (RWX) access. Supports directory quota policies and encrypted NFS transport through `StorageClass` mount options.Dynamic provisioning of FlashArray File Services

FlashArray block volumesProvisions FADA block volumes, including volumes in synchronously replicated ActiveCluster pods.Dynamic provisioning of FlashArray block volumes

FlashBlade file systemsProvisions FBDA NFS file systems, including FlashBlade//EXA file systems associated with a data node group. Supports exports through multi-tenancy servers and Purity realms.Dynamic provisioning of FlashBlade file systems

Static provisioningMakes an existing FlashArray volume, FlashArray File Services directory, or FlashBlade file system available through a Kubernetes PVC without provisioning new storage.Static provisioning

Shared raw block volumes for KubeVirtAllows a FADA volume to be attached as a read-write raw block device to multiple nodes, supporting KubeVirt live migration.Raw block volumes for live migration

FlashArray File for vTPMUses FlashArray File Services volumes to store persistent state for virtual machines that use a virtual Trusted Platform Module (vTPM), supporting VM live migration.FlashArray File for live migration with vTPM

Volume placement by arrayPlaces volumes created from a `StorageClass` on a specific FlashArray by using its array ID.Control volume placement using array ID

CSI topologyRestricts volume provisioning and attachment based on the nodes and zones that can access a storage backend.Enable CSI topology

ActiveClusterProvisions FADA volumes in an ActiveCluster pod and provides paths to the volumes through both member FlashArrays.Use FlashArray ActiveCluster

Subnet-aware iSCSIRestricts iSCSI sessions to subnets accessible from each node.Configure subnet-aware iSCSI

### Manage provisioned storage​

FeatureDescriptionReference

FlashArray snapshotsCreates, deletes, and restores FlashArray snapshots as Kubernetes `VolumeSnapshot` resources. You can also replicate snapshots to another FlashArray, create cross-array snapshots, and provision volumes from the remote snapshots.Snapshot a FlashArray volume

FlashBlade snapshotsCreates on-demand snapshots of FBDA file systems, optionally by using a FlashBlade snapshot policy, and restores snapshots to new file systems.Snapshot a FlashBlade volume

PVC cloningCreates a new PVC from an existing Direct Access PVC.Clone a PVC

PVC resizeExpands a Direct Access PVC and its corresponding volume on the storage system.Resize a PVC

PVC deletionDeletes Direct Access PVCs and handles storage-specific dependencies, such as existing snapshots, FlashBlade snapshot policies, and FlashArray File managed directories.Delete a PVC

Backup and restoreRebuilds missing `PureVolume` and `PureSnapshot` custom resources from the storage system to support resource-only backup and restore of Direct Access volumes.Backup and restore

Portworx Enterprise continues to manage FADA CloudSnap backup and restore operations.

### Monitor and troubleshoot​

FeatureDescriptionReference

Volume and storage metricsExports volume usage and capacity metrics for FADA and FBDA volumes and node-level health metrics for storage connectivity to Prometheus.Monitor storage

Grafana dashboardsProvides Grafana dashboards for monitoring FlashArray and FlashBlade storage metrics.Grafana dashboards

Pure1 telemetrySends FA/FB driver logs and diagnostic information to Pure1 through Portworx Enterprise telemetry.Telemetry

CLIProvides cluster status, image, diagnostic, backend credential, volume, and snapshot operations through the `kubectl px csi` command.CLI reference

### Configure storage connectivity​

FeatureDescriptionReference

Storage transportsSupports FlashArray volume attachment over iSCSI, Fibre Channel, NVMe/TCP, and NVMe-oF, with transport configuration available per node.Prepare FlashArray

Native NVMe multipathingSupports kernel-native NVMe multipathing with stable device paths as an alternative to device-mapper multipathing.Prepare FlashArray

Volume attachment limitsAdvertises per-node volume attachment limits to the kubelet.Volume attachment limits

GPUDirect StoragePasses remote direct memory access (RDMA) NFS mount options to FBDA mounts to support GPUDirect Storage.StorageClass reference

In addition to the features available in Portworx Enterprise 3.7.1, this release includes the following capabilities:

- You can use an ActiveCluster stretched pod that connects two FlashArray realms, one on each array, to provision FlashArray Direct Access (FADA) volumes over iSCSI or Fibre Channel (FC). Realms provide secure multi-tenancy on FlashArray. For more information, see Use FlashArray ActiveCluster.

- Portworx automatically creates a quota policy based on the size requested in a PVC and applies it to the volume's directory on FlashArray File Services. This limits the volume to the requested size. Previously, the quota policy specified in the `StorageClass` applied to every volume created from it. For more information, see Configure FA File PVC size enforcement.

note

PVC size enforcement requires Purity 6.7.1 or later.

- You can restore a FlashBlade Direct Access (FBDA) snapshot to a new volume without changing the source file system. Portworx creates the new volume from the snapshot. For more information, see Restore from a snapshot.

note

Restoring a FlashBlade snapshot to a new volume requires Purity//FB 4.8.0 or later.

- Support for SUSE Virtualization (Harvester) 1.8.x. For more information, see Compatibility and Interoperability Matrix.

### Provision storage​

FeatureDescriptionReference

FlashArray File ServicesProvisions shared NFS volumes from FlashArray File Services with `ReadWriteMany` (RWX) access. Supports directory quota policies and encrypted NFS transport through `StorageClass` mount options.Dynamic provisioning of FlashArray File Services

FlashArray File Services PVC size enforcementCreates a quota policy that matches the size requested in the PVC and applies it to the volume's directory, which limits the volume to the requested size.Configure FA File PVC size enforcement

FlashArray block volumesProvisions FADA block volumes, including volumes in synchronously replicated ActiveCluster pods.Dynamic provisioning of FlashArray block volumes

FlashBlade file systemsProvisions FBDA NFS file systems, including FlashBlade//EXA file systems associated with a data node group. Supports exports through multi-tenancy servers and Purity realms.Dynamic provisioning of FlashBlade file systems

Static provisioningMakes an existing FlashArray volume, FlashArray File Services directory, or FlashBlade file system available through a Kubernetes PVC without provisioning new storage.Static provisioning

Shared raw block volumes for KubeVirtAllows a FADA volume to be attached as a read-write raw block device to multiple nodes, supporting KubeVirt live migration.Raw block volumes for live migration

FlashArray File for vTPMUses FlashArray File Services volumes to store persistent state for virtual machines that use a virtual Trusted Platform Module (vTPM), supporting VM live migration.FlashArray File for live migration with vTPM

Volume placement by arrayPlaces volumes created from a `StorageClass` on a specific FlashArray by using its array ID.Control volume placement using array ID

CSI topologyRestricts volume provisioning and attachment based on the nodes and zones that can access a storage backend.Enable CSI topology

ActiveClusterProvisions FADA volumes in an ActiveCluster pod and provides paths to the volumes through both member FlashArrays. Supports stretched pods that connect two FlashArray realms, one on each array, over iSCSI and FC.Use FlashArray ActiveCluster

Subnet-aware iSCSIRestricts iSCSI sessions to subnets accessible from each node.Configure subnet-aware iSCSI

### Manage provisioned storage​

FeatureDescriptionReference

FlashArray snapshotsCreates, deletes, and restores FlashArray snapshots as Kubernetes `VolumeSnapshot` resources. You can also replicate snapshots to another FlashArray, create cross-array snapshots, and provision volumes from the remote snapshots.Snapshot a FlashArray volume

FlashBlade snapshotsCreates on-demand snapshots of FBDA file systems, optionally by using a FlashBlade snapshot policy, and restores a snapshot to a new volume without changing the source file system.Snapshot a FlashBlade volume

PVC cloningCreates a new PVC from an existing Direct Access PVC.Clone a PVC

PVC resizeExpands a Direct Access PVC and its corresponding volume on the storage system.Resize a PVC

PVC deletionDeletes Direct Access PVCs and handles storage-specific dependencies, such as existing snapshots, FlashBlade snapshot policies, and FlashArray File managed directories.Delete a PVC

Backup and restoreRebuilds missing `PureVolume` and `PureSnapshot` custom resources from the storage system to support resource-only backup and restore of Direct Access volumes.Backup and restore

Portworx Enterprise continues to manage FADA CloudSnap backup and restore operations.

### Monitor and troubleshoot​

FeatureDescriptionReference

Volume and storage metricsExports volume usage and capacity metrics for FADA and FBDA volumes and node-level health metrics for storage connectivity to Prometheus.Monitor storage

Grafana dashboardsProvides Grafana dashboards for monitoring FlashArray and FlashBlade storage metrics.Grafana dashboards

Pure1 telemetrySends FA/FB driver logs and diagnostic information to Pure1 through Portworx Enterprise telemetry.Telemetry

CLIProvides cluster status, image, diagnostic, backend credential, volume, and snapshot operations through the `kubectl px csi` command.CLI reference

### Configure storage connectivity​

FeatureDescriptionReference

Storage transportsSupports FlashArray volume attachment over iSCSI, Fibre Channel, NVMe/TCP, and NVMe-oF, with transport configuration available per node.Prepare FlashArray

Native NVMe multipathingSupports kernel-native NVMe multipathing with stable device paths as an alternative to device-mapper multipathing.Prepare FlashArray

Volume attachment limitsAdvertises per-node volume attachment limits to the kubelet.Volume attachment limits

GPUDirect StoragePasses remote direct memory access (RDMA) NFS mount options to FBDA mounts to support GPUDirect Storage.StorageClass reference

## Prerequisites​

Before enabling the FA/FB driver, ensure that your environment meets the following requirements:

-
Prepare your Everpure systems: Prepare the FlashArray and FlashBlade systems that you plan to use:

- Prepare FlashArray

- Prepare FlashBlade

-
Store FlashArray and FlashBlade credentials: Store the FlashArray and FlashBlade credentials in the `px-pure-secret` Kubernetes Secret or in Vault by using the `px-vault` secret. For more information, see Add FlashArray configuration to a secret store provider and Add FlashBlade configuration to a secret store provider.

note

If you store the FlashArray and FlashBlade credentials in Vault, `px-pure-secret` is still required while Portworx migrates existing Direct Access volume metadata to the FA/FB driver. After the migration completes, the driver no longer requires `px-pure-secret`.

-
Complete active FADA CloudSnap backups: Before enabling the FA/FB driver on an existing cluster, ensure that no FADA CloudSnap backup operations are in progress. Wait for active backups to complete before starting the migration.

-
Configure control plane tolerations: If Portworx Enterprise runs on control plane nodes, create a `ComponentK8sConfig` custom resource before enabling the FA/FB driver. By default, the `px-pure-csi-node` DaemonSet does not tolerate the `NoSchedule` taints applied to control plane nodes. Without the required tolerations, Kubernetes cannot schedule the FA/FB driver node component on these nodes.

Create the following `ComponentK8sConfig` custom resource:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: px-pure-csi-node-config

  namespace: <px-namespace>

spec:

  components:

    - componentNames:

        - PxeCSIPlugin

      workloadConfigs:

        - workloadNames:

            - px-pure-csi-node

          placement:

            tolerations:

              - key: node-role.kubernetes.io/master

                operator: Exists

                effect: NoSchedule

              - key: node-role.kubernetes.io/control-plane

                operator: Exists

                effect: NoSchedule

```

Replace `<px-namespace>` with the namespace where Portworx Enterprise is installed.

If the `px-pure-csi-node` DaemonSet is not scheduled on a Portworx node, FA/FB driver node services are unavailable on that node and the `csi-node-driver-registrar` container in the `portworx-api` pod can enter the `CrashLoopBackOff` state.

note

Use a `ComponentK8sConfig` custom resource to configure the tolerations. Do not patch the `px-pure-csi-node` DaemonSet directly because the Portworx Operator reverts direct changes during reconciliation.

-
Configure StorageClasses when PX-Security is enabled: When PX-Security is enabled, Portworx requires authentication for volume operations. The Portworx Operator creates the `px-user-token` secret when you enable PX-Security. For more information about PX-Security and the `px-user-token` secret, see Configure PX-Security on your cluster.

To authenticate provisioning, attachment, expansion, and staging operations, add the following secret parameters to each `StorageClass` that provisions Direct Access volumes:

```

csi.storage.k8s.io/provisioner-secret-name: px-user-token

csi.storage.k8s.io/provisioner-secret-namespace: <px-namespace>

csi.storage.k8s.io/node-publish-secret-name: px-user-token

csi.storage.k8s.io/node-publish-secret-namespace: <px-namespace>

csi.storage.k8s.io/controller-expand-secret-name: px-user-token

csi.storage.k8s.io/controller-expand-secret-namespace: <px-namespace>

csi.storage.k8s.io/node-stage-secret-name: px-user-token

csi.storage.k8s.io/node-stage-secret-namespace: <px-namespace>

csi.storage.k8s.io/controller-publish-secret-name: px-user-token

csi.storage.k8s.io/controller-publish-secret-namespace: <px-namespace>

```

Replace `<px-namespace>` with the namespace where the `px-user-token` secret exists.

The following example shows a FADA `StorageClass` configured for PX-Security:

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: fio-fa-da-sc

provisioner: pxd.portworx.com

parameters:

  backend: "pure_block"

  max_iops: "1000"

  max_bandwidth: "1G"

  csi.storage.k8s.io/fstype: "ext4"

  pure_fa_pod_name: "<fa-pod-name>"

  csi.storage.k8s.io/provisioner-secret-name: px-user-token

  csi.storage.k8s.io/provisioner-secret-namespace: <px-namespace>

  csi.storage.k8s.io/node-publish-secret-name: px-user-token

  csi.storage.k8s.io/node-publish-secret-namespace: <px-namespace>

  csi.storage.k8s.io/controller-expand-secret-name: px-user-token

  csi.storage.k8s.io/controller-expand-secret-namespace: <px-namespace>

  csi.storage.k8s.io/node-stage-secret-name: px-user-token

  csi.storage.k8s.io/node-stage-secret-namespace: <px-namespace>

  csi.storage.k8s.io/controller-publish-secret-name: px-user-token

  csi.storage.k8s.io/controller-publish-secret-namespace: <px-namespace>

volumeBindingMode: WaitForFirstConsumer

allowVolumeExpansion: true

```

Replace `<fa-pod-name>` with the FlashArray pod name and `<px-namespace>` with the namespace where the `px-user-token` secret exists.

For information about the `px-user-token` secret and authenticating CSI requests, see Set up a StorageClass to authenticate requests.

important

-
Enable PX-Security before provisioning Direct Access volumes. If you enable PX-Security after Direct Access volumes have been provisioned from StorageClasses that do not contain the required secret references, subsequent operations on those volumes, including detach and delete operations, can fail. Kubernetes does not allow you to add the required secret references to existing `PersistentVolume` specifications.

To add the secret parameters to an existing `StorageClass`, delete the `StorageClass` and create it again with the same name and the required secret parameters. To continue using volumes that were provisioned before you enabled PX-Security, enable the guest role. For more information, see Managing the guest role yourself.

-
If you enable PX-Security without the guest role, a `VolumeAttachment` for an existing FADA volume might remain in the `Terminating` state, preventing the associated `PersistentVolume` from being deleted. Portworx by Everpure recommends enabling the guest role to recover affected volumes.

## Enable the FA/FB driver​

The FA/FB driver is a component of Portworx Enterprise. When you enable the driver, the Portworx Operator deploys the required components, including the `px-pure-csi-node` DaemonSet. On an existing cluster, the Operator also migrates Direct Access volume metadata to Kubernetes custom resources, including `PureVolume`, `PureSnapshot`, and `PureStorageCluster`.

Kubernetes continues to provision storage through the Portworx Enterprise `pxd.portworx.com` provisioner, and existing StorageClasses, PVCs, and PVs continue to work after you enable the driver. The migration does not restart Portworx or disrupt I/O for existing applications and pods.

important

- If your cluster is running a Portworx Enterprise version earlier than 3.7.0, upgrade the cluster to version 3.7.0 or later, verify that the upgrade is complete on all nodes, and then enable the FA/FB driver.

- After you enable the FA/FB driver, you cannot disable it or revert to the previous Direct Access volume implementation.

You can enable the FA/FB driver in either of the following ways:

- For a new Portworx Enterprise installation, select the Enhanced FA/FB Driver checkbox when generating the specification in Portworx Central.

- For a new or existing Portworx Enterprise cluster, add the `portworx.io/pure-csi-integration` annotation to the `StorageCluster` specification.

Both methods configure the same annotation in the `StorageCluster` specification.

### Enable the FA/FB driver in Portworx Central​

Follow the steps in Install Portworx with FlashArray to deploy Portworx Enterprise.

On the Deployment page in Portworx Central, select the Enhanced FA/FB Driver checkbox.

Portworx Central adds the `portworx.io/pure-csi-integration` annotation to the generated `StorageCluster` specification.

### Enable the FA/FB driver by using an annotation​

Add the following annotation to the `StorageCluster` specification:

```

metadata:

  annotations:

    portworx.io/pure-csi-integration: "true"

```

When you enable the FA/FB driver on an existing cluster, the Portworx Operator migrates existing Direct Access volume metadata to the Kubernetes custom resources required by the driver.

important

- Avoid enabling the FA/FB driver when you expect frequent new volume creation or attachment.

- Before starting the migration, ensure that the Kubernetes and Portworx clusters are healthy and that Portworx has connectivity to the FlashArray systems.

- After the pre-migration phase completes successfully and before the post-migration phase completes, new Direct Access volume operations, such as volume creation and attachment, might be delayed briefly. As a result, new pods that require these operations might take longer to start.

- The migration does not restart Portworx or disrupt I/O for existing applications and pods.

- If the migration fails, retry it as described in Recover from a failed migration. If the migration continues to fail after retrying, contact Portworx Support.

## Verify the FA/FB driver​

To verify that the FA/FB driver is ready, complete the following steps.

-
For an existing Portworx Enterprise cluster, verify that the metadata migration completed successfully. For a new installation, skip this step because metadata migration is not required.

```

kubectl get jobs -n <px-namespace> | grep pure-csi-migrator

```

Example output:

```

NAME                     STATUS     COMPLETIONS   DURATION   AGE

post-pure-csi-migrator   Complete   1/1           5s         41s

pre-pure-csi-migrator    Complete   1/1           8s         51s

```

Verify that both migration `Job` resources have a status of `Complete`.

The migration resources perform the following operations:

- `pre-pure-csi-migrator` migrates existing Portworx metadata to Kubernetes custom resources, including `PureVolume`, `PureSnapshot`, and `PureStorageCluster`.

- `post-pure-csi-migrator` performs post-migration reconciliation.

-
Verify that the `px-pure-csi-node` DaemonSet is available:

```

kubectl get daemonset -n <px-namespace> | grep px-pure-csi-node

```

Example output:

```

NAME               DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR          AGE

px-pure-csi-node   6         6         6       6            6           kubernetes.io/os=linux 34s

```

Verify that the `READY` and `AVAILABLE` values match the `DESIRED` value.

-
Verify that the `PureStorageCluster` resource is running:

```

kubectl get purestoragecluster -n <px-namespace>

```

Example output:

```

NAME       CLUSTER UUID   STATUS    VERSION   AGE

test-stc   xxxxxx         Running   3.7.0     75s

```

Verify that the `STATUS` value is `Running`.

The FA/FB driver is ready when the migration, if applicable, completes successfully, the `px-pure-csi-node` DaemonSet is ready on the expected nodes, and the `PureStorageCluster` resource reports a `Running` status.

### Recover from a failed migration​

The Portworx Operator creates the `pre-pure-csi-migrator` Kubernetes `Job` with a `backoffLimit` of `0`, so it does not retry automatically if it fails. When the migration fails, the `PxeUsingCSIMigration` condition on the `StorageCluster` remains `InProgress`.

To recover from a failed migration:

-
Remove the `portworx.io/pure-csi-integration` annotation from the `StorageCluster` specification.

-
Review the migration logs and resolve the reported error:

```

kubectl logs -n <px-namespace> job/pre-pure-csi-migrator

```

-
Verify that:

- KVDB is healthy.

- The Portworx cluster is healthy.

- Your applications are running normally.

-
Restore the `portworx.io/pure-csi-integration` annotation in the `StorageCluster` specification.

-
Delete the failed migration `Job` to allow the Portworx Operator to restart the migration:

```

kubectl delete job -n <px-namespace> pre-pure-csi-migrator

```

If the migration continues to fail after retrying, contact Portworx Support.

## Upgrade the FA/FB driver​

The FA/FB driver is a component of Portworx Enterprise and cannot be upgraded independently. Each Portworx Enterprise release includes the supported version of the driver.

To upgrade the FA/FB driver, upgrade Portworx Enterprise. For more information, see Upgrade Portworx Enterprise.

## Limitations​

The following limitations apply when the FA/FB driver is enabled:

- FADA volume limit: Portworx by Everpure recommends a maximum of 512 FADA volumes per node.

- QoS settings and tags in `pxctl volume inspect`: The `pxctl volume inspect` command does not display QoS settings or tags for FADA volumes. Portworx applies changes to these settings, and you can view the current values on the FlashArray.

- `VolumeAttributeClass`: Modifying the bandwidth or IOPS limits of a FlashArray volume after provisioning through `ControllerModifyVolume` is not supported. To modify these limits, use `pxctl`.

- Purity realms in a `StorageClass`: You cannot specify a Purity realm as a `StorageClass` parameter for FADA volumes. Configure the realm in the backend configuration instead.

- NVMe over Fibre Channel for FlashArray Cloud Drive: NVMe over Fibre Channel is not supported as a transport for FlashArray Cloud Drive.

- FADA CloudSnap group snapshots: CloudSnap does not support group snapshots of FADA volumes.

- FADA CloudSnap schedules: Portworx CloudSnap schedules are not supported for FADA volumes. You can schedule these snapshots by using Stork.

- First FADA CloudSnap after enabling the FA/FB driver: The first CloudSnap of a FADA volume is always a full backup, even if an incremental backup chain existed before the driver was enabled. Portworx uses this full backup as the base for a new incremental backup chain.

- FADA backup immediately after enabling the FA/FB driver: If you trigger a backup immediately after enabling the FA/FB driver on an existing Portworx cluster, the backup might fail for FADA volumes with a `Volume not found` error. Wait for `VolumeAttachment` reconciliation to complete before taking a FADA backup. To verify the migration status, see Verify the FA/FB driver.

In this topic:
