# Portworx Metrics for monitoring

Source: https://docs.portworx.com/portworx-enterprise/reference/metrics (Portworx Enterprise latest)

Portworx Metrics for monitoring | Portworx Enterprise Documentation

## Alert metrics​

Alert metrics use variable labels depending on the resource type. Each metric has a label named after its resource type (such as `node`, `volume`, `drive`, or `cluster`) that contains the resource ID, plus a `clusterid` label.

NameLabelsDescription

px_alerts_callhomefailurenode, clusteridIncrements when a call-home failure alert is raised; decrements when cleared

px_alerts_nodestatechangenode, clusteridIncrements when a node state-change alert is raised; decrements when cleared

px_alerts_nodestartsuccessnode, clusteridIncrements when a node successfully starts; decrements when cleared

## Backup metrics​

Per-backup metrics include `volume` and `volumename` labels that identify the backed-up volume. Node-level transfer metrics (`px_backup_stats_node_*`) do not include volume labels.

NameLabelsDescription

px_backup_stats_backup_statuscluster, clusterUUID, nodeID, node, volume, volumenameStatus for this backup (0=InProgress,1=Done,2=Failed)

px_backup_stats_backup_sizecluster, clusterUUID, nodeID, node, volume, volumenameSize in bytes for this backup

px_backup_stats_backup_duration_secondscluster, clusterUUID, nodeID, node, volume, volumenameDuration in seconds for this backup

px_backup_stats_backup_uploaded_bytes_mbscluster, clusterUUID, nodeID, node, volume, volumenameDelta bytes uploaded in MB/s from last interval for this backup

px_backup_stats_download_size_bytescluster, clusterUUID, nodeID, node, volume, volumenameSize of downloaded bytes during backup/restore from cloud

px_backup_stats_upload_size_bytescluster, clusterUUID, nodeID, node, volume, volumenameSize of uploaded bytes during backup/restore from cloud

px_backup_stats_get_apis_invokedcluster, clusterUUID, nodeID, node, volume, volumenameNumber of times GET API was invoked

px_backup_stats_put_apis_invokedcluster, clusterUUID, nodeID, node, volume, volumenameNumber of times PUT API was invoked

px_backup_stats_read_time_secondscluster, clusterUUID, nodeID, node, volume, volumenameTime spent in read operations during cloudsnap backup

px_backup_stats_write_time_secondscluster, clusterUUID, nodeID, node, volume, volumenameTime spent in write operations during cloudsnap restore

px_backup_stats_upload_time_secondscluster, clusterUUID, nodeID, node, volume, volumenameTime spent in upload operations during cloudsnap backup

px_backup_stats_download_time_secondscluster, clusterUUID, nodeID, node, volume, volumenameTime spent in download operations during cloudsnap restore

px_backup_stats_compress_time_secondscluster, clusterUUID, nodeID, node, volume, volumenameTime spent in compression during cloudsnap backup

px_backup_stats_encrypt_time_secondscluster, clusterUUID, nodeID, node, volume, volumenameTime spent in encryption during cloudsnap backup

px_backup_stats_node_upload_bytes_totalcluster, clusterUUID, nodeID, nodeTotal bytes uploaded from this node across all cloudsnaps

px_backup_stats_node_download_bytes_totalcluster, clusterUUID, nodeID, nodeTotal bytes downloaded to this node across all cloudsnaps

px_backup_stats_node_upload_bytes_intervalcluster, clusterUUID, nodeID, nodeBytes uploaded from this node in the current interval

px_backup_stats_node_download_bytes_intervalcluster, clusterUUID, nodeID, nodeBytes downloaded to this node in the current interval

px_backup_stats_node_upload_rate_bytes_per_seccluster, clusterUUID, nodeID, nodeCurrent upload rate in bytes per second for this node

px_backup_stats_node_download_rate_bytes_per_seccluster, clusterUUID, nodeID, nodeCurrent download rate in bytes per second for this node

## Cluster metrics​

NameLabelsDescription

px_cluster_cpu_percentcluster, clusterUUID, nodeID, nodePercentage of CPU used

px_cluster_memory_utilized_percentcluster, clusterUUID, nodeID, nodePercentage of memory utilization

px_cluster_disk_total_bytescluster, clusterUUID, nodeID, nodeTotal storage space in bytes for this node

px_cluster_disk_available_bytescluster, clusterUUID, nodeID, nodeAvailable storage space in bytes for this node

px_cluster_disk_utilized_bytescluster, clusterUUID, nodeID, nodeUtilized storage space in bytes for this node

px_cluster_pendingiocluster, clusterUUID, nodeID, nodeNumber of read and write operations currently in progress for this node

px_cluster_trashcan_volumescluster, clusterUUID, nodeID, nodeNumber of volumes currently in the trashcan

## Cluster status metrics​

NameLabelsDescription

px_cluster_status_cluster_sizecluster, clusterUUID, nodeID, nodeNode count for your Portworx cluster. Deprecated.

px_cluster_status_sizecluster, clusterUUID, nodeID, nodeNode count for your Portworx cluster

px_cluster_status_cluster_quorumcluster, clusterUUID, nodeID, nodeIndicates if the cluster is in quorum. Deprecated.

px_cluster_status_quorumcluster, clusterUUID, nodeID, nodeIndicates if the cluster is in quorum

px_cluster_status_nodes_onlinecluster, clusterUUID, nodeID, nodeNumber of online nodes in the cluster (includes storage and storageless)

px_cluster_status_nodes_offlinecluster, clusterUUID, nodeID, nodeNumber of offline nodes in the cluster (includes storage and storageless)

px_cluster_status_nodes_storage_downcluster, clusterUUID, nodeID, nodeNumber of nodes where the storage is full or down

px_cluster_status_storage_nodes_onlinecluster, clusterUUID, nodeID, nodeNumber of storage nodes that are online

px_cluster_status_storage_nodes_offlinecluster, clusterUUID, nodeID, nodeNumber of storage nodes that are offline

px_cluster_status_storage_nodes_decommissionedcluster, clusterUUID, nodeID, nodeNumber of storage nodes that are decommissioned

## Device delete metrics​

NameLabelsDescription

px_device_delete_delete_after_discard_enabledcluster, clusterUUID, nodeID, node, poolidCurrent configuration value indicating if NBDD is enabled

px_device_delete_discard_bytes_totalcluster, clusterUUID, nodeID, node, poolidTotal bytes discarded across all device deletes

px_device_delete_discard_duration_msec_totalcluster, clusterUUID, nodeID, node, poolidTotal time spent in discard operations in milliseconds across all device deletes

px_device_delete_discard_errors_totalcluster, clusterUUID, nodeID, node, poolidTotal number of discard errors encountered across all device deletes

px_device_delete_discard_operations_totalcluster, clusterUUID, nodeID, node, poolidTotal number of discard operations performed across all device deletes

px_device_delete_discard_size_bytescluster, clusterUUID, nodeID, node, poolidCurrent configuration value for discard size in bytes

px_device_delete_operations_completed_totalcluster, clusterUUID, nodeID, node, poolidTotal number of delete operations completed

px_device_delete_operations_inprogresscluster, clusterUUID, nodeID, node, poolidCurrent number of delete operations in progress

px_device_delete_operations_queuedcluster, clusterUUID, nodeID, node, poolidCurrent number of delete operations queued

px_device_delete_release_bytes_totalcluster, clusterUUID, nodeID, node, poolidTotal size of devices processed for storage release in bytes

px_device_delete_release_duration_msec_totalcluster, clusterUUID, nodeID, node, poolidTotal time spent in storage release operations in milliseconds

px_device_delete_release_operations_totalcluster, clusterUUID, nodeID, node, poolidTotal number of devices processed for storage release

## Disk metrics​

NameLabelsDescription

px_disk_stats_used_bytescluster, clusterUUID, nodeID, node, disk, poolTotal storage in bytes for this disk

px_disk_stats_interval_secondscluster, clusterUUID, nodeID, node, disk, poolinterval_seconds

px_disk_stats_io_secondscluster, clusterUUID, nodeID, node, disk, poolTime spent doing IO in seconds for this disk

px_disk_stats_progress_iocluster, clusterUUID, nodeID, node, disk, poolIO's currently in progress for this disk

px_disk_stats_disk_read_bytescluster, clusterUUID, nodeID, node, disk, poolTotal bytes read for this disk. Deprecated.

px_disk_stats_read_bytescluster, clusterUUID, nodeID, node, disk, poolTotal bytes read for this disk

px_disk_stats_write_bytes_secondscluster, clusterUUID, nodeID, node, disk, poolTotal written bytes for this disk. Deprecated.

px_disk_stats_written_bytescluster, clusterUUID, nodeID, node, disk, poolTotal written bytes for this disk

px_disk_stats_read_secondscluster, clusterUUID, nodeID, node, disk, poolTotal time spent reading in seconds for this disk

px_disk_stats_write_secondscluster, clusterUUID, nodeID, node, disk, poolTotal time spent writing in seconds for this disk

px_disk_stats_read_latency_secondscluster, clusterUUID, nodeID, node, disk, poolAverage time spent per read operation in seconds for this disk

px_disk_stats_write_latencycluster, clusterUUID, nodeID, node, disk, poolAverage time spent per write operation in seconds for this disk. Deprecated.

px_disk_stats_write_latency_secondscluster, clusterUUID, nodeID, node, disk, poolAverage time spent per write operation in seconds

px_disk_stats_disk_num_readscluster, clusterUUID, nodeID, node, disk, poolTotal number of read operations completed successfully for this disk. Deprecated.

px_disk_stats_disk_num_writescluster, clusterUUID, nodeID, node, disk, poolTotal number of write operations completed successfully for this disk. Deprecated.

px_disk_stats_num_readscluster, clusterUUID, nodeID, node, disk, poolTotal number of read operations completed successfully for this disk

px_disk_stats_num_writescluster, clusterUUID, nodeID, node, disk, poolTotal number of write operations completed successfully for this disk

px_disk_stats_num_reads_totalcluster, clusterUUID, nodeID, node, disk, poolTotal number of read operations completed successfully for this disk

px_disk_stats_num_writes_totalcluster, clusterUUID, nodeID, node, disk, poolTotal number of write operations completed successfully for this disk

px_disk_stats_written_bytes_totalcluster, clusterUUID, nodeID, node, disk, poolTotal bytes written for this disk

px_disk_stats_read_bytes_totalcluster, clusterUUID, nodeID, node, disk, poolTotal bytes read for this disk

px_disk_stats_read_seconds_totalcluster, clusterUUID, nodeID, node, disk, poolTotal time spent reading in seconds for this disk

px_disk_stats_write_seconds_totalcluster, clusterUUID, nodeID, node, disk, poolTotal time spent writing in seconds for this disk

## FA/FB API metrics​

NameLabelsDescription

px_fafb_apis_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to all the configured FA/FB endpoints

px_fafb_apis_array_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /arrays endpoint

px_fafb_apis_login_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /login endpoint

px_fafb_apis_controllers_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /controllers endpoint

px_fafb_apis_alerts_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /alerts endpoint

px_fafb_apis_ports_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /ports endpoint

px_fafb_apis_volumes_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /volumes endpoint

px_fafb_apis_volumesnapshots_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /volume-snapshots endpoint

px_fafb_apis_hosts_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /hosts endpoint

px_fafb_apis_connections_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /connections endpoint

px_fafb_apis_version_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of API requests made to the /api_version endpoint

## Kube Datastore metrics​

Use the following Prometheus metrics to monitor Kube Datastore capacity and performance:

NameLabelsDescription

`px_kube_datastore_total_bytes``kube_datastore`Total capacity, in bytes, across all storage pools in the Kube Datastore.

`px_kube_datastore_used_bytes``kube_datastore`Used capacity, in bytes, across all storage pools in the Kube Datastore.

`px_kube_datastore_available_bytes``kube_datastore`Available capacity, in bytes, across all storage pools in the Kube Datastore.

`px_kube_datastore_provisioned_bytes``kube_datastore`Provisioned volume capacity, in bytes, for the Kube Datastore.

`px_kube_datastore_used_percent``kube_datastore`Used capacity as a percentage of the total Kube Datastore capacity.

`px_kube_datastore_provisioned_percent``kube_datastore`Provisioned capacity as a percentage of the total Kube Datastore capacity.

`px_kube_datastore_write_iops``kube_datastore`Write IOPS for the Kube Datastore, calculated as a 5-minute rate.

`px_kube_datastore_write_throughput_bytes_per_second``kube_datastore`Write throughput, in bytes per second, for the Kube Datastore, calculated as a 5-minute rate.

`px_kube_datastore_write_latency_seconds``kube_datastore`Write latency, in seconds, for the Kube Datastore, calculated over a 5-minute rate.

note

-
Kube Datastore metrics are generated from storage pool metrics by using Prometheus recording rules installed by the Portworx Operator. Prometheus is required to evaluate these rules. On OpenShift, additional configuration is required to enable the recording rules. For more information, see Enable Kube Datastore metrics.

-
Storage pool metrics include the `kube_datastore` label, which identifies the Kube Datastore associated with each pool.

-
Kube Datastore I/O metrics are available only for write operations because storage pool metrics for read operations are not available.

## KVDB metrics​

NameLabelsDescription

px_kvdb_get_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of get requests for a key

px_kvdb_snapshot_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of kvdb snapshot requests for a list of prefixes

px_kvdb_put_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of put requests for a key

px_kvdb_create_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of create requests for a key

px_kvdb_update_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of update requests for a key

px_kvdb_enumerate_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of enumerate requests for a key

px_kvdb_delete_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of delete requests for a key

px_kvdb_keys_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of list key requests for a prefix

px_kvdb_cas_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of compare and sets for a key

px_kvdb_cad_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of compare and deletes for a key

px_kvdb_lock_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of lock requests for a key

px_kvdb_unlock_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of unlock requests for a key

px_kvdb_watchkey_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of watch requests for a key from a node

px_kvdb_watchtree_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of watch requests for a prefix from a node

px_kvdb_adduser_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of add user requests

px_kvdb_removeuser_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of remove user requests

px_kvdb_grantuser_access_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of grant access requests for a user

px_kvdb_revokeuser_access_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of revoke access requests for a user

px_kvdb_addmember_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of add member requests from a node

px_kvdb_addlearner_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of add learner requests from a node

px_kvdb_removemember_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of remove member requests from a node

px_kvdb_updatemember_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of update member requests from a node

px_kvdb_listmembers_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of list member requests from a node

px_kvdb_setendpoints_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of set endpoint requests from a node

px_kvdb_getendpoints_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of get endpoint requests from a node

px_kvdb_defragment_requests_totalcluster, clusterUUID, nodeID, nodeTotal number of defragment requests from a node

px_kvdb_watch_latency_secondscluster, clusterUUID, nodeID, nodeTime taken in seconds between a kvdb put and a corresponding watch update

## KVDB health metrics​

NameLabelsDescription

px_kvdb_health_state_node_viewcluster, clusterUUID, nodeID, nodeThis node's kvdb state (1 = healthy, 2 = not healthy)

px_kvdb_health_state_cluster_viewcluster, clusterUUID, nodeID, nodeThis node's view of other node's kvdb state (1 = healthy, 2 = not healthy)

## License metrics​

NameLabelsDescription

px_license_expirycluster, clusterUUID, nodeID, nodeLicense expiry in days. A negative value indicates the license has expired.

px_license_next_refreshcluster, clusterUUID, nodeID, nodeNext license refresh timestamp in minutes. A negative value indicates that the license will not be refreshed.

px_license_typecluster, clusterUUID, nodeID, nodeIndicates the type of license (0=PX-Developer, 1=Legacy Enterprise, 2=Trial, 3=PX-Enterprise, 4=PX-Enterprise floating, 5=IBM Cloud Pak for Data, 6=CISCO OEM, 7=PX-Essential, 8=Portworx CSI for FA/FB, 9=INVALID LICENSE)

## Network I/O metrics​

NameLabelsDescription

px_network_io_bytessentcluster, clusterUUID, nodeID, nodeNumber of bytes sent during this interval

px_network_io_received_bytescluster, clusterUUID, nodeID, nodeNumber of bytes received during this interval

px_network_io_sent_bytes_totalcluster, clusterUUID, nodeID, nodeTotal number of bytes sent

px_network_io_received_bytes_totalcluster, clusterUUID, nodeID, nodeTotal number of bytes received

px_network_io_reservation_waitscluster, clusterUUID, nodeID, node, nodeidTotal number of SM waits for reservation

px_network_io_reservation_wake_upscluster, clusterUUID, nodeID, node, nodeidTotal number of SM wake ups after getting the reservation

## NFS pool metrics​

NameLabelsDescription

px_nfs_pool_stats_packets_arrivedcluster, clusterUUID, nodeID, nodeCounts the number of NFS packets that arrived on the socket.

px_nfs_pool_stats_sockets_enqueuedcluster, clusterUUID, nodeID, nodeCounts how many times an NFS transport is enqueued to wait for an nfsd thread to service it, i.e. no nfsd thread was considered available.

px_nfs_pool_stats_threads_wokencluster, clusterUUID, nodeID, nodeCounts how many times an idle nfsd thread is woken to try to receive some data from an NFS transport.

px_nfs_pool_stats_threads_timedoutcluster, clusterUUID, nodeID, nodeCounts how many times an nfsd thread triggered an idle timeout, i.e. was not woken to handle any incoming network packets for some time.

## Node metrics​

NameLabelsDescription

px_node_stats_free_memcluster, clusterUUID, nodeID, nodeAvailable memory in bytes

px_node_stats_total_memcluster, clusterUUID, nodeID, nodeTotal memory in bytes

px_node_stats_used_memcluster, clusterUUID, nodeID, nodeUsed memory in bytes

px_node_stats_cpu_usagecluster, clusterUUID, nodeID, nodePercent of CPU consumption

px_node_stats_busy_threads_percentcluster, clusterUUID, nodeID, nodePercentage of busy threads

px_node_stats_thread_pool_high_priority_queue_sizecluster, clusterUUID, nodeID, nodeThread Pool High Priority Queue Size

px_node_stats_thread_pool_long_running_busy_threadscluster, clusterUUID, nodeID, nodeLong Running Thread Pool Number Of Busy Threads

px_node_stats_thread_pool_long_running_queue_sizecluster, clusterUUID, nodeID, nodeLong Running Thread Pool Pending Items In Queue

px_node_stats_thread_pool_long_running_max_threadscluster, clusterUUID, nodeID, nodeLong Running Thread Pool Count Of Max Threads

px_node_stats_writeback_list_num_dirty_poolscluster, clusterUUID, nodeID, nodeWriteback List Number of Dirty Pools

px_node_stats_writeback_list_num_pending_log_bufscluster, clusterUUID, nodeID, nodeWriteback List Number of Pending Log Buffers

px_node_stats_writeback_list_low_cos_queue_sizecluster, clusterUUID, nodeID, nodeWriteback List Low Cos Queue Size

px_node_stats_writeback_list_high_cos_queue_sizecluster, clusterUUID, nodeID, nodeWriteback List High Cos Queue Size

px_node_stats_sm_run_queue_sizecluster, clusterUUID, nodeID, nodeStatemachine Run Queue Size

px_node_stats_kaio_pending_queue_sizecluster, clusterUUID, nodeID, nodeKaio Pending Queue Size

px_node_stats_request_scheduler_queue_sizecluster, clusterUUID, nodeID, nodeRequest Scheduler Queue Size

px_node_stats_num_readscluster, clusterUUID, nodeID, nodeNumber of read operations in the last interval for this node

px_node_stats_read_bytescluster, clusterUUID, nodeID, nodeRead bytes in the last interval for this node

px_node_stats_read_mscluster, clusterUUID, nodeID, nodeTotal time in milliseconds spent reading in the last interval for this node

px_node_stats_read_iopscluster, clusterUUID, nodeID, nodeAverage number of completed read operations per second for this node

px_node_stats_readthroughputcluster, clusterUUID, nodeID, nodeAverage number of bytes read per second for this node

px_node_stats_read_latency_secondscluster, clusterUUID, nodeID, nodeAverage time spent per read operation for this node

px_node_stats_num_writescluster, clusterUUID, nodeID, nodeNumber of write operations in the last interval for this node

px_node_stats_written_bytescluster, clusterUUID, nodeID, nodeBytes written since last interval for this node

px_node_stats_write_mscluster, clusterUUID, nodeID, nodeTotal time in milliseconds spent writing in the last interval for this node

px_node_stats_write_iopscluster, clusterUUID, nodeID, nodeAverage number of completed write operations per second for this node

px_node_stats_writethroughputcluster, clusterUUID, nodeID, nodeAverage number of bytes written per second for this node

px_node_stats_write_latency_secondscluster, clusterUUID, nodeID, nodeAverage time spent per write operation for this node

px_node_stats_num_discardscluster, clusterUUID, nodeID, nodeNumber of discard operations in the last interval for this node

px_node_stats_discarded_bytescluster, clusterUUID, nodeID, nodeBytes discarded since last interval for this node

px_node_stats_discard_mscluster, clusterUUID, nodeID, nodeTotal time in milliseconds spent discarding in the last interval for this node

px_node_stats_discard_iopscluster, clusterUUID, nodeID, nodeAverage number of completed discard operations per second for this node

px_node_stats_discardthroughputcluster, clusterUUID, nodeID, nodeAverage number of bytes discarded per second for this node

px_node_stats_discard_latency_secondscluster, clusterUUID, nodeID, nodeAverage time spent per discard operation for this node

px_node_stats_num_flushescluster, clusterUUID, nodeID, nodeNumber of flush(sync) operations in the last interval for this node

px_node_stats_flushed_bytescluster, clusterUUID, nodeID, nodeNumber of flushed bytes since last interval for this node

px_node_stats_flushmscluster, clusterUUID, nodeID, nodeLatency for flush for this node

px_node_stats_flush_iopscluster, clusterUUID, nodeID, nodeAverage number of completed flush operations per second for this node

px_node_stats_flushthroughputcluster, clusterUUID, nodeID, nodeAverage number of bytes flushed per second for this node

px_node_stats_flush_latency_secondscluster, clusterUUID, nodeID, nodeAverage time spent per flush operation for this node

px_node_stats_num_ioscluster, clusterUUID, nodeID, nodeNumber of IO operations in the last interval for this node

px_node_stats_io_bytescluster, clusterUUID, nodeID, nodeIO bytes in the last interval for this node

px_node_stats_io_mscluster, clusterUUID, nodeID, nodeTotal time in milliseconds spent doing IO in the last interval for this node

px_node_stats_io_iopscluster, clusterUUID, nodeID, nodeAverage number of completed IO operations per second for this node

px_node_stats_iothroughputcluster, clusterUUID, nodeID, nodeAverage number of bytes IO per second for this node

px_node_stats_io_latency_secondscluster, clusterUUID, nodeID, nodeAverage time spent per IO operation for this node

px_node_stats_procfs_mem_available_bytescluster, clusterUUID, nodeID, nodeAvailable memory in bytes

px_node_stats_procfs_mem_dirty_bytescluster, clusterUUID, nodeID, nodeThe total amount of memory waiting to be written back to the disk

px_node_stats_procfs_mem_writeback_bytescluster, clusterUUID, nodeID, nodeThe total amount of memory actively being written back to the disk

px_node_stats_procfs_mem_total_bytescluster, clusterUUID, nodeID, nodeTotal amount of usable RAM which is physical RAM minus a number of reserved bits and the kernel binary code

px_node_stats_procfs_mem_free_bytescluster, clusterUUID, nodeID, nodeThe amount of physical RAM, in bytes, left unused by the system.

px_node_stats_procfs_mem_buffers_bytescluster, clusterUUID, nodeID, nodeThe amount, in bytes, of temporary storage for raw disk blocks

px_node_stats_procfs_mem_cached_bytescluster, clusterUUID, nodeID, nodeThe amount of physical RAM, in bytes, used as cache memory

px_node_stats_procfs_mem_active_anon_bytescluster, clusterUUID, nodeID, nodeThe amount of anonymous and tmpfs/shmem memory, in bytes, that is in active use, or was in active use since the last time the system moved something to swap

px_node_stats_procfs_mem_inactive_anon_bytescluster, clusterUUID, nodeID, nodeThe amount of anonymous and tmpfs/shmem memory, in bytes, that is a candidate for eviction

px_node_stats_procfs_mem_active_file_bytescluster, clusterUUID, nodeID, nodeThe amount of file cache memory, in bytes, that is in active use, or was in active use since the last time the system reclaimed memory

px_node_stats_procfs_mem_inactive_file_bytescluster, clusterUUID, nodeID, nodeThe amount of file cache memory, in bytes, that is newly loaded from the disk, or is a candidate for reclaiming

px_node_stats_procfs_mem_unevictable_bytescluster, clusterUUID, nodeID, nodeThe amount of memory, in bytes, discovered by the pageout code, that is not evictable because it is locked into memory by user programs

px_node_stats_procfs_mem_mlocked_bytescluster, clusterUUID, nodeID, nodeThe total amount of memory, in bytes, that is not evictable because it is locked into memory by user programs

px_node_stats_procfs_mem_anon_pages_bytescluster, clusterUUID, nodeID, nodeThe total amount of memory, in bytes, used by pages that are not backed by files and are mapped into userspace page tables

px_node_stats_procfs_mem_mapped_bytescluster, clusterUUID, nodeID, nodeThe memory, in bytes, used for files that have been mmaped, such as libraries

px_node_stats_procfs_mem_sh_mem_bytescluster, clusterUUID, nodeID, nodeThe total amount of memory, in bytes, used by shared memory (shmem) and tmpfs

px_node_stats_num_skinnysnapscluster, clusterUUID, nodeID, nodeThe number of SkinnySnaps

px_node_stats_skinnysnaps_num_repls_skipscluster, clusterUUID, nodeID, nodeThe number of target replicas skipped for a snapshot due to SkinnySnap

px_node_stats_skinnysnaps_num_repls_snapshotscluster, clusterUUID, nodeID, nodeThe number of target replicas that underwent a snapshot operation due to SkinnySnap

px_node_stats_relaxed_reclaim_pendingcluster, clusterUUID, nodeID, nodeThe number of volumes in RelaxedReclaim pending queue

px_node_stats_relaxed_reclaim_skippedcluster, clusterUUID, nodeID, nodeThe number of volume deletes that were skipped from being delayed even when RelaxedReclaim was enabled.

px_node_stats_relaxed_reclaim_deletedcluster, clusterUUID, nodeID, nodeThe number of volume deletes done through RelaxedReclaim

px_node_stats_num_volumescluster, clusterUUID, nodeID, nodeThe number of volumes hosted on this node

px_node_stats_local_snapshot_countcluster, clusterUUID, nodeID, nodeTotal number of local snapshots present on this node. If a snapshot has HA>1, it will be counted on each node where it is replicated.

px_node_stats_cloud_snapshot_countcluster, clusterUUID, nodeID, nodeTotal number of active/in-progress cloud snapshots from this node (Active, Queued states).

px_node_stats_group_snapshot_countcluster, clusterUUID, nodeID, nodeTotal number of unique group IDs on this node (counts distinct group snapshots including local snapshots and completed cloud backups).

px_node_stats_local_group_snapshot_countcluster, clusterUUID, nodeID, nodeTotal number of unique local group snapshot IDs present on this node (excludes cascaded cloud-backup references).

px_node_stats_cloud_group_snapshot_countcluster, clusterUUID, nodeID, nodeTotal number of active/in-progress cloud group snapshots from this node (Active, Queued states).

px_node_stats_volume_replica_countcluster, clusterUUID, nodeID, nodeTotal number of volume replicas hosted on this node.

## Node status metrics​

NameLabelsDescription

px_node_status_node_statuscluster, clusterUUID, nodeID, nodeStatus of this node (https://libopenstorage.github.io/w/master.generated-api/#status)

px_node_status_license_expirycluster, clusterUUID, nodeID, nodeNumber of days until License (or License lease) expires (<0 means Expired)

## Storage pool metrics​

NameLabelsDescription

px_pool_stats_pool_written_bytescluster, clusterUUID, nodeID, node, poolBytes written since last interval for this pool. Deprecated.

px_pool_stats_pool_write_latency_secondscluster, clusterUUID, nodeID, node, poolAverage time spent per write operation for this pool. Deprecated.

px_pool_stats_pool_writethroughputcluster, clusterUUID, nodeID, node, poolAverage number of bytes written per second for this pool. Deprecated.

px_pool_stats_pool_flushed_bytescluster, clusterUUID, nodeID, node, poolNumber of flushed bytes since last interval for this pool. Deprecated.

px_pool_stats_pool_num_flushescluster, clusterUUID, nodeID, node, poolNumber of flush(sync) operations since last interval for this pool. Deprecated.

px_pool_stats_pool_flushmscluster, clusterUUID, nodeID, node, poolLatency for flush for this pool. Deprecated.

px_pool_stats_pool_provisioned_bytescluster, clusterUUID, nodeID, node, poolProvisioned storage space in bytes for this pool. Deprecated.

px_pool_stats_pool_statuscluster, clusterUUID, nodeID, node, poolStatus of this Pool (0=Offline,1=Online). Deprecated.

px_pool_stats_num_readscluster, clusterUUID, nodeID, node, poolNumber of read operations in the last interval for this pool

px_pool_stats_read_bytescluster, clusterUUID, nodeID, node, poolRead bytes in the last interval for this pool

px_pool_stats_read_mscluster, clusterUUID, nodeID, node, poolTotal time in milliseconds spent reading in the last interval for this pool

px_pool_stats_read_iopscluster, clusterUUID, nodeID, node, poolAverage number of completed read operations per second for this pool

px_pool_stats_readthroughputcluster, clusterUUID, nodeID, node, poolAverage number of bytes read per second for this pool

px_pool_stats_read_latency_secondscluster, clusterUUID, nodeID, node, poolAverage time spent per read operation for this pool

px_pool_stats_written_bytescluster, clusterUUID, nodeID, node, poolBytes written since last interval for this pool

px_pool_stats_num_writescluster, clusterUUID, nodeID, node, poolNumber of write operations in the last interval for this pool

px_pool_stats_write_mscluster, clusterUUID, nodeID, node, poolTotal time in milliseconds spent writing in the last interval for this pool

px_pool_stats_write_latency_secondscluster, clusterUUID, nodeID, node, poolAverage time spent per write operation for this pool

px_pool_stats_write_iopscluster, clusterUUID, nodeID, node, poolAverage number of completed write operations per second for this pool

px_pool_stats_writethroughputcluster, clusterUUID, nodeID, node, poolAverage number of bytes written per second for this pool

px_pool_stats_num_discardscluster, clusterUUID, nodeID, node, poolNumber of discard operations in the last interval for this pool

px_pool_stats_discarded_bytescluster, clusterUUID, nodeID, node, poolBytes discarded since last interval for this pool

px_pool_stats_discard_mscluster, clusterUUID, nodeID, node, poolTotal time in milliseconds spent discarding in the last interval for this pool

px_pool_stats_discard_iopscluster, clusterUUID, nodeID, node, poolAverage number of completed discard operations per second for this pool

px_pool_stats_discardthroughputcluster, clusterUUID, nodeID, node, poolAverage number of bytes discarded per second for this pool

px_pool_stats_discard_latency_secondscluster, clusterUUID, nodeID, node, poolAverage time spent per discard operation for this pool

px_pool_stats_flushed_bytescluster, clusterUUID, nodeID, node, poolNumber of flushed bytes since last interval for this pool

px_pool_stats_num_flushescluster, clusterUUID, nodeID, node, poolNumber of flush(sync) operations since last interval for this pool

px_pool_stats_flushmscluster, clusterUUID, nodeID, node, poolLatency for flush for this pool

px_pool_stats_flush_iopscluster, clusterUUID, nodeID, node, poolAverage number of completed flush operations per second for this pool

px_pool_stats_flushthroughputcluster, clusterUUID, nodeID, node, poolAverage number of bytes flushed per second for this pool

px_pool_stats_flush_latency_secondscluster, clusterUUID, nodeID, node, poolAverage time spent per flush operation for this pool

px_pool_stats_num_ioscluster, clusterUUID, nodeID, node, poolNumber of IO operations in the last interval for this pool

px_pool_stats_io_bytescluster, clusterUUID, nodeID, node, poolIO bytes in the last interval for this pool

px_pool_stats_io_mscluster, clusterUUID, nodeID, node, poolTotal time in milliseconds spent doing IO in the last interval for this pool

px_pool_stats_io_iopscluster, clusterUUID, nodeID, node, poolAverage number of completed IO operations per second for this pool

px_pool_stats_iothroughputcluster, clusterUUID, nodeID, node, poolAverage number of bytes IO per second for this pool

px_pool_stats_io_latency_secondscluster, clusterUUID, nodeID, node, poolAverage time spent per IO operation for this pool

px_pool_stats_provisioned_bytescluster, clusterUUID, nodeID, node, poolProvisioned storage space in bytes for this pool

px_pool_stats_statuscluster, clusterUUID, nodeID, node, poolStatus of this Pool (0=Offline,1=Online,2=Full,3=NotFound,4=Maintenance,5=Degraded,6=Background activity)

px_pool_stats_available_bytescluster, clusterUUID, nodeID, node, poolAvailable storage space in bytes for this pool

px_pool_stats_used_bytescluster, clusterUUID, nodeID, node, poolUsed storage space in bytes for this pool

px_pool_stats_total_bytescluster, clusterUUID, nodeID, node, poolTotal storage space in bytes for this pool

px_pool_stats_written_bytes_totalcluster, clusterUUID, nodeID, node, poolTotal bytes written for this pool

px_pool_stats_flushed_bytes_totalcluster, clusterUUID, nodeID, node, poolTotal number of flushed bytes

px_pool_stats_num_flushes_totalcluster, clusterUUID, nodeID, node, poolTotal number of flush(sync) operations

px_pool_stats_flushms_totalcluster, clusterUUID, nodeID, node, poolTotal time spent in flush

## Process metrics​

NameLabelsDescription

px_proc_stats_virtcluster, clusterUUID, nodeID, node, procVirtual memory in bytes

px_proc_stats_rescluster, clusterUUID, nodeID, node, procResident set size memory in bytes

px_proc_stats_cputimecluster, clusterUUID, nodeID, node, procAmount of time that this process has been scheduled in user and kernel mode measured in clock ticks

## Portworx cache metrics​

NameLabelsDescription

px_px_cache_statuscluster, clusterUUID, nodeID, node, poolCache enabled (0=No,1=Yes)

px_px_cache_total_blockscluster, clusterUUID, nodeID, node, poolNumber of total blocks in the cache

px_px_cache_used_blockscluster, clusterUUID, nodeID, node, poolNumber of used blocks in the cache

px_px_cache_dirty_blockscluster, clusterUUID, nodeID, node, poolNumber of dirty blocks in the cache

px_px_cache_read_hitscluster, clusterUUID, nodeID, node, poolNumber of read hits for the cache

px_px_cache_read_misscluster, clusterUUID, nodeID, node, poolNumber of read misses for the cache

px_px_cache_write_hitscluster, clusterUUID, nodeID, node, poolNumber of write hits for the cache

px_px_cache_write_misscluster, clusterUUID, nodeID, node, poolNumber of write misses for the cache

px_px_cache_block_sizecluster, clusterUUID, nodeID, node, poolBlock size for the cache

px_px_cache_modecluster, clusterUUID, nodeID, node, poolMode of the cache

px_px_cache_migrate_promotecluster, clusterUUID, nodeID, node, poolNumber of blocks promoted to the cache

px_px_cache_migrate_demotecluster, clusterUUID, nodeID, node, poolNumber of block demoted from the cache

px_px_cache_io_mbpscluster, clusterUUID, nodeID, node, poolApprox cache bandwidth from cache internal actions

## Rebalance metrics​

NameLabelsDescription

px_rebalance_rebalance_job_statecluster, clusterUUID, nodeID, nodeRebalance job state (0 = pending, 1 = running, 2 = done, 3 = paused, 4 = cancelled)

px_rebalance_provision_space_rebalanced_bytes_totalcluster, clusterUUID, nodeID, nodeTotal provisioned space rebalanced (only counts add (since remove has equal value as add))

px_rebalance_used_space_rebalanced_bytes_totalcluster, clusterUUID, nodeID, nodeTotal used space rebalanced (only counts add (since remove has equal value as add))

px_rebalance_volumes_rebalanced_totalcluster, clusterUUID, nodeID, nodeTotal volumes affected by rebalance operation

px_rebalance_overloaded_pools_totalcluster, clusterUUID, nodeID, nodeNumber of overloaded pools

## Volume metrics​

NameLabelsDescription

px_volume_usage_bytescluster, clusterUUID, nodeID, node, volume, volumenameUsed storage space in bytes for this volume

px_volume_capacity_bytescluster, clusterUUID, nodeID, node, volume, volumenameConfigured size in bytes for this volume

px_volume_halevelcluster, clusterUUID, nodeID, node, volume, volumenameConfigured HA level for this volume

px_volume_currhalevelcluster, clusterUUID, nodeID, node, volume, volumenameCurrent HA level for this volume

px_volume_ioprioritycluster, clusterUUID, nodeID, node, volume, volumenameConfigured IO priority for this volume

px_volume_elapsed_time_since_detached_secondscluster, clusterUUID, nodeID, node, volume, volumenameSeconds elapsed since the volume is detached

px_volume_elapsed_time_since_attached_secondscluster, clusterUUID, nodeID, node, volume, volumenameSeconds elapsed since the volume is attached

px_volume_attachedcluster, clusterUUID, nodeID, node, volume, volumenameAttached state for this volume (0=detached,1=attached)

px_volume_statuscluster, clusterUUID, nodeID, node, volume, volumenameStatus for this volume (https://libopenstorage.github.io/w/master.generated-api/#volumestatus)

px_volume_statecluster, clusterUUID, nodeID, node, volume, volumenameState for this volume (https://libopenstorage.github.io/w/master.generated-api/#volumestate)

px_volume_attached_statecluster, clusterUUID, nodeID, node, volume, volumenameAttached state for this volume (valid only if volume is attached) (https://libopenstorage.github.io/w/master.generated-api/#attachstate)

px_volume_fs_health_statuscluster, clusterUUID, nodeID, node, volume, volumenameFilesystem health status for this volume (https://libopenstorage.github.io/w/master.generated-api/#filesystemhealthstatus)

px_volume_replication_statuscluster, clusterUUID, nodeID, node, volume, volumenameReplication Status for this volume (0 : up, 1 : not in quorum, 2 : resync state, 3 : degraded, 4 : detached, 5 : restore)

px_volume_fs_usage_bytescluster, clusterUUID, nodeID, node, volume, volumenameUsed storage space in bytes as reported by the filesystem for this volume

px_volume_fs_capacity_bytescluster, clusterUUID, nodeID, node, volume, volumenameTotal storage space in bytes as reported by the filesystem for this volume

px_volume_vol_read_bytescluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully read bytes during this interval for this volume. Deprecated.

px_volume_vol_written_bytescluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully written bytes during this interval for this volume. Deprecated.

px_volume_vol_readscluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully completed read operations during this interval for this volume. Deprecated.

px_volume_vol_writescluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully completed write operations during this interval for this volume. Deprecated.

px_volume_read_bytescluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully read bytes during this interval for this volume

px_volume_written_bytescluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully written bytes during this interval for this volume

px_volume_readscluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully completed read operations during this interval for this volume

px_volume_writescluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully completed write operations during this interval for this volume

px_volume_read_bytes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully read bytes for this volume

px_volume_written_bytes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully written bytes for this volume

px_volume_reads_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully completed read operations for this volume

px_volume_writes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully completed write operations for this volume

px_volume_iopscluster, clusterUUID, nodeID, node, volume, volumenameNumber of successful completed I/O operations per second during this interval for this volume

px_volume_write_iopscluster, clusterUUID, nodeID, node, volume, volumenameAverage number of completed write operations per second for this volume

px_volume_read_iopscluster, clusterUUID, nodeID, node, volume, volumenameAverage number of completed read operations per second for this volume

px_volume_vol_num_sequential_writescluster, clusterUUID, nodeID, node, volume, volumenameNumber of sequential write I/O operations during this interval for this volume

px_volume_vol_num_sequential_readscluster, clusterUUID, nodeID, node, volume, volumenameNumber of sequential read I/O operations during this interval for this volume

px_volume_vol_num_random_writescluster, clusterUUID, nodeID, node, volume, volumenameNumber of random write I/O operations during this interval for this volume

px_volume_vol_num_random_readscluster, clusterUUID, nodeID, node, volume, volumenameNumber of random read I/O operations during this interval for this volume

px_volume_depth_iocluster, clusterUUID, nodeID, node, volume, volumenameNumber of I/O operations currently in progress for this volume

px_volume_readthroughputcluster, clusterUUID, nodeID, node, volume, volumenameNumber of bytes read per second during this interval for this volume

px_volume_writethroughputcluster, clusterUUID, nodeID, node, volume, volumenameNumber of bytes written per second during this interval for this volume

px_volume_vol_bytes_reclaimedcluster, clusterUUID, nodeID, node, volume, volumenameNumber of bytes reclaimed by fstrim operation

px_volume_vol_bytes_reclaimablecluster, clusterUUID, nodeID, node, volume, volumenameNumber of bytes reclaimable on the volume as seen by fstrim operation

px_volume_vol_read_latency_secondscluster, clusterUUID, nodeID, node, volume, volumenameAverage time spent per successfully completed read operation in seconds during this interval for this volume. Deprecated.

px_volume_vol_write_latency_secondscluster, clusterUUID, nodeID, node, volume, volumenameAverage time spent per successfully completed write operation in seconds during this interval for this volume. Deprecated.

px_volume_read_latency_secondscluster, clusterUUID, nodeID, node, volume, volumenameAverage time spent per successfully completed read operation in seconds for this volume

px_volume_write_latency_secondscluster, clusterUUID, nodeID, node, volume, volumenameAverage time spent per successfully completed write operation in seconds for this volume

px_volume_num_long_readscluster, clusterUUID, nodeID, node, volume, volumenameNumber of long reads for this volume

px_volume_num_long_writescluster, clusterUUID, nodeID, node, volume, volumenameNumber of long writes for this volume

px_volume_num_long_flushescluster, clusterUUID, nodeID, node, volume, volumenameNumber of long flushes for this volume

px_volume_num_db_flushescluster, clusterUUID, nodeID, node, volume, volumenameNumber of DB flushes for this volume

px_volume_replica_read_bytes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully read bytes for this replica volume

px_volume_replica_written_bytes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully written bytes for this replica volume

px_volume_replica_reads_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully completed read operations for this replica volume

px_volume_replica_writes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully completed write operations for this replica volume

px_volume_replica_flushes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully completed flush operations for this replica volume

px_volume_replica_read_ms_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal time spent doing read operations in milliseconds for this replica volume

px_volume_replica_write_ms_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal time doing write operations in milliseconds for this replica volume

px_volume_replica_flush_ms_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal time doing write operations in milliseconds for this replica volume

px_volume_dev_depth_iocluster, clusterUUID, nodeID, node, volume, volumenameNumber of I/O operations currently in progress as reported by the kernel pxd device for this volume

px_volume_dev_writethroughputcluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully written bytes per second as reported by the kernel pxd device for this volume

px_volume_dev_readthroughputcluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully read bytes per second as reported by the kernel pxd device for this volume

px_volume_dev_read_latency_secondscluster, clusterUUID, nodeID, node, volume, volumenameAverage time spent per successfully completed read in seconds as reported by the kernel pxd device for this volume

px_volume_dev_write_latency_secondscluster, clusterUUID, nodeID, node, volume, volumenameAverage time spent per successfully completed write in seconds as reported by the kernel pxd device for this volume

px_volume_dev_read_bytes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully read bytes as reported by the kernel pxd device for this volume

px_volume_dev_written_bytes_totalcluster, clusterUUID, nodeID, node, volume, volumenameNumber of successfully written bytes as reported by the kernel pxd device for this volume

px_volume_dev_reads_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully completed read operations as reported by the kernel pxd device for this volume

px_volume_dev_writes_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal number of successfully completed write operations as reported by the kernel pxd device for this volume

px_volume_dev_read_seconds_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal time spent reading in seconds for this disk as reported by the kernel pxd device for this volume

px_volume_dev_write_seconds_totalcluster, clusterUUID, nodeID, node, volume, volumenameTotal time spent writing in seconds for this disk as reported by the kernel pxd device for this volume

px_volume_unique_blockscluster, clusterUUID, nodeID, node, volume, volumenameSize(in bytes) of unique blocks for this volume

px_volume_timestamp_recordscluster, clusterUUID, nodeID, node, volume, volumenameNumber of timestamp records accumulated

px_volume_timestamp_records_per_nodecluster, clusterUUID, nodeID, node, volume, volumenameNumber of timestamp records accumulated for a node

px_volume_num_discard_opscluster, clusterUUID, nodeID, node, volume, volumenameNumber of discard operations for this volume

px_volume_discarded_bytescluster, clusterUUID, nodeID, node, volume, volumenameNumber of discarded bytes for this volume

## Autopilot metrics​

The following Autopilot Prometheus metrics are available starting with Portworx Operator version 25.6.0.

NameDescription

autopilot_errors_totalTotal number of autopilot errors

autopilot_action_failed_countTotal number of declined or failed actions

autopilot_action_failed_totalTotal number of failed actions per rule object

autopilot_objects_in_stable_condition_totalTotal number of objects with stable conditions per rule

autopilot_action_taken_totalTotal number of actions taken per rule object

autopilot_objects_totalTotal number of objects per rule

autopilot_objects_with_rules_totalTotal number of objects matching any rules

autopilot_rules_in_systemTotal number of rules in the system

The following Autopilot Datadog metrics are available starting with Autopilot version 1.5.0.

NameDescription

autopilot_datadog_empty_response_totalTotal number of Datadog queries that returned empty results

autopilot_datadog_query_validation_failures_totalTotal number of Datadog query validation failures

autopilot_datadog_failures_totalTotal number of Datadog query failures by type

autopilot_datadog_success_totalTotal number of successful Datadog queries

The following Autopilot metrics are available starting with Autopilot version 1.6.0.

NameDescription

autopilot_object_evaluation_duration_secondsTime taken to evaluate managed objects and process their state transitions.

autopilot_engine_evaluation_duration_secondsTime taken to discover and process Autopilot rules in the cluster.

autopilot_prom_auth_token_refresh_totalTotal number of successful Prometheus authentication token refreshes.

autopilot_prom_auth_token_refresh_failures_totalTotal number of failed Prometheus authentication token refreshes.

autopilot_action_blockedBoolean that indicates if an action is blocked by another action (1: Blocked, 0: Not Blocked)

## Portworx DR and Stork metrics​

The following Prometheus metrics are available starting with Stork version 25.6.0.

### Migration metrics​

MetricTypeLabelsDescription

stork_migration_statusGaugecluster, name, namespace, clusterpair, schedule, statusMigration status—used to filter and list migrations by status within the cluster.

stork_migration_stageGaugename, namespace, scheduleStage of migration (0 = Initial, 1 = PreExecRule, 2 = PostExecRule, 3 = Volumes, 4 = Applications, 5 = Final).

stork_migration_durationGaugecluster, name, namespace, schedule, stageDuration of migration in seconds. Stage label values: `volume` (volume migration) or `resource` (resource migration).

stork_migration_duration_secondsHistogramcluster, namespace, clusterpair, schedule, stageTotal time taken by a migration in seconds.

stork_migration_resourcesGaugecluster, name, namespace, clusterpair, schedule, stateCount of resources collected for migration (state: planned or migrated).

stork_migration_volumesGaugecluster, name, namespace, clusterpair, schedule, stateVolumes planned for migration (state: planned or migrated).

stork_migration_created_totalCountercluster, namespace, schedule, clusterpairIncrements when a migration is created.

stork_migration_completed_totalCountercluster, namespace, schedule, status, clusterpairIncrements when a migration reaches a terminal state (Successful, Failed, or PartialSuccess).

stork_migration_transfer_rateGaugecluster, name, namespace, clusterpair, scheduleData transfer rate for a single migration (bytes/second).

stork_migration_transferred_bytesHistogramcluster, namespace, schedule, clusterpairTotal bytes transferred during a single migration.

stork_migration_completion_timestamp_secondsGaugecluster, namespace, schedule, status, clusterpairTimestamp when the latest migration completed for a schedule with the status being Successful, PartialSuccess, or Failed.

### Migration schedule metrics​

MetricTypeLabelsDescription

stork_migration_schedule_statusGaugecluster, name, namespace, clusterpair, statusStatus of migration schedules.

stork_migration_schedule_last_run_statusGaugecluster, name, namespace, clusterpair, statusStatus of the latest run of each migration schedule.

### Action metrics (Failover/Failback)​

MetricTypeLabelsDescription

stork_action_statusGaugecluster, type, name, namespace, schedule, statusStatus of Failover or Failback actions.

stork_action_created_totalCountercluster, type, namespace, scheduleIncrements when a Failover/Failback action is created.

stork_action_completed_totalCountercluster, type, namespace, schedule, statusIncrements when a Failover/Failback action reaches a terminal state.

stork_action_completion_timestamp_secondsGaugecluster, type, name, namespace, schedule, statusTimestamp when a Failover/Failback action completes with the status as Successful, Failed, RollbackSuccessful, or RollbackFailed.

### ClusterPair metrics​

MetricTypeLabelsDescription

stork_clusterpair_scheduler_statusGaugename, namespaceStatus of the cluster pair's health with respect to Kubernetes (0 = NotCreated, 1 = NotReady, 2 = Ready, 3 = Error, 4 = Degraded, 5 = Deleting, 6 = NotProvided, 7 = Paused, 8 = Unknown, 9 = MaintenanceMode).

stork_clusterpair_storage_statusGaugename, namespaceStatus of the cluster pair's health with respect to storage provisioner (0 = NotCreated, 1 = NotReady, 2 = Ready, 3 = Error, 4 = Degraded, 5 = Deleting, 6 = NotProvided, 7 = Paused, 8 = Unknown, 9 = MaintenanceMode).

### Namespace metrics​

MetricTypeLabelsDescription

stork_all_namespacesGaugeclusterNumber of namespaces in the Kubernetes cluster, including Kubernetes system namespaces.

stork_protected_namespacesGaugeclusterCount of namespaces being migrated through active migration schedules.

### Stork Scheduler metrics​

MetricTypeLabelsDescription

stork_hyperconverged_pods_totalGaugepod, namespaceNumber of pods scheduled on a node where replicas for all pod volumes exist (hyper-converged by the Stork scheduler).

stork_non_hyperconverged_pods_totalGaugepod, namespaceNumber of pods not hyper-converged by the Stork scheduler.

stork_semi_hyperconverged_pods_totalGaugepod, namespaceNumber of pods partially hyper-converged (scheduled on nodes with some but not all volume replicas).

stork_pods_rescheduled_totalCounterThe total number of pods rescheduled by the Stork Pod Monitor.

#### Notes​

- Stork Scheduler metrics are exported from all Stork pods because scheduling requests can reach any pod.

- DR metrics are exported only from the Stork leader pod.

- For metrics where status or stage is a label (such as `stork_migration_status` or `stork_action_status`), the label represents the actual state, and the metric value is always `1` when present.

In this topic:
