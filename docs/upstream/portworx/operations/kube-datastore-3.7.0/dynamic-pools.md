# Dynamic Pool Failover for Portworx Enterprise 3.7.0

Source: https://docs.portworx.com/portworx-enterprise/operations/kube-datastore-3.7.0/dynamic-pools (Portworx Enterprise latest)

Dynamic Pool Failover for Portworx Enterprise 3.7.0 | Portworx Enterprise Documentation

important

Kube Datastore (KDS) dynamic pools was available under Directed Availability (DA) in Portworx Enterprise 3.7.0 and is now generally available (GA) in version 3.7.2. Upgrade to Portworx Enterprise 3.7.2 to access additional capabilities, including higher scale limits, compute-aware placement and hyperconvergence, and fastpath support on dynamic pools.

For more information, see Kube Datastore for Portworx Enterprise 3.7.2 and Set Up KDS Dynamic Pools on a Portworx Cluster.

Dynamic pool failover allows Portworx to move eligible storage pools between Kubernetes nodes during node failures, maintenance, upgrades, and administrator-initiated operations. During relocation, Portworx detaches the pools from the source node and attaches it to a healthy node.

This topic describes how dynamic pools in Kube Datastore (KDS) fail over to healthy nodes, how Portworx Enterprise selects destination nodes and rebalances pools, and how to enable and manually migrate dynamic pools in Portworx Enterprise 3.7.0.

## Dynamic pool failover and node selection​

Dynamic pools with `repl=1` volumes can fail over to any node in the cluster. The only exception is nodes explicitly marked as `storageless`, which are not eligible to host storage in a disaggregated cluster.

During failover, Portworx Enterprise automatically migrates the affected pool to a healthy node without restarting the Portworx service and without interrupting application I/O. This applies to both planned maintenance events and unplanned node failures. As a result, volumes remain available and workloads continue running with minimal disruption.

A coordinator node manages the failover process. It monitors node health and orchestrates pool migration by selecting a suitable destination node based on the volume placement strategy, failure domain, attached volume replica count, and overall node health. If the coordinator node fails shortly after a storage node failure, failover timing may be further delayed. For more information on how a node is selected for migration, see Node selection during pool migration.

Pool failover operations are retried automatically up to three times if they fail. If all retries fail, manual intervention may be required. After the underlying issue is resolved, triggering failover again typically restores normal operation.

If multiple pools fail over at the same time, each pool migrates independently. Portworx Enterprise manages pool migration using the node selection criteria described in Node selection during pool migration. Based on these criteria, pools may migrate to the same node or to different nodes.

After a pool fails over to a new node, it does not automatically fail back to the original node. Portworx Enterprise rebalances and redistributes the pool based on cluster imbalance conditions. For more information, see Dynamic pool rebalance.

note

- During VM deployments, Portworx Enterprise attempts to co-locate cloned PVCs (for example, those created from golden images) and data drives on the same storage pool. To achieve this placement, Portworx Enterprise temporarily performs a high-availability (HA) update that increases the replica count and then reduces it after the placement completes. This operation typically occurs shortly after VM creation. Pool failover is temporarily blocked during the brief window when these HA operations are in progress.

- When both pool resize and pool failover operations are triggered, the operation that starts first takes precedence. The other operation remains blocked until the first operation completes.

### Dynamic pool failover scenarios​

Portworx Enterprise supports automatic pool migration in several scenarios:

-
Unexpected node failure - When a node fails unexpectedly, Portworx Enterprise detects the failure and automatically migrates the affected pools to healthy nodes. Applications using `repl=1` volumes continue running without interruption.
During unexpected outages, failover timing depends on how quickly the FlashArray storage backend detects that the connection to the failed node is lost. If volumes are remotely attached to virtual machines, a delayed failover can cause disk I/O timeout events.

-
Planned maintenance or upgrades - During planned node maintenance, or upgrades, Portworx Enterprise receives a notification from the orchestrator or administrator about any node-related activity. Portworx Enterprise pre-migrates pools from the affected node, allowing upgrades to proceed without impacting application availability.
Planned operations such as OpenShift upgrades or CLI-triggered pool migrations typically complete without downtime.

-
Manual pool migration - You can also manually migrate a pool to another node for maintenance or optimization. For more information, see Manual migration of dynamic pools.

### Fast node-down detection for dynamic pool failover​

Portworx Enterprise uses fast node-down detection to reduce dynamic pool failover time during unexpected node failures.

When a peer node enters a suspect state, Portworx Enterprise performs additional liveness and cluster-safety checks instead of waiting for the standard membership suspicion timeout. If these checks confirm that the node is unavailable, Portworx Enterprise typically initiates dynamic pool failover within 7 to 12 seconds.

Before marking a node as down, Portworx Enterprise performs the following additional checks:

- Verifies that the peer node remains in the suspect state.

- Checks the cluster view to protect against network partitions.

- Verifies that the surviving node can communicate with another healthy node.

- Probes an independent host-level liveness endpoint on the affected node.

If these checks cannot confirm that the node is unavailable, Portworx Enterprise uses the standard node-down detection mechanism instead.

Fast node-down detection uses a host-level liveness service to verify node availability independently of the Portworx service. For OpenShift deployments, ensure that TCP port `17024` is open between all Portworx nodes. Network policies, host firewalls, security groups, and other network controls must allow node-to-node traffic on this port for fast node-down detection to function. Port `17024` is required in addition to the existing Portworx communication ports. For more information, see Network requirements.

note

When upgrading a cluster with dynamic pools enabled, the liveness service starts as each node is upgraded, which might trigger unintended pool failovers. To prevent these failovers, pause dynamic pool failover before starting the upgrade:

```

pxctl cluster options update --pause-pool-failovers=true

```

After the upgrade completes on all nodes, resume dynamic pool failover:

```

pxctl cluster options update --pause-pool-failovers=false

```

### Early failover intent on node reboot or shutdown​

When a node is rebooted or shut down, Portworx Enterprise uses a `systemd-logind` delay inhibitor to detect the event and attempts to record the pool failover intent in KVDB before the node goes down.

When the intent is recorded successfully, the surviving nodes can start pool migration immediately instead of waiting for the node-expiry timeout. This reduces dynamic pool failover time during planned node reboots and shutdowns.

This mechanism is best-effort. If Portworx Enterprise cannot record the failover intent before the node goes down, fast node-down detection detects the node failure and triggers failover.

### Node selection during pool migration​

During pool migration, Portworx Enterprise selects a target node using a filtering and scoring process. This ensures that pools move only to suitable nodes and that workload impact is minimized.

#### Node filtering​

Portworx Enterprise first filters out nodes that do not meet the required criteria. A node is not considered for migration if it:

- Is in a different zone than the source node

- Is not in an UP state

- Is cordoned

- Is undergoing autoscaling

- Is in maintenance mode

- Does not have a metadata drive

- Has reached maximum pool capacity

- Has offline storage pools

Only nodes that pass all the above filtering checks are considered for migration.

#### Node scoring​

After filtering, Portworx Enterprise evaluates the remaining nodes and assigns a score based on the number of attached volume replicas. Nodes with fewer attached volume replicas receive a higher score. This helps distribute load evenly across the cluster and avoids overloading individual nodes. Portworx Enterprise selects the node with the highest score as the migration target.

note

Node selection is based primarily on attached volume replica counts. This approach may result in uneven pool distribution across nodes, as pool count per node is not considered during placement.

#### Exclude a node from pool migration​

To prevent Portworx Enterprise from selecting a specific node as the target for pool migration, cordon the node. Portworx excludes cordoned nodes when selecting targets for pool failover, rebalance, and manual migration.

Consider cordoning a node when:

- You migrate pools from one node to another and do not want Portworx to select the source node as a target for subsequent migrations.

- You plan to take a node down for maintenance and do not want Portworx to migrate additional pools to it.

To exclude a node from pool migration:

-
Cordon the node:

```

oc adm cordon <node-name>

```

Replace `<node-name>` with the name of the node to exclude.

-
Perform the pool migration or maintenance operation.

-
Uncordon the node to make it eligible for pool migration again:

```

oc adm uncordon <node-name>

```

note

Cordoning a node affects only its eligibility as a migration target. It does not migrate pools currently hosted on the node or prevent the node from serving as the source of a pool migration.

## Dynamic pool rebalance​

Dynamic pool rebalance automatically maintains a balanced distribution of eligible storage pools across nodes in a Portworx cluster. Over time, pool distribution can become uneven due to node failures, maintenance-driven migrations, or the addition of new nodes. Rebalance periodically evaluates the cluster and redistributes eligible pools to reduce imbalance and minimize workload impact during future failures.

Dynamic pool rebalance runs automatically in the background and evaluates pool distribution across nodes at regular intervals. It detects imbalance based on `repl=1` workload distribution and selects eligible pools for migration. Pool movement uses the same mechanism as dynamic pool failover and maintains the same availability guarantees. Portworx Enterprise adjusts how frequently rebalance runs based on the severity of imbalance.

note

- After a failover event, rebalance operations do not run immediately. A cooldown period of approximately 15 minutes is enforced before rebalance resumes.

- During an active rebalance operation, additional pool failover attempts from the same node are temporarily blocked until the rebalance completes.

- Rebalance does not perform automatic failback. Instead, it redistributes pools based on imbalance conditions.

- Rebalance triggers when a node exceeds 50% above the average replica count.

Cluster imbalance is determined by uneven distribution of `repl=1` workloads across nodes. Based on this distribution, Portworx Enterprise classifies cluster state into levels such as balanced, low, moderate, or severe imbalance and adjusts rebalance frequency accordingly.

Rebalance is triggered when a node exceeds the configured imbalance threshold based on the average number of attached volume replicas in the cluster. By default, this occurs when a node has more than 50% above the average attached volume replica count. Rebalance runs at an adaptive interval that depends on the degree of imbalance. Higher imbalance results in more frequent rebalance operations, while lower imbalance reduces the frequency. You can configure the imbalance threshold using runtime options. For more information, see Dynamic pool failover and rebalance runtime options.

A pool is eligible for rebalance only if it meets all of the following conditions:

- It has active (attached) volumes

- It is not currently undergoing failover

- Moving the pool does not violate placement constraints

- The source node retains at least one pool after migration

note

Dynamic pools containing unsupported volume types are not eligible for rebalance.

## Prerequisites​

Ensure that your cluster meets the following prerequisites before you enable dynamic pools:

- Portworx Enterprise version 3.6.0 or later is installed.

- Portworx Operator version 26.1.0 or later is installed.

- OpenShift version 4.18 or later is running.

- The cluster is deployed on FlashArray Cloud Drives (FACD).

- The cluster is deployed on PX-StoreV2.

- TCP port `17024` is open between Portworx nodes. Fast node-down detection uses this port for the host-level liveness service. For more information, see Fast node-down detection for dynamic pool failover.

## Limitations​

Before enabling dynamic pools, consider the following limitations:

-
Supported only on Pure FlashArray storage platform.

-
Supported only on OpenShift distribution.

-
Does not support Auto Journal Device.

-
Does not support Smart upgrade.
Portworx Enterprise limits the number of nodes and pools that can participate in a failover at a time and performing a smart upgrade can exceed these limits delaying failover operations.

-
Does not support multi-drive pools. Dynamic pools require exactly one FACD drive per pool. Clusters that already contain multi-drive pools cannot be upgraded to a dynamic pool enabled configuration.

-
Pool failover does not occur if the pool contains any of the following volume types:

- SharedV4 volumes

- Volumes with Journal profiles

- Volumes with replication factor greater than 1 (`repl=2` or higher)

- PX-Fast volumes

-
Pool failover is temporarily blocked on both source and target nodes during pool expansion operations. Failover resumes automatically after the expansion completes.

-
Pool failover fails if volume attach operations are in progress for volumes on the same pool.

-
Automatic VM re-alignment does not occur after pool migration. Virtual machines are not rebalanced to align with data locality.

-
Dynamic pools are validated for up to 5,000 volumes per cluster. Within this cluster-wide limit, Portworx validates the following per-node configurations:

- Single dynamic pool per node: Up to 256 volumes.

- Multiple dynamic pools per node: Up to four dynamic pools, with a maximum of 100 volumes per pool.
Portworx by Everpure recommends that you do not exceed 100 volumes per pool.

Exceeding these validated configurations might affect failover performance and workload I/O. On Windows VMs, it can also result in storage-related operating system events. Portworx by Everpure recommends staying within the validated configurations for consistent performance and reliability.

-
When you upgrade Portworx Enterprise, you can enable dynamic pools only if the cluster is already running Portworx Enterprise version 3.5.0 or later. If the cluster is running an earlier version, first upgrade to 3.6.0. After the upgrade, manually update the `StorageCluster` specification. For more information on how to update the `StorageCluster` specification, see Enable Dynamic Pools.

## Enable Dynamic Pools​

You can enable dynamic pools using the `StorageCluster` custom resource.

-
Generate the Portworx specification from Portworx Central.
Ensure that you select Pure FlashArray as the platform, PX-StoreV2 as the storage provider, and Openshift 4+ as the distribution.
For more information, see Installation of Portworx with FlashArray using Portworx Central.

-
In the `spec` section of the `StorageCluster`, configure dynamic pools and the storage provider:

```

spec:

  kubeDatastore:

    enableDynamicPools: true

  cloudStorage:

    provider: pure

```

-
Verify the configuration to confirm that the dynamic pools is enabled:

```

kubectl get stc -n portworx <pxcluster> -o jsonpath='{.spec.kubeDatastore}'

```

You should see an output similar to:

```

kubeDatastore:

  {“enableDynamicPools”:true}

```

-
Check the status of the `StorageCluster`:

```

kubectl get stc px-cluster -n portworx

```

The `STATUS` field should display `Updating` or `Running`.

important

If the `StorageCluster` status displays `Degraded`, you must check for errors and fix any issues before retrying to enable dynamic pools. To do this, perform the following steps:

-
Check the `StorageCluster` to identify the issue:

```

kubectl describe stc px-cluster -n portworx

```

Review the events and error messages to determine the cause.

-
Resolve the underlying issue identified in the previous step.

-
Reapply the configuration change if necessary:

```

kubectl apply -f <updated-storagecluster.yaml>

```

-
Verify that the StorageCluster status transitions to `Updating` and then to `Running`:

```

kubectl get stc px-cluster -n portworx

```

Dynamic pools are successfully enabled when the `enableDynamicPools` field is set to `true` and the `StorageCluster` status is `Running`.

note

When you enable dynamic pools, Portworx Enterprise automatically adds a metadata drive to all non-storageless nodes. This drive supports dynamic pool operations and remain fixed to the node and does not move during pool relocation.
If you disable dynamic pools, these metadata drives remain on the nodes. You must manually decommission these metadata-only nodes to remove them.

## Dynamic pool failover and rebalance runtime options​

The following table provides the runtime options that can be used to configure dynamic pool failover behavior and the imbalance threshold at runtime.

warning

Do not modify the runtime options unless necessary. Contact Portworx Support before changing the runtime options.

ParameterDescriptionDefault value

`pause-pool-failovers`Pauses dynamic pool failover. When enabled, automatic movement of storage pools between nodes is disabled.`false`

`pause-dynamic-pool-rebalance`Pauses dynamic pool rebalance. When enabled, automatic redistribution of pools is disabled. Applies only when dynamic pools are enabled.`false`

`failover-cleanup-retention-hours`Specifies how long failover-related metadata is retained before cleanup.`12h`

`max-active-failover-nodes`Specifies the maximum number of nodes that can participate in failover at a time.`5`

`max-active-failover-pools`Specifies the maximum number of pools that can participate in failover at a time.`16`

`dynamic-pool-rebalance-min-interval-secs`Specifies the minimum interval between rebalance cycles during severe imbalance conditions.`900`

`dynamic-pool-rebalance-default-interval-secs`Specifies the default interval used during moderate imbalance conditions.`1800`

`dynamic-pool-rebalance-max-interval-secs`Specifies the maximum interval between rebalance cycles during low or balanced conditions.`3600`

`dynamic-pool-rebalance-tolerance-percent`Specifies the threshold that defines when the cluster is considered balanced.`50`

`dynamic-pool-rebalance-moderate-imbalance-percent`Specifies the threshold that defines moderate imbalance in the cluster.`100`

`dynamic-pool-rebalance-severe-imbalance-percent`Specifies the threshold that defines severe imbalance in the cluster.`200`

`dynamic-pool-rebalance-max-moves-per-cycle`Specifies the maximum number of pool movements allowed in a single rebalance cycle.`1` (max `5`)

## Manual migration of dynamic pools​

During planned node upgrades, maintenance, or optimization, you can manually migrate all pools on a node, or select specific pools from that node to migrate individually.

-
To manually migrate all the pools in a node to another node:

```

pxctl service pool migrate --node <node-id>

```

Replace `<node-id>` with the id of the node that hosts the pools to migrate.

 Portworx automatically selects the destination node and relocates the pools without disrupting active workloads.

-
To migrate specific pools from a node to another node:

```

pxctl service pool migrate --node <node-id> [--pools <uuid1,uuid2>]

```

Replace:

- `<node-id>` with the id of the node that hosts the pools to migrate.

- `<uuid1,uuid2>` with the UUIDs of the pools to migrate. You can specify one or more pool UUIDs separated by commas.

 Portworx automatically selects the destination node and relocates the pools without disrupting active workloads.

-
To view all pool migration plans and intents in the cluster:

```

pxctl sv pool migrate list

```

-
To view only the pool migration plans in the cluster:

```

pxctl sv pool migrate list --plans

```

-
To view only the pool migration intents in the cluster:

```

pxctl sv pool migrate list --intents

```

-
To view only active migration intents in the cluster:

```

pxctl sv pool migrate list --active-only

```

-
To check the status of ongoing or completed pool migration operations:

```

pxctl sv pool migrate status [--source-node-id <node-id>] [--pool <pool-uuid>] [--plan-id <plan-id>] [--intent-id <intent-id>]

```

Replace:

- `<node-id>` with the id of the node that hosts the migrated pools.

- `<pool-uuid>` with the UUID of the migrated pool.

- `<plan-id>` with the ID of the migration plan.

- `<intent-id>` with the ID of the migration intent.

In this topic:
