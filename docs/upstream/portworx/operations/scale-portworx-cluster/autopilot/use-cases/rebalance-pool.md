# Automatically rebalance Portworx storage pools

Source: https://docs.portworx.com/portworx-enterprise/operations/scale-portworx-cluster/autopilot/use-cases/rebalance-pool (Portworx Enterprise latest)

Automatically rebalance Portworx storage pools | Portworx Enterprise Documentation

You can use Autopilot to rebalance Portworx storage pools automatically when they begin to run out of space.

Autopilot monitors the metrics in your cluster (for example, via Prometheus) and detects conditions that require rebalancing of existing volumes in the cluster.

## Prerequisites​

- Autopilot version: 1.3.0 or newer

## Examples​

- Rebalance based on provisioned and used space mean deviation

- Rebalance based on provisioned and used space absolute values

The following example Autopilot rule will rebalance all storage pools which meet either of following conditions:

- Pool's provision space is over 20% or under 20% of mean value across pools

- Pool's used space is over 20% or under 20% of mean value across pools

```

apiVersion: autopilot.libopenstorage.org/v1alpha1

kind: AutopilotRule

metadata:

  name: pool-rebalance

spec:

  conditions:

    requiredMatches: 1

    expressions:

    - keyAlias: PoolProvDeviationPerc

      operator: NotInRange

      values:

        - "-20"

        - "20"

    - keyAlias: PoolUsageDeviationPerc

      operator: NotInRange

      values:

        - "-20"

        - "20"

  actions:

    - name: "openstorage.io.action.storagepool/rebalance"

```

The AutopilotRule spec consists of two important sections: `conditions` and `actions`.

-
The `conditions` section establishes threshold criteria dictating when the rule must perform its action. In this example, that criteria contains 2 formulas:

- `PoolProvDeviationPerc` is an alias for a Prometheus query that gives a storage pool's provisioned space deviation percentage relative to other pools in the cluster.

- The `NotInRange` operator checks if the value of the metric is outside the range specified in the `values`.

- In this case, the condition is met when the pool's provisioned space goes over 20% or under 20% compared to mean value across pools.

- For example, if a particular pool's provisioned space is 25% lower compared to mean provisioned space across all pools in the cluster, then the condition is met.

- `PoolUsageDeviationPerc` is an alias for a Prometheus query that gives a storage pool's used space deviation percentage relative to other pools in the cluster.

- The `NotInRange` operator checks if the value of the metric is outside the range specified in the `values`.

- In this case, the condition is met when the pool's used space goes over 20% or under 20% compared to mean value across pools.

- For example, if a particular pool's used space is 25% higher compared to mean used space across all pools in the cluster, then the condition is met.

- `requiredMatches` indicates that only one of the expressions need to match for the conditions to be considered as being met.

-
The `actions` section in the above specs specify what action Portworx performs when the conditions are met. The action name here is the Storage Pool rebalance action.

In the example above, the rule's condition does two jobs at once: it decides when the rule fires, and it supplies the threshold Autopilot sends to Portworx for the rebalance itself. This works because each condition uses a metric Autopilot recognizes for rebalance: `PoolProvDeviationPerc` or `PoolUsageDeviationPerc`.

If your rule triggers on anything else, Autopilot has no threshold to read from the condition and falls back to its default mean deviation for provisioned and used space. It records a `RebalanceUsingDefaultThresholds` warning event against the rule when this happens.

To trigger a rebalance on one metric while controlling its sensitivity with another, set the thresholds directly on the action:

```

apiVersion: autopilot.libopenstorage.org/v1alpha1

kind: AutopilotRule

metadata:

  name: pool-rebalance-explicit-threshold

spec:

  # Fires on total pool size — not a metric Autopilot can derive a threshold from.

  conditions:

    requiredMatches: 1

    expressions:

      - key: "px_pool_stats_total_bytes/(1024*1024*1024)"

        operator: Gt

        values:

          - "100"

  actions:

    - name: "openstorage.io.action.storagepool/rebalance"

      params:

        poolProvDeviationPerc: "4"

        poolUsageDeviationPerc: "4"

```

This rebalances at 4% deviation on pools larger than 100 GiB, even though the condition says nothing about deviation.

ParameterDescription

`poolProvDeviationPerc`Rebalance a pool whose provisioned space deviates from the cluster mean by more than this percentage, in either direction.

`poolUsageDeviationPerc`Rebalance a pool whose used space deviates from the cluster mean by more than this percentage, in either direction.

All values are non-negative integers written as strings. Note the following:

- The two deviation parameters are symmetric. A single value sets the threshold in both directions, because deviation from the mean has an over- and under-loaded side.

- If you set any of these two parameters, they determine every rebalance threshold and the rule's conditions are not consulted. Setting only `poolUsageDeviationPerc` therefore leaves no threshold for provisioned space, rather than taking that one from the conditions. Set both when you want both.

- These parameters apply only to the rebalance action. They do not affect when the rule triggers; that is governed entirely by `spec.conditions`.

The following example Autopilot rule will rebalance all storage pools which meet either of following conditions:

- Pool's provision space is over 120%

- Pool's used space is over 70%

```

apiVersion: autopilot.libopenstorage.org/v1alpha1

kind: AutopilotRule

metadata:

  name: pool-rebalance

spec:

  conditions:

    requiredMatches: 1

    expressions:

    - key: 100 * (px_pool_stats_provisioned_bytes/ on (pool) px_pool_stats_total_bytes)

      operator: Gt

      values:

        - "120"

    - key: 100 * (px_pool_stats_used_bytes/ on (pool) px_pool_stats_total_bytes)

      operator: Gt

      values:

        - "70"

  actions:

    - name: "openstorage.io.action.storagepool/rebalance"

```

The AutopilotRule spec consists of two important sections: `conditions` and `actions`.

- The `conditions` section establishes threshold criteria dictating when the rule must perform its action. In this example, that criteria contains 2 formulas:

- `100 * (px_pool_stats_provisioned_bytes/ on (pool) px_pool_stats_total_bytes) ` is a Prometheus query that gives a storage pool's provisioned space percentage

- The `Gt` operator checks if the value of the metric is greater than `120%`.

- `100 * (px_pool_stats_used_bytes/ on (pool) px_pool_stats_total_bytes) ` is a Prometheus query that gives a storage pool's used space percentage

- The `Gt` operator checks if the value of the metric is greater than `70%`.

- `requiredMatches` indicates that only one of the expressions need to match for the conditions to be considered as being met.

- The `actions` section in the above specs specify what action Portworx performs when the conditions are met. The action name here is the Storage Pool rebalance action.

In the example above, the rule's condition does two jobs at once: it decides when the rule fires, and it supplies the threshold Autopilot sends to Portworx for the rebalance itself. This works because each condition uses a metric Autopilot recognizes for rebalance: `PoolProvPerc`, or `PoolUsagePerc`.

To trigger a rebalance on one metric while controlling its sensitivity with another, set the thresholds directly on the action:

```

apiVersion: autopilot.libopenstorage.org/v1alpha1

kind: AutopilotRule

metadata:

  name: pool-rebalance-explicit-threshold

spec:

  # Fires on total pool size — not a metric Autopilot can derive a threshold from.

  conditions:

    requiredMatches: 1

    expressions:

      - key: "px_pool_stats_total_bytes/(1024*1024*1024)"

        operator: Gt

        values:

          - "100"

  actions:

    - name: "openstorage.io.action.storagepool/rebalance"

      params:

        poolProvPerc: "80"

        poolUsagePerc: "80"

```

ParameterDescription

`poolProvPerc`Rebalance a pool whose provisioned space exceeds this percentage of its capacity. Not capped at 100, so values above 100 are valid for thin-provisioned pools.

`poolUsagePerc`Rebalance a pool whose used space exceeds this percentage of its capacity. Must not exceed 100.

All values are non-negative integers written as strings. Note the following:

- The two absolute parameters set only an upper bound.

- If you set any of these two parameters, they determine every rebalance threshold and the rule's conditions are not consulted.

- These parameters apply only to the rebalance action. They do not affect when the rule triggers; that is governed entirely by `spec.conditions`.

## Implement the Autopilot rule​

Perform the following steps to deploy this example.

### Create specs​

note

- Other rebalance rules: If you have other AutopilotRules in the cluster for pool rebalance, Portworx Enterprise. recommends you delete them for this test. This will make it easier to confirm that the rule in this example was triggered.

- TESTING ONLY: The specs below all volumes to initially land on a single Portworx node. This is done so that we can test the rebalance rule later on to rebalance the volumes across all nodes.

#### Application and PVC specs​

Create the storage and application spec files:

-
Identify the ID of a single Portworx node in the cluster.

List the cluster nodes and pick the first node. In this example, we will pick the first node xxxxxxxx-xxxx-xxxx-xxxx-75339f2ada81 in the list.

- OpenShift

- Kubernetes

```

PX_POD=$(oc get pods -l name=portworx -n portworx -o jsonpath='{.items[0].metadata.name}')

oc exec $PX_POD -n portworx -- /opt/pwx/bin/pxctl status

```

```

Cluster ID: px-autopilot-demo

Cluster UUID: xxxxxxxx-xxxx-xxxx-xxxx-a0534c91a417

Status: OK

Nodes in the cluster:

ID                                      SCHEDULER_NODE_NAME                     DATA IP         CPU             MEM TOTAL       MEM FREE        CONTAINERS      VERSION                 Kernel                  OS                      STATUS

xxxxxxxx-xxxx-xxxx-xxxx-75339f2ada81    xxxxxxxx-xxxx-xxxx-xxxx-2ff85c418afe    X.X.X.1      2.641509        8.4 GB          7.0 GB          N/A             2.6.0.0-d88b8c6         4.15.0-72-generic       Ubuntu 16.04.6 LTS      Online

xxxxxxxx-xxxx-xxxx-xxxx-5431da0e8b0a    xxxxxxxx-xxxx-xxxx-xxxx-c0ae5965deac    X.X.X.3      3.666245        8.4 GB          6.9 GB          N/A             2.6.0.0-d88b8c6         4.15.0-72-generic       Ubuntu 16.04.6 LTS      Online

xxxxxxxx-xxxx-xxxx-xxxx-63b06936395b    xxxxxxxx-xxxx-xxxx-xxxx-2b8561e244eb    X.X.X.2      3.530895        8.4 GB          7.0 GB          N/A             2.6.0.0-d88b8c6         4.15.0-72-generic       Ubuntu 16.04.6 LTS      Online

```

```

PX_POD=$(kubectl get pods -l name=portworx -n portworx -o jsonpath='{.items[0].metadata.name}')

kubectl exec $PX_POD -n portworx -- /opt/pwx/bin/pxctl status

```

```

Cluster ID: px-autopilot-demo

Cluster UUID: xxxxxxxx-xxxx-xxxx-xxxx-a0534c91a417

Status: OK

Nodes in the cluster:

ID                                      SCHEDULER_NODE_NAME                     DATA IP         CPU             MEM TOTAL       MEM FREE        CONTAINERS      VERSION                 Kernel                  OS                      STATUS

xxxxxxxx-xxxx-xxxx-xxxx-75339f2ada81    xxxxxxxx-xxxx-xxxx-xxxx-2ff85c418afe    X.X.X.1      2.641509        8.4 GB          7.0 GB          N/A             2.6.0.0-d88b8c6         4.15.0-72-generic       Ubuntu 16.04.6 LTS      Online

xxxxxxxx-xxxx-xxxx-xxxx-5431da0e8b0a    xxxxxxxx-xxxx-xxxx-xxxx-c0ae5965deac    X.X.X.3      3.666245        8.4 GB          6.9 GB          N/A             2.6.0.0-d88b8c6         4.15.0-72-generic       Ubuntu 16.04.6 LTS      Online

xxxxxxxx-xxxx-xxxx-xxxx-63b06936395b    xxxxxxxx-xxxx-xxxx-xxxx-2b8561e244eb    X.X.X.2      3.530895        8.4 GB          7.0 GB          N/A             2.6.0.0-d88b8c6         4.15.0-72-generic       Ubuntu 16.04.6 LTS      Online

```

-
Create `postgres-sc.yaml` and place the following content inside it.

```

##### Portworx storage class

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: postgres-pgbench-sc

provisioner: pxd.portworx.com

parameters:

  repl: "1"

  nodes: "xxxxxxxx-xxxx-xxxx-xxxx-75339f2ada81"

allowVolumeExpansion: true

```

note

Notice how the `nodes` section pin the volumes from this StorageClass to initially land only on xxxxxxxx-xxxx-xxxx-xxxx-75339f2ada81. You should use this for testing only, and you must change the value to suit your environment.

-
Create `postgres-vol.yaml` and place the following content inside it.

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

  name: pgbench-data

  labels:

    app: postgres

spec:

  storageClassName: postgres-pgbench-sc

  accessModes:

    - ReadWriteOnce

  resources:

    requests:

      storage: 30Gi

```

You will not deploy any application pod using this PVC. This tutorial only demonstrates rebalancing the pools.

-
Create the StorageClass and create 3 PVCs in 3 unique namespaces:

- OpenShift

- Kubernetes

```

oc apply -f postgres-sc.yaml

for i in {1..3}; do

  oc create ns pg$i || true

  oc apply -f postgres-vol.yaml -n pg$i

done

```

```

kubectl apply -f postgres-sc.yaml

for i in {1..3}; do

  kubectl create ns pg$i || true

  kubectl apply -f postgres-vol.yaml -n pg$i

done

```

-
Wait until all PVCs are bound and confirm that one pool has all the volumes.

The output from the following commands should show all PVCs as bound:

- OpenShift

- Kubernetes

```

oc get pvc -n pg1

oc get pvc -n pg2

oc get pvc -n pg3

```

```

kubectl get pvc -n pg1

kubectl get pvc -n pg2

kubectl get pvc -n pg3

```

The output from this command should show that the provisioned space for the pool for the Portworx node that you selected in Step 1 has gone up by 90Gi since all the volumes are created there. You will see this in the `PROVISIONED` column of the output.

- OpenShift

- Kubernetes

```

oc exec $PX_POD -n portworx -- /opt/pwx/bin/pxctl cluster provision-status --output-type wide

```

```

kubectl exec $PX_POD -n portworx -- /opt/pwx/bin/pxctl cluster provision-status --output-type wide

```

#### AutopilotRule spec​

Once you've created the PVCs, you can create an AutopilotRule to rebalance the pools.

- Create a YAML spec for the autopilot rule named `autopilotrule-pool-rebalance-example.yaml` and place the following content inside it:

- Rebalance based on provisioned and used space mean deviation

- Rebalance based on provisioned and used space absolute values

-
Set rebalance thresholds based on the trigger:

```

apiVersion: autopilot.libopenstorage.org/v1alpha1

kind: AutopilotRule

metadata:

  name: pool-rebalance

spec:

  conditions:

    requiredMatches: 1

    expressions:

    - keyAlias: PoolProvDeviationPerc

      operator: NotInRange

      values:

        - "-20"

        - "20"

    - keyAlias: PoolUsageDeviationPerc

      operator: NotInRange

      values:

        - "-20"

        - "20"

  actions:

    - name: "openstorage.io.action.storagepool/rebalance"

```

-
Set rebalance thresholds independent of the trigger:

```

apiVersion: autopilot.libopenstorage.org/v1alpha1

kind: AutopilotRule

metadata:

  name: pool-rebalance-explicit-threshold

spec:

  # Fires on total pool size — not a metric Autopilot can derive a threshold from.

  conditions:

    requiredMatches: 1

    expressions:

      - key: "px_pool_stats_total_bytes/(1024*1024*1024)"

        operator: Gt

        values:

          - "100"

  actions:

    - name: "openstorage.io.action.storagepool/rebalance"

      params:

        poolProvDeviationPerc: "4"

        poolUsageDeviationPerc: "4"

```

```

apiVersion: autopilot.libopenstorage.org/v1alpha1

kind: AutopilotRule

metadata:

  name: pool-rebalance

spec:

  conditions:

    requiredMatches: 1

    expressions:

    - key: 100 * (px_pool_stats_provisioned_bytes/ on (pool) px_pool_stats_total_bytes)

      operator: Gt

      values:

        - "120"

    - key: 100 * (px_pool_stats_used_bytes/ on (pool) px_pool_stats_total_bytes)

      operator: Gt

      values:

        - "70"

  actions:

    - name: "openstorage.io.action.storagepool/rebalance"

```

-
Apply the rule:

- OpenShift

- Kubernetes

```

oc apply -f autopilotrule-pool-rebalance-example.yaml

```

```

kubectl apply -f autopilotrule-pool-rebalance-example.yaml

```

### Monitor​

Now that you've created the rule, Autopilot will now detect that one specific pool is over-provisioned and it will start rebalancing the 3 volumes across the pools.

Enter the following command to retrieve all the events generated for the `pool-rebalance` rule:

- OpenShift

- Kubernetes

```

oc get events --field-selector involvedObject.kind=AutopilotRule,involvedObject.name=pool-rebalance --all-namespaces --sort-by .lastTimestamp

```

```

kubectl get events --field-selector involvedObject.kind=AutopilotRule,involvedObject.name=pool-rebalance --all-namespaces --sort-by .lastTimestamp

```

You should see events that will show the rule has triggered. About 30 seconds later, the rebalance actions will begin.

Once you see actions have begun on the pools, you can use pxctl to again check the cluster provision status.

Below should now show that the provisioned space for all your pools are balanced and spread evenly. You will see this in the `PROVISIONED` column of the output.

- OpenShift

- Kubernetes

```

oc exec $PX_POD -n portworx -- /opt/pwx/bin/pxctl cluster provision-status --output-type wide

```

```

kubectl exec $PX_POD -n portworx -- /opt/pwx/bin/pxctl cluster provision-status --output-type wide

```

In this topic:
