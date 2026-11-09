# Portworx Enterprise Release Notes

Source: https://docs.portworx.com/portworx-enterprise/release-notes (Portworx Enterprise latest)

Portworx Enterprise Release Notes | Portworx Enterprise Documentation

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
KDS affinity for volume placement: Use the `kube_datastore_affinity` parameter in a `StorageClass` to place volumes on a specific KDS during provisioning and subsequent storage rebalancing. For more information, see Kube Datastore affinity.

-
KDS-aware StorageClasses for KubeVirt VMs: The Portworx Operator automatically creates KDS-aware versions of the default KubeVirt StorageClasses for each KDS, simplifying VM disk placement through Kubernetes-native storage workflows. For more information, see Kube Datastore-aware StorageClasses.

-
KubeVirt VM disk migration between Kube Datastores: Move KubeVirt VM disks between Kube Datastores by selecting the KDS-aware `StorageClass` for the destination KDS, without recreating the VM. For more information, see Migrate KubeVirt VM disks to a different Kube Datastore.

-
Faster dynamic pool failover: Fast node-down detection reduces recovery time after unexpected node failures. When liveness and cluster-safety checks confirm that a node is unavailable, Portworx Enterprise typically initiates dynamic pool failover within 7 to 12 seconds, reducing workload disruption. For more information, see Fast node-down detection.

-
Increased validated scale for dynamic pools: Dynamic pools supports up to 5,000 volumes per cluster. A node with a single dynamic pool supports up to 256 volumes. Configurations with multiple dynamic pools supports up to four pools per node and 100 volumes per pool. For more information, see Dynamic Pools for Volumes with Replication Factor 1.

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
 Workaround: No workaround is available.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-54529
Issue: Telemetry is not supported on IPv6-only clusters. On dual-stack clusters, telemetry can also become unhealthy when `PX_PREFER_IPV6_NETWORK_IP` is set to `true`, because Portworx Enterprise selects an IPv6 management address that cannot reach the telemetry endpoint.
 User Impact: `pxctl status` reports telemetry as unhealthy, and Portworx Enterprise cannot send telemetry data to Pure1. Storage functionality is not affected.
 Workaround: No workaround is available.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-56345
Issue: On KDS clusters with a large number of volumes, a controlled pool failover initiated through the CLI can take significantly longer to complete. The delay increases with the number of volumes in the affected pool because pool deactivation and activation operations, including device cleanup and LVM activation, require additional processing for each volume.
 User Impact: CLI-initiated pool failovers can take up to two minutes to complete on large-scale clusters, delaying pool availability on the target node.
 Workaround: No workaround is available.
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
 Workaround: No workaround is available.
 Components: Control Plane
 Affected Versions: 3.7.0
Major

PWX-57452
Issue: During KDS pool failover on PX-StoreV2 clusters, pool activation can occasionally take significantly longer than expected. The delay occurs primarily during LVM activation on the target node. In some cases, LVM operations such as `vgchange -ay` can spend tens of seconds waiting for thin-pool checks or device-mapper operations to complete, increasing the overall pool failover time.
 User Impact: KDS pool failover can take longer than expected, delaying pool availability on the target node. The failover eventually completes successfully, but workloads that depend on the affected pool might experience a longer recovery interval.
 Workaround: No workaround is available.
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
 Workaround: No workaround is available.
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
