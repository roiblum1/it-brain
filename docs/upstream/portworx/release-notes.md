# Portworx Enterprise Release Notes

Source: https://docs.portworx.com/portworx-enterprise/release-notes (Portworx Enterprise latest)

Portworx Enterprise Release Notes | Portworx Enterprise Documentation

## 3.7.2​

November 12, 2026

To install or upgrade Portworx Enterprise to version 3.7.2, ensure that your cluster meets all system requirements and is running Operator 26.5.0 or later, Stork 26.5.0 or later, and one of the supported kernels.

### New Features​

-
Kube Datastore dynamic pools (General Availability)
 Kube Datastore (KDS) dynamic pools are now generally available. Dynamic pools let you run eligible workloads that use replication factor 1 (`repl=1`) on FlashArray storage. Portworx can move a pool between nodes without copying data. Because volumes rely on FlashArray for redundancy and data reduction, Portworx doesn't replicate them across nodes. This reduces storage overhead and network traffic between nodes. For more information, see Kube Datastore for Portworx Enterprise 3.7.2.

-
Higher scale limits
 Each node supports up to 12 dynamic pools (recommended) and up to 16 dynamic pools (hard limit). Each pool supports up to 150 volumes, or 450 volumes including snapshots. More pools per node give Portworx more options to distribute pools across the remaining nodes during node maintenance or after a node failure. For more information, see Scale Limits for KDS Dynamic Pools.

-
Compute-aware placement and hyperconvergence
 When you use a `WaitForFirstConsumer` StorageClass, Portworx uses the node where Kubernetes schedules the VM or pod as a placement hint. Portworx places the volumes on that node when capacity and placement rules allow. After pool placement changes, Portworx can request that Stork live migrate VMs to the nodes that host their storage. This reduces network traffic between nodes. For more information, see Configure and Manage KubeVirt VM Hyperconvergence.

-
Pool relocation during maintenance and failover
 A dynamic pool moves as a unit to a healthy node without rebuilding data across nodes. After you upgrade to Portworx Enterprise 3.7.2, Portworx relocates eligible pools from a node before the node restarts during later Portworx Enterprise or OpenShift upgrades. For more information, see Pool Placement and Rebalance.

-
Fastpath support on dynamic pools
 Dynamic pools support local and remote PX-Fast volumes without preventing pool failover. Portworx reconfigures fastpath when a pool moves between nodes. To use fastpath, all nodes in the cluster must run PX fuse kernel driver version 3.7.2 or later. For more information, see Fastpath behavior during dynamic pool failover.

-
Remote fastpath for PX-Fast volumes
 Portworx Enterprise now supports remote fastpath for volumes with replication factor 1 (`repl=1`) that are attached to a node other than the node hosting the volume replica. In disaggregated environments, remote fastpath allows the application node to access the replica over NVMe over Fabrics using TCP (NVMe-oF/TCP), bypassing the standard Portworx I/O path to reduce I/O latency. For more information, see Create PX-Fast PVCs.

-
FlashArray/FlashBlade (FA/FB) driver enhancements
 Portworx Enterprise now supports the following FA/FB driver capabilities:

- ActiveCluster with FlashArray realms: Supports FlashArray ActiveCluster with realms over iSCSI and Fibre Channel (FC).

- Per-PVC quota for FlashArray File Services volumes: Sets the enforced directory quota based on the capacity requested in the PersistentVolumeClaim (PVC), instead of using the quota policy specified in the `StorageClass` for all volumes.

- FlashBlade snapshot restore: Supports restoring a FlashBlade Direct Access (FBDA) snapshot to a separate volume.

- SUSE Virtualization (Harvester) 1.8.0: Supports deployments with the FA/FB driver over iSCSI and NVMe.

For more information, see FlashArray/FlashBlade Driver.

### Improvements​

Improvement NumberImprovement DescriptionComponent

PWX-56296Portworx Enterprise now provides a Grafana dashboard that shows per-disk I/O performance for the backing devices of Portworx storage pools. The Source Disks Performance dashboard reports read and write latency, IOPS, and throughput for each disk on each node, and you can filter by cluster, instance, and device. Use the dashboard to find slow or saturated disks and to determine whether a performance problem comes from the backing storage or from elsewhere in the stack.
For more information, see Monitor a Portworx cluster and Configure Portworx Monitoring on Kubernetes.Monitoring

### Fixes​

Issue NumberDescriptionSeverity

PWX-48460Issue: In RKE2 environments, restarting the containerd service could cause Portworx to continuously log `containerd.sock: connection refused` errors. Portworx could not reconnect to the recreated containerd socket without restarting the Portworx service or pod.
User Impact: Affected nodes could generate excessive connection error logs even after containerd recovered, making troubleshooting difficult and requiring a Portworx restart to stop the repeated errors.
Resolution: Portworx Enterprise now uses a directory mount instead of a socket-file mount for containerd in RKE2 environments. This allows Portworx to reconnect automatically after containerd restarts, preventing continuous connection errors without requiring a Portworx restart. This fix requires Operator 26.5.0 or later.
Components: Operator
Affected Versions: 3.7.1 or earlierCritical

PWX-55273Issue: On raw block volumes with write-zero enabled, discard operations could leave some blocks unchanged when the underlying LVM thin-pool chunk size was not a power of two. As a result, reads from discarded regions could return previously written data instead of zeros.
User Impact: Applications that expected zero-filled data after write-zero or discard operations could read nonzero data, potentially affecting data integrity.
Resolution: Portworx Enterprise now uses power-of-two LVM thin-pool chunk sizes when creating storage pools, ensuring that discard granularity aligns with block-layer requirements. This allows write-zero and discard operations to return zero-filled data correctly from the affected regions.
Components: Drive & Pool Management
Affected Versions: 3.7.1 or earlierCritical

PWX-56345Issue: On KDS clusters with a large number of volumes, a controlled pool failover initiated through the CLI can take significantly longer to complete. The delay increases with the number of volumes in the affected pool because pool deactivation and activation operations, including device cleanup and LVM activation, require additional processing for each volume.
User Impact: Pool failover operations could take longer than expected, delaying pool availability on destination nodes.
Resolution: Portworx Enterprise now uses an updated udev rule that prevents unnecessary nfsrahead operations on non-NFS Portworx devices. This reduces device activation overhead and improves pool failover performance in large clusters.
Components: Control Plane
Affected Versions: 3.7.1 or earlierCritical

PWX-57452Issue: During KDS pool failover on PX-StoreV2 clusters, pool activation can occasionally take significantly longer than expected. The delay occurs primarily during LVM activation on the target node. In some cases, LVM operations such as `vgchange -ay` can spend tens of seconds waiting for thin-pool checks or device-mapper operations to complete, increasing the overall pool failover time.
User Impact: KDS pool failover can take longer than expected, delaying pool availability on the target node. The failover eventually completes successfully, but workloads that depend on the affected pool might experience a longer recovery interval.
Resolution: Portworx Enterprise now skips block-mapping checks during LVM activation for controlled pool failovers while continuing to validate the thin-pool superblock. This optimization, along with improvements to udev processing, reduces pool activation latency and improves failover performance.
Components: Control Plane
Affected Versions: 3.7.1 or earlierCritical

PWX-58857Issue: When Portworx Enterprise was installed or started on a node configured with a custom core dump handler, it could overwrite the existing `kernel.core_pattern` setting with its default core dump location. This prevented third-party core dump handlers, such as the IBM core-dump-handler, from functioning as configured.
User Impact: Custom core dump handlers could fail to collect or upload core dumps to their configured destinations, affecting crash diagnostics and troubleshooting.
Resolution: Portworx Enterprise now supports the `PX_PRESERVE_CORE_PATTERN` environment variable to preserve custom kernel core dump configurations. Setting this variable to true prevents Portworx from overwriting the existing `kernel.core_pattern` setting during startup, allowing third-party core dump handlers to operate as configured.
Components: Control Plane
Affected Versions: 3.7.1 or earlierCritical

PWX-60649Issue: When Stork restarted or changed leaders during a VM backup, it could resubmit a CloudSnap creation request for an existing backup task. Portworx incorrectly returned an HTTP 503 error instead of HTTP 409, causing the duplicate request to be treated as a failure.
User Impact: VM backups could be incorrectly marked as failed or partially successful, even when the original CloudSnap tasks completed successfully. This could also trigger cleanup operations that deleted completed CloudSnap backups.
Resolution: Portworx Enterprise now returns HTTP 409 (Conflict) for duplicate CloudSnap creation requests, allowing clients to recognize existing backup tasks instead of treating them as service failures. HTTP 503 (Service Unavailable) remains applicable to service-unavailability errors.
Components: Cloudsnaps
Affected Versions: 3.7.1 or earlierCritical

PWX-60707Issue: During node wipe operations, including StoreV1-to-StoreV2 migration, Portworx could incorrectly identify host devices as Portworx-managed devices if their names contained pwx. This could result in unintended wiping of non-Portworx host volumes.
User Impact: Affected host volumes, such as those mounted at `/opt/pwx` and `/opt/pwx-cores`, could become corrupted and return I/O errors, preventing Portworx pods from starting. Recovery could require manually recreating the affected volumes.
Resolution: Portworx Enterprise now uses more precise device identification during node wipe operations to avoid wiping non-Portworx devices whose names contain pwx. The node wipe process also reports any remaining Portworx device-mapper devices, improving troubleshooting and protecting host volumes during node decommissioning and migration.
Components: Install & Uninstall
Affected Versions: 3.7.1 and earlierCritical

PWX-62814Issue: When Dynamic Pools were enabled, OpenShift storage live migration of KubeVirt VM disks between Kube Datastores could fail during volume provisioning. Conflicting volume placement rules prevented Portworx from selecting an eligible storage pool in the destination Kube Datastore.
User Impact: Users could not migrate KubeVirt VM disks between Kube Datastores through the OpenShift console when Dynamic Pools were enabled.
Resolution: Portworx Enterprise now considers only VM volumes within the same Kube Datastore when applying volume colocation rules. This prevents conflicting placement constraints and allows KubeVirt VM disks to be migrated successfully to the destination Kube Datastore.
Components: Volume Placement & Balancing
Affected Versions: 3.7.1 or earlierCritical

PWX-38497Issue: In VMware vSphere environments, Portworx could incorrectly include disk partitions when counting the drives attached to a virtual machine (VM), resulting in an inaccurate drive count.
User Impact: The reported drive count could be higher than the actual number of attached disks, potentially affecting operations that rely on accurate drive information.
Resolution: Portworx Enterprise now excludes disk partitions when counting drives attached to VMs in vSphere environments, ensuring that only actual disks are included in the drive count.
Components: Drive & Pool Management
Affected Versions: 3.7.1 or earlierMajor

PWX-52220Issue: After a Vault disaster recovery (DR) failover, some Portworx nodes could continue using existing connections to the previous Vault endpoint instead of connecting to the active Vault endpoint. This could cause secret retrieval to fail with a path disabled in replication DR secondary mode error.
User Impact: Affected Portworx nodes could fail to retrieve secrets required for encrypted volume operations, potentially preventing volumes from being attached or mounted until the Vault connection was refreshed.
Resolution: Portworx Enterprise now refreshes stale Vault connections after a DR failover, allowing affected nodes to connect to the active Vault endpoint and retrieve secrets without requiring a Portworx restart.
Components: Control Plane
Affected Versions: 3.7.1 or earlierMajor

PWX-53982Issue: In VMware vSphere environments, when provisioning a drive set with multiple VMDKs, a failure while creating one of the drives could cause Portworx to restart without cleaning up the drives created earlier in the same request.
User Impact: Orphaned VMDKs could remain in vCenter after a failed drive set provisioning operation, consuming storage capacity and requiring manual cleanup.
Resolution: Portworx Enterprise now automatically cleans up previously created VMDKs when a subsequent drive creation fails during drive set provisioning. This prevents orphaned drives and eliminates the need for manual cleanup after partial provisioning failures.
Components: Control Plane
Affected Versions: 3.7.1 or earlierMajor

PWX-55900Issue: During pool failover or rebalancing operations, Portworx could select Kubernetes nodes that were not ready or were experiencing resource pressure as destination nodes.
User Impact: Selecting unhealthy nodes as pool failover or rebalance destinations could cause operations to fail or be delayed, potentially affecting storage availability and cluster stability.
Resolution: Portworx Enterprise now considers Kubernetes node health when selecting destinations for pool failover and rebalancing operations. Nodes that are not ready, have an unknown or missing Ready condition, or are experiencing memory, disk, or PID pressure are excluded from destination selection. This improves the reliability of pool failover and rebalancing operations.
Components: Control Plane
Affected Versions: 3.7.1 or earlierMajor

PWX-57329Issue: In large clusters, when a zone recovered from an outage, multiple eligible nodes could simultaneously attempt to join the same available KVDB member slot during automatic rebalancing. This could cause repeated KVDB member additions and removals, resulting in unstable KVDB membership and repeated px-etcd restarts.
User Impact: During zone recovery, excessive KVDB membership changes could delay automatic rebalancing, disrupt KVDB availability, and affect cluster stability until the competing operations subsided.
Resolution: Portworx Enterprise now accounts for KVDB nodes undergoing provisioning when determining whether a member slot is available, preventing multiple nodes from competing for the same slot. It also improves bootstrap lock handling through adjusted lock timeouts, more reliable lock renewal, improved error handling, and Kubernetes API request timeouts. These changes reduce KVDB contention and improve cluster stability during zone recovery and automatic rebalancing.
Components: KVDB
Affected Versions: 3.7.1 or earlierMajor

PWX-57757Issue: During incremental CloudSnap backups with no changed data, Portworx could retain local staging snapshots after the backups completed successfully. These snapshots were not always cleaned up when they were no longer needed.
User Impact: Unnecessary local snapshots could accumulate and consume additional storage capacity, increasing snapshot management overhead.
Resolution: Portworx Enterprise now cleans up local staging snapshots after successful incremental CloudSnap backups with no changed data on non-FADA volumes. For FlashArray Direct Access (FADA) volumes, Portworx continues to retain the local snapshot required for subsequent incremental backups and cleans up the previous snapshot.
Components: Cloudsnaps
Affected Versions: 3.7.1 or earlierMajor

PWX-57585Issue: In environments using CSI-managed cloud drives, such as IBM Cloud VPC Block storage, Portworx Enterprise could incorrectly compare storage capacity values during pool expansion. This could cause the expansion operation to fail prematurely with a `PVC hasn't been updated` error, even when the requested capacity had been updated.
User Impact: Storage pool expansion operations could fail unexpectedly, preventing users from reliably increasing pool capacity.
Resolution: Portworx Enterprise now correctly compares storage capacity values during CSI-managed cloud drive resizing, preventing false resize failures and allowing storage pool expansion operations to complete successfully.
Components: Control Plane
Affected Versions: 3.7.1 or earlierMajor

PWX-58470Issue: During asynchronous disaster recovery (DR) operations, Portworx could incorrectly restrict snapshot searches to node 0 and pool 0 instead of searching across all eligible nodes and pools.
User Impact: During DR failover, particularly when the source cluster continued running DR operations, Portworx could fail to locate existing snapshots on other nodes or pools, potentially disrupting restore and failover operations.
Resolution: Portworx Enterprise now searches for snapshots across all eligible nodes and pools without applying an incorrect location constraint. This ensures that existing snapshots can be located correctly during asynchronous DR operations, supporting reliable failover and failback.
Components: Snaps and clones
Affected Versions: 3.7.1 or earlierMajor

PWX-58809Issue: When the initial and maximum Sharedv4 NFS thread counts were configured with the same value, Portworx could fail to apply the configured thread count to the NFS server. As a result, the server could continue running with the default number of threads, even after a restart.
User Impact: Affected Sharedv4 volumes could experience reduced NFS performance because the server was running with fewer threads than configured. This could also trigger repeated Sharedv4ServerHighLoadWarn alerts.
Resolution: Portworx Enterprise now correctly applies the configured Sharedv4 NFS thread count, even when the initial and maximum values are equal. It also updates the NFS server thread count when the configuration changes or the server restarts, ensuring that the active thread count reflects the configured value.
Components: Shared Volumes (NFS)
Affected Versions: 3.7.1 or earlierMajor

PWX-59548Issue: Portworx could repeatedly attempt to clean up stale sentinel mounts for deleted Sharedv4 volumes. When a volume no longer existed in KVDB, the cleanup process could leave its mount directory and cleanup task behind, resulting in repeated retries and excessive log messages.
User Impact: Repeated cleanup attempts could generate large volumes of logs, potentially filling the host's /var/log partition. Volume I/O was not affected.
Resolution: Portworx Enterprise now cleans up stale sentinel mounts and their directories when the corresponding Sharedv4 volumes have been deleted. It also removes these volumes from the cleanup queue, preventing unnecessary retries and excessive log generation.
Components: Shared Volumes (NFS)
Affected Versions: 3.7.1 or earlierMajor

PWX-60987Issue: When temporary KVDB loss support was disabled, Portworx could repeatedly skip KVDB compaction because nodes did not publish their KVDB watch indexes.
User Impact: KVDB data could accumulate until the storage quota was exhausted, potentially causing KVDB failures and cluster-wide storage unavailability.
Resolution: Portworx Enterprise now enables temporary KVDB loss support by default and removes the --disabled-temporary-kvdb-loss-support cluster option. Previously configured values are ignored and automatically cleaned up during an upgrade. This ensures that disabling temporary KVDB loss support no longer prevents KVDB compaction.
Components: KVDB
Affected Versions: 3.7.1 or earlierMajor

PWX-58248Issue: Under heavy write activity, delayed NFS mount status checks could cause Portworx to incorrectly mark healthy Sharedv4 volumes as read-only, even when the underlying storage remained operational.
User Impact: Affected volumes could be incorrectly reported as read-only, causing Kubernetes to evict pods using those volumes. This could result in unnecessary pod restarts and application disruption.
Resolution: Portworx Enterprise now correctly handles delayed or ongoing NFS mount status checks without incorrectly marking healthy Sharedv4 volumes as read-only. This prevents unnecessary pod evictions and restarts caused by temporary NFS status-check delays.
Components: Control Plane
Affected Versions: 3.7.1 or earlierMinor

### Known issues (Errata)​

Issue NumberDescriptionSeverity

PWX-63016
Issue: Asynchronous disaster recovery (DR) is not supported across clusters with different FlashArrays when the source volumes use `kube_datastore_affinity`. Portworx retains the source FlashArray ID in the volume's placement rules during restoration. Because the destination cluster does not have the same FlashArray, the volume restore fails.
 User Impact: VMs with KDS-affinity volumes cannot be restored to DR clusters that use different FlashArrays. If a VM is moved to a KDS after DR protection is configured, subsequent replication of its new disks can fail while older disks continue to replicate. A failover might then restore outdated data, resulting in data loss.
 Workaround: For asynchronous DR across clusters with different FlashArrays, do not configure `kube_datastore_affinity` in the StorageClass. Instead, use a custom volume placement strategy (VPS) that does not depend on system-defined labels.
 Components: Control Plane
 Affected Versions: 3.7.2
Critical

PWX-51182
Issue: During a Kubernetes platform upgrade, replacement nodes with the Portworx Storage Node (PSN) label initially join as storageless nodes and wait for 15 minutes. If the existing storage nodes are not drained and removed within this period, the replacement nodes can provision new cloud drives instead of reusing the existing drives.
 User Impact: Unintended cloud drive provisioning during platform upgrades can cause storage disruption, quorum loss, and potential data loss.
 Workaround: Before starting the platform upgrade, add the `portworx.io/suspend-storage-node-provisioning="true"` annotation to suspend new storage node provisioning. Remove the annotation after the upgrade completes.
 Components: Control Plane
 Affected Versions: 3.7.2
Major

PWX-59063
Issue: During a SharedV4 volume failover, an existing NFS sentinel mount can prevent Portworx from recreating the NFS export on the new server. If the volume later returns to the original server, Portworx might reuse the stale sentinel mount without restoring the NFS export. As a result, affected pods fail to start with a `permission denied` error.
 User Impact: Pods using the affected SharedV4 volume might fail to start after a failover. The volume data remains intact, but affected applications remain unavailable until the stale sentinel mount is removed and the NFS export is recreated.
 Workaround: Scale down all applications on the affected node that use the volume. After all bind mounts are released and Portworx removes the stale sentinel mount, scale the applications back up to trigger a fresh NFS mount and export.
 Components: Volume Management
 Affected Versions: 3.7.2
Major

PWX-60263
Issue: Cloning a FlashArray Direct Access (FADA) volume in a FlashArray pod using the `pxctl volume clone` command can fail with a `failed to get volume from backend` error. With FlashArray CSI integration enabled, this command is not supported for Pure volumes.
 User Impact: FADA volume cloning using the `pxctl volume clone` command fails, preventing applications from using the cloned volumes.
 Workaround: Enable FlashArray CSI integration and use Kubernetes CSI PVC cloning instead. Create a PVC with the `dataSource` field referencing the source PVC.
 Components: Snaps and clones
 Affected Versions: 3.7.2
Major

PWX-60884
Issue: During an uncontrolled pool failover, pool activation can remain stuck indefinitely if the target node has an unresponsive NFS mount. Portworx uses `xfs_admin` to update the pool's XFS metadata label. The older `xfsprogs` version checks all mounted file systems, including NFS mounts. If an NFS mount is unresponsive, the command can block indefinitely, preventing pool activation from completing.
 User Impact: The affected storage pool remains offline, and workloads using the pool may become unavailable. The failover plan remains in `activation_in_progress` without reporting an error.
 Workaround: On the affected target node, force-unmount and lazily detach each unresponsive NFS mount using `umount -f -l <mountpoint>`. If the unmount succeeds, restart the Portworx container. If the unmount fails or the node remains unresponsive, reboot the node.
 Components: Drive & Pool Management
 Affected Versions: 3.7.2
Major

PWX-60944
Issue: When a node hosting a Sharedv4 service volume reboots, Portworx might fail to restore the volume's NFS export. This typically occurs if the volume has a replication factor of 1, or when the failover does not move the Sharedv4 volume to another node before the server node comes back. For KubeVirt virtual machines that use hotplug disks, the existing NFS mounts can become stale, preventing the virt-launcher pods from terminating and the virtual machines from restarting.
 User Impact: Affected virtual machines remain in the `Stopped` state, and their virt-launcher pods cannot terminate because of stale NFS mounts. The virtual machines remain unavailable until the stale mounts are removed.
 Workaround: On each affected client node, run `umount -l` on the stale `hotplug-disks/name.img` mount associated with the terminating virt-launcher pod. After the mount is removed, the pod can terminate, allowing the virtual machine to restart.
 Components: Shared Volumes (NFS)
 Affected Versions: 3.7.2
Major

PWX-61738
Issue: When a CLI-initiated pool migration fails on a Kube Datastore (KDS) cluster, Portworx automatically retries the migration up to three times. If all retries fail, the pool remains offline, and Portworx does not attempt further recovery, even when eligible destination nodes become available.
 User Impact: Volumes on the affected pool remain unavailable, and KubeVirt virtual machines can experience I/O errors or remain paused until the pool is recovered.
 Workaround: Investigate the migration failure and ensure that an eligible destination node is available. Manually initiate another pool migration by using `pxctl service pool migrate`, and verify that the migration completes successfully.
 Components: Control Plane
 Affected Versions: 3.7.2
Major

PWX-61795
Issue: On a CSIv3-integrated FlashArray Direct Access (FADA) cluster, a CloudSnap backup can fail if its processing node reboots and Portworx attempts to resume the backup on a different node. The existing clone VolumeAttachment still references the original node, preventing the new node from attaching the clone. As a result, the backup enters the `Backup-Failed` state. Resuming the backup on the original node is not affected.
 User Impact: CloudSnap backups interrupted by a processing-node reboot can fail when recovery moves to another node. The failed backup can leave behind clone-related resources, including the FlashArray clone, PureVolume CR, clone PVC, and VolumeAttachment. The source volume and previously completed backups remain unaffected.
 Workaround: Delete the failed `VolumeSnapshot` and retry the backup, or wait for the next scheduled backup. Contact Pure Storage Support to clean up any orphaned clone-related resources.
 Components: Cloudsnaps
 Affected Versions: 3.7.2
Major

PWX-61848
Issue: When pool migration occurs during a large number of concurrent cloud snapshot operations, CloudSnap and CloudMigrate events can delay pool failover processing because they share a serial KVDB watch queue. As a result, the coordinator can take longer to process pool failover stage transitions, delaying the pool from coming back online even after storage recovery completes.
 User Impact: Pool migrations can exceed the expected 30-second completion threshold, extending storage unavailability and potentially disrupting applications. In the observed case, the pool remained offline for 43 seconds.
 Workaround: Avoid performing pool migrations while a large number of cloud snapshots are being created, particularly during disaster recovery (DR) operations.
 Components: Control Plane
 Affected Versions: 3.7.2
Major

PWX-61849
Issue: During pool rebalance, Portworx might select a target node that reports as online before its pool-migration service is fully initialized. As a result, the source pool can go offline while the target node is unable to process the migration. The migration resumes automatically after the target completes initialization, but pool recovery is delayed.
 User Impact: Affected storage pools can remain offline longer than the expected 30-second recovery target, temporarily disrupting workloads that depend on those pools. The migration resumes automatically, with no data loss or permanently stuck pools observed.
 Components: Control Plane
 Affected Versions: 3.7.2
Major

PWX-61915
Issue: If the number of configured cloud drives exceeds the `limit_pools_count` setting, Portworx can create orphaned drives that are not associated with any storage pool. During cleanup, Portworx detaches these drives but retains their entries as `In Use` in the cloud-drive ConfigMap. This leaves the drive set partially attached and prevents subsequent pool expansion.
 User Impact: Storage pools that run low on capacity can become offline, and attempts to expand them fail with the error `failed to get attached cloud drives for pool expansion: no drive sets attached to the node`. This can disrupt workloads that depend on the affected pools.
 Workaround: Ensure that `limit_pools_count` is configured to support the required number of storage pools. If the issue occurs:

- Identify the orphaned drive in the cloud-drive ConfigMap that has an empty `PoolID`.

- Change the orphaned drive's `State` from `In Use` to `To Delete`.

- Restart Portworx on the affected node.

- Retry the pool expansion.

Components: Drive & Pool Management
 Affected Versions: 3.7.2
Major

PWX-62334
Issue: When a node with multiple storage pools reboots or becomes unavailable, Portworx processes concurrent pool failovers that update the same cloud-drive ConfigMap. These updates are serialized through a shared lock, which can delay pool recovery. In a 15-pool failover scenario, one ConfigMap update took approximately 20 seconds, extending the affected pool's downtime to 69 seconds.
 User Impact: Storage pools can remain offline longer than expected during concurrent failovers, potentially disrupting workloads that depend on the affected pools.
 Workaround: For planned node reboots, migrate the storage pools by using the Portworx CLI before rebooting the node to avoid concurrent reboot-triggered pool failovers.
 Components: Control Plane
 Affected Versions: 3.7.2
Major

PWX-62378
Issue: When a storage pool reaches full capacity, a pool failover can cause Portworx storage processes to crash on the target node and can leave storage nodes in the `StorageDown` state. During pool recovery, Portworx may attempt to recreate missing logical volumes. If the thin pool is full, LVM cannot create these volumes, causing the storage process to abort. Repeated failures can leave storage nodes in the `StorageDown` state.
 User Impact: Pool failovers involving full storage pools can cause storage process crashes on additional nodes, potentially extending workload downtime and affecting cluster availability. The issue can occur during controlled pool migrations or uncontrolled failovers.
 Workaround: Monitor storage pool utilization and expand pools before they approach full capacity. Avoid initiating CLI-based pool migrations or rebalances involving full pools when possible. Ensure sufficient free capacity before performing planned upgrades or maintenance.
 Components: Storage
 Affected Versions: 3.7.2
Major

PWX-63024
Issue: During KubeVirt virtual machine (VM) storage migration, destination Portworx volumes can consume their full provisioned capacity even when the source volumes contain little data. This occurs because the migration writes zero-filled blocks to the destination, which allocates thin-provisioned storage space.
 User Impact: Migrated VM disks can consume significantly more storage capacity than their source volumes, potentially reducing available pool capacity.
 Workaround: After the migration completes, manually run `fstrim` on the destination volume to reclaim unused space.
 Components: Dmthin
 Affected Versions: 3.7.2
Major

PWX-63161
Issue: When restoring a CloudSnap backup from a Kube Datastore (KDS) cluster to a non-KDS cluster, Portworx retains the source volume's KDS affinity rule. Because the destination cluster does not have storage pools that satisfy this rule, the restore fails with a volume placement error.
 User Impact: CloudSnap backups of volumes with KDS affinity cannot be restored to non-KDS clusters. The restore operation fails because no eligible storage pools are found on the destination cluster.
 Components: CloudSnaps
 Affected Versions: 3.7.2
Major

PWX-63268
Issue: If Portworx remains stopped on a node hosting the only replica of an ext4 volume (repl-1) beyond the `pxd_timeout_secs` timeout (default: 600 seconds), pending I/O operations can fail and cause the ext4 journal to abort. If a pod remounts the volume before the filesystem error is recorded, the filesystem can become read-only. If the device remains in use, the automatic filesystem check fails, and Portworx marks the volume as `NEEDS_INSPECTION`, preventing automatic recovery.
 User Impact: Affected pods remain in the `CreateContainerError` state, and the volume becomes unavailable until the filesystem is repaired. Portworx raises the `FilesystemCheckFailed` alert. The `SharedV4FsckRemediation` alert might also appear for non-sharedv4 RWO volumes, but this alert is benign in version 3.7.2.
 Workaround:

- Scale down or delete all pods using the affected volume. Ensure that the filesystem is fully unmounted by confirming the `EXT4-fs (dm-N): unmounting filesystem <uuid>` message in the kernel logs.

- Run `pxctl volume check start --mode fix_all <volume>` to repair the filesystem.

- Run `pxctl volume check status <volume>` until the status shows `FS_CHECK_COMPLETED` and `FS_HEALTH_STATUS_HEALTHY`.

- Scale the application back up.

To prevent this issue, use volumes with a replication factor of 2 or higher, or ensure that Portworx downtime on a node hosting a repl-1 volume does not exceed `pxd_timeout_secs`.
 Components: Storage
 Affected Versions: 3.7.2
Major

PWX-63299
Issue: The Dynamic Pools descheduler might incorrectly include unused volumes when generating a pool affinity-group plan. This can occur when old PVCs remain after a cross-KDS storage migration or when a cloudsnap-restored volume retains the source VM's labels. As a result, the descheduler might group unrelated VMs together or report incorrect pool placement constraints.
 User Impact: The affinity-group plan might display warnings such as `cannot put them on one node` or `no move`, even when the VM's active disks are correctly placed. This can prevent the plan from recommending appropriate pool rebalancing. Existing VM data and running workloads are not affected.
 Workaround: After completing a cross-KDS storage migration, delete the old PVCs that are no longer used by the VM. For cloudsnap-restored volumes that retain the source VM's labels, update the stale VM ownership and affinity labels to reflect the correct volume association.
 Components: Control Plane
 Affected Versions: 3.7.2
Major

PWX-63336
Issue: During Kube Datastore (KDS) pool migration, Portworx runs a host-wide `udevadm settle` command while removing storage devices. If an unrelated NVMe-oF/TCP device has stalled udev events, the command might wait for the 30-second execution timeout, delaying pool deactivation.
 User Impact: Pool migrations can exceed the 30-second failover threshold, extending storage unavailability.
 Components: Control Plane
 Affected Versions: 3.7.2
Major

PWX-63611
Issue: On clusters using remote fastpath over NVMe/TCP, a node can be marked Down even though the host remains running. During snapshot or clone operations, Portworx demotes the volume's fastpath. Under heavy storage load, the target-side cleanup can time out, leaving an NVMe/TCP controller in the `live` state without active TCP connections. The resulting kernel log flood can block the Portworx logging pipeline, preventing Portworx services from responding to heartbeats.
 User Impact: Peer nodes can mark the affected node Down or Offline even though the host remains running. I/O to Portworx volumes on the affected node can hang, and SSH access might become unavailable. The local `pxctl status` command might still report `PX is operational`. The issue does not resolve automatically.
 Workaround:

- On the affected node, identify the stuck NVMe/TCP controller that remains in the `live` state without active TCP connections to the target.

- Reset the controller by running `echo 1 > /sys/class/nvme/<nvme-controller>/reset_controller`. If SSH is unavailable, use `kubectl exec` to run the command from the Portworx pod with the required permissions.

- Wait for the kernel log flood to stop and the Portworx logging pipeline to recover. The `px-storage` process might restart during recovery.

- On the fastpath target node, restart Portworx to clean up stale NVMe-oF subsystems left by the failed cleanup operation.

Components: Storage
 Affected Versions: 3.7.2
Major

PWX-58652
Issue: When a CloudSnap backup fails, Portworx might not delete the local snapshot created for the backup. The snapshot is removed only after a subsequent backup of the same source volume succeeds using the same backup credential. If the credential is changed or deleted, the snapshot is not automatically removed.
 User Impact: These orphaned snapshots consume storage capacity and metadata resources. They persist across Portworx restarts and can accumulate over time.
 Workaround: Run `pxctl volume inspect <snapshot-ID>` and check the `cloudsnapcreds` label to identify orphaned snapshots. Delete them manually by running `pxctl volume delete <snapshot-ID>`.
 Components: CloudSnaps
 Affected Versions: 3.7.2
Minor

PWX-62383
Issue: When deleting a sharedv4 service volume, stale NFSv4 client state might prevent Portworx from unmounting the volume's export path, resulting in a `device or resource busy` error. If an NFS server restart is skipped because of the 30-minute restart limit, subsequent deletion attempts do not automatically clear the stale state.
 User Impact: The affected volume remains attached, and its PersistentVolume (PV) stays in the `Released` state despite repeated deletion attempts. The volume continues to consume storage resources until the stale NFS client state is cleared.
 Workaround: Restart the NFS server or Portworx on the node where the affected volume is attached. This clears the stale NFS client state and allows subsequent volume deletion attempts to succeed.
 Components: Shared Volumes (NFS)
 Affected Versions: 3.7.2
Minor

## 3.7.1.1​

October 27, 2026

This version adds support for Flatcar Container Linux Stable up to kernel version 6.12.113-flatcar.

To install or upgrade Portworx Enterprise to version 3.7.1.1, ensure that your cluster meets all system requirements and is running Operator 26.4.0 or later, Stork 26.4.2 or later, and one of the supported kernels.

## 3.7.1​

September 30, 2026

To install or upgrade Portworx Enterprise to version 3.7.1, ensure that your cluster meets all system requirements and is running Operator 26.4.0 or later, Stork 26.4.2 or later, and one of the supported kernels.

### New Features​

- Cross-array snapshots for FlashArray volumes
 The FA/FB driver now supports cross-array snapshots for asynchronously replicating a FlashArray Direct Access (FADA) volume snapshot to another FlashArray in the same cluster. For more information, see FlashArray/FlashBlade Driver.

### Fixes​

Issue NumberDescriptionSeverity

PWX-48926Issue: During an Async DR restore, if Portworx restarted while an internal snapshot was transitioning between attachment states, the snapshot could remain externally attached after the restart.
User Impact: Internal snapshots could remain attached without an associated workload and might not be removed through the normal cleanup process, resulting in unnecessary storage consumption.
Resolution: Portworx Enterprise now preserves the internal attachment state of Async DR snapshots during restart recovery, preventing internal snapshots from being incorrectly left externally attached.
Components: Cloudsnaps
Affected Versions: 3.7.0 or earlierCritical

PWX-50070Issue: After a transient backend storage connectivity failure, a Portworx node could remain in the `StorageDown` state even after connectivity was restored. Recovering the node required a manual maintenance cycle.
User Impact: Storage on the affected node could remain unavailable after the underlying connectivity issue was resolved, requiring manual intervention to restore the node to a healthy storage state.
Resolution: Portworx Enterprise now makes a best-effort attempt to recover a node by automatically initiating a maintenance cycle when the node enters the `StorageDown` state because of a transient backend storage connectivity failure. If the condition is recoverable through a maintenance cycle, Portworx can recover the node and return its storage pools to a healthy state after connectivity is restored. Not all `StorageDown` conditions can be recovered through a maintenance cycle. If automatic recovery does not succeed, manual pool repair might be required. Contact Portworx Support for assistance.
Components: Storage
Affected Versions: 3.7.0 or earlierCritical

PWX-55832Issue: When a snapshot or clone had a lower replication factor than its parent volume, the VPS fixer job could repeatedly attempt to correct the replica placement even when the lower-replication volume's replicas were already correctly collocated with a subset of the parent volume's replicas.
User Impact: The VPS fixer job could run continuously and perform unnecessary replica add and remove operations, increasing storage activity and potentially affecting workloads on the involved nodes.
Resolution: Portworx Enterprise now accounts for differences in replication factors when evaluating replica placement. When the replicas of a lower-replication snapshot or clone are already correctly collocated with the parent volume's replicas, Portworx does not trigger unnecessary VPS fix operations.
Components: Drive & Pool Management
Affected Versions: 3.7.0 or earlierCritical

PWX-57207Issue: When a Sharedv4 export path could not be unmounted because it was still in use, Portworx did not provide sufficient diagnostic information to identify the process holding the path open.
User Impact: A Sharedv4 volume could remain attached after its clients were removed, and identifying the process preventing the server-side unmount required additional troubleshooting.
Resolution: Portworx Enterprise now identifies and logs the process and container holding a Sharedv4 export path open when the unmount fails. Portworx also raises a SharedV4ExportUnmountFailure alert to notify administrators of the failed unmount and provide better diagnostic visibility.
Components: Shared Volumes (NFS)
Affected Versions: 3.7.0 or earlierCritical

PWX-60144Issue: Clone and restore operations could fail when the source and destination StorageClasses had different parameters because Portworx enforced StorageClass validation for volume and snapshot clone operations.
User Impact: Existing backup, restore, and KubeVirt workflows that clone or restore volumes across StorageClasses with different parameters could fail validation.
Resolution: Portworx Enterprise now skips `StorageClass` validation for snapshot-to-volume clones by default and raises a warning when it detects an infrastructure mismatch. When `disable-clone-sc-validation` is not set, this behavior matches the behavior of releases earlier than 3.7.0, so existing workflows that use different volume properties between the source snapshot and destination `StorageClass` continue to work without configuration changes. To change the validation behavior, use the `disable-clone-sc-validation` runtime option. For more information, see Configure `StorageClass` validation for clones.
Components: Control Plane
Affected Versions: 3.7.0 or earlierCritical

### Known issues (Errata)​

Issue NumberDescriptionSeverity

PWX-59402
Issue: On Anthos on VMware 1.35 and 1.36 clusters that use Ubuntu 24.04 node images, SharedV4 volumes can fail to mount on nodes other than the volume coordinator. The node image masks `nfs-server.service` and `rpcbind.socket` by default, preventing the NFS services required for remote SharedV4 mounts from starting.
 User Impact: Pods that use SharedV4 volumes can remain in the `ContainerCreating` state when they are scheduled on a node other than the volume coordinator. Mount failures can report errors such as `rpc.statd is not running`, `requested NFS version or transport protocol is not supported`, or `context deadline exceeded`.
 Workaround: On each node, unmask and start the required NFS and RPC services before installing Portworx:

```
sudo systemctl unmask nfs-server.service rpcbind.socket rpcbind.service
sudo systemctl start rpcbind.socket rpcbind.service nfs-server.service
```
 Verify that the `rpcbind.service`, `rpcbind.socket`, and `nfs-server.service` are enabled and running as required before using SharedV4 volumes.
 Components: Storage
 Affected Versions: 3.7.1
Major

## 3.7.0​

September 8, 2026

To install or upgrade Portworx Enterprise to version 3.7.0, ensure that your cluster meets all system requirements and is running Operator 26.3.2 or later, Stork 26.4.1 or later, and one of the supported kernels.

Upgrade advisory for CSI snapshot-based backup and clone workflows

If you use CSI snapshot-based backup, restore, or clone workflows, do not upgrade to Portworx Enterprise 3.7.0. Upgrade to 3.7.1 or later. If you already run 3.7.0, upgrade to 3.7.1 or later, or validate these workflows with Pure Storage Technical Support before enabling production backup schedules.

Portworx Enterprise 3.7.0 validates that the volume properties recorded in a snapshot are compatible with the destination `StorageClass` before creating a volume from that snapshot. If Portworx Enterprise detects an incompatible property, such as replication factor, `nodiscard`, backend type, Kube Datastore affinity, or volume mode, it rejects the clone and the destination PVC remains in the `Pending` state. Earlier releases allowed the clone despite the mismatch and applied the source volume properties to the cloned volume. For more information, see PWX-56067 in Fixes.

This behavior can affect workflows that create PVCs from CSI `VolumeSnapshot` resources, including:

- Backup and restore workflows that create temporary PVCs from CSI snapshots such as Rubrik, Cohesity, and Dell PowerProtect Data Manager (PPDM).

- KubeVirt workflows that use CDI with `cloneStrategy: snapshot`.

- Clone workflows on clusters where SkinnySnaps is enabled.

Portworx Enterprise 3.7.1 resolves this issue. Portworx skips `StorageClass` validation for snapshot-to-volume clones by default and raises a warning when it detects an infrastructure mismatch. To change the validation behavior, use the `disable-clone-sc-validation` runtime option. For more information, see PWX-60144 in Fixes and Configure `StorageClass` validation for clones.

### New Features​

-
Kube Datastore and dynamic pool enhancements (Directed Availability)
 Portworx Enterprise expands Kube Datastore (KDS) and dynamic pool capabilities to simplify volume placement and migration for KubeVirt workloads, improve dynamic pool failover, and support larger configurations.

-
KDS affinity for volume placement: Use the `kube_datastore_affinity` parameter in a `StorageClass` to place volumes on a specific KDS during provisioning and subsequent storage rebalancing. For more information, see Provision volumes with KDS-aware StorageClasses.

-
KDS-aware StorageClasses for KubeVirt VMs: The Portworx Operator automatically creates KDS-aware versions of the default KubeVirt StorageClasses for each KDS, simplifying VM disk placement through Kubernetes-native storage workflows. For more information, see Kube Datastore-aware StorageClasses.

-
KubeVirt VM disk migration between Kube Datastores: Move KubeVirt VM disks between Kube Datastores by selecting the KDS-aware `StorageClass` for the destination KDS, without recreating the VM. For more information, see Migrate KubeVirt VM disks to a different Kube Datastore.

-
Faster dynamic pool failover: Fast node-down detection reduces recovery time after unexpected node failures. When liveness and cluster-safety checks confirm that a node is unavailable, Portworx Enterprise typically initiates dynamic pool failover within 7 to 12 seconds, reducing workload disruption. For more information, see Fast node-down detection.

-
Increased validated scale for dynamic pools: Dynamic pools supports up to 5,000 volumes per cluster. A node with a single dynamic pool supports up to 256 volumes. Configurations with multiple dynamic pools supports up to four pools per node and 100 volumes per pool. For more information, see Limitations.

-
Enhanced FlashArray and FlashBlade capabilities with the FA/FB driver
 Portworx Enterprise now includes an FA/FB driver that provides enhanced storage capabilities for FlashArray Direct Access (FADA), FlashArray File Services, and FlashBlade Direct Access (FBDA) volumes. The FA/FB driver provides FlashArray File Services volumes, static provisioning of existing array storage, FlashBlade snapshots and snapshot policies, cross-array FlashArray snapshot replication, per-node transport selection, parallel volume attachment, GPUDirect Storage, and storage connectivity metrics. For more information, see FlashArray/FlashBlade Driver.

important

If you are upgrading an existing cluster to Portworx Enterprise version 3.7.0 or later, complete the Portworx Enterprise upgrade on all nodes before enabling the FA/FB driver. Verify that every node is running Portworx Enterprise 3.7.0 or later, and then enable the driver.

-
Support for Amazon EKS clusters with hybrid nodes
 Portworx Enterprise now supports Amazon EKS clusters with worker nodes running in on-premises environments. For more information, see Installation on an Amazon EKS Cluster with Hybrid Nodes.

-
Auto Cordon support for PX-StoreV2
 Portworx Enterprise now supports Auto Cordon for PX-StoreV2, helping restore a node and its healthy storage pools after a drive failure takes a pool offline. Auto Cordon moves eligible replicas from the offline pool, cordons the failed pool, and returns the node and its healthy pools online, limiting the impact of the failure. For more information, see Recover Storage Nodes with Auto Cordon.

-
Pool Trim for reclaiming unused storage
 Portworx Enterprise can now reclaim unused capacity from PX-StoreV2 pools on thin-provisioned storage, making freed capacity available for reuse on the storage backend. Pool Trim is particularly useful for reclaiming capacity from volumes and snapshots deleted before non-blocking device delete (NBDD) was enabled. For more information, see Reclaim Unused Storage with Pool Trim.

-
Non-disruptive pool resize
 Portworx Enterprise can now expand eligible PX-StoreV2 storage pools without entering pool maintenance mode or restarting Portworx, reducing application disruption during pool expansion. This behavior is enabled by default for eligible `resize-drive` operations, including Autopilot-triggered expansions. For more information, see Non-Disruptive Pool Resize.

-
SSL certificate verification for FlashArray and FlashBlade connections
 Portworx Enterprise can now verify the identity of FlashArray and FlashBlade management endpoints by validating their SSL certificates. This capability strengthens storage control-path security and helps meet enterprise security and compliance requirements. For more information, see Enable SSL Certificate Verification for FlashArray and FlashBlade.

-
Restrict Portworx services to configured network interfaces
 Portworx Enterprise can now restrict service listeners to configured management, data, and local loopback addresses instead of listening on all network interfaces. This capability reduces network exposure and supports stronger network segmentation. Enable it by setting `PX_DISABLE_WILDCARD_LISTENERS` to `"true"`.

-
FlashArray realm support for FADA volumes
 Portworx Enterprise can now provision FlashArray Direct Access (FADA) volumes in a specific FlashArray realm, providing realm-based placement for Kubernetes workloads. Specify the target realm by using the `pure_fa_realm` parameter in the `StorageClass`. Before provisioning volumes, ensure that the required array-level hosts are shared with the target realm. For more information, see Provision volumes on a specific FlashArray realm.

-
CloudSnap health improvements
 Portworx Enterprise improves CloudSnap reliability and operational visibility, helping you monitor backup health and identify and troubleshoot protection issues more quickly.

### Early access features​

- Write Zeroes for RWX Block volumes
 Portworx Enterprise now supports Write Zeroes for raw block (RWX Block) volumes on new deployments. Write Zeroes avoids physically writing zeroed blocks to thin-provisioned storage, reducing unnecessary network I/O, compute resource consumption, and storage usage. This can improve KubeVirt VM image import and cloning performance, including VMware vSphere migrations with Forklift and CDI imports. For more information, see Write Zeroes for RWX Block Volumes.

### Improvements​

Improvement NumberImprovement DescriptionComponent

PWX-52363Portworx Enterprise improves support for KubeVirt VMs by using `px-shared-raw-block` for root disks and `fada-shared-raw-block` for the hosted Portworx cluster. This enhancement extends Portworx Enterprise support to hosted clusters running on KubeVirt VMs that use volumes provisioned from a management cluster running Portworx Enterprise. For more information, see How to deploy OpenShift hosted clusters with PortworxControl Plane

PWX-52576Portworx Enterprise supports RWX volumes on platforms that do not support NFS 4.0 by allowing the use of NFS 4.1 or NFS 4.2. Portworx first attempts to mount an RWX/SharedV4 volume by using NFS 4.0. If NFS 4.0 is unavailable, Portworx retries with NFS 4.1 and then NFS 4.2. Seamless NFS server failover with NFS 4.1 or NFS 4.2 is not supported in the same way as with NFS 4.0. Workloads restart if the NFS server fails. Existing NFS 4.0 environments continue to use NFS 4.0 and retain the existing seamless failover behavior. To enable RWX support on platforms that do not support NFS 4.0, use either of the following methods:

- Set the `PX_ENABLE_SHAREDV4_NFS_NEGOTIATION` environment variable to `true` in the StorageCluster.

- Run `pxctl cluster options update --enable-sharedv4-nfs-negotiation true`. This method takes effect immediately and does not require a Portworx restart. To verify the setting, run `pxctl cluster options list`.

For more information, see NFS version fallback.Control Plane

PWX-53046Portworx Enterprise improves troubleshooting for storage I/O timeouts caused by an unresponsive replica node. Previously, timeout messages did not identify the replica node that failed to respond, making it difficult to determine the source of the issue.

Portworx Enterprise now raises a `ReplicaResponseTimeout` alert when a storage I/O request times out waiting for a replica response. The alert identifies the coordinator node, volume, and replica node that did not respond, helping you identify the affected node without analyzing core dumps.

To view the alert, run `pxctl alerts show --type node`. For more information, see Portworx Alerts.

The alert helps identify the unresponsive replica node but does not prevent node restarts or resolve the underlying storage backend issue.Monitoring

PWX-55682Portworx Enterprise now provides a Grafana dashboard for monitoring Non-Blocking Device Delete (NBDD) operations and space reclamation. The dashboard provides visibility into NBDD configuration and pool-level settings, completed, in-progress, and queued deletion operations, discard throughput and errors, reclaimed capacity, and discard and release durations. Use the dashboard to monitor space reclamation, identify deletion backlogs, and evaluate rate limit and concurrency settings.
For more information, see Configure Portworx Monitoring on Kubernetes and Non-Blocking Device Delete.Monitoring

### Fixes​

Issue NumberDescriptionSeverity

PWX-55091Issue: When a journal device was configured on a partition, a failure during initialization could cause Portworx to restart repeatedly because detaching the old journal drive set failed. The detach operation failed because the journal device holder was a partition rather than an MD device.
User Impact: Affected nodes could enter a Portworx restart loop and fail to initialize.
Resolution: Portworx Enterprise now removes the partition before detaching the journal drive set, preventing the restart loop.
Components: Drive & Pool Management
Affected Versions: 3.6.2 or earlierCritical

PWX-55396Issue: Portworx did not detach Sharedv4 (NFS) volumes when they were deleted.
User Impact: Sharedv4 volumes could remain attached to a node after deletion.
Resolution: Portworx Enterprise now detaches Sharedv4 (NFS) volumes when they are deleted.
Components: Shared Volumes (NFS)
Affected Versions: 3.6.2 or earlierCritical

PWX-56112Issue: Stale PXD devices could remain on nodes after the lazy detach of Sharedv4 volumes. If I/O was issued to these devices, they returned I/O errors, and tools such as Node Problem Detector that scan block devices could generate a large number of I/O errors.
User Impact: Stale PXD devices could cause repeated I/O errors and excessive logging on affected nodes.
Resolution: Portworx Enterprise now scans for and cleans up stale devices every 10 minutes. You can also override the list of encapsulated devices by using the `PX_ENCAPSULATED_DEVICES` environment variable, which accepts the values `all`, `nfs`, `encrypted`, or `none`.
Components: Shared Volumes (NFS)
Affected Versions: 3.5.1Critical

PWX-43544Issue: The Portworx Performance dashboard in Grafana displayed incorrect values in several panels, including NaN latency, volume latency reported in incorrect units, node identifiers shown as IP addresses, and a typo in the read-throughput query.
User Impact: The dashboard could display inaccurate performance metrics, making it harder to monitor cluster performance.
Resolution: Portworx Enterprise now reports accurate metrics in the affected Performance dashboard panels and queries.
Components: Monitoring
Affected Versions: 3.6.2 or earlierMajor

PWX-45402Issue: The `px_volume_replica_write` and `px_volume_replica_read` metrics reported incorrect values.
User Impact: Per-replica read and write metrics could be inaccurate, affecting volume performance monitoring.
Resolution: Portworx Enterprise now reports the `px_volume_replica_write` and `px_volume_replica_read` metrics correctly.
Components: Monitoring
Affected Versions: 3.6.2 or earlierMajor

PWX-47726Issue: When a FlashArray host was initially created with only a subset of its World Wide Names (WWNs) and additional WWNs became available later, Portworx did not add the new WWNs to the existing host registration.
User Impact: Delayed Fibre Channel path recovery could cause duplicate WWN failures during later attach or boot attempts and could trigger a degraded multipath alert.
Resolution: Portworx Enterprise now updates the existing FlashArray host registration to include newly available WWNs, avoiding duplicate WWN failures and removing the need for the degraded multipath alert in this scenario.
Components: Control Plane
Affected Versions: 3.6.2 or earlierMajor

PWX-49017Issue: When the number of pending deletes in the non-blocking device delete (NBDD) queue exceeded the configured limit, Portworx disabled NBDD on the affected pool but continued to delete the queued volumes and snapshots without pacing them.
User Impact: Multiple volumes could be deleted at the same time after NBDD was disabled, which could increase filesystem latency on the affected pool and cause request abort timeouts.
Resolution: Portworx Enterprise now pairs NBDD with RelaxedReclaim to pace deletes:

- When the NBDD queue exceeds 256 pending deletes (`max_queue`, which you can change by using the CLI), Portworx disables NBDD on the pool and enables RelaxedReclaim, which deletes one volume or snapshot per minute.

- When the NBDD queue drops below 128 pending deletes (default) and the RelaxedReclaim queue drops below 8 pending deletes (default), Portworx re-enables NBDD on the pool and disables RelaxedReclaim.

Portworx honors the RelaxedReclaim setting that you configured. When Portworx disables RelaxedReclaim, it restores your configured value. For more information, see Non-Blocking Device Delete and RelaxedReclaim.
Components: Storage
Affected Versions: 3.6.2 or earlierMajor

PWX-50021Issue: When a CloudSnap operation was stopped after a Portworx restart, or when a queued CloudSnap operation was stopped, the associated local snapshot was not cleaned up.
User Impact: Unused local snapshots could accumulate and consume storage capacity.
Resolution: Portworx Enterprise now cleans up associated local snapshots when CloudSnap operations are stopped or fail.
Components: CloudSnap
Affected Versions: 3.6.2 or earlierMajor

PWX-50507Issue: Before creating a snapshot or clone, Portworx issued an LVM delete operation for the target device without first checking whether the device existed. This could introduce unnecessary processing and delay snapshot or clone creation.
User Impact: Snapshot and clone operations could take longer to complete because of unnecessary LVM delete operations.
Resolution: Portworx Enterprise now checks whether the target device exists before attempting the LVM delete operation, avoiding unnecessary deletion attempts and improving snapshot and clone creation efficiency.
Components: Snaps and clones
Affected Versions: 3.6.2 or earlierMajor

PWX-50841Issue: Portworx repeatedly read node labels to determine whether the cluster was running in disaggregated mode, which was inefficient in large clusters.
User Impact: Frequent disaggregated-mode discovery could add load to the Kubernetes API server in large clusters.
Resolution: Portworx Enterprise now caches the disaggregated-mode information, reducing repeated node-label reads.
Components: Drive & Pool Management
Affected Versions: 3.6.2 or earlierMajor

PWX-53028Issue: Each time Portworx acquired a distributed volume lock, the lock-refresh logic granted a new etcd lease every few seconds without revoking the previous lease. As a result, detached leases remained in the KVDB until they expired.
User Impact: Unused etcd leases could accumulate and add load to the KVDB.
Resolution: Portworx Enterprise now refreshes the existing lease instead of granting a new lease on each refresh, preventing unnecessary etcd lease accumulation.
Components: KVDB
Affected Versions: 3.6.2 or earlierMajor

PWX-53464Issue: CloudSnap status monitoring could fail to capture the final backup status, causing a completed backup to remain indefinitely in the `Backup-Active` state.
User Impact: The affected backup continued to appear active even though the data upload had completed. Subsequent backups for the same source volume could remain queued and fail to start.
Resolution: Portworx Enterprise now detects when the final CloudSnap status is no longer available during backup monitoring, updates the affected backup status, cleans up associated resources, and processes queued backups so subsequent backup operations can proceed.
Components: CloudSnap
Affected Versions: 3.6.2 or earlierMajor

PWX-53714Issue: Portworx failed to install on nodes where array-level FlashArray hosts were shared into a realm in FlashArray Secure Multi-Tenancy (SMT) configurations.
User Impact: Installation could fail in FlashArray SMT configurations that use array-level shared hosts.
Resolution: Portworx Enterprise now discovers and uses array-level hosts alongside realm-scoped hosts during deployment in FlashArray SMT configurations.
Components: Control Plane
Affected Versions: 3.6.2 or earlierMajor

PWX-53746Issue: An incorrect counter in the messenger component could cause a node to be repeatedly marked as down.
User Impact: Affected nodes could be repeatedly marked as down, disrupting cluster operations.
Resolution: Portworx Enterprise now tracks the counter correctly in the messenger component, preventing nodes from being repeatedly marked as down.
Components: Control Plane
Affected Versions: 3.6.2 or earlierMajor

PWX-54076Issue: A snapshot retry could trigger an assertion in the messenger component, causing Portworx to restart.
User Impact: Portworx could restart when a snapshot retry triggered the assertion.
Resolution: Portworx Enterprise now handles snapshot retries correctly, preventing the assertion in the messenger component.
Components: Snaps and clones
Affected Versions: 3.6.2 or earlierMajor

PWX-54293Issue: When a FlashArray REST API timeout caused a `VolumeDiff` operation to fail during a FADA CloudSnap backup, the backup could remain indefinitely in the `Backup-NotStarted` state.
User Impact: Affected CloudSnap backups did not complete or transition to a failed state, which could block subsequent backup operations and leave the associated local snapshot behind.
Resolution: Portworx Enterprise now marks the affected CloudSnap backup as failed when the `VolumeDiff` operation fails and cleans up the associated local snapshot. Subsequent backups can proceed normally after connectivity to the FlashArray is restored.
Components: Snaps and clones
Affected Versions: 3.6.2 or earlierMajor

PWX-55285Issue: When KVDB returned `too many requests` or `context deadline exceeded` errors, Portworx could immediately retry the failed operations. Repeated retries could generate additional load on an already busy KVDB.
User Impact: In large or heavily loaded clusters, repeated KVDB retries could increase etcd load and contribute to further request throttling or delays.
Resolution: Portworx Enterprise now applies a backoff before retrying KVDB operations after rate-limit or timeout errors. This reduces retry storms and helps prevent additional load on the KVDB during periods of high contention.
Components: KVDB
Affected Versions: 3.6.2 or earlierMajor

PWX-55680Issue: In large clusters, when a storage node was down, every storageless node determined whether the cluster was in disaggregated mode by reading all labels on all nodes.
User Impact: This behavior could add significant load to the Kubernetes API server during a storage-node outage.
Resolution: Portworx Enterprise now maintains an in-memory cache of the disaggregated-mode information, reducing Kubernetes API server load.
Components: Drive & Pool Management
Affected Versions: 3.6.2 or earlierMajor

PWX-56067Issue: When CDI used the `snapshot` clone strategy, Portworx did not validate whether the source and destination volumes had compatible volume properties. As a result, a PVC cloned through an intermediate snapshot could inherit properties from the source volume even when different properties were specified for the destination volume.
User Impact: A cloned PVC could be provisioned with properties inherited from the source volume instead of the properties specified for the destination volume, resulting in an incorrectly provisioned volume.
Resolution: Portworx Enterprise now validates volume compatibility for snapshot-to-volume clones in addition to volume-to-volume clones. The validation includes backend type, Kube Datastore affinity, replication factor, volume mode, I/O profile, format, shared volume settings, Sharedv4 settings, sticky flag, journal, compression, deduplication, discard behavior, fast path, encryption, near-sync replication, automatic file system trim, copy-on-write on demand, aggregation level, scale, snapshot interval, snapshot schedule, and volume labels.
If Portworx detects an incompatible property between the source and destination volumes, it rejects the clone operation with a validation error instead of provisioning the destination volume with properties inherited from the source.
Components: Control Plane
Affected Versions: 3.6.2 or earlierMajor

PWX-56070Issue: When a Portworx node attempted to acquire a lock that was already held by another node, repeated lock acquisition attempts could create unnecessary etcd leases while waiting for the existing lock to be released.
User Impact: Frequent lock contention could generate unnecessary KVDB activity and increase load on etcd.
Resolution: Portworx Enterprise now checks whether an existing lock has been released before creating a new lease and retrying lock acquisition. This reduces unnecessary lease operations and lowers the load on the KVDB during lock contention.
Components: KVDB
Affected Versions: 3.6.2 or earlierMajor

PWX-56259Issue: Portworx could trigger an assertion when a volume attribute was set to `nodiscard` but the block device was still exported with discards enabled because the discard setting was not propagated correctly.
User Impact: The assertion could cause Portworx to restart on affected nodes.
Resolution: Portworx Enterprise now propagates the `discard` or `nodiscard` setting only on new volume attachments, preventing the assertion.
Components: Storage
Affected Versions: 3.6.2 or earlierMajor

PWX-56617, PWX-56728Issue: When uninstalling Portworx by using the `UninstallAndDelete` strategy in a FlashArray environment with iSCSI or Fibre Channel connectivity, the backend volumes were deleted successfully, but stale multipath maps and SCSI devices could remain on the host.
User Impact: Stale host-side storage entries could remain after Portworx was uninstalled, requiring manual cleanup or a node reboot.
Resolution: Portworx Enterprise now cleans up the associated multipath maps and SCSI devices from the host when the `UninstallAndDelete` strategy is used with iSCSI or Fibre Channel connectivity.
Components: Install & Uninstall
Affected Versions: 3.6.2Major

PWX-36048Issue: During an AKS upgrade, Azure could copy the `topology.portworx.io/zone` label from one node to another, so a buffer node could inherit a zone label that did not match its actual zone.
User Impact: Nodes could report an incorrect zone, which could affect volume provisioning and placement decisions.
Resolution: Portworx Enterprise now reconciles the `topology.portworx.io/zone` label on cloud providers so that nodes retain the correct zone label after an AKS upgrade.
Components: Drive & Pool Management
Affected Versions: 3.6.2 or earlierMinor

PWX-48871Issue: When the `px-pure-secret` used standard Kubernetes topology labels (`topology.kubernetes.io/zone`) instead of `topology.portworx.io/zone`, the FlashArray zone defaulted to `default`, causing a node-array zone mismatch.
User Impact: Volume provisioning could fail because of the node-array zone mismatch.
Resolution: Portworx Enterprise now migrates `topology.kubernetes.io/*` labels to `topology.portworx.io/*`, so FlashArray topology honors standard Kubernetes topology labels.
Components: Control Plane
Affected Versions: 3.6.2 or earlierMinor

PWX-49795Issue: During a CloudSnap restore, Portworx validated snapshots that were not relevant to the restore operation, which added unnecessary processing.
User Impact: CloudSnap restore operations could take longer than necessary in environments with many snapshots.
Resolution: Portworx Enterprise now validates only the snapshots that are relevant to the restore, improving restore efficiency.
Components: CloudSnap
Affected Versions: 3.6.2 or earlierMinor

PWX-53467Issue: After an OS or kernel upgrade, additional Fibre Channel (FC) HBA ports could become available on a node. If the node's WWNs were distributed across separate FlashArray host objects, Portworx could incorrectly detect duplicate WWNs and fail to start.
User Impact: Affected Portworx nodes could enter a restart loop after an OS or kernel upgrade, making storage on those nodes unavailable until the FlashArray host configuration was manually corrected.
Resolution: Portworx Enterprise now correctly identifies the Portworx data host when WWNs for the same node are distributed across multiple FlashArray host objects. Portworx can start using the available paths instead of failing because of duplicate WWNs. It also raises the `FCSplitHostDegradedMultipath` warning to indicate the degraded multipath configuration so that administrators can correct the FlashArray host configuration.
Components: Control Plane
Affected Versions: 3.6.2 or earlierMinor

### Known issues (Errata)​

Issue NumberDescriptionSeverity

PWX-52475
Issue: For KubeVirt virtual machines that use Shared Raw Block (RWX Block) volumes, Portworx cannot report filesystem usage because the filesystem is inside the guest VM, which Portworx cannot inspect.
 User Impact: Filesystem usage for Shared Raw Block volumes is not available through Portworx volume usage metrics.
 Workaround: Obtain filesystem usage for these volumes from the KubeVirt `kubevirt_vmi_filesystem_used_bytes` metric that KubeVirt exports.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-53654
Issue: On Dynamic Pools, pool failover can take longer when an RWO volume is attached to a remote node that becomes unavailable. Subsequent attach operations can be delayed while Portworx repeatedly attempts to contact the unavailable node, and pool locks can remain held during these attempts, delaying pool failover.
 User Impact: Pool failover for Dynamic Pools can take longer when affected RWO volumes are present. RWX volumes are not affected by this specific issue.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-54529
Issue: Telemetry is not supported on IPv6-only clusters. On dual-stack clusters, telemetry can also become unhealthy when `PX_PREFER_IPV6_NETWORK_IP` is set to `true`, because Portworx Enterprise selects an IPv6 management address that cannot reach the telemetry endpoint.
 User Impact: `pxctl status` reports telemetry as unhealthy, and Portworx Enterprise cannot send telemetry data to Pure1. Storage functionality is not affected.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-56345
Issue: On KDS clusters with a large number of volumes, a controlled pool failover initiated through the CLI can take significantly longer to complete. The delay increases with the number of volumes in the affected pool because pool deactivation and activation operations, including device cleanup and LVM activation, require additional processing for each volume.
 User Impact: CLI-initiated pool failovers can take up to two minutes to complete on large-scale clusters, delaying pool availability on the target node.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-56840
Issue: Pool resize operations can take longer on pools with multiple drives, particularly when the journal is configured on the data pool. The resize duration increases with the number of drives because Portworx performs multiple storage-device operations for each drive during the resize.
 User Impact: Applications can experience increased I/O latency while the pool resize is in progress. The resize operation completes successfully.
 Workaround: Where possible, configure fewer drives per pool. For FlashArray deployments, use the recommended configuration of one drive per pool.
 Components: Drive & Pool Management
 Affected Versions: 3.7.0
Minor

PWX-57002
Issue: On Portworx Enterprise clusters configured with multiple FlashArrays, a FADA volume can be created on more than one FlashArray if a volume creation request times out and Portworx retries the request on another backend. Subsequent operations on the affected volume fail because Portworx detects duplicate volumes with the same name.
 User Impact: PVC provisioning or volume attachment can fail with a `Duplicate volumes found` or `found on multiple backends` error, preventing affected pods from starting. The duplicate volume also continues to consume capacity on the additional FlashArray.
 Workaround: Manually delete the duplicate volume from the FlashArray that Portworx did not record for the PVC. Retain the volume on the FlashArray associated with the PVC.
 Components: FA/FB driver
 Affected Versions: 3.7.0
Major

PWX-57247
Issue: Under abnormal cluster conditions, such as high KVDB latency, a Sharedv4 service volume failover can be triggered. If the volume attaches to the new NFS server but the mount and export operation does not complete, existing client mounts can become stale. Pods that use the affected volume can then remain in the `CreateContainerError` state with a `stale NFS file handle` error.
 User Impact: Pods using the affected Sharedv4 service volume cannot start until the stale NFS mount is replaced.
 Workaround: After the cluster is stable, delete the affected pods so that Kubernetes recreates them and Portworx remounts the volume.
 Components: Shared Volumes (NFS)
 Affected Versions: 3.5.1 and later
Major

PWX-57381
Issue: If you enable the FA/FB driver while a FlashArray Direct Access (FADA) cloud snapshot backup is in progress, Portworx Enterprise stops applying KVDB updates to FADA volumes, including the clone created by the backup. Portworx cannot delete the previous backup because the legacy delete path depends on a KVDB update, and the FA/FB driver cannot locate a volume that has no PVC. As a result, the previous backup remains on the FlashArray as an orphaned volume.
 User Impact: One or more orphaned FlashArray volumes can remain after you enable the FA/FB driver and continue to consume capacity on the array. Only backups that are in progress when you enable the driver are affected.
 Workaround: Ensure that no FADA cloud snapshot backups are in progress before you enable the FA/FB driver. If orphaned volumes remain, delete them manually from the FlashArray.
 Components: Cloudsnaps
 Affected Versions: 3.7.0
Major

PWX-57434
Issue: During an uncontrolled KDS pool failover, the failover can be delayed when the source node goes down while holding the pool ConfigMap lock. The target coordinator must wait for the stale lock's approximately 15-second TTL to expire before it can continue. It can then spend additional time waiting for the pool write lock while in-flight volume operations complete. These waits can add approximately 20 seconds before pool deactivation and activation begin.
 User Impact: Uncontrolled pool failover can take longer than expected, increasing the time before the affected pool becomes available on the target node. Workloads using the pool can experience a longer I/O interruption during the failover.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-57452
Issue: During KDS pool failover on PX-StoreV2 clusters, pool activation can occasionally take significantly longer than expected. The delay occurs primarily during LVM activation on the target node. In some cases, LVM operations such as `vgchange -ay` can spend tens of seconds waiting for thin-pool checks or device-mapper operations to complete, increasing the overall pool failover time.
 User Impact: KDS pool failover can take longer than expected, delaying pool availability on the target node. The failover eventually completes successfully, but workloads that depend on the affected pool might experience a longer recovery interval.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-57527
Issue: The Kube Datastore (KDS) VM count does not decrease after you delete a KubeVirt virtual machine when its DataVolumes, PVCs, and Portworx volumes are retained. The retained Portworx volumes still contain labels for the deleted VM's name and UID, and KDS counts the VM metadata found on the retained volumes without verifying that the associated Kubernetes VM object still exists.
 User Impact: The `pxctl kds list` command can report a VM count that is higher than the actual number of virtual machines, which can result in inaccurate KDS usage reporting.
 Workaround: Delete the retained Portworx volumes that belonged to the removed virtual machine to clear the stale count. The stale count does not affect volume operations.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-57757
Issue: When an incremental cloud backup has no changed data, Portworx retains its local snapshot as the base for the next incremental backup. After a subsequent backup no longer requires this snapshot, Portworx might not delete it promptly, leaving the snapshot on the storage pool longer than necessary.
 User Impact: Retained local snapshots can continue to consume storage pool capacity until they are removed by a later cleanup operation or when the source volume is deleted.
 Components: Cloudsnaps
 Affected Versions: 3.7.0
Major

PWX-57878
Issue: In Portworx Enterprise deployments where the FA/FB driver is not enabled, concurrent cloudsnap operations can create duplicate Portworx IDs for the same local cloudsnap clone. When Portworx removes the duplicate ID, it can also delete the corresponding volume on the FlashArray while leaving the original KVDB entry behind. If you later enable the FA/FB driver, the metadata migration can fail because the KVDB entry references a backend volume that no longer exists.
 User Impact: The metadata migration can stop when Portworx encounters the stale KVDB entry, leaving the migration incomplete until the entry is removed.
 Workaround: Remove the stale KVDB entry for the missing FADA cloudsnap clone, and then retrigger the metadata migration.
 Components: Cloudsnaps
 Affected Versions: 3.7.0
Major

PWX-57891
Issue: During large-scale NFS cloudsnap operations that use a 100 MB object size, checksum processing can consume significant memory. Because checksum memory is allocated dynamically, concurrent backup activity can increase Portworx memory usage enough to cause memory pressure and process termination on nodes with limited memory.
 User Impact: Ongoing cloudsnap backups can fail, and Portworx processes can restart or nodes can be marked down when the node runs out of available memory.
 Workaround: For large-scale NFS cloudsnap workloads that use a 100 MB object size, provision nodes with at least 32 GB of memory to provide sufficient headroom for checksum processing.
 Components: Cloudsnaps
 Affected Versions: 3.7.0
Major

PWX-57895
Issue: If a pool expansion using `add-drive` is interrupted when the node enters maintenance mode, the newly added drive can remain in the `Pending Add` state. After the node exits maintenance mode, a subsequent pool expansion request can complete the previous pending operation instead of expanding the pool to the newly requested size. The operation can report success even though the pool size does not increase to the requested value.
 User Impact: A pool expansion can report success without adding the newly requested capacity, and the pool remains at its existing size.
 Workaround: After the node exits maintenance mode, retry the pool expansion to complete the pending operation. Verify the pool size before submitting another expansion request.
 Components: Drive & Pool Management
 Affected Versions: 3.7.0
Major

In this topic:
