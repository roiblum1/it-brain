# Configure Portworx Monitoring on OpenShift

Source: https://docs.portworx.com/portworx-enterprise/operations/observability/set-ocp-prometheus (Portworx Enterprise latest)

Configure Portworx Monitoring on OpenShift | Portworx Enterprise Documentation

This topic provides instructions on how to configure monitoring for Portworx deployments on an OpenShift cluster. With OpenShift versions 4.12 or later, Portworx uses OpenShift’s Prometheus deployment for monitoring, rather than deploying its own.

Perform the steps mentioned in this topic to integrate Portworx, Autopilot, Grafana with OpenShift’s Prometheus deployment.

## Prerequisites​

- Portworx Operator version 23.10.3 or later.

- Autopilot version 1.3.13 or later.

## How to export Portworx metrics to OpenShift Prometheus​

In OpenShift version 4.12 or later, you must disable Portworx Prometheus and export your Portworx metrics to OpenShift Prometheus by configuring user workload monitoring.

Disable the Portworx Prometheus deployment in the Portworx StorageCluster spec:

```

spec:

  monitoring:

    prometheus:

      enabled: false

      exportMetrics: true

      alertManager:

        enabled: false

```

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
Fetch the Thanos host, for Prometheus metrics access using one of the following options based on your setup:

-
If Grafana is installed outside the OpenShift cluster or is connecting to an external OpenShift cluster, fetch the Thanos host using the following command:

```

oc get route thanos-querier -n openshift-monitoring -o json | jq -r '.spec.host'

```

```

thanos-querier-openshift-monitoring.tp-nextpx-iks-catalog-pl-80e1e1cd66534115bf44691bf8f01a6b-0000.us-south.containers.appdomain.cloud

```

-
If Grafana is installed within the same OpenShift cluster, you can directly use the internal service DNS:

```

https://thanos-querier.openshift-monitoring.svc.cluster.local:9091

```

Configure Autopilot to use the retrieved Thanos route host to access Prometheus metrics.

## Enable Kube Datastore metrics​

Kube Datastore metrics are generated from storage pool metrics by Prometheus recording rules installed by the Portworx Operator in the `portworx` `PrometheusRule`. On OpenShift, you must add the required labels to this `PrometheusRule` so that OpenShift monitoring evaluates the recording rules.

-
Add the required labels to the `portworx` `PrometheusRule`:

```

kubectl -n <portworx-namespace> patch prometheusrule portworx \

  --type merge -p '{

    "metadata": {

      "labels": {

        "openshift.io/user-monitoring": "true",

        "openshift.io/prometheus-rule-evaluation-scope": "leaf-prometheus"

      }

    }

  }'

```

```

prometheusrule.monitoring.coreos.com/portworx patched

```

-
Verify that Prometheus reports Kube Datastore metrics by querying a metric such as `px_kube_datastore_total_bytes`.

For the list of available metrics, see Kube Datastore metrics.

## Configure Autopilot​

important

When configuring Autopilot, the use of self-signed certificates for the default Ingress is supported in on-premises environments.

Edit the Autopilot spec within the Portworx manifest. Include the Thanos Querier host URL you retrieved in the step above. Replace `<THANOS-QUERIER-HOST>` with the actual host URL:

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

You can connect to Prometheus using Grafana to visualize your data. Grafana is a multi-platform open source analytics and interactive visualization web application. It provides charts, graphs, and alerts.

note

- Grafana is critical for observability hence you should reserve sufficient CPU and memory for it.

- The following steps use the `portworx` namespace. If you want to install in a different namespace, replace all instances of `portworx` with your namespace.

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

oc  -n portworx apply -f https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana-service-account.yaml

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
On the `url: https://<THANOS_QUERIER_HOST>` line, replace `<THANOS_QUERIER_HOST>` with the URL you retrieved in the Fetch the Thanos Querier route host section:

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

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-nbdd-dashboard.json" -o portworx-nbdd-dashboard.json && \

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-source-disks-performance-dashboard.json" -o portworx-source-disks-performance-dashboard.json && \

# Optional: Following files are required only if you need to monitor API requests sent to FlashArray.

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/fa-apis-dashboard1.json" -o fa-apis-dashboard1.json && \

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/fa-apis-dashboard2.json" -o fa-apis-dashboard2.json && \

# Optional: Following file is required only if you use Stork for DR/migrations

curl "https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-dr-dashboard.json" -o portworx-dr-dashboard.json

```

```

oc -n portworx create configmap grafana-dashboards \

--from-file=portworx-cluster-dashboard.json \

--from-file=portworx-performance-dashboard.json \

--from-file=portworx-node-dashboard.json \

--from-file=portworx-volume-dashboard.json \

--from-file=portworx-etcd-dashboard.json \

--from-file=portworx-nbdd-dashboard.json \

--from-file=portworx-source-disks-performance-dashboard.json \

# Optional: Following dashboards are required only if you need to monitor API requests sent to FlashArray.

--from-file=fa-apis-dashboard1.json \

--from-file=fa-apis-dashboard2.json \

# Optional: Following dashboard is required only if you use Stork for DR/migrations

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
