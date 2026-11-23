# Kube Datastore for Portworx Enterprise 3.7.0

Source: https://docs.portworx.com/portworx-enterprise/operations/kube-datastore-3.7.0 (Portworx Enterprise latest)

Kube Datastore for Portworx Enterprise 3.7.0 | Portworx Enterprise Documentation

important

Kube Datastore (KDS) was available under Directed Availability (DA) in Portworx Enterprise 3.7.0 and is now generally available (GA) in version 3.7.2. Upgrade to Portworx Enterprise 3.7.2 to access additional capabilities, including higher scale limits, compute-aware placement and hyperconvergence, and fastpath support on KDS dynamic pools. For more information, see Kube Datastore for Portworx Enterprise 3.7.2 and Dynamic Pool Failover.

Kube Datastore (KDS) is a logical grouping of Portworx storage pools backed by the same FlashArray. KDS consists of one or more static or dynamic pools attached to different Kubernetes worker nodes. In a FlashArray Cloud Drive (FACD) deployment, Portworx creates one KDS for each FlashArray used by the cluster.
For example, if a cluster uses two FlashArrays, Portworx creates two Kube Datastores and each KDS contains the storage pools backed by its corresponding FlashArray.

With KDS, you can:

- View storage capacity at the FlashArray level.

- Place volumes on storage pools backed by a specific FlashArray.

- Manage storage pools across multiple Kubernetes nodes.

- Use dynamic pools to provide availability for `repl=1` volumes during node failures or maintenance.

Portworx applies the following labels to storage pools associated with a KDS:

LabelValueDescription

`kube_datastore`FlashArray nameIdentifies the KDS that contains the pool. Portworx uses this value as the KDS display name.

`kube_datastore_id`FlashArray UUIDUniquely identifies the KDS. Portworx uses this value in volume placement rules.

Portworx manages these labels automatically. You cannot manually add, modify, or remove them.

## Static and dynamic storage pools in KDS​

Portworx defines static and dynamic pools as follows:

Static pools: Static pools are storage pools that cannot move between nodes during pool failover. These pools contain volumes with `repl=2` or higher. If a node fails, another replica on a healthy node can continue serving replicated volumes. These pools can containSharedV4 volumes, or volumes with journal profiles.

Dynamic pools: Dynamic pools are storage pools that can move between nodes during failover. These pools contain volumes with replication factor 1 (`repl=1`). They use FlashArray Cloud Drives (FACD) and rely on FlashArray for storage redundancy. If a node fails, Portworx moves the pool and its volumes to a healthy node. The data remains on FlashArray, so Portworx does not need to copy data or rebuild replicas.

A KDS can contain both, dynamic pools with `repl=1` volumes and static pools with `repl=2` volumes. If a node fails, only the dynamic pools move.

For more information about failover behavior, destination-node selection, and conditions that prevent failover, see Dynamic Pool Failover.

### When to use static vs dynamic pools​

Choose the pool type based on your workload's storage and availability requirements.

-
Use dynamic pools for KubeVirt VMs, container workloads, and other applications that use `repl=1` volumes on FlashArray. Choose dynamic pools if you want Portworx to move pools and their volumes to healthy nodes during failover without copying data or rebuilding replicas. Dynamic pools rely on FlashArray for storage redundancy, reducing storage consumption, network traffic, and processing overhead associated with Portworx replication.

-
Use static pools for workloads that require repl=2 or higher for data availability, or when you use SharedV4 volumes or volumes with journal profiles. Pools backed by local or pre-provisioned storage also remain static.

To control volume placement, use volume placement strategies.

## Why use KDS dynamic pools?​

In a traditional shared-nothing environment, each Kubernetes worker node has its own storage. Portworx replicates volumes across nodes to protect data. For example, a volume with `repl=3` has three replicas on different nodes.

However, when multiple storage pools use the same FlashArray, Portworx replication adds overhead because FlashArray already provides storage-level redundancy. This overhead includes:

- Storage capacity: Multiple replicas consume additional capacity on the same FlashArray.

- Network traffic: Portworx sends replicated writes between worker nodes.

- Storage processing: FlashArray processes the additional data created by Portworx replication.

KDS dynamic pools reduce this overhead by using volumes with replication factor 1 (`repl=1`). These volumes rely on FlashArray for data protection, while Portworx provides availability by moving dynamic pools between nodes instead of maintaining additional replicas.

Dynamic pools provide the following benefits:

- Reduced storage consumption: Volumes use one Portworx replica instead of multiple replicas.

- Reduced network traffic: Portworx does not generate replication or replica rebuild traffic between nodes for `repl=1` volumes.

- Reduced storage processing: FlashArray does not process the additional copies created by Portworx replication.

- Pool failover without copying data: Portworx moves the pool and its volumes to another node without copying data or rebuilding replicas.

- Flexible pool placement: Portworx can move pools between healthy nodes that meet the placement and capacity requirements.

- VM storage placement: Portworx can keep related KubeVirt VM storage pools together on the same node to improve I/O performance.

## Storage configuration for dynamic and static Pools​

In environments that use both dynamic and static pools, clusters may contain a mix of `repl=1` and `repl=2` (or higher) volumes. Mixed pool configurations are supported but require explicit planning to ensure correct workload placement and failover behavior.

Dynamic pools support only `repl=1` volumes and enable pool-level failover. Volumes with higher replication factors (`repl=2` or `repl=3`) use replication-based high availability and do not participate in dynamic pool failover.

When you configure storage, follow these guidelines:

- Use dynamic pools for workloads that require fast failover using shared storage backends.

- Use static pools for workloads that require replication-based availability (`repl=2+`).

- Configure storage classes with the appropriate replication factor. For example,`repl=1` for dynamic pools.

If you are migrating from a replication-based setup to dynamic pools:

- Convert existing volumes to `repl=1` using HA reduction. For more information, see Decreasing the replication factor.

- Pool failover does not occur if any volume in the pool has a replication factor greater than 1.

In mixed environments:

- Pools with `repl=1` volumes can fail over across nodes.

- Pools with `repl=2+` volumes use replication-based recovery.

- Failover eligibility is determined at the pool level based on the volumes present.

## Create a Kube Datastore on a specific FlashArray​

Portworx Enterprise creates a Kube Datastore when the first storage pool is provisioned on a FlashArray. To control which FlashArray Portworx uses for a storage pool, specify the `storage_backend` field in the device specification. Set the value to the FlashArray name or management endpoint.

### Create pools from multiple FlashArrays during installation​

To provision a separate storage pool from each FlashArray on every storage node, add a device specification for each FlashArray to the `cloudStorage` section of the `StorageCluster`:

```

spec:

  cloudStorage:

    deviceSpecs:

      - size=100,storage_backend=<fa1-name>

      - size=100,storage_backend=<fa2-management-endpoint>

      - size=200,storage_backend=<fa3-name>

```

This configuration provisions three separate storage pools on each storage node, one from each FlashArray. Portworx creates a separate Kube Datastore for each FlashArray when its first pool is provisioned.

Pool provisioning honors CSI topology. If a device specification includes the `pod` field, Portworx also honors the specified FlashArray pod placement.

note

Portworx Enterprise applies `deviceSpecs` only when provisioning a new storage node. Changes to `deviceSpecs` do not affect existing storage nodes. Similarly, changes that you make to storage pools on an existing node by using `pxctl` are not reflected in the `StorageCluster` specification.

### Create a pool on a FlashArray added to an existing cluster​

To create a storage pool on a FlashArray that you added to an existing Portworx cluster, run the following command on each storage node where you want to create the pool:

```

pxctl service drive add --newpool --spec size=<size>,storage_backend=<fa-name>

```

Replace:

- `<size>` with the pool size.

- `<fa-name>` with the name of the FlashArray.

Portworx Enterprise creates a Kube Datastore for the FlashArray when the first storage pool is provisioned on it. Additional pools provisioned on the same FlashArray are automatically associated with the existing Kube Datastore.

## Kube Datastore affinity​

Kube Datastore affinity lets you place volumes created from a `StorageClass` on a specific KDS. Configure KDS affinity by setting the `kube_datastore_affinity` parameter in the `StorageClass` to the name of the target KDS. Portworx Enterprise then provisions volumes created from that `StorageClass` on pools that belong to the specified KDS.

KDS affinity acts as a placement rule similar to a volume placement strategy (VPS). Portworx honors the KDS affinity during initial volume provisioning and subsequent storage rebalancing operations.

note

The `kube_datastore_affinity` parameter is not supported for FlashArray Direct Access (FADA) volumes. Use this parameter only for volumes provisioned from Portworx storage pools.

If a volume has other placement rules, including the internal volume affinity rule that Portworx uses to colocate disks for a KubeVirt VM, Portworx combines the rules by using a logical AND.

WARNING

-
If you plan to use asynchronous disaster recovery (DR) or cloudsnap restore with Kube Datastore (KDS) across clusters that use different FlashArrays, do not set `kube_datastore_affinity` in the `StorageClass`. Portworx stores the source FlashArray ID in the volume's KDS affinity rule and retains this rule during restoration. If the destination cluster uses a different FlashArray, the restore fails.
 To control volume placement in this configuration, use a custom volume placement strategy (VPS) rule that does not use system-defined labels.

-
The `kube_datastore_affinity` parameter accepts only one KDS name. You cannot configure a volume with affinity to multiple Kube Datastores.

### How volumes map to Kube Datastores​

KDS affinity specifies where Portworx should place a volume, while the current replica locations indicate where its data resides. Therefore, KDS affinity and current KDS membership might differ.

Portworx considers a volume to be associated with a KDS when either of the following conditions is true:

- The volume has affinity to the KDS through a `replicaAffinity` rule.

- At least one volume replica resides on a pool in the KDS.

A volume can therefore be associated with multiple Kube Datastores. For example:

-
A volume can have affinity to one KDS while its replicas reside on another KDS. The behavior differs by volume type:

- KubeVirt VM disks: Portworx periodically re-evaluates replica placement and moves replicas to pools in the KDS specified by the affinity rule.

- Other volumes: Portworx does not automatically relocate existing replicas. The affinity rule applies only to new and replacement replicas. To move an existing volume to the target KDS, migrate its data to a PVC that uses a StorageClass with affinity to that KDS.

-
A volume has no KDS affinity and has replicas on pools that belong to different Kube Datastores.

### Create a KDS-aware StorageClass​

To place volumes on a specific KDS, create a `StorageClass` and set `kube_datastore_affinity` to the KDS name.

The following example places volumes on the `fa-x90-1a` KDS:

StorageClass

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: px-kds-fa-x90-1a

provisioner: pxd.portworx.com

parameters:

  repl: "2"

  kube_datastore_affinity: "fa-x90-1a"

volumeBindingMode: WaitForFirstConsumer

allowVolumeExpansion: true

```

To find the KDS names available in your cluster, see List Kube Datastores. For information about supported `StorageClass` parameters, see Portworx Enterprise StorageClass.

note

- For KubeVirt VMs, you do not need to create KDS-aware StorageClasses manually. The Portworx Operator generates a KDS-aware version of each default KubeVirt `StorageClass` for every KDS in the cluster. For more information, see Kube Datastore-aware StorageClasses.

- If you rename a FlashArray, the name of the KDS associated with it also changes. Recreate any `StorageClass` that references the previous KDS name, and update any user-defined VPS rules that reference that name.

## Migrate VM disks to a different Kube Datastore​

You can use KDS-aware StorageClasses to migrate existing KubeVirt VM disks between Kube Datastores. During storage migration, select the KDS-aware `StorageClass` associated with the destination KDS.

For more information, see Migrate KubeVirt VM disks to a different Kube Datastore.

## List Kube Datastores​

To list the Kube Datastores in your Portworx cluster, run the following command:

```

pxctl kubedatastore list

```

You can also use the `kds` alias:

```

pxctl kds list

```

Example output:

```

NAME            SIZE            AVAILABLE       USED    PROVISIONED     NUMBER OF POOLS

ph530-a25       882 GiB         838 GiB         44 GiB  0 B             6

```

For more information, see pxctl kubedatastore.

note

The `AVAILABLE` value represents the total available capacity across all pools in the KDS. Because this capacity is distributed across multiple pools, the maximum size of an individual volume can be smaller than the reported `AVAILABLE` value.

## Limitations​

Consider the following when you use Kube Datastore:

-
Kube Datastore supports only the FlashArray CloudDrive (FACD) backend.

-
Portworx Enterprise creates a KDS for a new FlashArray only after at least one storage pool is created on that FlashArray.

-
A pool associated with a KDS cannot include drives from another FlashArray.

-
Because KDS affinity requires all replicas of a volume to reside in the same Kube Datastore, the target KDS must have enough storage pools on distinct nodes to satisfy the volume's replication factor.

If the target KDS does not have enough eligible pools on distinct nodes, volume provisioning fails with the following error:

```

could not find enough nodes to provision volume

```

-
The `pxctl kds list` command reports only the current KDS capacity. To monitor historical KDS capacity and performance trends, use the Kube Datastore metrics.

## Related topics​

- Dynamic Pool Failover for Portworx Enterprise 3.7.0

- Storage pools

- Volume Placement Strategies

- Migrate KubeVirt VM Disks to a Different Kube Datastore (3.7.0)

In this topic:
