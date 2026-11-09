# Upgrade OpenShift using Smart Upgrade

Source: https://docs.portworx.com/portworx-enterprise/platform/upgrade/upgrade-ocp (Portworx Enterprise latest)

Upgrade OpenShift using Smart Upgrade | Portworx Enterprise Documentation

Previously, Portworx came packaged with its own Prometheus deployment. With new versions of OpenShift, Portworx uses the OpenShift Prometheus deployment instead.

## Smart upgrade​

The Smart upgrade feature introduces a streamlined, resilient upgrade process for Kubernetes nodes, allowing them to be upgraded in parallel while maintaining volume quorum and without application disruption.

Per-node PodDisruptionBudgets (PDBs) streamline the upgrade process for Kubernetes clusters. The Operator creates a dedicated PDB for each Portworx storage node. These per-node PDBs ensure granular control over node disruptions, allowing parallel upgrades without risking volume quorum.

During upgrades, the Operator dynamically adjusts the PDBs to enable safe draining of nodes selected for upgrade. The Operator carefully selects nodes to avoid disrupting volume availability and disables volume provisioning on upgrading nodes. This method significantly reduces upgrade times, enhances cluster resilience, and maintains high availability throughout the process.

By default, smart upgrade is disabled, and cluster-wide PDB will be used where `minAvailable` set to `numStorageNodes - 1`, which means one Kubernetes node is upgraded at a time.

You can enable the smart upgrade by setting the `portworx.io/disable-non-disruptive-upgrade` annotation to `false`. You can also configure the minimum number of nodes that must be available at a time using the `portworx.io/storage-pdb-min-available` annotation in the StorageCluster.

The following are the key benefits of using smart upgrades:

- Parallel upgrades: Based on volume distribution, the Portworx Operator tries the best to select multiple nodes for concurrent upgrades, accelerating the upgrade process while eliminating downtime and application disruption.

- Volume quorum maintenance: Ensures volume quorum is maintained throughout the upgrade process.

- Managed node upgrades: You can use the `portworx.io/storage-pdb-min-available` annotation in the StorageCluster CRD to manage the number of nodes upgraded in parallel.

- Automatic reconciliation: The Portworx operator actively monitors and reconciles the storage nodes during upgrades, ensuring smooth progression while preserving quorum integrity.

important

- There will be a downtime for applications using volumes with a replication factor of 1.

- Smart upgrade is not supported for synchronous DR setup.

- If you override the default PodDisruptionBudget, ensure that the `storage-pdb-min-available` value is greater than or equal to OCP's MCP `maxUnavailable`.

- During an upgrade, Portworx pods are deleted and re-created on the nodes selected for upgrade to apply the spec changes. The `spec.updateStrategy` field in the StorageCluster resource controls how nodes are upgraded. By default, the update strategy is RollingUpdate, and the `maxUnavailable` field specifies the maximum number of nodes that can be unavailable at a time. The default value of `maxUnavailable` is 1. This is expected behavior, and you might see pod deletion events in the Kubernetes audit logs. You don't need to take any action.

## Prerequisites​

For smart upgrades, ensure the following prerequisites are met:

- Required Portworx and Operator versions:

- Portworx version 3.1.2 or later

- Operator version 24.2.0 or later

- The cluster must be ready and available for upgrade. You can use the `pxctl status` and `kubectl get storagenodes -n portworx` commands to check the cluster status.

- No nodes or pools should be under maintenance.

- No decommissioned nodes should appear in the output of the `oc get storagenodes` command.

- No nodes should have the `px/service=stop` or `px/service=disabled` label. If nodes have these labels, remove them and restart the Portworx service or decommission the node before the upgrade.

## Upgrade OpenShift cluster​

Perform the following steps to upgrade your OpenShift cluster:

important

Before upgrading your OpenShift cluster, run the `pxfslib` update DaemonSet at least once to ensure that kernel module dependencies required by the new OCP kernel version are available on all nodes. This step is required even if you are not upgrading Portworx Enterprise. Skipping this step can cause nodes to enter a `StorageDown` state after rebooting, especially in air-gapped environments where nodes cannot download updated modules from `mirrors.portworx.com`. For more information, see Update Portworx file system dependencies.

-
If you are upgrading your OpenShift cluster from version 4.11 or older to version 4.12 or newer, you must disable the Portworx Prometheus deployment in the Portworx StorageCluster spec to configure OpenShift Prometheus for monitoring Portworx.

important

Ensure that the entire monitoring block below is present in the Portworx StorageCluster spec.

```

spec:

  monitoring:

  prometheus:

    enabled: false

    exportMetrics: true

    alertManager:

    enabled: false

```

note

When you disable the Portworx Prometheus deployment, Autopilot rules stop functioning due to the absence of Prometheus endpoints. You will need to manually perform pool or volume resizing operations until the OpenShift upgrade process is complete.

-
Upgrade your Portworx Operator to the latest release.

-
(Optional) For enabling smart upgrades, set the `portworx.io/disable-non-disruptive-upgrade` annotation to `false`.

note

When smart upgrade is enabled, the Operator uses `quorum` as the `minAvailable` value by default. If you want to override the value, use the `portworx.io/storage-pdb-min-available` annotation.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

  annotations:

    portworx.io/disable-non-disruptive-upgrade: "false"

    # If you want to override the default value of `minAvailable`, uncomment the below line and set a desired value.

    #portworx.io/storage-pdb-min-available: "2"

```

-
Upgrade your OpenShift cluster to 4.12 or newer.

## Configure the OpenShift Prometheus deployment​

After upgrading your OpenShift cluster, follow these steps to integrate OpenShift’s Prometheus deployment with Portworx:

-
Create a `cluster-monitoring-config` ConfigMap in the `openshift-monitoring` namespace to integrate OpenShift’s monitoring and alerting system with Portworx:

```

apiVersion: v1

kind: ConfigMap

metadata:

  name: cluster-monitoring-config

  namespace: openshift-monitoring

data:

  config.yaml: |

    enableUserWorkload: true

```

The `enableUserWorkload` parameter enables monitoring for user-defined projects in the OpenShift cluster. This action creates a `prometheus-operated` service in the `openshift-user-workload-monitoring` namespace.

-
Fetch the Thanos host, which is part of the OpenShift monitoring stack:

```

oc get route thanos-querier -n openshift-monitoring -o json | jq -r '.spec.host'

```

```

thanos-querier-openshift-monitoring.tp-nextpx-iks-catalog-pl-80e1e1cd66534115bf44691bf8f01a6b-0000.us-south.containers.appdomain.cloud

```

Configure Autopilot using the above route host to enable its access to Prometheus's statistics.

## Configure Autopilot​

Edit the Autopilot spec within the Portworx StorageCluster spec to include the Thanos Querier host URL you retrieved in the previous step. Replace `<THANOS-QUERIER-HOST>` with the actual host URL:

```

spec:

  autopilot:

    enabled: true

    image: <autopilot-image>

    providers:

    - name: default

      params:

        url: https://<THANOS-QUERIER-HOST>

      type: prometheus

```

This configuration tells Autopilot to use the OpenShift Prometheus deployment (via Thanos Querier) for metrics and monitoring.

## Configure Grafana​

You can connect to Prometheus using Grafana to visualize your data. Grafana is a multi-platform, open-source analytics and interactive visualization web application. It provides charts, graphs, and alerts.

note

The following steps use the `portworx` namespace. If you want to install in a different namespace, replace all instances of `portworx` with your namespace.

-
Enter the following commands to download the Grafana dashboard and datasource configuration files:

```

curl -O https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana-dashboard-config.yaml

```

```

% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current

                                Dload  Upload   Total   Spent    Left  Speed

100   211  100   211    0     0    596      0 --:--:-- --:--:-- --:--:--   596

```

```

curl -O https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana-datasource-ocp.yaml

```

```

% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current

                                Dload  Upload   Total   Spent    Left  Speed

100  1625  100  1625    0     0   4456      0 --:--:-- --:--:-- --:--:--  4464

```

-
Create the `grafana` service account:

```

oc -n portworx apply -f https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana-service-account.yaml

```

-
The `grafana` service account was created alongside the Grafana instance. Grant it the `cluster-monitoring-view` cluster role:

```

oc -n portworx adm policy add-cluster-role-to-user cluster-monitoring-view -z grafana

```

-
The bearer token for this service account is used to authenticate access to OpenShift Prometheus. Create a service account token secret:

```

oc -n portworx create token grafana --duration=8760h

```

-
Modify the `grafana-datasource-ocp.yaml` file:

-
On the `url: https://<THANOS_QUERIER_HOST>` line, replace `<THANOS_QUERIER_HOST>` with the URL you retrieved in the Configure the OpenShift Prometheus deployment section:

-
On the `httpHeaderValue1: 'Bearer <BEARER_TOKEN>'` line, replace `<BEARER_TOKEN>` with the bearer token value you created in the step above.

-
Create a configmap for the dashboard and data source:

```

oc -n portworx create configmap grafana-dashboard-config --from-file=grafana-dashboard-config.yaml

```

```

oc -n portworx create configmap grafana-source-config --from-file=grafana-datasource-ocp.yaml

```

-
Download and install Grafana dashboards using the following commands:

```

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-cluster-dashboard.json" -o portworx-cluster-dashboard.json && \

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-node-dashboard.json" -o portworx-node-dashboard.json && \

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-volume-dashboard.json" -o portworx-volume-dashboard.json && \

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-performance-dashboard.json" -o portworx-performance-dashboard.json && \

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-etcd-dashboard.json" -o portworx-etcd-dashboard.json && \

# Optional: Download these files only if you need to monitor API requests sent to FlashArray

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/fa-apis-dashboard1.json" -o fa-apis-dashboard1.json && \

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/fa-apis-dashboard2.json" -o fa-apis-dashboard2.json && \

# Optional: Download this file only if you use Stork for DR/migrations

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-dr-dashboard.json" -o portworx-dr-dashboard.json

```

```

oc -n portworx create configmap grafana-dashboards \

--from-file=portworx-cluster-dashboard.json \

--from-file=portworx-performance-dashboard.json \

--from-file=portworx-node-dashboard.json \

--from-file=portworx-volume-dashboard.json \

--from-file=portworx-etcd-dashboard.json \

# Optional: Include these dashboards only if you need to monitor API requests sent to FlashArray.

--from-file=fa-apis-dashboard1.json \

--from-file=fa-apis-dashboard2.json \

# Optional: Include this dashboard only if you use Stork for DR/migrations.

--from-file=portworx-dr-dashboard.json

```

-
Enter the following command to download and install the Grafana YAML file:

```

oc -n portworx apply -f https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana-ocp.yaml

```

-
Verify if the Grafana pod is running using the following command:

```

oc -n portworx get pods | grep -i grafana

```

```

grafana-7d789d5cf9-bklf2                   1/1     Running   0              3m12s

```

-
Access Grafana by setting up port forwarding and browsing to the specified port. In this example, port forwarding is provided for ease of access to the Grafana service from your local machine using the port 3000:

```

oc -n portworx port-forward service/grafana 3000:3000

```

-
Navigate to Grafana by browsing to `http://localhost:3000`.

-
Enter the default credentials to log in.

- login: `admin`

- password: `admin`

In this topic:
