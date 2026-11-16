# Troubleshoot Dynamic Pools and KubeVirt Workloads

Source: https://docs.portworx.com/portworx-enterprise/operations/kube-datastore-3.7.2/kds-troubleshoot (Portworx Enterprise latest)

Troubleshoot Dynamic Pools and KubeVirt Workloads | Portworx Enterprise Documentation

Use this topic to troubleshoot issues with dynamic pool failover, pool migration, rebalance, KubeVirt VM placement, and cluster upgrades.

For information about the alerts and cluster options referenced in this topic, see Cluster options, alerts, and metrics.

## A pool does not fail over​

If a dynamic pool does not fail over, check whether its volume configuration or an ongoing operation is preventing migration.

-
Check the storage pools:

-
To view storage pools on the current node, run:

```

pxctl service pool show

```

-
To view storage pools across the cluster, run:

```

pxctl cluster provision-status

```

Check the `DYNAMIC` column. If a pool that you expect to be dynamic is not marked as dynamic, verify that it does not contain any of the following volumes that prevent pool failover:

- Volumes with a replication factor greater than 1.

- SharedV4 volumes.

- Volumes with journal profiles.

To resolve the issue, move the volume that prevents failover to a static pool or, where appropriate, reduce its replication factor. Then retry the migration.

-
Verify that no operation is blocking pool failover.

For the complete list of conditions, see When pool failover does not occur.

-
Check for alerts related to pool failover:

```

pxctl alerts show

```

For more information on these alerts, see Alerts.

## A pool migration does not progress​

If a pool migration remains in the same stage, check the migration plan and the health of the source and destination nodes.

-
Check the migration status:

```

pxctl service pool migrate status --intent-id <intent-id>

```

A migration progresses through the following stages:

```

init

pending

deactivation_in_progress

activation_in_progress

activation_pool_ready

PLAN_SUCCEEDED

```

-
After the migration reaches PLAN_SUCCEEDED, check the node health:

```

pxctl status

```

Verify that the source and destination nodes show an `Online` status.

-
Check the storage node status:

```

kubectl get storagenodes -A

```

note

An intent represents a node-level migration request. Each intent contains a failover plan for every pool being moved.

A plan that remains in `init` might be waiting for the failover sequencer while another pool attaches to the same destination node.

## Not all pools moved after a node-level migration​

A CLI-initiated node-level migration can report `FAILOVER_SUCCEEDED` even when some pools remain on the source node.

Portworx limits the number of concurrent pool failovers across the cluster. If other migrations are using the available failover slots, Portworx moves only as many pools as the remaining slots allow and defers the rest. When this happens, Portworx raises the `PoolFailoverPoolsDeferred` alert.

This behavior applies only to CLI-initiated node-level migrations. During Portworx upgrades and planned node reboots, Portworx migrates all eligible pools on the node.

Portworx does not automatically retry deferred pools when failover slots become available.

To resolve the issue:

-
Check which pools remain on the source node:

```

pxctl cluster provision-status

```

In the output, check the `NODE` column for pools that are still on the source node.

-
Verify that the pools are eligible for migration.

note

Pools containing volumes with a replication factor greater than 1, SharedV4 volumes, or journal volumes are not eligible for failover.

For more information, see When pool failover does not occur.

-
Wait for active migrations to complete:

```

pxctl service pool migrate list --active-only

```

-
Run the node-level migration command again:

```

pxctl service pool migrate --node <node-id>

```

For information about configuring the maximum number of concurrent pool failovers, see Cluster options.

## A pool affinity group is split across nodes​

A pool affinity group is split when its pools are distributed across multiple nodes.

To investigate the issue:

-
Check the affinity group:

```

pxctl service pool affinity-group --group-by affinity-group

```

-
Check the `SPLIT` column.

A value of `yes` indicates that the pools in the affinity group are distributed across multiple nodes.

-
Verify that an eligible node has enough capacity to host all pools in the affinity group.

Common reasons for a split affinity group include:

- No node has enough available pool slots for all pools in the group.

- A node that could host the group is cordoned, unhealthy, or in maintenance.

- The affinity group contains more pools than can fit on one node.

Portworx attempts to bring the pools together during rebalance.

If the group contains more pools than can fit on one node, consider splitting the workload across two affinity groups.

If the group remains split for 10 consecutive rebalance cycles, Portworx raises the `PoolAffinityGroupSplit` alert.

## Pause pool failover​

If a storage pool or node has an issue that requires investigation, you can temporarily pause automatic pool failover to prevent Portworx from initiating additional pool relocations while you troubleshoot the issue.

To pause automatic pool failover, run:

```

pxctl cluster options update --pause-pool-failovers=true

```

After resolving the issue, resume automatic pool failover:

```

pxctl cluster options update --pause-pool-failovers=false

```

important

Resume automatic pool failover after troubleshooting is complete. While failover is paused, Portworx does not automatically relocate pools when a node becomes unavailable, which can affect workload availability.

## Rebalance does not run​

Rebalance can be delayed or blocked by other cluster operations.

Check whether any of the following conditions apply:

- An upgrade is in progress.

- Pool failover is in progress.

- A failover intent is active.

- A not is not up.

- Rebalance is paused by a cluster option.

Also verify that non-decommissioned nodes are available as rebalance destinations.

Resolve the blocking condition and allow the next rebalance cycle to run.

For more information, see Dynamic pool rebalance.

## A fastpath volume does not return to active after a pool move​

During pool migration, Portworx switches fastpath volumes to the standard I/O path.

After the pool comes online on the destination node, Portworx attempts to reactivate fastpath for eligible volumes.

A volume can report an inactive fastpath state during and shortly after migration.

If a volume remains inactive:

- Allow time for fastpath to reactivate. Pools with many fastpath volumes can take longer to complete activation.

- Verify that no pool migration plan exists for the pool. Portworx prevents fastpath activation while a migration plan exists.

- Verify that the nodes involved in the remote fastpath connection run the same Portworx Enterprise version.

- Check for fastpath alerts on the affected volumes.

For more information, see Fastpath behavior during failover.

## A VM migration from VMware fails​

Rapid VM Migration runs a conversion job on a node that hosts a volume replica. The job requires access to the local thin pool metadata and the backing FlashArray volume.

If a migration fails, perform the following checks:

-
Review the conversion job logs for data-copy failures, resource pressure, and scheduler errors.

-
Verify that the Portworx nodes hosting the volume replicas are healthy.

-
Verify that the destination nodes have enough CPU and memory to schedule the intermediate VM instance.

-
Verify that pool failover is paused.

If a pool moves during an `XCOPY` operation, Portworx deletes the device-mapper (dm) devices that `XCOPY` writes to. This causes the copy to fail, and the migration pod continues to report errors.

To recover:

-
Pause pool failover.

For more information, see Pause pool failover.

-
Check the `XCOPY` pods for transient `XCOPY` errors.

-
If the pods report these errors, delete the hook pod in the `openshift-mtv` namespace.

Deleting the hook pod removes the PVCs and `XCOPY` pods and starts the migration again. With pool failover paused, the same pool-movement error does not recur.

-
If the cluster uses multiple FlashArrays, verify that the destination volumes are on the same FlashArray as the source datastore. `XCOPY` cannot copy data between FlashArrays.

To place the destination volumes on the same FlashArray, set the `kube_datastore_affinity` parameter in the destination `StorageClass` to the Kube Datastore (KDS) of the source VM disk:

```

parameters:

  kube_datastore_affinity: <source-kds-name>

```

Set this parameter only on the Portworx (`pxd`) `StorageClass`. Do not set it on the FADA `StorageClass` that you map in the storage map.

If the VM has disks on different datastores, create a separate `StorageClass` for each datastore.

For more information, see Rapid VM Migration limitations.

Intermediate VM instances and temporary conversion pods are removed automatically, whether the migration succeeds or fails.

For more information, see Migrate VMs from VMware to Kube Datastore.

## A VM remains in the `Scheduling` state after node recovery​

After multiple nodes recover from an outage, a VM can remain in the `Scheduling` state with its pod in `Init:0/1`, even though the storage pools are online and Portworx reports no attachment errors.

This condition typically indicates a backlog of pending `VolumeAttachment` objects rather than a Portworx storage failure.

When multiple nodes recover, Kubernetes can generate many attach and detach requests, which the CSI external attacher processes serially.

To investigate the issue:

-
Check the `VolumeAttachment` objects associated with the affected VM's PVCs:

```

kubectl get volumeattachment

```

-
Check for pending `VolumeAttachment` objects with the following characteristics:

- `attached` is `false`.

- No attachment or detachment errors are reported.

- No finalizers are set.

- The object is not being deleted.

-
To assess the cluster-wide backlog, compare the total number of `VolumeAttachment` objects with the number that report `attached: false`.

-
Check the `csi-attacher` container logs for client-side throttling:

```

kubectl logs -n <portworx-namespace> deployment/px-csi-ext -c csi-attacher | grep "client-side throttling"

```

Messages similar to the following confirm that the Kubernetes API client is throttling the attacher:

```

"Waited before sending request" delay="143ms" reason="client-side throttling, not priority and fairness" verb="PATCH" URL=".../volumeattachments/<csi-...>/status"

```

If these messages don't appear, the pending `VolumeAttachment` objects have a different cause. Check the other conditions in this section before you change any settings.

VMs with multiple disks can experience longer delays because all their PVCs must be attached before they can start.

### Resolution​

If the logs show client-side throttling, increase the `--kube-api-qps` and `--kube-api-burst` values for the `csi-attacher` container by using a `ComponentK8sConfig` custom resource. For the procedure and recommended values, see Configure CSI attacher API rate limits.

After the CSI external attacher processes the pending attachment requests, the VMs can start.

## An upgrade remains in `UpdatePaused`​

During a rolling upgrade, the Portworx Operator waits for dynamic pool relocation and VM migration to complete before continuing with a node.

While these operations are in progress, the `StorageCluster` reports `UpdatePaused` and the number of nodes remaining in the upgrade.

If the upgrade does not progress:

-
Check the nodes that are still pending:

```

kubectl get storagenodes -A

```

-
Check active pool migrations:

```

pxctl service pool migrate list

```

-
Check active VM live migrations:

```

kubectl get vmim -A

```

A VM live migration that cannot complete can prevent the upgrade from progressing. For example, the migration can remain pending if no eligible destination node has enough resources to run the VM.

Resolve the underlying scheduling issue. The Operator continues the upgrade during the next reconciliation.

If another node crashes or reboots during the upgrade, the Operator excludes that offline node as a pool relocation destination to protect VM availability.

## Collect diagnostics​

If you contact Portworx Support about a Kube Datastore issue, collect the following information:

- Output of `pxctl cluster provision-status` to show pool distribution and dynamic pool status.

- Portworx diagnostics from the affected nodes. The diagnostics include the pool migration records and affinity group information. When remote fastpath is enabled, the diagnostics include NVMe-oF/TCP information, such as the output of `nvme list -v` and `nvme list-subsys -v`, in the `misc` folder.

For more information, see Collecting diagnostics.

In this topic:
