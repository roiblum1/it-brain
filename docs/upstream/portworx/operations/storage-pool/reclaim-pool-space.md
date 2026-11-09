# Reclaim Unused Storage with Pool Trim

Source: https://docs.portworx.com/portworx-enterprise/operations/storage-pool/reclaim-pool-space (Portworx Enterprise latest)

Reclaim Unused Storage with Pool Trim | Portworx Enterprise Documentation

Use Pool Trim to reclaim unused capacity on the thin-provisioned storage used by a PX-StoreV2 pool. Pool Trim is useful when deleted volumes or snapshots have released space within the Portworx pool, but the underlying storage continues to report that capacity as consumed. Reclaiming this space makes the unused capacity available to other consumers of the underlying storage.

PX-StoreV2 uses LVM thin pools for storage pools. When you delete a volume or snapshot, the thin pool makes the freed extents available for reuse within the Portworx pool but does not automatically notify the underlying storage that those extents are no longer in use. As a result, thin-provisioned backends such as FlashArray or a storage area network (SAN) can continue to account for this capacity as consumed.

Non-blocking device delete (NBDD) helps prevent unused capacity from accumulating on the underlying storage by issuing discard requests in the background before a deletion completes. However, capacity might remain allocated on the underlying storage in the following cases:

- Volumes or snapshots were deleted before you enabled NBDD.

- NBDD did not process a deletion, for example, because deletions were queued, Portworx restarted, or the storage pool became unavailable.

Over time, the capacity reported as consumed by the underlying storage can differ from the capacity actually used by the Portworx pool. Run a Pool Trim operation to reclaim this unused capacity. Pool Trim identifies unmapped extents in the thin pool and issues discard requests to release the corresponding capacity on the underlying storage.

## How pool trim works​

Portworx must deactivate the thin pool to safely access its metadata during a pool trim. Therefore, you must place the node in pool maintenance mode before starting the operation.

When you start a pool trim, Portworx:

- Deactivates the volume group that hosts the pool.

- Creates temporary recovery devices that map to the thin pool metadata and data devices.

- Runs the trim in the background and issues discard requests for unmapped extents.

- Removes the temporary recovery devices and reactivates the volume group after the trim completes.

If temporary recovery devices remain after a trim operation, the pool might fail to come online. To prevent this issue, Portworx automatically removes any remaining recovery devices during startup.

## Prerequisites​

Before you trim a storage pool, ensure that:

- The cluster uses PX-StoreV2.

- The cluster has Portworx Enterprise version 3.7.0 or later installed.

- You have shell access to the node that hosts the pool. Pool trim is a node-local operation, and you must run the commands on that node.

## Considerations​

Review the following considerations before starting a pool trim:

- Service interruption: Pool trim is a disruptive operation that requires pool maintenance mode. Schedule the operation during a maintenance window.

- Interrupted operations: A pool trim cannot resume from its previous progress. If Portworx restarts, the node reboots, or the operation fails or is stopped, start the trim again.

- Operation duration: The time required to complete a pool trim depends on pool fragmentation. Pools with more unmapped extents can take longer to trim.

- Reported pool capacity: Pool trim reclaims capacity on the backing storage only. It does not change the pool capacity reported by Portworx.

- Supported backends: Pool trim is supported only on thin-provisioned backends such as FlashArray or a storage area network (SAN).

## Trim a storage pool​

note

Before starting a pool trim, ensure that no volume devices are attached to or mounted on the node.

To reclaim unused capacity on the storage backend:

-
Open a shell session on the Portworx node that hosts the pool.

-
Identify the ID of the pool:

```

pxctl service pool show

```

-
Enter pool maintenance mode:

```

pxctl service pool maintenance --enter

```

```

This is a disruptive operation, PX will restart in maintenance mode.

Are you sure you want to proceed ? (Y/N):

```

Enter `Y` when prompted.

-
Verify that the node is in pool maintenance mode:

```

pxctl status

```

```

Status: PX storage in pool maintenance

```

-
Start the pool trim:

```

pxctl service pool trim start <pool-ID>

```

Replace `<pool-id>` with the ID of the pool that you want to trim.

To trim every pool on the node, run:

```

pxctl service pool trim start -a

```

-
Monitor the operation:

```

pxctl service pool trim status

```

Run the command periodically until the operation completes. If the trim fails, the status reports the failure.

-
After the trim completes, exit pool maintenance mode:

```

pxctl service pool maintenance --exit

```

## Stop a pool trim​

To stop a pool trim that is in progress, run the following command on the node where the operation is running:

```

pxctl service pool trim stop

```

A stopped pool trim cannot resume. To reclaim any remaining unused capacity, start a new pool trim from the beginning.

## Related topics​

- pxctl service

- Non-Blocking Device Delete

- Maintain volumes using Filesystem Trim

- Manage your Storage Pool Capacity

- Portworx Datastores

In this topic:
