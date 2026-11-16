# Manage your Storage Pool Capacity

Source: https://docs.portworx.com/portworx-enterprise/operations/storage-pool/manage-storagepool (Portworx Enterprise latest)

Manage your Storage Pool Capacity | Portworx Enterprise Documentation

As your cluster usage increases and the data on your storage pools grows, you may start to run out of capacity. Portworx periodically measures and saves storage pool space usage statistics, which can be queried via the appropriate metrics or the CLI tool.

This page provides information on how Portworx alerts you when a storage pool reaches its maximum capacity and the consequences of taking no action. It also explains how to recover your pool if it has reached its maximum capacity.

## Alerts and impacts when a pool reaches maximum capacity​

To manage your pools' storage capacity, Portworx triggers alerts and takes necessary actions to avoid disruption.

-
When a storage pool reaches 80% of its capacity, Portworx triggers an alert that the storage pool has high space usage.

-
When a storage pool reaches either 90% of its capacity or the total pool size minus 100 GiB (whichever threshold is higher), Portworx takes the following actions:

- Sets the pool as full and the node as `StorageDown`.

- Rejects all active IOs on the pool with the `ENOSPC` error.

- Sets mountpoints as read-only, and write operations will not be allowed.

To avoid disruption, you must expand your storage pool capacity by adding drives or increasing disk size. For more details, refer to the Expand your storage pool size section.

## Implications of a full pool​

If, for some reason, you could not expand your storage pool, it can lead to resource allocation issues. The following table explains the implications of a full pool in different scenarios:

Volume typeNode healthImplications

repl 1All nodes are marked full

- Read operations are allowed on the device.

- The existing mounts will continue to be accessible

- Portworx rejects new mount requests

- Portworx block devices can be manually mounted with the correct options
.

repl 2 or 3All nodes are marked full

- The volume will be out of a quorum

- No read operations will be allowed on the device.

-  Portworx rejects new mount requests.

.

repl 2 or 3Some nodes are marked fullRead operations are allowed as long as the volume is in clean state.

If all the nodes with volume replication are marked as full, the volume will become unavailable, resulting in no read or write operations. You need to revive your storage pool for further operations.

## Revive your storage pool​

You can restore a pool by deleting data or volume, or replication volume. Choose one of the following methods to restore your storage pool.

-
Update volume replicas

- Volume with 1 replica: Increase the replicas by 1 in another healthy node and then remove the replica from the full node.

- Volume with 2 or 3 replicas: Remove 1 replica from the full node then increase in a healthy node.

Refer to Update a volume's replication factor to perform operation based on your volume configurations.

-
Delete data or volume

```

pxctl volume delete <vol-name>

```

-
Cordon affected node to increase free space

Use `kubectl` or `oc` depending on the platform you're on to cordon the affected nodes. Then, temporarily increase the free space threshold value and bring the pools online:

- Kubernetes

- OpenShift

```

pxctl cluster options update --free-space-threshold-gb <threshold-value>

```

```

pxctl cluster options update --free-space-threshold-gb <threshold-value>

```

## Move Volumes using Pool Drain​

Use the Pool Drain operation to evacuate all volumes from a set of storage pools or nodes to other pools or nodes in your Portworx cluster. This feature can be used to safely clear out all volume replicas on a node, prior to performing any disruptive operations on it.

The pool drain operation automates the movement of volume replicas to other eligible pools in the cluster while preventing data loss and honoring defined volume placement strategies. Creating new volumes on the pools being drained is not allowed; however, writes to volumes being moved continue uninterrupted.

## When to use Pool Drain?​

Use pool drain before performing disruptive operations on a pool or node, such as decommissioning a node. This is an enhancement over the current workflow of having to manually increase the replication factor for each volume temporarily, and then removing the volume replicas on the node to be decommissioned.

## How to use Pool Drain?​

-
Submit a pool drain Job

Use the below command to cordon the pool and begin the drain operation.

```

pxctl service pool drain submit --source-uuids <pool-ID1>,<pool-ID-2>

```

::: note Only one active pool drain request can be submitted at a time. To submit a new request, the current job must be either `DONE` or `CANCELLED`. :::

```

pxctl sv pool drain submit --source-uuids 0fxxxx7e-03ee-4ab4-ae6e-524838exxxx5

```

```

Pool drain request: xxxx08682720967179 submitted successfully.

For latest status: pxctl service pool drain status --job-id xxxx08682720967179

```

Specify multiple source pools and/or define target pools as needed. To move all volumes from a node, provide the source node and the target node in a similar manner.

```

pxctl service pool drain submit --source-uuids <node-ID-1>,<node-ID-2> --target-uuids <node-ID-3>,<node-ID-4>

```

If no targets are specified, Portworx Enterprise will automatically select an appropriate node or pool for moving the volume.

-
Monitor the status of a pool drain job

You can monitor the progress of an ongoing pool drain job as follows

```

pxctl sv pool drain status --job-id <job-id>

```

```

pxctl sv pool drain status --job-id xxxx08682720967179

```

```

Rebalance summary:

Job ID             : xxxx08682720967179

Job State          : DONE

Last updated       : Thu, 29 May 2025 22:22:47 UTC

Total running time : 3 minutes and 33 seconds

Job summary

    - Provisioned space balanced : 40 GiB done, 0 B pending

    - Volume replicas balanced   : 2 done, 0 pending

Rebalance actions:

Replica add action:

    Volume             : XXXX0581640481XXXX

    Pool               : be1bXXXX-f59a-XXXX-b147-4c0c5d1933dc

    Node               : 8d12XXXX-87e8-48c0-XXXX-a59759a9e533

    Replication set ID : 0

    Start              : Thu, 29 May 2025 22:19:13 UTC

    End                : Thu, 29 May 2025 22:19:35 UTC

    State              : DONE

    Work summary

        - Provisioned space balanced : 20 GiB done, 0 B pending

Replica remove action:

    Volume             : 892905816404812476

    Pool               : 0fxxxx7e-03ee-4ab4-ae6e-524838exxxx5

    Node               : a4aaXXXX-dc7e-XXXX-8b8a-8c244bfb423b

    Replication set ID : 0

    Start              : Thu, 29 May 2025 22:19:35 UTC

    End                : Thu, 29 May 2025 22:19:36 UTC

    State              : DONE

    Work summary

        - Provisioned space balanced : 20 GiB done, 0 B pending

```

This shows the list of volumes currently being acted on, their operation status, and any errors encountered during the move. Once all volumes have been moved from the sources, the status of the pool drain job is updated to `DONE`.

-
Pause, resume or cancel a pool drain job

You can pause an active pool drain job, halting any further processing of volumes, using the command:

```

pxctl sv pool drain pause --job-id <job-id>

```

note

Previously submitted ha-increase or ha-reduce operations may still progress even after the job is paused.

To resume a paused pool drain job, run:

```

pxctl sv pool drain resume --job-id <job-id>

```

To cancel an active pool drain job, use the following command:

```

pxctl sv pool drain cancel --job-id <job-id>

```

important

- You cannot resume a canceled pool drain job.

- Canceling an active pool drain job can leave some volumes with incorrect high-availability (HA) levels.

- Portworx automatically cancels a pool drain job if it cannot generate new actions for 30 minutes. For example, this can happen when the target node already has a replica of the volume being moved. Portworx cancels the job and reports an error indicating the cause.

- Portworx also cancels a pool drain job if it exceeds the maximum job duration, which is 24 hours by default.

- If a node hosting `repl=1` volumes enters the `Offline`, `StorageDown`, or `Maintenance` state while a volume is being moved, the pool drain operation cannot continue. If the node remains in this state until the maximum job duration is reached, Portworx cancels the job.

-
Clear Pool drain status

Provisioning volumes on pools that are being drained is not allowed. Once Portworx successfully moves all volume replicas from a storage pool, it updates the pool status to `drained`.

```

pxctl sv pool show

```

```

PX drive configuration:

Pool ID: 0

    UUID:  0fxxxx7e-03ee-4ab4-ae6e-524838exxxx5

    IO Priority:  LOW

    Labels:  iopriority=LOW,medium=STORAGE_MEDIUM_MAGNETIC

    Size: 1000 GiB

    Status: Drained

    Has metadata:  Yes

    Balanced:  Yes

    Drives:

    1: /dev/sdc, Total size 1000 GiB, Online

    Cache Drives:

    No Cache drives found in this pool

```

To allow for provisioning volumes on the storage pool again, clear the status of a pool using:

```

pxctl sv pool drain clear --uuid <pool-ID>

```

note

`pxctl sv pool drain clear` command only works with pool IDs. Pools being cleared must be present on the node where this command is being run. To clear the drain status for multiple pools, run this command for each pool.

### Troubleshooting Pool Drain operations​

-
As a first step, run `pxctl sv pool drain status --job-id <job-id>`. The output shows the list of volumes being acted on, their operation status, and any errors encountered while the job is running.

For example:

```

  pxctl service pool drain status --job-id 1062367299915123456

```

```

Pool drain summary:

Job ID             : 1062367299915123456

Job State          : RUNNING

Last updated       : Fri, 29 Aug 2025 06:43:47 UTC

Total running time : 0 seconds

Pool drain errors encountered during the job run:

Note: These errors might require manual fixes.

Header: alert id - alert timestamp - alert message

			- 136751234566681012 - poolDrain: failed to drain volume (136751234566681012) from pool (123f6662-6256-123c-afaa-aadcc7xxbd53) with err could not find additional node: 2 out of 6 pools could not be selected because they did not satisfy the following requirement: pool and its node must be online (and not offline or full). 4 out of 6 pools could not be selected because they did not satisfy the following requirement: provisioning is disabled on pools that have either been drained or are currently being drained.

```

-
Ensure source pools or nodes are online and healthy before starting.

## Pool Drain Command line reference​

ActionCommand Example

Submit job`pxctl service pool drain submit --source-uuids <pool-ID1>` If you define target pool: `pxctl service pool drain submit --source-uuids <pool-ID1>,<pool-ID2> --target-uuids <pool-ID3>,<pool-ID4>`

List jobs`pxctl service pool drain list`

Check job status`pxctl service pool drain status --job-id <job-id>`

Pause job`pxctl service pool drain pause --job-id <job-id>`

Resume job`pxctl service pool drain resume --job-id <job-id>`

Cancel job`pxctl service pool drain cancel --job-id <job-id>`

Clear pool status`pxctl service pool drain clear --uuid <pool-ID>`

## Recover an offline storage pool​

A storage pool can transition to an offline state due to various reasons such as device failure, device detachment, or other underlying issues. When a pool is offline, Portworx may enter a storage down state.

After resolving the root cause of the issue and performing the necessary corrective actions, the storage pool can be recovered by running a node maintenance cycle.

```

pxctl service maintenance --cycle

```

The above command enters and immediately exits node maintenance mode, which clears storage-related errors and brings the storage pool back online with Portworx to Operational state.

To automatically bring a node back online while keeping the offline pool cordoned, see Recover nodes automatically with Auto Cordon.

## What to do next​

-
Expand your storage pool size

-
Expanding your Storage Pool with Autopilot

### Related topics​

- Considerations for PX-StoreV2 pools

In this topic:
