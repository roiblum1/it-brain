# Run Hyperconverged Using Stork

Source: https://docs.portworx.com/portworx-enterprise/operations/tune-performance/hyperconvergence (Portworx Enterprise latest)

Run Hyperconverged Using Stork | Portworx Enterprise Documentation

## Hyperconvergence​

When a pod runs on the same host as its volume, it is known as convergence or hyperconvergence. This configuration reduces the network overhead of an application, resulting in improved performance. Hyperconverged Portworx storage cluster deployment shows a diagram of this deployment pattern.

### Enabling hyperconvergence​

Portworx Enterprise recommends using Stork to run your pods hyperconverged.

Once you have installed Stork, the webhook controller is enabled by default and uses Stork as the scheduler. If you have disabled `webhook-controller` with the flag, all you need to do is add `schedulerName: stork` in your application specs. Stork then ensures that the nodes with data for a volume are prioritized when pods are scheduled.

note

On Amazon EKS with hybrid nodes, the Stork admission webhook can set the scheduler automatically only when the on-premises pod network is routable from the virtual private cloud (VPC). If the pod network is not routable, keep Stork on the on-premises nodes and add `schedulerName: stork` to each workload that requires Stork scheduling. Hyperconvergence then works as described in this topic. For more information, see Configure hyperconvergence for workloads.

For example, this is how you specify the scheduler name in a MySQL deployment:

```

apiVersion: apps/v1

kind: Deployment

metadata:

  name: mysql

spec:

  selector:

    matchLabels:

      app: mysql

  strategy:

    rollingUpdate:

      maxSurge: 1

      maxUnavailable: 1

    type: RollingUpdate

  replicas: 1

  template:

    metadata:

      labels:

        app: mysql

        version: "1"

    spec:

      schedulerName: stork

      containers:

      - image: mysql:5.6

        name: mysql

        env:

        - name: MYSQL_ROOT_PASSWORD

          value: password

        ports:

        - containerPort: 3306

        volumeMounts:

        - name: mysql-persistent-storage

          mountPath: /var/lib/mysql

      volumes:

      - name: mysql-persistent-storage

        persistentVolumeClaim:

          claimName: mysql-data

```

note

-
To enforce strict pod hyperconvergence with respect to all its PVC replicas, include `stork.libopenstorage.org/preferLocalNodeOnly: "true"` in the `spec.template.metadata.annotations` section of your StatefulSet object. This filters out nodes without a replica before scoring runs.

-
Use volume placement strategy to place volumes on specific nodes.

-
Portworx Enterprise limits each node to 1024 local volume attaches under its license. When Stork schedules a pod, the Stork scheduler extender filters out any node that would exceed this limit. Stork calculates the projected attach count for a node by adding the pod's new volume attaches to the node's existing attaches, and then subtracting the volumes that are already attached to that node. Stork also lowers the hyperconvergence score of nodes that are approaching the limit, so that pods are scheduled on less loaded nodes before any node reaches the limit. For the Stork parameters that control this behavior, see Stork Configuration.

-

### Enable Stork normalization and tune hyperconvergence scoring​

Stork scores every feasible node for a pod's placement, based on how much of the pod's data it holds. The Kubernetes scheduler combines this score with the scores from its own built-in plugins to decide which feasible node to place the pod on. Stork's scoring favors the node that holds the pod's data.

Starting with Stork 26.4.2, the `spec.stork.args.normalize-stork-scores` parameter is enabled by default, which normalizes hyperconvergence scores during pod scheduling. This normalization allows factors such as node load, CPU utilization, memory consumption, and other scheduling policy settings (taints, node affinity, topology spread) to influence the final score assigned to feasible nodes. For example, before Stork normalization scoring, a pod could be scheduled on a node that held its data despite that node having higher CPU or memory usage. With normalization enabled, the same pod may instead be scheduled on a node with lower CPU and memory usage, even if that node does not hold the pod's data, thus not hyperconverged.

Normalization and tuning of hyperconvergence scores is only supported starting with Stork 26.4.2, Portworx Operator 26.4.0, and Portworx Enterprise 3.6.2 or later.

You can tune or disable this Stork normalization scoring through `spec.stork.args` in the `StorageCluster`:

- `spec.stork.args.normalize-stork-scores` enables or disables Stork's normalization scoring behavior.

- `spec.stork.scheduler.kubeSchedulerExtenderWeight` tunes how strongly Stork's hyperconvergence competes with other scheduling signals.

- When `spec.stork.args.normalize-stork-scores` is enabled, `spec.stork.args.replica-score`, `spec.stork.args.rack-score`, `spec.stork.args.zone-score`, `spec.stork.args.region-score`, and `spec.stork.args.remote-score` flags let you set individual weightage for each parameter. If edited, ensure values of the flags maintain the order: `replica-score` > `rack-score` > `zone-score` > `region-score`.

For the full list of flags and their defaults, see Stork configuration.

#### Example​

Each parameter's value is the score given to a node at that level of closeness to the pod's data:

ParameterScore prior to Stork 26.4.2Default score starting with Stork 26.4.2 (normalize-stork-scores: true)Applies to

`replica-score`1004The node holding the data

`rack-score`503A node in the same rack

`zone-score`252A node in the same zone

`region-score`101A node in the same region

`remote-score`50Every other node

The `weight` (`5` before normalization, `1` starting with Stork 26.4.2) multiplies this score before Kubernetes scales it by a further `10` to bring it onto the same scale as the plugin score: `10 × weight × score`.

Consider a cluster with the following topology, where Node A holds the pod's only replica:

```

Region us-east

├── Zone-1

│   ├── Rack-1: Node A (REPLICA)   Node C

│   └── Rack-2: Node D

Region us-west

└── Zone-2

    └── Rack-3: Node B

```

Node A is also the busiest node in the cluster (80% CPU usage), Node C and Node D are moderately loaded, and Node B is far lighter (25% CPU usage) but holds none of the pod's data:

Node A (replica, busy)Node C (same rack)Node D (same zone)Node B (remote, light)

Relationship to Node AHolds the replicaSame rackSame zone, different rackDifferent region

Built-in plugin score (resource fit, resource balance, image locality, and taints)418430425468

Before normalization (weight 5)418 + (100 × 5 × 10) = 5418 (wins)430 + (50 × 5 × 10) = 2930425 + (25 × 5 × 10) = 1675468 + (5 × 5 × 10) = 718

After normalization (weight 1)418 + (4 × 1 × 10) = 458430 + (3 × 1 × 10) = 460425 + (2 × 1 × 10) = 445468 + (0 × 1 × 10) = 468 (wins)

Before normalization, Node A wins by a wide margin. Even Node D, which shares only a zone with Node A, outscores the far lighter Node B. After normalization, Node B wins instead, since resource load now outweighs the small locality bonus given to Node A, Node C, and Node D. This helps Stork schedule pods more fairly across the cluster, even if it means a pod is not hyperconverged.

### Disabling hyperconvergence​

You can disable Stork's hyperconverged pod prioritization with the `stork.libopenstorage.org/disableHyperconvergence: "true"` pod annotation.

note

For sharedv4 volumes, when `disableHyperconvergence` is enabled, Portworx ignores Stork's node score logic, and all input nodes are scored equally. Also, the StorageClass parameters listed below are ignored.

- `stork.libopenstorage.org/preferRemoteNodeOnly`

- `stork.libopenstorage.org/preferRemoteNode`

In this topic:
