# Cluster Options, Alerts, and Metrics

Source: https://docs.portworx.com/portworx-enterprise/operations/kube-datastore-3.7.2/kds-alerts (Portworx Enterprise latest)

Cluster Options, Alerts, and Metrics | Portworx Enterprise Documentation

This topic provides reference information for configuring and monitoring Kube Datastore (KDS) and dynamic pools in Portworx Enterprise.

Use this topic to:

- Find cluster options that control pool failover, rebalance, and placement.

- Configure runtime options, `StorageCluster` fields, Stork flags, and CSI attacher settings.

- Identify alerts raised during dynamic pool operations.

- Find metrics and commands for monitoring pool placement, migration, and VM hyperconvergence.

## Cluster options​

Cluster options control dynamic pool failover, rebalance, and placement behavior.

To view the current cluster options, run:

```

pxctl cluster options list

```

To update a cluster option, run:

```

pxctl cluster options update --<option-name>=<value>

```

Replace `<option-name>` with the option you want to change and `<value>` with the required value.

warning

Changing cluster options can affect pool failover, placement, and workload availability. Do not change these options unless necessary. Contact Portworx Support before modifying these settings.

### Failover options​

The following options control dynamic pool failover and migration history.

ParameterDescriptionDefault value

`pause-pool-failovers`Pauses automatic dynamic pool failover.`false`

`disable-failover-sequencer`Disables sequential processing of pool failover plans for each destination node. When set to `true`, multiple pools can fail over to the same destination node simultaneously. Portworx by Everpure does not recommend enabling this option.`false`

`max-active-failover-nodes`Sets the maximum number of nodes that can participate in failover simultaneously.`5`

`max-active-failover-pools`Sets the maximum number of pools that can participate in failover simultaneously.`16`

`max-concurrent-failovers-per-target-node`Sets the maximum number of pools that can fail over to the same destination node simultaneously.`1`

`failover-cleanup-retention-hours`Sets how long Portworx retains failover-related metadata. The maximum is 12 hours. Longer retention periods can cause `pxctl service pool migrate list` to exceed the response size limit on clusters with frequent pool failovers.`6h`

For more information about pool failover behavior, see Pool failover.

### Rebalance and placement options​

The following options control pool rebalance, placement, and VM hyperconvergence requests.

ParameterDescriptionDefault value

`pause-dynamic-pool-rebalance`Pauses automatic dynamic pool rebalance. Applies only when dynamic pools are enabled.`false`

`pause-vm-hyperconvergence-requests`Pauses VM live migration requests while allowing pool rebalance to continue.`false`

`dynamic-pool-rebalance-max-moves-per-cycle`Sets the maximum number of pools that Portworx can move during one rebalance cycle. This value ranges from 1 to 16. The maximum supported value is `16`.`16`

`pool-rebalance-interval-seconds`Sets the interval, in seconds, between rebalance cycles.`120`

For information about how Portworx uses these settings, see Pool placement and rebalance.

## Runtime options​

Runtime options control storage pool limits and sizing.

Configure these options under `spec.runtimeOptions` in the `StorageCluster` resource.

For example:

```

spec:

  runtimeOptions:

    limit_pools_count: "8"

```

The following table describes the available options.

OptionDescriptionDefault value

`limit_pools_count`Sets the maximum number of storage pools allowed on a node. The hard limit is 16 pools. Configure this value to leave enough pool slots for failover.`8`

### Plan pool capacity for failover​

When configuring `limit_pools_count`, consider how many pools a node normally hosts and how many additional pools it might need to accept after another node fails.

For example, if a node normally hosts four pools and `limit_pools_count` is set to `8`, the node can accept up to four additional pools, provided it meets the other failover requirements.

Portworx recommends reserving four additional pool slots on each node. Set `limit_pools_count` to the number of pools on the node plus four, up to the maximum of 16. The default value is `12`.

Do not fill every node to its configured pool limit. Pool failover requires eligible destination nodes with available pool slots.

For more information about pool capacity planning, see Scale limits.

## StorageCluster fields​

The following `StorageCluster` fields control dynamic pool enablement and relocation behavior during upgrades.

FieldDescriptionDefault value

`spec.kubeDatastore.enableDynamicPools`Enables dynamic pools in the cluster.`false`

`spec.kubeDatastore.disableOCPUpgradeBlockOnPoolMigration`When set to `true`, OpenShift node drains do not wait for pool migration to complete. Pool migration still occurs.`false`

`spec.updateStrategy.rollingUpdate.disablePoolRelocate`When set to `true`, the Portworx Operator skips pool relocation before restarting Portworx during an upgrade and performs only VM live migration. The setting applies to all remaining nodes in the upgrade. For more information, see Disable pool relocation during upgrades.`false`

For installation and upgrade procedures, see Set Up Kube Datastore Dynamic Pools.

## Stork flags​

Stork can live migrate VMs after pool placement changes to restore hyperconvergence by moving VMs to the nodes that host their storage.

The following Stork flags control VM live migration for scheduling optimization:

FlagDescriptionDefault value

`--enable-scheduling-optimization`Enables VM live migration for scheduling optimization.`true`

`--scheduling-optimization-max-parallel-migrations`Sets the maximum number of VM migrations that Stork can run at the same time.`5`

`--scheduling-optimization-cool-off`Sets the minimum time between migrations of the same VM.`1h`

`--scheduling-optimization-migration-timeout`Sets the timeout for each VM migration.`30m`

To configure these flags:

-
Edit the `StorageCluster` resource:

```

kubectl edit stc <stc-name> -n <portworx-namespace>

```

-
Set the flags under `spec.stork.args`.

For example:

```

spec:

  stork:

    args:

      scheduling-optimization-max-parallel-migrations: "10"

      scheduling-optimization-cool-off: "2h"

```

-
Save the changes to the `StorageCluster` resource.

For more information, see Configure and Manage KubeVirt VM Hyperconvergence.

## CSI attacher parameters​

On clusters with more than 5,000 volumes, including snapshots, the default Kubernetes API rate limits for the `csi-attacher` container might delay volume attachment operations.

Increase the following parameters to support clusters with a large number of VMs.

ParameterDefault valueRecommended value

`--kube-api-qps``5``50`

`--kube-api-burst``10``100`

### Configure CSI attacher API rate limits​

This configuration requires Portworx Operator 26.5.0 or later.

-
Create a file named `componentk8sconfig.yaml` with the following configuration:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: px-csi-tuning

  namespace: portworx

spec:

  components:

    - componentNames: ["CSI"]

      workloadConfigs:

        - workloadNames: ["px-csi-ext"]

          containerConfigs:

            - containerNames: ["csi-attacher"]

              args:

                - "--kube-api-qps=50"

                - "--kube-api-burst=100"

```

-
Apply the configuration:

```

kubectl apply -f componentk8sconfig.yaml

```

The configuration sets the Kubernetes API query rate to `50` requests per second and allows a burst of up to `100` requests for the CSI attacher.

## Alerts​

Portworx raises alerts when dynamic pool operations fail or when pool placement does not meet the expected requirements.

To view alerts, run:

```

pxctl alerts show

```

The following table describes alerts related to dynamic pool failover, migration, and repair.

AlertResourceSeverityDescription

`PoolFailoverLimitation`PoolWarningA pool does not meet the requirements for failover because it contains an unsupported volume type, such as a SharedV4 volume, a journal volume, or a volume with replication factor greater than 1 (`repl>1`).

`PoolFailoverPlanFailed`PoolWarningPortworx cannot create a failover plan because no suitable destination node is available or a replica placement rule prevents migration.

`PoolFailoverFailed`PoolAlarmPool failover fails during deactivation, activation, or completion. The alert identifies the failed stage and reason.

`PoolFailoverOrphanedPools`NodeWarningPortworx received a request to migrate pools, but some pools do not have corresponding migration plans.

`PoolMoveFastpathDriverUnsupported`PoolAlarmA node uses a `px.ko` driver that does not support fast failover, so Portworx cancels the pool migration.

`PoolFailoverDestinationOverridden`PoolWarningPortworx selects a different destination node when retrying a migration initiated with `--destination-node`.

`PoolAffinityGroupSplit`PoolWarningPools belonging to the same affinity group remain on different nodes for 10 consecutive rebalance cycles.

`PoolFailoverIntentQueueFull`NodeWarningThe failover intent queue is full. Portworx retries the request during reconciliation.

`PoolFailoverPoolsDeferred`NodeWarningThe maximum number of concurrent pool failovers has been reached, so Portworx defers the remaining pools. The deferred pools stay on the source node until you run another migration.

`PoolRepair`PoolWarningPool failover triggers a pool repair operation.

`PoolRepairFailed`PoolAlarmA pool repair operation fails or does not restore the pool to a healthy state.

For information about identifying and resolving these issues, see Troubleshoot Dynamic Pools and KubeVirt Workloads.

## Metrics​

Portworx provides metrics for monitoring Kube Datastore capacity, storage pool performance, pool failover, rebalance, and VM hyperconvergence.

### Kube Datastore capacity and performance metrics​

Kube Datastore capacity and performance metrics use the `px_kube_datastore_` prefix.

These metrics include a `kube_datastore` label that identifies the KDS.

Storage pool metrics also include this label, allowing you to group and analyze pool metrics by Kube Datastore.

For the complete list of supported metrics, see Kube Datastore metrics.

note

Portworx generates Kube Datastore metrics from storage pool metrics by using Prometheus recording rules installed by the Portworx Operator.

On OpenShift, additional configuration is required to enable these recording rules. For more information, see Enable Kube Datastore metrics.

In this topic:
