# Configure Portworx Monitoring on Kubernetes

Source: https://docs.portworx.com/portworx-enterprise/operations/observability/set-kubernetes-prometheus (Portworx Enterprise latest)

Configure Portworx Monitoring on Kubernetes | Portworx Enterprise Documentation

This topic provides instructions on how to configure monitoring for Portworx deployments on a Kubernetes cluster.

## Configure Prometheus​

You can monitor your Portworx cluster using Prometheus. Select a tab based on the Prometheus instance you want to use.

- PX Prometheus

- External Prometheus

-
Set `spec.monitoring.prometheus.enabled: true` in the `StorageCluster` spec.

-
Verify that Prometheus pods are running by entering the following command in the namespace where you deployed Portworx:

```

kubectl -n <px-namespace> get pods -A | grep -i prometheus

```

```

<px-namespace>   prometheus-px-prometheus-0                              2/2     Running            0                59m

<px-namespace>   px-prometheus-operator-59b98b5897-9nwfv                 1/1     Running            0                60m

```

-
Verify that the Prometheus `px-prometheus` and `prometheus-operated` services exist:

```

kubectl -n <px-namespace> get service | grep -i prometheus

```

```

prometheus-operated         ClusterIP   None             <none>        9090/TCP                       63m

px-prometheus               ClusterIP   10.99.61.133     <none>        9090/TCP                       63m

```

To monitor Portworx using an external Prometheus instance, disable PX Prometheus and enable `exportMetrics`.

-
In the `StorageCluster` spec, configure the following:

```

spec:

  monitoring:

    prometheus:

      enabled: false

      exportMetrics: true

```

-
Ensure that you have a `ServiceMonitor` named `portworx` exists in the namespace where you deployed Portworx :

```

kubectl get servicemonitor -n <portworx>

```

```

NAME        AGE

portworx    18h

```

-
Ensure your external Prometheus instance is configured to discover `ServiceMonitor` resources across namespaces.
 In the Prometheus CRD, set the following:

```

serviceMonitorNamespaceSelector: {}

```

-
Verify that the Prometheus Operator is running and scraping targets:

```

kubectl get pods -n <external-prometheus-namespace>

```

After configuring an external Prometheus, you must specify its endpoint in the Autopilot configuration. For more information, see Autopilot Install and Setup.

### Access the Prometheus UI​

To access the Prometheus UI to view Status, Graph and default Alerts, you also need to set up port forwarding and browse to the specified port. In this example, Port forwarding is provided for ease of access to the Prometheus UI service from your local machine using the port 9090.

-
Set up port forwarding:

```

kubectl -n <px-namespace> port-forward service/px-prometheus 9090:9090

```

-
Access the Prometheus UI by browsing to `http://localhost:9090/alerts`.

## Configure Alertmanager​

Prometheus Alertmanager handles alerts sent from the Prometheus server based on rules you set. If any Prometheus rule is triggered, Alertmanager sends a corresponding notification to the specified receivers. You can configure these receivers using an Alertmanager config file. Perform the following steps to configure and enable Alertmanager:

-
Create a valid Alertmanager configuration file and name it `alertmanager.yaml`. The following is a sample for Alertmanager, and the settings used in your environment may be different:

```

global:

  # The smarthost and SMTP sender used for mail notifications.

  smtp_smarthost: 'smtp.gmail.com:587'

  smtp_from: 'username@company.com'

  smtp_auth_username: "username@company.com"

  smtp_auth_password: 'xyxsy'

route:

  group_by: [Alertname]

  # Send all notifications to me.

  receiver: email-me

receivers:

- name: email-me

  email_configs:

  - to: username@company.com

    from: username@company.com

    smarthost: smtp.gmail.com:587

    auth_username: "username@company.com"

    auth_identity: "username@company.com"

    auth_password: "username@company.com"

```

-
Create a secret called `alertmanager-portworx` in the same namespace as your StorageCluster object:

```

kubectl -n <px-namespace> create secret generic alertmanager-portworx --from-file=alertmanager.yaml=alertmanager.yaml

```

-
Edit your StorageCluster object to enable Alertmanager:

```

kubectl -n <px-namespace> edit stc <px-cluster-name>

```

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

monitoring:

    prometheus:

      enabled: true

      exportMetrics: true

      alertManager:

        enabled: true

```

-
Verify that the Alertmanager pods are running using the following command:

```

kubectl -n <px-namespace> get pods | grep -i alertmanager

```

```

alertmanager-portworx-0                    2/2     Running   0              4m9s

alertmanager-portworx-1                    2/2     Running   0              4m9s

alertmanager-portworx-2                    2/2     Running   0              4m9s

```

note

To view the complete list of out-of-the-box default rules, see View provided Prometheus rules.

### Access the Alertmanager UI​

To access the Alertmanager UI and view the Alertmanager Status and alerts, you need to set up port forwarding and browse to the specified port. In this example, port forwarding is provided for ease of access to the Alertmanager service from your local machine using the port 9093.

-
Set up port forwarding:

```

kubectl -n <px-namespace> port-forward service/alertmanager-portworx --address=<masternodeIP> 9093:9093

```

-
Access Prometheus UI by browsing to `http://<masternodeIP>:9093/#/status`

note

Portworx Central on-premises includes Grafana and Portworx dashboards natively, which you can use to monitor your Portworx cluster. Refer to the Portworx Central documentation for further details.

### View provided Prometheus rules​

To view the complete list of out-of-the-box default rules used for event notifications, perform the following steps.

-
Get the Prometheus rules:

```

kubectl -n <px-namespace> get prometheusrules

```

```

NAME       AGE

portworx   46d

```

-
Save the Prometheus rules to a YAML file:

```

kubectl -n <px-namespace> get prometheusrules portworx -o yaml > prometheusrules.yaml

```

-
View the contents of the file:

```

cat prometheusrules.yaml

```

## Configure Grafana​

You can connect to Prometheus using Grafana to visualize your data. Grafana is a multi-platform open source analytics and interactive visualization web application. It provides charts, graphs, and alerts.

note

Grafana is critical for observability hence reserve sufficient CPU and memory for it.

-
Enter the following commands to download the Grafana dashboard and datasource configuration files:

```

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana-dashboard-config.yaml

```

```

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana-datasource.yaml

```

-
Create a configmap for the dashboard and data source:

```

kubectl -n <px-namespace> create configmap grafana-dashboard-config --from-file=grafana-dashboard-config.yaml

```

```

kubectl -n <px-namespace> create configmap grafana-source-config --from-file=grafana-datasource.yaml

```

-
Download and install Grafana dashboards using the following commands:

```

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-cluster-dashboard.json

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-node-dashboard.json

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-volume-dashboard.json

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-performance-dashboard.json

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-etcd-dashboard.json

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-nbdd-dashboard.json

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-source-disks-performance-dashboard.json

# Optional: Following files are required only if you need to monitor API requests sent to FlashArray.

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/fa-apis-dashboard1.json

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/fa-apis-dashboard2.json

# Optional: Following file is required only if you use Stork for DR/migrations

wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/portworx-dr-dashboard.json

```

```

kubectl -n <px-namespace> create configmap grafana-dashboards \

--from-file=portworx-cluster-dashboard.json \

--from-file=portworx-performance-dashboard.json \

--from-file=portworx-node-dashboard.json \

--from-file=portworx-volume-dashboard.json \

--from-file=portworx-etcd-dashboard.json  \

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

kubectl -n <px-namespace> apply -f https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana.yaml

```

note

For the SUSE Linux Micro distribution, download the grafana.yaml file using the command `wget https://docs.portworx.com/portworx-enterprise/samples/k8s/pxc/grafana.yaml`. We recommend to update the Grafana image version to `9.5.21` in the downloaded file and use this file name in the command above.

-
Verify if the Grafana pod is running using the following command:

```

kubectl -n <px-namespace> get pods | grep -i grafana

```

```

grafana-7d789d5cf9-bklf2                   1/1     Running   0              3m12s

```

-
Access Grafana by setting up port forwarding and browsing to the specified port. In this example, port forwarding is provided for ease of access to the Grafana service from your local machine using the port 3000:

```

kubectl -n <px-namespace> port-forward service/grafana 3000:3000

```

-
Navigate to Grafana by browsing to `http://localhost:3000`.

-
Enter the default credentials to log in.

- login: `admin`

- password: `admin`

## Install Node Exporter​

After you have configured Grafana, install the Node Exporter binary. For Portworx, Node Exporter collects key metrics such as Network Sent/Received, Volume, Latency, Input/Output Operations per Second (IOPS), and Throughput, which Grafana can visualize to monitor these resources.

The following DaemonSet will be running in the `portworx` namespace.

note

The examples below use the `portworx` namespace, you should update this to the correct namespace for your environment. Be sure to install in the same namespace where Prometheus and Grafana are running.

-
Install node-exporter via DaemonSet by creating a YAML file named `node-exporter.yaml`:

```

apiVersion: apps/v1

kind: DaemonSet

metadata:

  labels:

    app.kubernetes.io/component: exporter

    app.kubernetes.io/name: node-exporter

  name: node-exporter

  namespace: portworx

spec:

  selector:

    matchLabels:

      app.kubernetes.io/component: exporter

      app.kubernetes.io/name: node-exporter

  template:

    metadata:

      labels:

        app.kubernetes.io/component: exporter

        app.kubernetes.io/name: node-exporter

    spec:

      containers:

      - args:

        - --path.sysfs=/host/sys

        - --path.rootfs=/host/root

        - --no-collector.wifi

        - --no-collector.hwmon

        - --collector.filesystem.ignored-mount-points=^/(dev|proc|sys|var/lib/docker/.+|var/lib/kubelet/pods/.+)($|/)

        - --collector.netclass.ignored-devices=^(veth.*)$

        name: node-exporter

        image: prom/node-exporter

        ports:

          - containerPort: 9100

            protocol: TCP

        resources:

          limits:

            cpu: 250m

            memory: 180Mi

          requests:

            cpu: 102m

            memory: 180Mi

        volumeMounts:

        - mountPath: /host/sys

          mountPropagation: HostToContainer

          name: sys

          readOnly: true

        - mountPath: /host/root

          mountPropagation: HostToContainer

          name: root

          readOnly: true

      volumes:

      - hostPath:

          path: /sys

        name: sys

      - hostPath:

          path: /

        name: root

```

-
Apply the object using the following command:

```

kubectl apply -f node-exporter.yaml -n portworx

```

```

daemonset.apps/node-exporter created

```

### Create a service​

Kubernetes service will connect a set of pods to an abstracted service name and IP address. The service provides discovery and routing between the pods. The following service will be called `node-exportersvc.yaml`, and it will use port `9100`.

-
Create the object file and name it `node-exportersvc.yaml`:

```

---

kind: Service

apiVersion: v1

metadata:

  name: node-exporter

  namespace: portworx

  labels:

    name: node-exporter

spec:

  selector:

      app.kubernetes.io/component: exporter

      app.kubernetes.io/name: node-exporter

  ports:

  - name: node-exporter

    protocol: TCP

    port: 9100

    targetPort: 9100

```

-
Create the service by running the following command:

```

kubectl apply -f node-exportersvc.yaml -n portworx

```

```

service/node-exporter created

```

### Create a service monitor​

The Service Monitor will scrape the metrics using the following `matchLabels` and endpoint.

-
Create the object file and name it `node-exporter-svcmonitor.yaml`:

```

apiVersion: monitoring.coreos.com/v1

kind: ServiceMonitor

metadata:

  name: node-exporter

  labels:

    prometheus: portworx

spec:

  selector:

    matchLabels:

      name: node-exporter

  endpoints:

  - port: node-exporter

```

-
Create the `ServiceMonitor` object by running the following command:

```

kubectl apply -f node-exporter-svcmonitor.yaml -n portworx

```

```

servicemonitor.monitoring.coreos.com/node-exporter created

```

-
Verify that the `prometheus` object has the following `serviceMonitorSelector:` appended:

```

kubectl get prometheus -n portworx -o yaml

```

```

    serviceMonitorSelector:

  matchExpressions:

  - key: prometheus

    operator: In

    values:

    - portworx

    - px-backup

```

The `serviceMonitorSelector` object is automatically appended to the `prometheus` object that is deployed by the Portworx Operator. The `ServiceMonitor` will match any `serviceMonitor` that has the key `prometheus` and value of `portworx` or `backup`

In this topic:
