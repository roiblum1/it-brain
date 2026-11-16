# Migrate KubeVirt VM Disks to a Different Kube Datastore (3.7.0)

Source: https://docs.portworx.com/portworx-enterprise/operations/kube-datastore-3.7.0/migrate-vm-disks (Portworx Enterprise latest)

Migrate KubeVirt VM Disks to a Different Kube Datastore (3.7.0) | Portworx Enterprise Documentation

important

Migration of KubeVirt VM disks between Kube Datastores was available under Directed Availability (DA) in Portworx Enterprise 3.7.0 and is now generally available (GA) in version 3.7.2. For information about migrating VM disks between Kube Datastores in Portworx Enterprise 3.7.2, see Migrate KubeVirt VM Disks to a Different Kube Datastore.

You can migrate KubeVirt virtual machine (VM) disks from one Kube Datastore (KDS) to another without recreating the VM. During storage migration, select the KDS-aware `StorageClass` associated with the destination KDS. OpenShift Virtualization copies the data to new persistent volumes provisioned through the selected `StorageClass` and updates the VM to use the new volumes.

You can migrate VM disks between Kube Datastores to:

- Rebalance storage capacity across FlashArrays.

- Move VM storage to a FlashArray that meets different performance or capacity requirements.

- Evacuate storage from a FlashArray before decommissioning it.

note

- You can keep the VM running during storage migration. OpenShift Virtualization might live migrate the VM as part of the storage migration workflow.

- OpenShift Virtualization performs a full copy of each migrated volume. Portworx Enterprise does not offload the copy operation to the FlashArray. VM I/O performance might be reduced while the migration is in progress.

## Prerequisites​

Before you migrate VM disks to another Kube Datastore, ensure that your cluster meets the following requirements:

- Has Portworx Enterprise 3.7.0 or later installed.

- Uses FlashArray Cloud Drive (FACD) as the storage backend.

- Has OpenShift Virtualization 4.18 or later installed.

- Has a node available for live migration. OpenShift Virtualization live migrates the VM to a different node as part of the storage migration.

- Has at least two Kube Datastores. To verify the available Kube Datastores, see List Kube Datastores.

- A KDS-aware `StorageClass` exists for the destination Kube Datastore. For more information, see Kube Datastore-aware StorageClasses.

- The VM is running. This procedure migrates the disks of one VM at a time.

- The destination Kube Datastore has sufficient available capacity for the VM disks. The source and destination volumes coexist until you delete the source PVCs and DataVolumes.

- The destination Kube Datastore has enough storage pools on distinct nodes to satisfy the replication factor configured in the destination `StorageClass`.

- The VM uses the same RWX volume type for all its disks. For more information, see Manage KubeVirt VMs with Portworx.

## Identify the current Kube Datastore​

Before starting the migration, identify the Kube Datastore that contains the VM disks.

-
List the PVCs used by the VM and identify their StorageClasses:

```

kubectl get pvc -n <namespace>

```

-
Determine the Kube Datastore for each PVC:

-
If the PVC uses a KDS-aware `StorageClass`, use the `StorageClass` name or configuration to identify its Kube Datastore.

-
If the PVC does not use a KDS-aware `StorageClass`, inspect the Portworx volume to identify the storage pools that hold its replicas:

```

pxctl volume inspect <volume-name>

```

Then, inspect the storage pools:

```

pxctl service pool show

```

The `kube_datastore` label identifies the Kube Datastore associated with each pool.

## Migrate the VM disks​

Storage migration is an OpenShift Virtualization workflow. To migrate the VM disks, follow the procedure in Migrating VM disks to a different storage class in the Red Hat OpenShift Container Platform documentation.

When the workflow prompts you for the destination storage class, select the KDS-aware `StorageClass` associated with the Kube Datastore to migrate the disks to. For example, to migrate the disks to the `fa-c20-2c` Kube Datastore, select `px-rwx-block-kubevirt-fa-c20-2c`.

OpenShift Virtualization copies the volume data to persistent volumes provisioned through the selected `StorageClass`. After the migration completes, the VM uses the new volumes on the destination Kube Datastore.

note

To migrate the disks of multiple VMs in a single operation, see Migrating VMs in a single cluster to a different storage class in the Red Hat OpenShift Container Platform documentation. On OpenShift Virtualization versions earlier than 4.20.14, migrating multiple VMs requires Migration Toolkit for Containers (MTC).

## Verify the migration​

After the migration completes:

-
Verify that the VM is running and its disks are accessible.

-
Verify that the migrated PVCs use the KDS-aware `StorageClass` associated with the destination Kube Datastore:

```

kubectl get pvc -n <namespace>

```

-
Verify that the volume replicas reside on storage pools associated with the destination Kube Datastore:

```

pxctl volume inspect <volume-name>

```

Identify the replica pools, and then run:

```

pxctl service pool show

```

Verify that the `kube_datastore` labels for the replica pools identify the destination Kube Datastore.

-
Verify the Kube Datastore capacity:

```

pxctl kubedatastore list

```

Confirm that the destination Kube Datastore reflects the migrated storage.

## Delete the source PVCs and DataVolumes​

OpenShift Virtualization does not delete the source PVCs after a storage class migration completes. Until you delete them, the source volumes continue to consume capacity in the source Kube Datastore.

If you created the VM from a template or golden image, each source disk also has a DataVolume that the VM still owns. If you delete only the PVC, the Containerized Data Importer (CDI) re-creates it with the same name and sets the DataVolume to `PendingPopulation`. In addition, the `Completed` virt-launcher pod from before the migration still references the source PVCs and keeps them in the `Terminating` state. To remove the source disks, delete the `Completed` pod, the source DataVolumes, and then any remaining source PVCs.

warning

Delete only the PVCs and DataVolumes that the migration replaced. Verify that the VM uses the new volumes and that its disks are accessible before you delete any PVC or DataVolume. Do not delete the golden image (the DataSource and its PVC) that the VM was cloned from.

After you verify that the migration completed successfully:

-
Verify that the VM runs on the new volumes and that its disks are accessible:

-
Verify that the VM is running:

```

kubectl get vm <vm-name> -n <namespace>

```

The `STATUS` column shows `Running`, and the `READY` column shows `True`.

-
List the PVCs that the running virt-launcher pod uses:

```

kubectl get pod <running-virt-launcher-pod-name> -n <namespace> -o jsonpath='{.spec.volumes[*].persistentVolumeClaim.claimName}'

```

To find the pod name, run `kubectl get pods -n <namespace> -l kubevirt.io=virt-launcher`. The running pod has the `Running` status.

The output lists only the new PVCs, which use the `StorageClass` of the destination Kube Datastore. If the output lists a source PVC, do not delete the source PVCs.

-
Open the VM console or connect to the VM, and verify that the guest operating system can read and write each disk. For example, list the disks and confirm that you can read the data on each mounted file system.

-
Identify the source disks. List the volumes that the VM currently uses:

```

kubectl get vm <vm-name> -n <namespace> -o jsonpath='{range .spec.template.spec.volumes[*]}{.name}{"\t"}{.dataVolume.name}{.persistentVolumeClaim.claimName}{"\n"}{end}'

```

Any PVC or DataVolume of this VM that the output does not list is a source disk that the migration replaced.

-
List the virt-launcher pods of the VM and identify the pod in the `Completed` state:

```

kubectl get pods -n <namespace> -l kubevirt.io=virt-launcher,vm.kubevirt.io/name=<vm-name>

```

-
Delete the `Completed` virt-launcher pod:

```

kubectl delete pod <completed-virt-launcher-pod-name> -n <namespace>

```

-
List the DataVolumes in the namespace:

```

kubectl get datavolume -n <namespace>

```

-
Delete each source DataVolume that you identified in step 2. Deleting a DataVolume also deletes its PVC:

```

kubectl delete datavolume <source-datavolume-name> -n <namespace>

```

-
If a source disk has no DataVolume, delete its PVC:

```

kubectl delete pvc <source-pvc-name> -n <namespace>

```

-
Verify that the source PVCs and DataVolumes no longer exist:

```

kubectl get pvc,datavolume -n <namespace>

```

important

If the source `StorageClass` uses `reclaimPolicy: Retain`, deleting the PVC leaves the PersistentVolume (PV) and the underlying Portworx volume intact. You must delete the PV and the Portworx volume to release the capacity. To do this:

-
Identify the source PVs in the `Released` state:

```

kubectl get pv

```

-
Delete each released source PV:

```

kubectl delete pv <source-pv-name>

```

-
To confirm that the source Kube Datastore released the capacity, run the following command:

```

pxctl kubedatastore list

```

## Backups and restores after disk migration​

Backups created before disk migration remain associated with the original PVCs. After migrating VM disks, consider the following:

-
In-place restores: Restoring a pre-migration backup in place restores the original PVC, not the disk currently used by the VM. If the original PVC has been deleted, the restore fails.

-
Restoring existing backups: To restore a pre-migration backup, restore it to a new PVC and attach the PVC to the VM as a disk. Use a KDS-aware `StorageClass` for the destination Kube Datastore. If the `StorageClass` does not specify KDS affinity, Portworx restores the disk to the source KDS.

-
Backup schedules: Existing backup schedules reference the original PVC names. Create new backup schedules for the migrated PVCs to ensure that the new VM disks are backed up. If backup schedules are created automatically, verify that a schedule exists for each new PVC:

```

storkctl get volumesnapshotschedule -n <namespace>

```

If a schedule does not exist for a new PVC, create one.

## Related topics​

- Kube Datastore for Portworx Enterprise 3.7.0

- Kube Datastore-aware StorageClasses

- Manage Portworx RWX Block Volumes on OpenShift for KubeVirt VMs

- Troubleshooting, Known Issues, and Limitations for KubeVirt VMs

In this topic:
