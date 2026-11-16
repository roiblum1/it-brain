# Kube Datastore-Aware Volume Placement

Source: https://docs.portworx.com/portworx-enterprise/operations/kube-datastore-3.7.2/kds-volume-placement (Portworx Enterprise latest)

Kube Datastore-Aware Volume Placement | Portworx Enterprise Documentation

Portworx Enterprise automatically creates and manages Kube Datastores (KDS) for FlashArrays used by the cluster. You can control which FlashArray backs a storage pool and where Portworx provisions volumes by using KDS affinity.

This topic describes how to:

- Select the KDS that provides capacity for storage pools.

- View Kube Datastores and identify the FlashArray associated with each pool.

- Create KDS-aware `StorageClass` resources to provision volumes on a specific KDS.

- Understand how KDS affinity affects volume placement and existing replicas.

## Select the KDS for storage pools​

Each KDS is backed by one FlashArray. Portworx creates a KDS when the first storage pool is provisioned on a FlashArray, and it adds later pools on that array to the same KDS. To select the KDS for a storage pool, set the `storage_backend` parameter in the device specification to the name or management endpoint of the FlashArray that backs the KDS.

You can select a KDS:

- when installing Portworx Enterprise, or

- when adding storage pools to an existing cluster.

### Create a storage pool on a FlashArray added to an existing cluster​

If you add a FlashArray to an existing cluster, you can create storage pools on that array.

note

To add a storage pool, the node must be in pool maintenance mode. Node maintenance mode alone is not sufficient. Otherwise, the command fails with the `Requires pool maintenance mode` error. For more information, see Storage pool maintenance.

To create a storage pool, run the following command on each storage node where you want to provision the pool:

```

pxctl service drive add --newpool --spec size=<size>,storage_backend=<fa-name>

```

Replace:

- `<size>` with the pool size.

- `<fa-name>` with the FlashArray name.

Portworx creates a KDS when the first storage pool is provisioned on the new FlashArray. Additional pools created on that FlashArray are added to the same KDS.

## View Kube Datastores and storage pools​

After provisioning storage pools, you can verify which Kube Datastores exist in the cluster and identify the FlashArray associated with each pool.

### List Kube Datastores​

To list the Kube Datastores in your cluster, run:

```

pxctl kubedatastore list

```

You can also use the `kds` alias:

```

pxctl kds list

```

The output is similar to the following:

```

NAME            SIZE            AVAILABLE       USED    PROVISIONED     NUMBER OF POOLS

ph530-a25       882 GiB         838 GiB         44 GiB  0 B             6

```

The output shows the capacity and number of storage pools associated with each KDS.

note

The `AVAILABLE` value represents the total available capacity across all pools in a KDS.

Because this capacity is distributed across multiple pools, the maximum size of an individual volume can be smaller than the reported `AVAILABLE` value.

For more information, see pxctl kubedatastore.

### Identify the Kube Datastore and FlashArray for a storage pool​

To identify the KDS and FlashArray associated with a storage pool, run:

```

pxctl service pool show

```

For each pool, check the following fields:

FieldDescription

`kube_datastore`Name of the KDS that contains the pool.

`kube_datastore_id`UUID of the FlashArray that backs the KDS.

`Drives`Device path of the FlashArray volume that provides storage capacity to the pool.

`Dynamic Pool`Indicates whether the pool supports dynamic pool failover.

## Provision volumes with KDS-aware StorageClasses​

KDS affinity allows you to provision volumes on storage pools backed by a specific FlashArray.

To configure KDS affinity, set the `kube_datastore_affinity` parameter in a `StorageClass` to the name of the target KDS.

Limitation

- The `kube_datastore_affinity` parameter is not supported for FlashArray Direct Access (FADA) volumes. Use this parameter only for volumes provisioned from Portworx storage pools.

- The `kube_datastore_affinity` parameter accepts only one KDS name. You cannot configure a volume with affinity to multiple Kube Datastores.

- If you plan to use asynchronous disaster recovery (DR) or cloudsnap restore with Kube Datastore (KDS) across clusters that use different FlashArrays, do not set `kube_datastore_affinity` in the `StorageClass`. Portworx stores the source FlashArray ID in the volume's KDS affinity rule and retains this rule during restoration. If the destination cluster uses a different FlashArray, the restore fails.
 To control volume placement in this configuration, use a custom volume placement strategy (VPS) rule that does not use system-defined labels.

- When restoring a CloudSnap backup to a specific Kube Datastore (KDS), explicitly specify the target KDS by setting `kube_datastore_affinity` in the restore PVC's `StorageClass` or by using `pxctl cloudsnap restore --label kube_datastore_affinity=<KDS>`. If you do not specify a KDS, Portworx Enterprise uses the source volume information stored in the backup. Moving the source volume to another KDS does not update this information in existing backups. To restore the volume to the new KDS, you must explicitly specify it.

- Portworx does not support restoring or cloning volumes from the trashcan directly to a different Kube Datastore (KDS). Restored or cloned volumes remain on the original KDS, even if you specify a different `kube_datastore_affinity` in the `StorageClass` or `pxctl` command. To move a volume to another KDS, first restore it from the trashcan or clone it, and then migrate it to the destination KDS.

When a workload requests storage, Portworx uses the following information to determine volume placement:

- The workload references a persistent volume claim (PVC).

- The PVC references a `StorageClass`.

- If the `StorageClass` specifies `kube_datastore_affinity`, Portworx selects eligible storage pools in the specified KDS.

- The selected pools provide storage capacity from the FlashArray associated with that KDS.

KDS affinity works as a placement rule, similar to a volume placement strategy (VPS). If other placement rules apply, Portworx combines them by using a logical AND. This includes the internal volume affinity rule used to colocate disks belonging to a KubeVirt VM.

Portworx applies KDS affinity during initial volume provisioning and subsequent storage rebalancing operations.

### Create a KDS-aware StorageClass​

To provision volumes on a specific KDS, create a `StorageClass` with the `kube_datastore_affinity` parameter.

note

When selecting a Kube Datastore (KDS) for a KubeVirt virtual machine (VM), Portworx by Everpure recommends that you provision all volumes of the VM within the same KDS to support pool colocation. If the volumes are placed in different Kube Datastores, Portworx might not be able to keep the VM and its storage on the same node.

For volumes that use dynamic pools, set the replication factor to `1`.

The following example creates a `StorageClass` that provisions `repl=1` volumes on the `fa-x90-1a` KDS.

-
Save the following configuration to a file named `px-kds-fa-x90-1a.yaml`:

px-kds-fa-x90-1a.yaml

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: px-kds-fa-x90-1a

provisioner: pxd.portworx.com

parameters:

  repl: "1"

  kube_datastore_affinity: "fa-x90-1a"

volumeBindingMode: WaitForFirstConsumer

allowVolumeExpansion: true

```

Replace `fa-x90-1a` with the name of the KDS where you want to provision volumes.

To find the available KDS names, see List Kube Datastores.

-
Create the `StorageClass`:

```

kubectl apply -f px-kds-fa-x90-1a.yaml

```

-
Verify that the `StorageClass` was created:

```

kubectl get storageclass px-kds-fa-x90-1a

```

For KubeVirt VM workloads, Portworx by Everpure recommends `volumeBindingMode: WaitForFirstConsumer`. This setting allows Portworx to consider the node selected for the VM when provisioning its volumes.

For more information, see Initial hyperconvergence.

For supported `StorageClass` parameters, see Portworx Enterprise StorageClass.

note

You do not need to manually create KDS-aware StorageClasses for KubeVirt VMs.

The Portworx Operator generates a KDS-aware version of each default KubeVirt `StorageClass` for every KDS in the cluster.

For more information, see Kube Datastore-aware StorageClasses.

### Update StorageClasses after renaming a FlashArray​

The KDS name is derived from the FlashArray name. Renaming a FlashArray therefore changes the name of its associated KDS.

If you rename a FlashArray:

- Recreate any `StorageClass` that references the previous KDS name.

- Update any user-defined volume placement strategy rules that reference the previous name.

## Understand how volumes are associated with Kube Datastores​

KDS affinity determines where Portworx should place a volume. However, the current locations of the volume's replicas determine where its data resides.

These two locations can differ, particularly when an existing volume is assigned a new KDS affinity rule.

Portworx considers a volume associated with a KDS when either of the following conditions is true:

- The volume has affinity to the KDS through a `replicaAffinity` rule.

- At least one replica of the volume resides on a storage pool in the KDS.

As a result, a volume can be associated with multiple Kube Datastores even though its `kube_datastore_affinity` parameter specifies only one KDS.

For example, a volume can have affinity to KDS A while its existing replicas remain on pools in KDS B.

How Portworx handles this difference depends on the volume type.

### KubeVirt VM disks​

For KubeVirt VM disks, Portworx periodically checks replica placement against the configured KDS affinity.

If the replicas are not on eligible pools in the specified KDS, Portworx moves them to eligible pools in that KDS.

### Other volumes​

For non-KubeVirt volumes, Portworx does not automatically move existing replicas when KDS affinity changes.

The affinity rule applies only to new or replacement replicas.

To move an existing non-KubeVirt volume to another KDS, migrate its data to a new PVC that uses a `StorageClass` with affinity to the target KDS.

### Volumes without KDS affinity​

Volumes that do not use KDS affinity are not restricted to a specific KDS.

Portworx can place their replicas on storage pools in different Kube Datastores, subject to the applicable volume placement rules.

## Related topics​

- Kube Datastore

- Portworx Enterprise StorageClass

- Volume Placement Strategies

- pxctl kubedatastore

In this topic:
