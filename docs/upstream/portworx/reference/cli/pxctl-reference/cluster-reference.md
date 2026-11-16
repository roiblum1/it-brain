# pxctl cluster

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/pxctl-reference/cluster-reference (Portworx Enterprise latest)

pxctl cluster | Portworx Enterprise Documentation

## pxctl cluster

```

pxctl cluster

```

#### Description

Manage the cluster

## pxctl cluster list

```

pxctl cluster list

```

#### Description

List nodes in the cluster

## pxctl cluster inspect

```

pxctl cluster inspect

```

#### Description

Inspect a node

## pxctl cluster delete

```

pxctl cluster delete <required-argument>

```

#### Description

Delete a node

#### Example

```

/opt/pwx/bin/pxctl cluster delete [flags] nodeID

```

#### Flags

FlagDescription

`--force`, `-f`

(`bool`)

Forcibly remove node, which may cause volumes to be irrevocably deleted

## pxctl cluster domains

```

pxctl cluster domains

```

#### Description

A set of commands to manage Portworx Cluster Domains

## pxctl cluster domains show

```

pxctl cluster domains show

```

#### Description

Lists all cluster domains

## pxctl cluster domains activate

```

pxctl cluster domains activate

```

#### Description

Activates the provided cluster domain

#### Flags

FlagDescription

`--name`, `-n`

(`str`)

name of the domain to activate

This flag is required.

## pxctl cluster domains deactivate

```

pxctl cluster domains deactivate

```

#### Description

Deactivates the provided cluster domain

#### Flags

FlagDescription

`--name`, `-n`

(`str`)

name of the domain to activate

This flag is required.

## pxctl cluster provision-status

```

pxctl cluster provision-status

```

#### Description

Show cluster provision status

#### Flags

FlagDescription

`--io_priority`

(`str`)

IO Priority
Valid values:

- `high`

- `medium`

- `low`

Default value: `low`

`--show-labels`

(`bool`)

Show all labels

## pxctl cluster token

```

pxctl cluster token

```

#### Description

Manage cluster authentication token

## pxctl cluster token show

```

pxctl cluster token show

```

#### Description

Display current authentication token

#### Flags

FlagDescription

## pxctl cluster token reset

```

pxctl cluster token reset

```

#### Description

Reset token if already present

## pxctl cluster pair

```

pxctl cluster pair

```

#### Description

Manage Portworx cluster pairs

## pxctl cluster pair create

```

pxctl cluster pair create

```

#### Description

Pair this cluster with another Portworx cluster

#### Flags

FlagDescription

`--ip`, `-i`

(`str`)

IP address of the remote cluster

This flag is required.

`--remote-port`, `-p`

(`uint`)

Port of the remote cluster

Default value: `9001`

`--token`, `-t`

(`str`)

Authentication token from the remote cluster

This flag is required.

`--default`, `-d`

(`bool`)

Set as the default cluster pair

`--dr-mode`

(`bool`)

Enable DR mode for the cluster pair

## pxctl cluster pair delete

```

pxctl cluster pair delete

```

#### Description

Delete a cluster pair

#### Flags

FlagDescription

`--id`, `-i`

(`str`)

ID of the remote cluster

This flag is required.

## pxctl cluster pair list

```

pxctl cluster pair list

```

#### Description

List the cluster pairs

## pxctl cluster pair validate

```

pxctl cluster pair validate

```

#### Description

Validate a cluster pair

#### Flags

FlagDescription

`--id`, `-i`

(`str`)

ID of the remote cluster

This flag is required.

## pxctl cluster options

```

pxctl cluster options

```

#### Description

List and update cluster wide options

## pxctl cluster options list

```

pxctl cluster options list

```

#### Description

List cluster wide options

## pxctl cluster options update

```

pxctl cluster options update

```

#### Description

Update cluster wide options

#### Flags

FlagDescription

`--auto-decommission-timeout`

(`uint`)

Timeout (in minutes) after which storage-less nodes will be automatically decommissioned. Timeout cannot be set to zero.

Default value: `20`

`--license-expiry-check`

(`uint`)

Number of `days` to raise alert before license expires. Set to zero to disable alerts.

Default value: `7`

`--license-expiry-check-interval`

(`str`)

Interval for license expiry checks. Valid only if 'license-expiry-check' is defined.

Default value: `6h`

`--internal-snapshot-interval`

(`uint`)

Interval (in minutes) after which internal snapshots are rotated

Default value: `30`

`--snapshot-create-timeout`

(`uint`)

Timeout (in minutes) to wait for a snapshot to complete in the backend

Default value: `20`

`--default-rpc-timeout`

(`int`)

Default RPC timeout (in minutes) for all client communications

Default value: `5`

`--repl-move-timeout`

(`uint`)

Timeout (in minutes) after which offline replicas will be moved to available nodes. Set timeout to zero to disable replica move.

Default value: `1440`

`--fb-lock-timeout`

(`uint`)

Timeout (in minutes) for which the kvdb lock will be held during FB create volume call. minimum duration 3 mins.

Default value: `3`

`--auto-cordon-pool-timeout`

(`uint`)

Timeout (in minutes) after which offline pool will be drained and AutoCordoned. Set timeout to zero to disable. Example: --auto-cordon-pool-timeout=30 will trigger the autocordon workflow if the node remains in StorageDown state for 30 mins.

`--fb-stats-expiry-duration`

(`uint`)

Duration (in minutes) after which cached stats for FB volumes will expire. minimum duration 1 min.

Default value: `15`

`--re-add-wait-timeout`

(`uint`)

Timeout (in minutes) after which re-add will abort and new replication node is added instead. Set timeout to zero to disable replica move.

Default value: `1440`

`--repl-move-timestamp-records-threshold`

(`uint`)

Timestamp record threshold after which offline replicas will be moved to available nodes. Set threshold to zero to disable replica move.

Default value: `134217728`

`--domain-policy`

(`str`)

Domain policy for domains
Valid values:

- `strict`

- `eventual`

Default value: `strict`

`--metro-dr-domain-protection`

(`str`)

Enable or disable Metro DR domain protection
Valid values:

- `on`

- `off`

Default value: `on`

`--stats-dump-interval-seconds`

(`int`)

Frequency of dumping stats in seconds.

Default value: `120`
Valid range:
30 3600

`--stats-dump-num-files`

(`int`)

Number of stats dump files to keep. Setting to 0 disables the periodic dumps.

Default value: `10`
Valid range:
0 100

`--default-io-profile`

(`str`)

Default IO-Profile for volumes
Valid values:

- `auto`

- `none`

Default value: `none`

`--optimized-restores`

(`str`)

Enable or disable optimized restores
Valid values:

- `on`

- `off`

Default value: `off`

`--cloudsnap-abort-timeout-minutes`

(`uint`)

Timeout in minutes for stalled cloudsnap abort. Should be => 10 minutes

Default value: `10`

`--cloudsnap-cleanup-failed-hours`

(`uint`)

Time in hours after which the failed cloudsnaps are deleted for a configured credential. 0 disables deleting failed cloudsnaps

`--cloudsnap-max-threads`

(`uint`)

Number of cloudsnap threads doing concurrent uploads/downloads. Valid values >= 2 and <= 16, others automatically rounded

Default value: `16`

`--cloudsnap-catalog`

(`str`)

Enable or disable cloudsnap catalog collection
Valid values:

- `on`

- `off`

Default value: `off`

`--cloudsnap-err-retry-limit`

(`uint`)

Retry limit on error for cloudsnap operations with objectstore.

Default value: `3`
Valid range:
1 15

`--cloudsnap-volumediff-batch-size`

(`uint`)

Batch size for volume diff request for cloudsnap

Default value: `10`
Valid range:
1 100

`--uniqueblocks-size-sched-interval-minutes`

(`uint`)

Configure periodic interval (in minutes) to query unique blocks size for volumes.

Default value: `720`

`--io-profile-derive-interval`

(`uint`)

Configure periodic interval (in seconds) to compute the IO profile for volume. Only applies to volumes with \"auto_journal\" IO profile.

Default value: `20`

`--disable-provisioning-labels`

(`str`)

Semi-colon separate string of labels, example 'node=uuid1,uuid2;io_priority=high'. Use '' to reset to default.

`--provisioning-commit-labels`

(`str`)

Json, example of global rule followed by node specific and pool specific rule: '[{'OverCommitPercent': 200, 'SnapReservePercent': 30},{'OverCommitPercent': 50, 'SnapReservePercent':30, 'LabelSelector':{'node':'node-1,node-2', 'poolLabel':'poolValue'},]'. Use '[]' to reset to default.

`--sharedv4-threads`

(`uint`)

Initial number of sharedv4 threads in the dynamic NFS thread pool. The number of threads will dynamically increase based on the load of the NFS server. This will affect sharedv4 volume performance as well as the amount of CPU and memory consumed for handling sharedv4 volumes.

Default value: `128`

`--max-sharedv4-threads`

(`uint`)

Maximum number of sharedv4 threads in the dynamic NFS thread pool. This will affect sharedv4 volume performance as well as the amount of CPU and memory consumed for handling sharedv4 volumes.

Default value: `2048`

`--sharedv4-mount-timeout-sec`

(`uint`)

Timeout in seconds for sharedv4 (NFS) mount commands.

Default value: `120`

`--sharedv4-attachment-limit`

(`uint`)

Maximum number of Sharedv4 attachments allowed on node.

Default value: `256`

`--sharedv4-sentinel-cleanup-timeout-sec`

(`uint`)

Timeout in seconds for sharedv4 sentinel mount cleanup. Valid range [0, 86400]. Values above the maximum are reset to the default (0s).

`--sharedv4-sentinel-cleanup-interval-sec`

(`uint`)

Interval in seconds for sharedv4 sentinel mount cleanup. Valid range [60, 3600]; 0 is also valid and means 'use the default interval (300s)' -- it does not disable the background cleanup task. Non-zero values outside the range are reset to the default (300s).

`--px-http-proxy`

(`str`)

proxy to be used by cloudsnap (setting not required if using PX_HTTP_PROXY/PX_HTTPS_PROXY env. variables)

`--cloudsnap-nw-interface`

(`str`)

network interface name used by cloudsnaps(data, mgmt, eth0, etc)

`--runtime-options`

(`str`)

Comma separated key value pairs for runtime options

`--runtime-options-action`

(`str`)

Specify type of action for runtime options
Valid values:

- `update-global`

- `delete-global`

- `update-node-specific`

- `delete-node-specific`

Default value: `update-global`

`--runtime-options-selector`

(`str`)

Comma separated key value labels for node specific runtime options.

`--snapshot-schedule-option`

(`str`)

for detached volumes none will not generate schedule snapshots, optimized will generated one, always will generate them always
Valid values:

- `none`

- `always`

- `optimized`

Default value: `optimized`

`--concurrent-api-limit`

(`uint`)

Maximum number of concurrent api invocations allowed

Default value: `20`

`--cache-flush`

(`str`)

Enable periodic cache flush
Valid values:

- `enabled`

- `disabled`

Default value: `disabled`

`--cache-flush-seconds`

(`uint`)

Interval at which cache flush would be performed.

Default value: `30`

`--poolcache`

(`str`)

Disable, or enable with a minimum and maximum dirty block percentage in cache. (Valid Range: [10 90]). e.g. on,33,67

`--volume-expiration-minutes`

(`uint`)

Expiration (in minutes) is the time the volume stays in trashcan before being purged.

`--cloudsnap-full-backup-frequency`, `-b`

(`uint`)

Sets the full backup frequency.

Default value: `7`
Valid range:
1 120

`--cloudsnap-using-metadata-enabled`

(`str`)

Enable cloudsnap using metadata optimization
Valid values:

- `on`

- `off`

Default value: `on`

`--cloudsnap-metadata-upload-percent-limit`

(`uint`)

Do not use cloudsnap using metadata optimization if metadata size is over this limit in percent with respect to upload size. Value set to 0 disables this check.

Default value: `15`

`--cloudsnap-metadata-upload-mb-bytes-limit`

(`uint`)

Do not use cloudsnap using metadata optimization if metadata size is over this limit in size in mebibytes. Value set to 0 disables this check.

Default value: `10240`

`--lttng-cmd`

(`str`)

Lttng command to execute
Valid values:

- ``

- `start`

- `stop`

- `pause`

- `resume`

`--lttng-disk-usage`

(`uint`)

Amount of disk space (GB) to be utilized by lttng trace files. Greater than 0 enables traces and 0 disables it

`--fstrim-schedule-start`

(`str`)

Start fstrim on a scheduled time (UTC). Example:daily=hh:mm or weekly=weekday@hh:mm. Autofstrim will be disabled in cluster.

`--fstrim-schedule-duration`

(`int`)

Duration of scheduled fstrim in hours. Daily limit is [1, 23] hrs and weekly limit is [1, 167] hrs.

`--fstrim-max-io-rate`

(`str`)

Maximum throughput (KiB, MiB or GiB) at which fstrim would free blocks to backing store, in each interval. Max value = 10GiB

Default value: `32MiB`

`--lttng-log-level`

(`str`)

Lttng loglevel setting
Valid values:

- `err`

- `emerg`

- `alert`

- `debug_unit`

- `debug_line`

- `unset`

- `debug_function`

- `debug_module`

- `debug_process`

- `debug_system`

- `notice`

- `debug_program`

- `debug`

- `warning`

- `info`

- `crit`

Default value: `unset`

`--lttng-blocking-timeout-us`

(`str`)

LTTng channel blocking timeout in microseconds. When buffers are full, the application blocks for up to this duration before discarding the event. 0=non-blocking (default, discard immediately), inf=block forever until space is available. Only applies to discard mode user space channels. Requires LTTNG_UST_ALLOW_BLOCKING=1 in the traced application.

Default value: `0`

`--lttng-sub-buf-num`

(`uint`)

Number of sub-buffers per LTTng channel ring buffer. Rounded up to the next power of two. More sub-buffers reduce the risk of event loss in overwrite mode but increase memory usage. Each channel uses (sub-buf-num * sub-buf-sz-kb * num_cpus * 2) KB of shared memory.

Default value: `2`

`--lttng-sub-buf-sz-kb`

(`uint`)

Individual size of each LTTng channel sub-buffer in KB. Rounded up to the next power of two. Larger sub-buffers reduce sub-buffer switching overhead and lower the risk of event loss under high throughput, but increase memory usage.

Default value: `1024`

`--fstrim-min-io-rate`

(`str`)

Minimum throughput (KiB, MiB or GiB) at which fstrim would free blocks to backing store, in each interval. Min value = 1MiB

Default value: `1MiB`

`--defrag-schedule-chunk-size`

(`uint`)

Chunk size (MB) of each defrag command issued by the defrag schedule

Default value: `32`
Valid range:
10 1024

`--defrag-schedule-pool-full-threshold`

(`uint`)

Pool used space percentage threshold above which defrag would be disabled on pools

Default value: `70`
Valid range:
1 100

`--skinnysnap`

(`str`)

Enable/Disable SkinnySnaps. Allows snapshots to be created with lower number of replicas than the parent volume.
Valid values:

- `on`

- `off`

Default value: `off`

`--skinnysnap-num-repls`

(`int`)

Skinnysnap Replication factor. If this value is same or greater than the volume replication level, number of snapshot replicas will be equal to the number of parent volume replicas.
Valid values:

- `1`

- `2`

- `3`

Default value: `1`

`--cloudsnap-network-limit-cluster`

(`uint`)

Cluster-wide average network bandwith usage limit in mebibytes per second, use 0 to disable this limit

`--relaxedreclaim-delete-seconds`

(`uint`)

The number of seconds to wait before deleting the volume/snapshot staged in RelaxedReclaim queue. Set to zero to disable RelaxedReclaim.

`--relaxedreclaim-max-pending`

(`uint`)

Maximum number of volumes/snapshots that can be staged for RelaxedReclaim.

Default value: `256`

`--auto-fstrim`

(`str`)

Enable/Disable automatic fstrim
Valid values:

- `on`

- `off`

Default value: `off`

`--fstrim-io-rate`

(`uint`)

Maximum throughput (in MBytes) at which fstrim would free blocks to backing store, in each interval(fstrim-io-rate-interval). Minimum is 10MB

Default value: `100`

`--fstrim-io-rate-interval`

(`uint`)

Internal(in seconds) associated with the fstrim-io-rate(MB) is freed to backing store. Minimum 1 second.

Default value: `1`

`--incremental-uploads-disabled`

(`str`)

Disable Pure1 incremental uploads of PX information
Valid values:

- `true`

- `false`

`--incremental-uploads-interval-mins`

(`int`)

Interval for Pure1 incremental uploads of PX information.

Default value: `30`

`--pure1-trace-upload`

(`str`)

Enable or disable Pure1 trace upload
Valid values:

- `true`

- `false`

Default value: `false`

`--pure1-core-upload`

(`str`)

Enable or disable Pure1 core upload
Valid values:

- `true`

- `false`

Default value: `false`

`--large-file-upload-interval-hours`

(`int`)

Interval in hours for Pure1 large file uploads (traces, cores)

Default value: `4`

`--migrate-legacy-shared-to-sharedv4-service`

(`str`)

Migrate legacy shared volumes to sharedv4 service volumes
Valid values:

- `false`

- `true`

`--kvdb-defrag-frequency-in-hours`

(`uint`)

Interval in hours at which a kvdb defrag will be run.

Default value: `336`
Valid range:
1 8760

`--min-kvdb-defrag-limit-mb`

(`uint`)

KVDB database size threshold (in MB) to trigger a defragmentation, regardless of the configured defrag frequency.

Default value: `2048`
Valid range:
100 8192

`--cloud-drive-locking`

(`bool`)

Enable or disable cloud drive resource locking. When enabled, PX creates locks on cloud disks to prevent accidental deletion. Currently only supported on Azure. Disable this before K8s cluster upgrades or nodepool operations and re-enable after completions. Valid values [true, false].

`--cloud-drive-locking-disable-for-hours`

(`uint`)

Temporarily disable cloud drive locking for specified hours. Valid range 1-168 hours (7 days). Can only be set when cloud-drive-locking is enabled. After the duration, locking will be automatically re-enabled.

`--bounce-pods-for-ro-vol`

(`str`)

Bounce app pods if a rw volume mount turns read-only. Default behavior is to look at all volume mounts.
Valid values:

- `fada`

- `all`

Default value: `all`

`--ro-vol-pod-bounce-interval`

(`uint`)

Interval (in seconds) at which the background task should check for read-only (ro) volume mounts which were supposed to be read-write (rw), so it can bounce pods using such volumes.

Default value: `15`

`--fastpath-protocol`

(`str`)

Cluster-wide fastpath protocol. When set, overrides the protocol configured at px-runc installation time on each node. (Valid Values: [local nvmeof-tcp])

Default value: `local`

`--flasharray-iscsi-allowed-ifaces`

(`str`)

Allowed iSCSI interfaces that can be used to connect to FlashArrays. Empty means all interfaces are allowed. Values must appear in output of 'iscsiadm -m iface'

`--enable-sharedv4-nfs-negotiation`

(`str`)

Enable NFS version negotiation for sharedv4 RWX mounts (probe 4.0 -> 4.1 -> 4.2). 4.1/4.2 do not preserve seamless failover.
Valid values:

- `true`

- `false`

`--fix-vps-frequency-in-minutes`

(`int`)

Interval in minutes at which a job to fix VPS will be run. Set to 0 to disable the job.

Default value: `15`

`--svmotion-interval`

(`uint`)

Storage vMotion (vSphere only) API timeout (minutes) interval. Disable job with value 0.

Default value: `15`

`--readahead`

(`str`)

Enable or disable readahead
Valid values:

- `on`

- `off`

Default value: `on`

`--failover-cleanup-retention-hours`

(`uint`)

Hours to retain pool failover history before automatic cleanup. Set to 0 to disable cleanup. Older pool failover records are automatically removed to free KVDB space.

Default value: `12`

`--max-active-failover-nodes`

(`uint`)

Maximum number of nodes that can be undergoing failover simultaneously. This limits concurrent node failovers to prevent cluster instability.

Default value: `5`

`--max-active-failover-pools`

(`uint`)

Maximum number of pool failover plans that can be active simultaneously across all node failover intents. Intent creation is rejected if active plans plus incoming pools would exceed this limit. Default is 16.

Default value: `16`
Valid range:
1 32

`--pause-pool-failovers`

(`bool`)

Pause or unpause pool failover across the cluster. When paused (true), no new pool failover intents will be created. When unpaused (false), normal pool failover operations will resume. Valid values [true, false].

`--disable-pool-failover-reboot-trigger`

(`bool`)

Disable or enable pool failover triggered by node reboot/shutdown. When disabled (true), the systemd-logind shutdown inhibitor will still run but failover intents with trigger Reboot will be rejected. Other triggers (NodeDown, Upgrade, CLI, Rebalance) are unaffected. Valid values [true, false].

`--pause-dynamic-pool-rebalance`

(`bool`)

Pause or unpause dynamic pool rebalancing across the cluster. When paused, automatic movement of storage pools between nodes is disabled. Only takes effect when enableDynamicPools is set to true. Valid values [true, false].

`--dynamic-pool-rebalance-min-interval-secs`

(`uint`)

Minimum interval (seconds) between dynamic pool rebalance cycles. Used during severe imbalance. Only takes effect when enableDynamicPools is set to true.

Default value: `300`

`--dynamic-pool-rebalance-default-interval-secs`

(`uint`)

Default interval (seconds) between dynamic pool rebalance cycles. Used during normal operation. Only takes effect when enableDynamicPools is set to true.

Default value: `900`

`--dynamic-pool-rebalance-max-interval-secs`

(`uint`)

Maximum interval (seconds) between dynamic pool rebalance cycles. Used when cluster is nearly balanced. Only takes effect when enableDynamicPools is set to true.

Default value: `1800`

`--dynamic-pool-rebalance-tolerance-percent`

(`uint`)

Threshold for considering the cluster balanced. If no node's pool count differs from the average by more than this percentage, dynamic pool rebalancing is skipped. Only takes effect when enableDynamicPools is set to true.

Default value: `50`
Valid range:
1 99

`--dynamic-pool-rebalance-severe-imbalance-percent`

(`uint`)

Use min-interval when max deviation exceeds this percent. Only takes effect when enableDynamicPools is set to true.

Default value: `200`
Valid range:
100 10000

`--dynamic-pool-rebalance-moderate-imbalance-percent`

(`uint`)

Use default-interval when max deviation exceeds this percent. Only takes effect when enableDynamicPools is set to true.

Default value: `99`
Valid range:
50 99

`--dynamic-pool-rebalance-max-moves-per-cycle`

(`uint`)

Maximum pool moves per dynamic pool rebalance cycle. Higher values speed convergence but increase complexity. Only takes effect when enableDynamicPools is set to true.

Default value: `1`
Valid range:
1 5

`--suspect-down-probe-enabled`

(`str`)

Enable or disable fast detection of unresponsive nodes. When disabled, node-down detection falls back to the slower gossip path. Only takes effect when enableDynamicPools is true.
Valid values:

- `true`

- `false`

Default value: `true`

`--otel-endpoint`

(`str`)

OTLP gRPC endpoint for distributed tracing. Set to 'localhost:4317' to enable tracing via a local OTel Collector. Set to '' to disable. Changes take effect on all nodes without restart.

`--non-disruptive-pool-resize`

(`str`)

Set to true to enable non-disruptive pool resize for Store-V2 pools. When true, pool resize uses the non-disruptive online resize flow. When false, pool resize falls back to the legacy behavior of entering maintenance mode and restarting PX.
Valid values:

- `true`

- `false`

Default value: `true`

`--diag-redaction-enabled`

(`str`)

Enable secret redaction in diags collection
Valid values:

- `true`

- `false`

Default value: `true`

`--diag-base64-redaction-enabled`

(`str`)

Enable base64 secret redaction in diags collection
Valid values:

- `true`

- `false`

## pxctl cluster defrag

```

pxctl cluster defrag

```

#### Description

File system defragmentation

## pxctl cluster defrag schedule

```

pxctl cluster defrag schedule

```

#### Description

Schedule of defragmentation job

## pxctl cluster defrag schedule create

```

pxctl cluster defrag schedule create

```

#### Description

Create a defrag schedule

#### Example

```

pxctl cluster defrag schedule create --start-time daily=19:15 --max-duration-minutes 90

```

#### Flags

FlagDescription

`--start-time`

(`str`)

Define the scheduled time to start running defrag tasks. Valid formats: daily=19:15, weekly=Sunday@19:15, monthly=22@19:15

This flag is required.

`--max-duration-minutes`

(`uint`)

Define how many minutes the individual defrag job should run

This flag is required.

`--max-nodes-in-parallel`

(`uint`)

Define the maximum number of nodes allowed to run defrag tasks in parallel

Default value: `1`

`--include-nodes`

(`str`)

Comma-separated node uuids to specify the list of nodes run by this schedule. If empty, run on all nodes. Cannot coexist with --exclude-nodes and --node-selector

`--exclude-nodes`

(`str`)

Comma-separated node uuids to specify the list of nodes skipped by this schedule. Cannot coexist with --include-nodes

`--node-selector`

(`str`)

Comma-separated label selectors of the form label1=value1,label2=value2 etc., to specify the list of nodes run by this schedule. Can coexist with --exclude-nodes but cannot coexist with --include-nodes

`--one-iteration-only`

(`bool`)

After running one iteration on all nodes, the schedule will be automatically deleted

`--include-volumes`

(`str`)

Comma-separated volume ids to specify the list of volumes to run defrag on by this schedule. If empty, run on all volumes. Cannot coexist with --exclude-volumes

`--exclude-volumes`

(`str`)

Comma-separated volume ids to specify the list of volumes skipped by this schedule. Cannot coexist with --include-volumes

## pxctl cluster defrag schedule show

```

pxctl cluster defrag schedule show

```

#### Description

Show defrag schedules in the system

#### Example

```

pxctl cluster defrag schedule show --schedule-id <schedule-id>

```

#### Flags

FlagDescription

`--schedule-id`

(`str`)

Schedule ID

## pxctl cluster defrag schedule delete

```

pxctl cluster defrag schedule delete <required-argument>

```

#### Description

Delete a defrag schedule

#### Example

```

pxctl cluster defrag schedule delete <schedule-id>

```

#### Flags

FlagDescription

## pxctl cluster defrag schedule clean-up

```

pxctl cluster defrag schedule clean-up

```

#### Description

Clean up defrag schedules and jobs

#### Example

```

pxctl cluster defrag schedule clean-up

```

#### Flags

FlagDescription

## pxctl cluster defrag status

```

pxctl cluster defrag status

```

#### Description

Show defragmentation status

#### Example

```

pxctl cluster defrag status --node <node-uuid>

```

#### Flags

FlagDescription

`--node`

(`str`)

Node UUID
