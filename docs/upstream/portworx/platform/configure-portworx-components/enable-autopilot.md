# Portworx Autopilot

Source: https://docs.portworx.com/portworx-enterprise/platform/configure-portworx-components/enable-autopilot (Portworx Enterprise latest)

Portworx Autopilot | Portworx Enterprise Documentation

Autopilot is a rule-based engine that responds to changes based on metric conditions and then automatically takes actions such as adding capacity, rebalancing storage and so on. Autopilot allows you to specify monitoring conditions along with actions it should take when the conditions occur.

A user creates a Portworx Autopilot rule. When an event occurs that is defined by an Autopilot rule, Autopilot can take a decision by fetching and using the metrics from the monitoring source configured on your cluster.

Autopilot allows your cluster to react dynamically without your intervention to events such as:

- Resizing PVCs when it is running out of capacity

- Scaling Portworx storage pools to accommodate increasing usage

- Rebalancing volumes across Portworx storage pools when they come unbalanced

This topic describes the steps to configure and upgrade Portworx Autopilot.

## Configure Autopilot​

Configuring Autopilot with Portworx on a Kubernetes cluster includes the following:

- Configure Metrics Collection

- Enable Autopilot with Portworx

- Customize Autopilot

- Configure Autopilot with PX-Security

### Configure Metrics Collection​

Portworx Enterprise requires you to Enable Prometheus, Enable Datadog, or Enable Azure Monitor to allow the agents to collect Portworx metrics.

#### Enable Prometheus​

Ensure that your cluster has a running Prometheus so that Autopilot can fetch the metrics from it and take actions if the monitoring conditions are met.

- OpenShift

- Kubernetes

Autopilot requires a running OpenShift Prometheus instance in your cluster. If you don't have Prometheus configured in your cluster, refer to the Observability section to set it up.

After you have enabled OpenShift Prometheus, fetch the Thanos host, which is part of the OpenShift monitoring stack.

```

oc get route thanos-querier -n openshift-monitoring -o json | jq -r '.spec.host'

```

```

thanos-querier-openshift-monitoring.tp-nextpx-iks-catalog-pl-80e1e1cd66534115bf44691bf8f01a6b-0000.us-south.containers.appdomain.cloud

```

Configure Autopilot using the above route host to enable its access to Prometheus's statistics.

Autopilot requires a running Prometheus instance in your cluster. If you don't have Prometheus configured in your cluster, refer to the Observability section to set it up.

After you have Prometheus running, find the Prometheus service endpoint in your cluster. Depending on how you installed Prometheus, the precise steps to find this may vary. In most clusters, you can find a service named Prometheus:

```

kubectl get service -n portworx prometheus

```

```

NAME         TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)          AGE

prometheus   LoadBalancer   10.0.201.44   X.X.X.0       9090:30613/TCP   11d

```

In the example above, `http://prometheus:9090` becomes the Prometheus endpoint. Portworx uses this endpoint in the Autopilot Configuration section.

note

Why `http://prometheus:9090` ?

`prometheus` is the name of the Kubernetes service for Prometheus in the portworx namespace. Since Autopilot also runs as a pod in the `portworx` namespace, it can access Prometheus using its Kubernetes service name and port.

#### Enable Datadog​

Autopilot uses Datadog’s Metrics API and needs a Datadog API key and Application key to authenticate. Create a Kubernetes Secret to provide these details. Here is an example manifest where you can replace the namespace, secret name, and encoded key values as required.

```

apiVersion: v1

kind: Secret

metadata:

  name: datadog-autopilot-credentials

  namespace: datadog-ns

  labels:

    app: autopilot

    component: datadog-provider

type: Opaque

data:

  # Base64 encoded Datadog API Key

  api-key: <base64-encoded-api-key>

  # Base64 encoded Datadog Application Key

  app-key: <base64-encoded-app-key>

```

Ensure that Autopilot has RBAC permission to read this Secret. The `app-key` must have metrics `Read` permission. The next step is to configure Datadog Agent to export Portworx metrics. Refer to the official Datadog Documentation to configure the Datadog agent. The steps mentioned below are a recommended approach to install and configure Datadog.
 Configure Datadog Agent to export PX metrics (Recommended)

-
Install Datadog using Helm chart with the following values config file:

```

datadog:

  site: "datadoghq.com"

  clusterName: "your-cluster-name"

  apiKeyExistingSecret: "datadog-autopilot-credentials"

  kubelet:

    tlsVerify: false

  clusterChecks:

    enabled: true

  orchestratorExplorer:

    enabled: true

  clusterAgent:

    enabled: true

    admissionController:

      enabled: true

      mutateUnlabelled: false

```

Replace `site`, `clusterName`, and `apiKeyExistingSecret` and save it in a file `datadog_config.yaml`. The Agent will be responsible for scraping PX metrics and sending them to Datadog.

```

helm repo add datadog https://helm.datadoghq.com

helm upgrade --install datadog-agent datadog/datadog -f ./datadog_config.yaml

```

This should bring up the Datadog Agent.

-
Portworx supports annotating Portworx, Stork, and Autopilot components in accordance with Datadog documentation. It is recommended to annotate component pods by adding Datadog annotations to `componentk8sconfig` so that the Datadog Agent knows which endpoints to scrape. For Portworx, use a host-based OpenMetrics endpoint with the Datadog `%%host%%` template (resolved by Datadog to the pod/host IP):

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: datadog-components-config

  namespace: portworx

spec:

  components:

    - componentNames:

        - Portworx API

      workloadConfigs:

        - workloadNames:

            - portworx-api

          annotations:

            ad.datadoghq.com/portworx-api.checks: |-

              {

                "openmetrics": {

                  "instances": [

                    {

                      "openmetrics_endpoint": "http://%%host%%:9001/metrics",

                      "namespace": "portworx",

                      "metrics": ["px_*"]

                    }

                  ]

                }

              }

    - componentNames:

        - Stork

      workloadConfigs:

        - workloadNames:

            - stork

          annotations:

            ad.datadoghq.com/stork.checks: |-

              {

                "openmetrics": {

                  "instances": [

                    {

                      "openmetrics_endpoint": "http://%%host%%:8099/metrics",

                      "namespace": "portworx",

                      "metrics": ["stork_*"]

                    }

                  ]

                }

              }

    - componentNames:

        - Autopilot

      workloadConfigs:

        - workloadNames:

            - autopilot

          annotations:

            ad.datadoghq.com/autopilot.checks: |-

              {

                "openmetrics": {

                  "instances": [

                    {

                      "openmetrics_endpoint": "http://%%host%%:9628/metrics",

                      "namespace": "portworx",

                      "metrics": ["autopilot_*"]

                    }

                  ]

                }

              }

```

note

- For Portworx API, `openmetrics_endpoint` is exposed on port 17001 for OpenShift and on port 9001 for Kubernetes.

- For most use cases, `portworx-api` metrics would be enough for AutopilotRule. It is recommended to remove the annotations from the above manifest for Autopilot and Stork components if you choose not to utilize them.

- You may choose the `metrics:` field to filter the metrics being scraped by the Datadog agent. Using `*` will cause a surge in metrics and spike costs for the Datadog instance. You are advised to only whitelist metrics which will be used in AutopilotRules.

#### Enable Azure Monitor​

Autopilot can query Portworx metrics from Azure Monitor Managed Prometheus. Azure Monitor requires OAuth 2.0 client credentials authentication. Autopilot fetches a short-lived access token from Microsoft Entra ID using the client credentials that you provide, attaches it to every query as a Bearer token, and refreshes it before it expires.

Before you begin, ensure that:

- You have the tenant ID, client ID, and client secret of the Microsoft Entra application that Autopilot uses to authenticate.

- You have assigned the Monitoring Data Reader role on the Azure Monitor workspace to the Microsoft Entra application. Autopilot only queries metrics, so you do not need the Monitoring Metrics Publisher role, which is used for metric ingestion.

To enable Azure Monitor for Autopilot, perform the following steps:

-
Create a Kubernetes Secret with the Microsoft Entra application credentials. Replace the namespace, secret name, and key values as required.

```

apiVersion: v1

kind: Secret

metadata:

  name: autopilot-prom-azure

  namespace: portworx

type: Opaque

stringData:

  auth.token_url: "https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token"

  auth.client_id: "<azure-app-client-id>"

  auth.client_secret: "<azure-app-client-secret>"

  auth.scope: "https://prometheus.monitor.azure.com/.default"

```

The following table describes the keys in the Secret:

KeyRequiredDescription

`auth.token_url`YesMicrosoft Entra ID v2.0 token endpoint that Autopilot uses to fetch the access token. Use `https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token`.

`auth.client_id`YesClient ID of the Microsoft Entra application.

`auth.client_secret`YesClient secret of the Microsoft Entra application.

`auth.scope`YesScope of the access token. For Azure Monitor, use `https://prometheus.monitor.azure.com/.default`.

`auth.resource`NoResource that the token is issued for. It is optional with the v2.0 endpoint.

important

Use the v2.0 token endpoint (`/oauth2/v2.0/token`). Autopilot cannot parse the token response from the v1 endpoint (`/oauth2/token`), and the token fetch fails.

-
Update the StorageCluster specification to add Azure Monitor as a Prometheus provider. Set `url` to the query endpoint of your Azure Monitor workspace, and `secretName` and `secretNamespace` to the Secret that you created.

```

kind: StorageCluster

spec:

  autopilot:

    enabled: true

    providers:

      - name: azure-monitor

        type: prometheus

        params:

          url: https://<workspace>.<region>.prometheus.monitor.azure.com

          secretName: autopilot-prom-azure

          secretNamespace: portworx

```

note

Autopilot supports only one provider of each type. If a provider of type `prometheus` already exists, replace it with the Azure Monitor provider details instead of adding another one.

-
Apply the updated StorageCluster specification and wait for Autopilot to roll out.

After Autopilot starts, it fetches an access token and refreshes it in the background. To rotate the client secret, update the Secret. Autopilot picks up the change at its next token refresh, and you do not need to restart the Autopilot deployment.

note

Autopilot logs only the HTTP status code and the OAuth 2.0 error code when a token request fails. Check the Autopilot logs if queries fail with `401` or `403` errors.

### Enable Autopilot with Portworx​

To enable Autopilot if you did not enable it during spec generation in Portworx Central, update the StorageCluster specification as follows:

```

kind: StorageCluster

spec:

  autopilot:

    enabled: true

```

Setting `spec.autopilot.enabled: true` in the StorageCluster specification enables Autopilot on the cluster.

For Datadog make the following additional changes to the StorageCluster specification as shown below:

```

kind: StorageCluster

spec:

  autopilot:

    enabled: true

    providers:

      - name: datadog

        type: datadog

        params:

          url: https://datadoghq.com

          secretName: datadog-autopilot-credentials

          secretNamespace: datadog-ns

  monitoring:

    prometheus:

      enabled: false

      exportMetrics: true

```

In this configuration, the following will be the impact:

- Datadog will be used as a provider by Autopilot when `spec.autopilot.providers.name` and `spec.autopilot.providers.type` are set to `datadog`.

- `secretName` and `secretNamespace` will be used from the Secret created while enabling Datadog to scrape the metrics.

- Both Datadog and Prometheus are supported simultaneously as well as on their own. However, an AutopilotRule, once configured with one of the providers, cannot interchangeably work with the other provider.

Apply the updated StorageCluster spec to the cluster and wait for Autopilot to roll out with Datadog support. If Datadog `secret` is updated, then restart the Autopilot `deployment` to fetch new changes.
 Configure proxy details to use Datadog provider in an Airgapped environment

To use Datadog as metrics provider in an airgapped cluster, add proxy server details in Storage Cluster as shown below.

```

autopilot:

    enabled: true

    env:

    - name: HTTPS_PROXY

      value: http://10.xx.xxx.xxx:3128

```

When the proxy environment variables are configured, all HTTP and HTTPS requests go through the proxy by default. Use the `NO_PROXY` environment variable to specify a comma-separated list of addresses or domains that bypass the proxy and communicate directly. This is essential for internal cluster communication, such as Kubernetes services (`.svc`, `.cluster.local`), loopback addresses (`localhost`, `127.0.0.1`), and pod and service CIDR ranges (for example, `10.0.0.0/8`).

### Customize Autopilot​

You can customize Autopilot by specifying configuration parameters to the Autopilot spec within your Portworx StorageCluster manifest. The following example shows how to customize Autopilot configuration to use a custom Prometheus URL and update the log level to debug based on your requirement.

- OpenShift

- Kubernetes

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

...

spec:

  autopilot:

    enabled: true

    image: portworx/autopilot:1.3.14

    providers:

    - name: default

      params:

        url: https://<THANOS-QUERIER-HOST>

      type: prometheus

    args:

      log-level: debug

```

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

...

spec:

  autopilot:

    enabled: true

    image: portworx/autopilot:1.3.14

    providers:

    - name: default

      params:

        url: http://px-prometheus:9090 # If you are using an external Prometheus, update the url with external Prometheus endpoint.

      type: prometheus

    args:

      log-level: debug

```

### Configure Autopilot with PX-Security​

To configure Autopilot with PX-Security using the Operator, modify the StorageCluster manifest. Add the following PX_SHARED_SECRET env var to the `spec.autopilot`:

```

  autopilot:

...

    env:

    - name: PX_SHARED_SECRET

      valueFrom:

        secretKeyRef:

          key: apps-secret

          name: px-system-secrets

```

### Configure Autopilot with Custom CA Certificates​

This section describes how to configure Autopilot to communicate with a Prometheus instance that uses self-signed or third-party signed TLS certificates.

- Kubernetes

- OpenShift

Use these steps to reach the Prometheus endpoint on a Kubernetes cluster that uses a self-signed or third-party signed CA certificate.

-
Create a secret that will store your custom CA cert.

```

kubectl -n portworx create secret generic px-autopilot-ca --from-file=public.crt

```

-
Update the Autopilot spec in the StorageCluster to mount the certificate

```

spec:

  autopilot:

    volumes:

    - name: px-autopilot-ca-cert

      mountPath: /etc/ssl/px-custom/

      secret:

        secretName: px-autopilot-ca

        items:

        - key: public.crt

          path: public.crt

```

Updating StorageCluster will restart Autopilot service and enable the access to the endpoint that is using self-signed or third-party signed CA certificate.

Use these steps when Autopilot needs to reach the OpenShift internal Thanos Querier endpoint: https://thanos-querier.openshift-monitoring.svc.cluster.local:9091, which uses a self-signed or third-party signed CA certificate.

-
Extract the CA certificate from the thanos-querier-tls secret:

```

SERVICE_CA_B64=$(oc get secret -n openshift-monitoring thanos-querier-tls -o jsonpath='{.data.tls\.crt}')

```

This command extracts the secret and saves it in SERVICE_CA_B64.

-
Patch the Autopilot Prometheus auth secret with the CA certificate:

```

oc -n portworx patch secret autopilot-prometheus-auth --type='json' \

  -p="[{\"op\":\"replace\",\"path\":\"/data/ca.cert\",\"value\":\"${SERVICE_CA_B64}\"}]"

```

This command patches the Autopilot Prometheus auth secret with the base64-encoded CA certificate.

note

`autopilot-prometheus-auth` secret is created when Autopilot and monitoring are enabled.

-
Update the Autopilot spec in the StorageCluster to mount the certificate and set the SSL_CERT_FILE environment variable:

```

spec:

  autopilot:

    env:

    - name: SSL_CERT_FILE

      value: /etc/ssl/px-custom/ca.cert

    volumes:

    - name: token-volume

      mountPath: /etc/ssl/px-custom/

      secret:

        defaultMode: 420

        items:

        - key: token

          path: token

        - key: ca.cert

          path: ca.cert

        secretName: autopilot-prometheus-auth

```

Updating StorageCluster will restart Autopilot service and should get this endpoint working: `https://thanos-querier.openshift-monitoring.svc.cluster.local:9091`

## Upgrade Autopilot​

To upgrade Autopilot, follow the appropriate procedure based on your setup:

### To latest Autopilot image without upgrading Portworx​

Portworx Operator takes care of updating all the components including Autopilot based on the update strategy. If `spec.autoUpdateComponents` is set to `Always` in the StorageCluster, Portworx will check for updates on a regular interval and update the Autopilot image if a new version is released.

### To a custom Autopilot image without upgrading Portworx​

To upgrade Autopilot to a custom image:

- Update the `configmap/px-versions` with the desired custom Autopilot image.

- Add the `autoUpdateComponents` field to the storage cluster specification:

```

kind: StorageCluster

spec:

  autoUpdateComponents: Once

```

This will prompt the Portworx Operator to reconcile the Autopilot component and pull the latest image from the updated ConfigMap.

### Along With Portworx Upgrade without ConfigMap​

-
Delete the `configmap/px-versions` file.

When Portworx is upgraded, the Operator will automatically upgrade all installed components, including Autopilot, to the recommended versions.

-
Upgrade the Portworx image in the storage cluster specification to proceed with the upgrade.

### Along With Portworx Upgrade with ConfigMap​

-
Download the latest Portworx version manifest:

```

curl -o versions.yaml "https://install.portworx.com/$<portworx-version>/version?kbver=$<kubernetes-version>&opver=$<operator-version>"

```

Replace:

- `<portworx_version>` with the Portworx version you want to use.

- `<kubernetes-version>` with the Kubernetes version you want to use.

- `<operator-version>` with the Operator version you want to use.

-
Update the px-versions ConfigMap with the downloaded version manifest:

```

kubectl -n <px-namespace> delete configmap px-versions

kubectl -n <px-namespace> create configmap px-versions --from-file=versions.yaml

```

-
Add the `autoUpdateComponents` field to the storage cluster specification:

```

kind: StorageCluster

spec:

  autoUpdateComponents: Once

```

This will prompt the Portworx Operator to reconcile all components and retrieve the latest images from the ConfigMap if available, or download them from the manifest if not.

## What to do next​

Create an Autopilot rule. For more information, see Automate storage operations with Autopilot

In this topic:
