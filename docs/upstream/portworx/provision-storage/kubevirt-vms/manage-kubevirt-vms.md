# Manage Shared File System for KubeVirt VMs

Source: https://docs.portworx.com/portworx-enterprise/provision-storage/kubevirt-vms/manage-kubevirt-vms (Portworx Enterprise latest)

Manage Shared File System for KubeVirt VMs | Portworx Enterprise Documentation

This topic explains how to configure and manage shared filesystem (RWX) storage for KubeVirt virtual machines running on Kubernetes with Portworx.

Portworx provides resources that VMs can use for both their initial startup process and for retaining data even when they are not running. To utilize OpenShift features, such as live migration, these volumes must have the `ReadWriteMany` access mode.

note

If you are using Operator version 24.2.3 or later with the PX Security feature, you cannot disable it—the Operator tries to live migrate the VM(s), and the operation fails.

To disable it, pause the VM(s) first.

## Prerequisites​

- An OpenShift cluster that supports KubeVirt.

- OpenShift Virtualization is enabled.

- Ensure that you are running the latest versions of OpenShift Virtualization and the Migration Toolkit for Virtualization Operator that are compatible with your current OpenShift version. Failing to do so may result in issues with Live Migration operations and other functionalities.

## Create a StorageClass​

If you are running Portworx Enterprise version 3.4.0 or later with Portworx Operator version 25.5.0 or later, the Portworx Operator creates the following StorageClasses by default when the `HyperConverged` custom resource is detected:

- `px-rwx-block-kubevirt`: RWX block volume class, and is annotated as the default KubeVirt StorageClass (only if no other default exists).

- `px-rwx-file-kubevirt`: Shared file system RWX class used for features like vTPM.

- `px-cdi-scratch`: Scratch space required for CDI image operations.

You can control the creation of these StorageClasses using the `spec.csi.kubeVirtStorageClasses` section in the `StorageCluster` custom resource.

note

The default `px-rwx-file-kubevirt` StorageClass doesn't explicitly set `sharedv4_svc_type`. For KubeVirt VMs, Portworx recommends using sharedv4 service volumes (`sharedv4_svc_type: ClusterIP`), because failover is seamless only with service volumes. To use them, create your own StorageClass by following the steps in this section.

If a StorageClass doesn't already exist, create one by following these steps.

To ensure PVCs are compatible with KubeVirt virtual machines, they must use the `ReadWriteMany` access mode and NFS version 3.0 with the `nolock` mount option, which you set in the `sharedv4_mount_options` parameter. To meet these requirements, create PVCs from a StorageClass with the following parameters:

- `sharedv4: "true"`

- `sharedv4_mount_options: vers=3.0,nolock`

- `sharedv4_svc_type: "ClusterIP"`: Recommended. Omit this parameter if your `StorageCluster` specifies different network interfaces for `dataInterface` and `mgmtInterface`.

-
Create the `px-kubevirt-sc.yaml` file:

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: portworx-rwx-kubevirt

provisioner: pxd.portworx.com

parameters:

  repl: "3"

  sharedv4: "true"

  sharedv4_mount_options: vers=3.0,nolock

  sharedv4_svc_type: "ClusterIP" # Omit if dataInterface and mgmtInterface use different interfaces.

volumeBindingMode: WaitForFirstConsumer

allowVolumeExpansion: true

```

note

- The `volumeBindingMode=WaitForFirstConsumer` flag enables Portworx to intelligently place the volumes. For more information, see the KubeVirt page.

- Note that the PVCs used by the VMs directly, should not include the annotation `cdi.kubevirt.io/storage.bind.immediate.requested=true`. This is because such an annotation overrides the `WaitForFirstConsumer` setting in the StorageClass.

- When migrating Forklift from vSphere to OpenShift Container Platform with Migration Toolkit for Virtualization, use `volumeBindingMode=immediate` for a successful migration.

-
Run the following command to apply your StorageClass:

```

oc apply -f px-kubevirt-sc.yaml

```

Portworx optimizes volume placement and access for KubeVirt VMs using principles of hyperconvergence and collocation.

-
Shared volumes for live migration: Live migration requires two `virt-launcher` pods to run simultaneously, with the same volume mounted in both pods. The type of shared volume—either bind-mounted or NFS-mounted—depends on the volume's attachment at the `virt-launcher` pod creation:

- Bind-mount: Used when the volume is attached on the same node where the `virt-launcher` pod starts, optimizing performance through hyperconvergence.

- NFS-mount: Used when the volume is attached on a different node. Volumes can switch between bind-mount and NFS by live-migrating or restarting the VM.

-
Collocation: Portworx ensures that multiple volumes used by a single KubeVirt VM are placed on the same set of replica nodes. This automatic collocation simplifies achieving hyperconvergence.

note

When a virtual machine uses multiple SharedV4 volumes and the VM is not hyperconverged, a failure of the node hosting one of the non-root SharedV4 volumes can cause the VM to restart. This behavior occurs if the volumes are not co-located, leading to temporary loss of volume access.
To avoid unexpected restarts, ensure that all SharedV4 volumes attached to the VM are hyperconverged. If a restart occurs, allow the VM to restart and verify that all volumes are successfully reattached.

## Create a PVC​

You can create PVCs using one of the following methods, and Portworx will automatically recognize them as KubeVirt volumes. Ensure these PVCs are configured with the `RWX` access mode:

- Virtualization tab in the OpenShift web console

- Konveyor Forklift or Migration Toolkit for Virtualization

- Containerized data importer's (CDI) DataVolume

note

Starting from OpenShift Container Platform (OCP) 4.17, the default `StorageProfile` for Portworx-backed `StorageClass` objects sets the access mode to ReadWriteMany (RWX) and the volume mode to Block.

For forklifting, ensure that the `StorageProfile` associated with the `StorageClass` matches the `accessModes` and `volumeMode` that you intend to use. For more information about `StorageProfile` configuration, see Configuring storage profiles.

Once PVCs are created, run the following command to verify if they have the `RWX` access mode:

```

oc get pvc -n <vm-namespace>

```

```

NAME                  STATUS   VOLUME             CAPACITY   ACCESS MODES   STORAGECLASS             AGE

<your-kubevirt-pvc>   Bound    pvc-xxxx-xxx-xxx   1Gi        RWX            portworx-rwx-kubevirt    15h

```

The output should show the PVCs with the `RWX` access mode.

important

If you are creating a PVC using some other mechanism, then ensure the following:

- Add the `portworx.io/app: kubevirt` annotation to the PVC spec. This ensures that Portworx will apply KubeVirt-specific logic when processing the volume.

- Maintain the same HA or replication factor for all volumes associated with a VM.

## Create a VM​

Refer to the applicable version of the OpenShift documentation to create a KubeVirt VM.

important

If your Portworx cluster is integrated with Everpure Fusion, you may reference a Fusion-backed `StorageClass` in the data volume template when creating a KubeVirt VM. When you create a VM that references a Fusion-backed StorageClass, the Portworx Fusion Controller automatically handles storage provisioning. It detects the StorageClass reference, creates a corresponding workload in Fusion, and provisions volumes based on the preset configuration. This behavior differs from standard Portworx provisioning and is required to use Fusion-managed storage.
For information on how to create a KubeVirt VM using a Fusion preset, see Create a KubeVirt VM using a Fusion Preset.

Once the VMs are created, each VM will start running in a `virt-launcher` pod.

Portworx ensures:

- The newly created VMs (even with operators such as Konveyor Forklift or Migration toolkit for Virtualization), have their volumes collocated during creation. Stork will schedule the VMs on nodes where volume replicas exist, making the VMs hyperconverged (bind mounted).

- During planned node maintenance, OpenShift will live-migrate the VMs out of that node. When OpenShift reboots the node, Portworx will perform a sharedv4 service (NFS) failover, and as part of this failover, it will live-migrate the VMs to ensure they are hyperconverged once again.

- Existing VMs with non-collocated volumes will be identified and corrected by a background job.

## Manage KubeVirt VMs during Portworx node upgrades​

When upgrading Portworx on a node, the Portworx Operator manages KubeVirt VMs by initiating a live migration before the upgrade begins. Here’s what happens during this process:

-
Eviction notice: As the operator attempts to evict VMs from a node, it generates an event on the storage node stating:

`Warning: UpdatePaused - The update of the storage node <node-name> has been paused because there are 3 KubeVirt VMs running on the node. Portworx will live-migrate the VMs, and the update will proceed once no VMs remain on this node.`

-
Migration failure: If the operator cannot successfully live-migrate a VM, the upgrade is paused, and the following event is recorded:

`Warning: FailedToEvictVM - Live migration <migration-name> failed for VM <vm-namespace>/<vm-name> on node <node-name>. Please stop or migrate the VM manually to continue the update of the storage node.`

### Opt out of VM evictions when updating the StorageCluster​

By default, the Portworx Operator evicts KubeVirt VMs during a Portworx upgrade to ensure that the VMs remain available and do not experience downtime. If you prefer to speed up the upgrade process and are willing to allow VMs to go down during the upgrade, you can opt out of this behavior.

To disable VM evictions during the upgrade, add the following annotation to the `StorageCluster` object:

```

operator.libopenstorage.org/evict-vms-during-update: "false"

```

You can also use this annotation to resume an upgrade that has been paused due to the presence of running KubeVirt VMs.

note

This feature is designed to upgrade one node at a time, which is the default setting. Upgrading multiple nodes simultaneously can lead to VMs being paused or restarted, and may stall the upgrade process.

## Manage KubeVirt VMs with adjusted filesystem overhead​

When creating VMs from templates on Portworx filesystem volumes, you might encounter an error due to insufficient filesystem overhead. To resolve this issue, follow the steps below to increase the overhead:

When you add a virtual machine disk to a PVC that uses the filesystem volume mode, you must ensure that there is enough space on the PVC for the VM disk and for file system overhead, such as metadata. By default, OpenShift Virtualization reserves 5.5% of the PVC space for overhead, reducing the space available for virtual machine disks by that amount. You can configure a different overhead value by editing the HyperConverged Operator (HCO) object.

### Prerequisite​

- Install the OpenShift CLI (`oc`).

The following procedure explains how to change the default file system overhead value to 8%:

-
Edit the HCO object:

```

oc edit hyperconverged kubevirt-hyperconverged -n openshift-cnv

```

-
Populate the fields to set the overhead to 8%. For example:

```

spec:

  filesystemOverhead:

    global: "0.08"

    storageClass:

      <storage_class_name>: "0.08"

```

where:

- `global`: The default file system overhead percentage used for any storage classes that do not already have a set value. Setting `global: "0.08"` reserves 8% of the PVC for file system overhead.

- `<storage_class_name>`: If you want to set the overhead for a specific storage class to 8%, replace <storage_class_name> with the name of your storage class.

-
Save and exit the editor to update the HCO object.

-
Verify changes to CDIConfig:

```

oc get cdiconfig -o yaml

```

-
View your specific changes to CDIConfig:

```

oc get cdiconfig -o jsonpath='{.items..status.filesystemOverhead}'

```

By following these steps, you can adjust the filesystem overhead to 8%, ensuring that there is enough space on the PVC for the VM disk and file system overhead. For further details, refer to the Red Hat article.

## Further Reading​

For more details on virtual machine live migration, refer to the Virtual machine live migration documentation.

In this topic:
