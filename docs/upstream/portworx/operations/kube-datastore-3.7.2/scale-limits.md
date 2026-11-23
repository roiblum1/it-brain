# Scale Limits and Limitations for KDS Dynamic Pools

Source: https://docs.portworx.com/portworx-enterprise/operations/kube-datastore-3.7.2/scale-limits (Portworx Enterprise latest)

Scale Limits and Limitations for KDS Dynamic Pools | Portworx Enterprise Documentation

This topic explains the scale limits for Kube Datastore (KDS) and dynamic pools, how to reserve capacity for node failures and pool failover, and the limitations of KDS and dynamic pools.

## Scale limits​

Portworx Enterprise applies scale limits for dynamic pools at the cluster, node, pool, and volume levels. Consider these limits when planning storage capacity and pool failover.

ScopeRecommended limitHard limit

Cluster5,000 attached volumesN/A

Node700 attached volumes1,024 attached volumes

Node12 storage pools16 storage pools

Pool450 volumes and snapshots combined, including up to 150 regular volumes (attached, detached, and clones) and up to 300 snapshots1,024 volumes

Volume2 snapshots per regular volume64 snapshots per volume

note

If you plan to provision more than 5,000 volumes in a cluster, additional CSI attacher configuration is required. For more information, see CSI attacher parameters.

### Pool sizing limits​

The following table lists the supported limits for dynamic pool size, drives per pool, and pools per node, including the recommended pool count to maintain capacity for failover.

SettingValueDescription

Drives per pool1Dynamic pools require exactly one FlashArray Cloud Drive (FACD) per pool.

Recommended pools per node12Keep each node at no more than 12 pools during normal operation to reserve capacity for pool failover.

Maximum pools per node (hard limit)16Portworx does not support more than 16 storage pools per node. Configure the pool count limit by using `limit_pools_count`. For more information, see limit_pools_count.

### Reserve capacity for node failures​

When a node fails, Portworx must have enough capacity on the surviving nodes to accommodate its pools and volumes.

The recommended limit of 700 attached volumes per node is lower than the hard limit of 1,024 to provide capacity for volumes relocated from failed nodes.

Smaller clusters need proportionally more available capacity because each node represents a larger share of the cluster.

For example, consider a three-node cluster with 700 attached volumes per node. If one node fails, the two surviving nodes must accommodate its 700 volumes. Assuming an even distribution, each surviving node would need to support 1,050 attached volumes, exceeding the hard limit of 1,024.

To survive one node failure, a three-node cluster can therefore support a maximum of 682 attached volumes per node, assuming volumes are evenly distributed.

Use the following formulas to calculate the maximum number of attached volumes and pools per node:

```

Attached volumes per node = min(700, 1024 × (N - f) / N)

Pools per node = min(12, 16 × (N - f) / N)

```

Where:

- `N` is the total number of nodes in the cluster.

- `f` is the number of simultaneous node failures the cluster must tolerate.

Round the calculated values down to the nearest whole number.

The recommended limit of 700 attached volumes per node applies from:

- Four nodes when planning for one node failure.

- Seven nodes when planning for two node failures.

- Ten nodes when planning for three node failures.

For additional headroom, plan to use approximately 90% of the calculated limits. For example, a three-node cluster designed to survive one node failure should target approximately 614 attached volumes per node.

When configuring `limit_pools_count`, reserve enough pool slots on the surviving nodes to accommodate the pools from at least one failed node. Do not configure every node to operate at its maximum pool count.

For example, consider a six-node cluster with eight pools per node. If one node fails, its eight pools must move to the five surviving nodes. Assuming the pools can be distributed evenly, each surviving node must be able to accept up to two additional pools. Set `limit_pools_count` to at least `10` to provide this capacity. As a general guideline, Portworx recommends reserving four additional pool slots on each node, which is `12` in this example.

### Plan capacity by cluster size​

The following table shows the calculated maximum number of attached volumes and pools per node for common cluster sizes, based on the number of node failures the cluster must tolerate.

NodesAttached volumes per node (1 failure)Pools per node (1 failure)Attached volumes per node (2 failures)Pools per node (2 failures)

3682103415

4700125128

5700126149

67001268210

77001270011

87001270012

note

- The cluster-wide limit of 5,000 attached volumes applies regardless of the number of nodes. If you plan to provision more than 5,000 volumes in a cluster, additional CSI attacher configuration is required. For more information, see CSI attacher parameters.

- These calculations assume an even distribution of volumes and pools. Actual failover also depends on eligible destination nodes, placement requirements, and available pool slots.

### Concurrent failover limits​

Portworx limits the number of node and pool failovers that can occur simultaneously.

ScopeLimit

Concurrent node failovers5 nodes

Concurrent pool failovers16 pools

These limits define the maximum number of failover operations that Portworx can process concurrently. They do not guarantee that all pools can be relocated.

Successful failover also requires eligible destination nodes with enough available pool slots and volume attachment capacity.

Exceeding the validated limits can increase pool failover time and affect workload I/O. On Windows VMs, storage delays can also cause storage-related operating system events.

## Limitations​

### KDS Limitations​

Consider the following limitations before using Kube Datastore:

-
A KDS must have enough storage pools on different nodes to support the replication factor of a volume. If the KDS does not have enough pools to place all replicas, volume provisioning fails.

-
The `pxctl kds list` command reports only the current KDS capacity. To monitor historical KDS capacity and performance trends, use the Kube Datastore metrics.

### Dynamic Pool Limitations​

Consider the following limitations before enabling dynamic pools:

- Dynamic pools do not support SharedV4 volumes.

- Dynamic pools do not support Auto Journal Device.

- Dynamic pools do not support smart and parallel upgrades.

- Dynamic pools require one FlashArray Cloud Drive (FACD) per pool. Clusters containing multi-drive pools cannot be upgraded to a configuration with dynamic pools enabled.

- Portworx Enterprise supports pool failover on a maximum of five nodes and 16 pools at the same time.

- Upgrading multiple nodes simultaneously when dynamic pools are enabled can disrupt pool relocation and cause application downtime. To reduce this risk, upgrade only one node at a time.

- Pool failover or dynamic pool rebalance during Rapid VM Migration with `XCOPY` can cause the data copy to fail. Pause both pool failover and dynamic pool rebalance before starting the migration, and resume them after the migration completes. For more information, see Step 6: Pause pool failover and rebalance.

- In clusters with multiple FlashArrays, `XCOPY` fails if the source and destination volumes reside on different FlashArrays. Set `kube_datastore_affinity` in the destination `StorageClass` (`PXD_STORAGE_CLASS`) to ensure that volumes are provisioned on the correct KDS. For VMs with disks on different datastores, create a separate storage secret and `StorageClass` for each datastore. For more information, see Rapid Migration of VMs from VMware to OpenShift Virtualization using XCOPY.

- Portworx does not support pool migration while a CloudSnap backup or restore is running on a volume in that pool. If the pool moves, the backup or restore can fail. Portworx deletes a partially restored volume if the restore fails, but the cloud snapshot remains unaffected.
Wait for running CloudSnap operations to complete before planned pool migrations, node reboots, or upgrades. After a pool moves, check the operation status by running `pxctl cloudsnap status` and retry any failed operations. A failed restore must start again with a new destination volume.

## Related topics​

- Manage Dynamic Pool Failover

- Pool placement and rebalance

In this topic:
