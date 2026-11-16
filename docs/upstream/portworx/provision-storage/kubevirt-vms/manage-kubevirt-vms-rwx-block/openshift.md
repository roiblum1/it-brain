# Manage Portworx RWX Block Volumes on OpenShift for KubeVirt VMs

Source: https://docs.portworx.com/portworx-enterprise/provision-storage/kubevirt-vms/manage-kubevirt-vms-rwx-block/openshift (Portworx Enterprise latest)

Manage Portworx RWX Block Volumes on OpenShift for KubeVirt VMs | Portworx Enterprise Documentation

Portworx enables the seamless integration of KubeVirt virtual machines (VMs) within Kubernetes clusters, leveraging the high performance of ReadWriteMany (RWX) volumes across OpenShift nodes. This approach supports raw block devices, which provide direct block storage access instead of a mounted filesystem. This is particularly beneficial for applications that demand low-latency and high-performance storage.

RWX block volumes allow shared access to raw block devices, enabling features such as live migration, high availability, and persistent VM storage across OpenShift nodes.

This section provides step-by-step instructions for managing Portworx RWX block volumes with KubeVirt virtual machines on OpenShift virtualization.

## Prerequisites​

- An OpenShift cluster that supports KubeVirt.

important

If you are using OpenShift Container Platform (OCP) 4.20, version 4.20.27 or later (RHCOS kernel 5.14.0-570.124.1.el9_6 or later) is required. OCP 4.20 versions earlier than 4.20.27 (including 4.20.17) contain a kernel-level discard race condition that affects Portworx block volumes. For the minimum required patch version for other OCP releases in the 4.18–4.22 range, see Red Hat Solution 7077108.

- Portworx Enterprise version 3.3.0 or later.

- Portworx Operator version 25.2.1 or later.

- Portworx Stork version 25.2.0 or later.

- OpenShift Virtualization is enabled.

- Ensure that you are running the latest versions of OpenShift Virtualization and the Migration Toolkit for Virtualization Operator that are compatible with your current OpenShift version. Failing to do so may result in issues with live migration operations and other functionalities.

- Review the Known issues.

## Create a StorageClass​

If you are running Portworx Enterprise version 3.4.0 or later with Portworx Operator version 25.5.0 or later, the Portworx Operator creates the following StorageClasses by default when the `HyperConverged` custom resource is detected:

- `px-rwx-block-kubevirt`: RWX block volume class, and is annotated as the default KubeVirt StorageClass (only if no other default exists). On new installations with dynamic pools enabled, `px-rwx-block-kubevirt-repl1` is the default instead. See the following note.

- `px-rwx-file-kubevirt`: Shared file system RWX class used for features like vTPM.

- `px-cdi-scratch`: Scratch space required for CDI image operations.

You can control the creation of these StorageClasses using the `spec.csi.kubeVirtStorageClasses` section in the `StorageCluster` custom resource.

important

Starting with Portworx Operator version 26.1.0, the Operator creates an additional StorageClass, `px-rwx-block-kubevirt-repl1`, when dynamic pools are enabled. For new installations running Portworx Enterprise 3.7.2 or later with Operator 26.5.0 or later, and dynamic pools enabled, the Operator makes `px-rwx-block-kubevirt-repl1` the default KubeVirt StorageClass by adding the `storageclass.kubevirt.io/is-default-virt-class: "true"` annotation. This replaces `px-rwx-block-kubevirt` with `px-rwx-block-kubevirt-repl1` as the default KubeVirt StorageClass for these installations. For existing or upgraded clusters, or installations without dynamic pools, the Operator does not add this annotation. In these cases, to make `px-rwx-block-kubevirt-repl1` the default KubeVirt StorageClass, add the annotation manually. For more information, see Dynamic Pool Failover.

When Portworx is configured as the default KubeVirt StorageClass, the Hyperconverged Cluster Operator (HCO) automatically manages OS image boot sources in the `openshift-virtualization-os-images` namespace.

- OpenShift 4.18 and later: Boot sources are automatically updated when the default storage class changes.

- OpenShift 4.17 and earlier: You must manually delete old boot sources after changing the default storage class. Existing VMs and PVCs are not affected by storage class changes. For more information, see the OpenShift Virtualization Storage documentation.

Create a StorageClass if one does not already exist. The following is an example StorageClass.

-
Create the `px-kubevirt-sc.yaml` file:

StorageClass

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: px-rwx-block-kubevirt

provisioner: pxd.portworx.com

parameters:

  repl: "3"

volumeBindingMode: WaitForFirstConsumer

allowVolumeExpansion: true

```

note

- OpenShift Virtualization (OSV) versions 4.18.4 and earlier have a known issue which handle discards incorrectly when used with Portworx block devices. As a workaround, you can disable discards for the Portworx volume by including the parameter `nodiscard: true` in the StorageClass.

- OCP 4.20 versions earlier than 4.20.27 (RHCOS kernel 5.14.0-570.99.1.el9_6 and earlier) contain a kernel-level discard race condition that affects Portworx block volumes. Upgrade to OCP 4.20.27 or later (kernel 5.14.0-570.124.1.el9_6 or later) to resolve this issue. If you cannot upgrade immediately, add `nodiscard: true` to the StorageClass as a workaround. For minimum required versions for other OCP releases in the 4.18–4.22 range, see Red Hat Solution 7077108.

- The `volumeBindingMode=WaitForFirstConsumer` flag enables Portworx to intelligently place the volumes. For more information, see the KubeVirt page.

- Note that the PVCs used by the VMs directly, should not include the annotation `cdi.kubevirt.io/storage.bind.immediate.requested=true`. This is because such an annotation overrides the `WaitForFirstConsumer` setting in the StorageClass.

- When migrating Forklift from vSphere to OpenShift Container Platform with Migration Toolkit for Virtualization, use `volumeBindingMode=immediate` for a successful migration.

-
Run the following command to apply your StorageClass:

```

oc apply -f px-kubevirt-sc.yaml

```

Portworx optimizes volume placement and ensures that multiple volumes used by a single KubeVirt VM are placed on the same set of replica nodes. This automatic co-location simplifies achieving hyperconvergence.

### Kube Datastore-aware StorageClasses​

In a FlashArray Cloud Drive (FACD) deployment, the Portworx Operator creates a Kube Datastore-aware (KDS-aware) `StorageClass` for each default KubeVirt `StorageClass` and Kube Datastore (KDS) combination. A KDS-aware `StorageClass` includes the `kube_datastore_affinity` parameter, which directs Portworx to provision its volumes on a specific Kube Datastore.

Use a KDS-aware StorageClass when you want to place KubeVirt VM disks on a specific Kube Datastore.

#### KDS-aware StorageClass naming​

The Operator generates each KDS-aware `StorageClass` name by combining the base KubeVirt `StorageClass` name with the Kube Datastore name.

For example, if a cluster has Kube Datastores named `fa-x90-1a` and `fa-c20-2c`, the Operator creates the following KDS-aware StorageClasses in addition to the base `px-rwx-block-kubevirt` and `px-rwx-file-kubevirt` StorageClasses:

StorageClassKube DatastorePurpose

`px-rwx-block-kubevirt-fa-x90-1a``fa-x90-1a`Provisions RWX block VM disks on the `fa-x90-1a` Kube Datastore.

`px-rwx-block-kubevirt-fa-c20-2c``fa-c20-2c`Provisions RWX block VM disks on the `fa-c20-2c` Kube Datastore.

`px-rwx-file-kubevirt-fa-x90-1a``fa-x90-1a`Provisions SharedV4 VM disks on the `fa-x90-1a` Kube Datastore.

`px-rwx-file-kubevirt-fa-c20-2c``fa-c20-2c`Provisions SharedV4 VM disks on the `fa-c20-2c` Kube Datastore.

To list the available KDS-aware StorageClasses in your cluster, run the following command:

```

oc get storageclass

```

When you create a VM, select the KDS-aware `StorageClass` associated with the Kube Datastore where you want Portworx to provision the VM disks. If you select the corresponding base KubeVirt `StorageClass`, Portworx provisions the volumes without Kube Datastore affinity.

#### Operator managed StorageClasses​

The Portworx Operator manages KDS-aware StorageClasses automatically:

- When a new Kube Datastore becomes available, the Operator creates the corresponding KDS-aware StorageClasses.

- When the Operator deletes a base KubeVirt `StorageClass`, it also deletes the KDS-aware StorageClasses generated from it.

note

- Portworx Enterprise automatically creates KDS-aware StorageClasses only for the default KubeVirt StorageClasses. It does not create KDS-aware variants of other default StorageClasses, such as `px-csi-db` or `px-csi-replicated`.

- You can create a custom KDS-aware StorageClass by setting the `kube_datastore_affinity` parameter to the target Kube Datastore. For more information, see Create a KDS-aware StorageClass.

- You can also use KDS-aware StorageClasses to migrate existing KubeVirt VM disks between Kube Datastores. During storage migration, select the KDS-aware `StorageClass` associated with the destination Kube Datastore. For more information, see Migrate KubeVirt VM disks to a different Kube Datastore.

## Boot source behavior with default storage class changes​

When you configure Portworx as the default virtualization storage class in OpenShift, the Hyperconverged Cluster Operator (HCO) may automatically recreate or update OS image boot sources in the `openshift-virtualization-os-images` namespace.

### OpenShift Container Platform 4.18 and later​

Starting with OpenShift Container Platform 4.18, boot sources are automatically managed when the default storage class changes:

- Boot sources are created using the default storage class.

- When the default storage class changes, existing boot sources are automatically updated to use the new default storage class.

- If your cluster does not have a default storage class, you must define one before boot sources can be created.

For more information, see Chapter 11. Storage in the OpenShift Container Platform 4.18 documentation.

### OpenShift Container Platform 4.17 and earlier​

For OpenShift Container Platform 4.17 and earlier versions, boot sources are not automatically updated when the default storage class changes. You must manually delete the existing boot sources configured with the previous default storage class.

For more information, see:

- Chapter 7. Virtual machines in the OpenShift Container Platform 4.17 documentation

- Chapter 9. Storage in the OpenShift Container Platform 4.17 documentation

note

Changing the default storage class and updating boot sources does not impact existing VMs or their associated PVCs that were created using the previous default storage class. Only new boot sources and newly provisioned VMs will use the updated default storage class.

## Create a PVC​

note

Starting with OpenShift Container Platform (OCP) version 4.17, the default `StorageProfile` for Portworx-backed `StorageClass` objects sets the access mode to `ReadWriteMany` and the volume mode to `Block`.
When creating or migrating (forklifting) new PX RWX Block volumes, ensure that the corresponding `StorageProfile` has `volumeMode` set to `Block` if it is not already configured by default in your OCP version.
For more information about `StorageProfile` configuration, see Configuring storage profiles.

-
Using the above StorageClass, define a PVC with the following configuration:

- `accessModes`: `ReadWriteMany` for shared volume access.

- `volumeMode`: `Block` to create a raw block device volume

PersistentVolumeClaim

```

apiVersion: v1

kind: PersistentVolumeClaim

metadata:

  name: rwx-disk-1

  labels:

    portworx.io/app: kubevirt

spec:

  accessModes:

  - ReadWriteMany

  resources:

    requests:

      storage: 100Gi

  storageClassName: px-rwx-block-kubevirt

  volumeMode: Block

```

-
Apply this PVC to your cluster:

```

kubectl apply -f pvc.yaml

```

When deploying KubeVirt VMs, reference the PVC created in the previous step to attach the Portworx RWX raw block volume to the VM. Ensure that the VM configuration specifies the correct StorageClass and volume.

After the VM is running with the specified PVC, you can perform live migration using OpenShift's native functionality. The shared RWX volume ensures data consistency during the migration process by allowing simultaneous read/write operations for the source and destination nodes.

important

If you are manually creating a PVC and attaching it to a VM, ensure the following:

- Add the `portworx.io/app: kubevirt` annotation to the PVC spec. This ensures that Portworx will apply KubeVirt-specific logic when processing the volume.

- Maintain the same HA or replication factor for all volumes associated with a VM.

## VM configuration guidelines for Portworx raw block volumes​

When you use Portworx RWX block volumes with VMs, specific configurations are required to ensure compatibility and performance. The following guidance outlines considerations for root and data disks, block sizes, and bootloaders.

### Block size and bootloader compatibility​

The VM disk configuration defaults to a 512-byte block size. The hypervisor makes it compatible so that 512-byte operations work over a provisioned Portworx storage disk with a 4096-byte block size. Therefore, no changes are needed because block size compatibility is ensured.

- Portworx block volumes always use a 4096-byte block size.

- VM disks default to a 512-byte block size unless otherwise specified. Specifying a logical block size of 512-byte and a physical block size of 4096-byte in the VM disk specification is an optional configuration detail within the VM that may help applications or file systems optimize performance, if supported.

- VM root disks also contain a bootloader, which can be either EFI or BIOS. BIOS supports booting only from disks with a 512-byte block size. EFI supports booting from disks with either a 4096-byte or 512-byte block size. EFI and BIOS are independent bootloading mechanisms. The root disk configuration determines which bootloader is used.

- You can identify the root disk configuration by examining the QCOW2 image or the disk partition table.

- EFI requires an EFI system partition, a GPT partition table, and related components.

- BIOS requires a partition marked as bootable.

- For example, RHEL configures its QCOW2 cloud images to boot using both EFI and BIOS by creating two partitions that contain the required information. Note that not all distributions support this configuration.

### VM spec example with custom block size​

VirtualMachine

```

...

spec:

  domain:

    devices:

      disks:

        - bootOrder: 1

          blockSize:

            custom:

              logical: 512

              physical: 4096

          disk:

            bus: virtio

          name: rootdisk

        - name: fio-data-disk-1

          blockSize:

            custom:

              logical: 4096

              physical: 4096

...

```

- Set `bootOrder: 1` to indicate the root disk.

- If `blockSize` is not specified, the default is 512 for both logical and physical sizes.

- For additional data disks, specifying both logical and physical block sizes as 4096 is recommended for improved performance.

### VM bootloader spec example​

Portworx supports both `UEFI` and `BIOS` bootloaders.

- To use UEFI, define the bootloader section with `efi: {}`.

- If no `bootloader` section is present, BIOS is used by default.

VirtualMachine

```

...

spec:

  domain:

    firmware:

      bootloader:

        efi: {}

...

```

### Supported configuration matrix​

#### VM Root disk​

S.NoPortworx block sizeVM physical block sizeVM logical block sizeBootloader (root disk only)Supported

140964096 / 512512BIOSYes

240964096 / 512512EFIYes

3409640964096BIOSNo

4409640964096EFI only (qcow2 with 4K block size)Yes

#### Additional disks​

S.NoPortworx block sizeVM physical block sizeVM logical block sizeSupported

140964096512Yes

2409640964096Yes (Recommended)

## Create a VM​

Refer to the applicable version of the OpenShift documentation and KubeVirt user guide to create a KubeVirt VM.

important

If your Portworx cluster is integrated with Everpure Fusion, you may reference a Fusion-backed `StorageClass` in the data volume template when creating a KubeVirt VM. When you create a VM that references a Fusion-backed StorageClass, the Portworx Fusion Controller automatically handles storage provisioning. It detects the StorageClass reference, creates a corresponding workload in Fusion, and provisions volumes based on the preset configuration. This behavior differs from standard Portworx provisioning and is required to use Fusion-managed storage.
For information on how to create a KubeVirt VM using a Fusion preset, see Create a KubeVirt VM using a Fusion Preset.

After the VMs are created, each VM will start running in a `virt-launcher` pod.

Portworx ensures that:

- The newly created non-cloned volumes in a VM are co-located during creation.

- The cloned volumes in a VM are automatically relocated after the VM starts, aligning them with the non-cloned volumes created for that VM.

## Manage KubeVirt VMs during Portworx node upgrades​

When you upgrade Portworx on a node, the Portworx Operator manages KubeVirt VMs by initiating a live migration before the upgrade begins. Here’s what happens during this process:

-
Eviction notice: As the operator attempts to evict virtual machines (VMs) from a node, it generates the following event if it is unable to migrate the VMs:

```

Warning: UpdatePaused - The update of the storage node <node-name> is paused because there are 3 KubeVirt VMs running on the node. Portworx live-migrates the VMs and updates the storage node after there are no VMs left on this node.

```

-
Migration failure: If the operator cannot successfully live-migrate a VM, the upgrade is paused, and the following event is recorded:

```

Warning: FailedToEvictVM - Live migration <migration-name> failed for VM <vm-namespace>/<vm-name> on node <node-name>. Please stop or migrate the VM manually to continue the update of the storage node.

```

In this topic:
