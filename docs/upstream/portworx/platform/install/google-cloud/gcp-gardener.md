# Installation on a GCP Gardener Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/google-cloud/gcp-gardener (Portworx Enterprise latest)

Installation on a GCP Gardener Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx Enterprise on a Gardener cluster running on Google Cloud Platform (GCP). Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

note

On GCP, Portworx authenticates to Google Cloud APIs using Workload Identity Federation. GKE Workload Identity is not supported because Portworx pods run with `hostNetwork: true`, which bypasses the iptables rules used by the GKE metadata server.

The following collection of tasks describes how to install Portworx Enterprise on a GCP Gardener cluster:

- Create a Shoot Cluster

- Configure Authentication

- Install Node Packages

- Install Portworx

- Monitor Portworx Nodes

- Verify Portworx Pod Status

- Verify Portworx Cluster Status

- Verify Portworx Pool Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx.

## Create a Shoot Cluster​

Use the Gardener dashboard or the Gardener API to create a shoot cluster on GCP. The shoot specification controls the worker node GCE instances, networking, and the OIDC issuer that Portworx federates against when using Workload Identity.

-
Sign in to your Gardener dashboard, or set up `kubectl` access to your Gardener landscape.

-
Create a shoot cluster on the `gcp` provider. In the shoot specification, ensure the following fields are set:

- `spec.cloudProfile.name: gcp`

- `spec.region` — set to the GCP region where Portworx will run.

- `spec.provider.workers` — define the worker pools. Each worker pool's GCE instances run with their own GCP service account (the node service account) that Portworx will be granted access to.

-
Once the shoot is reconciled, download its `kubeconfig` from the Gardener dashboard or via `kubectl`, and confirm you can reach the cluster:

```

kubectl get nodes

```

-
SAP Gardener automatically configures a public OIDC issuer for every shoot cluster. No manual setup is required. Verify that the issuer is present:

```

kubectl get --raw /.well-known/openid-configuration | jq -r '.issuer'

```

This must return a non-empty HTTPS URL. If it is empty or the endpoint is unreachable, contact your Gardener administrator before proceeding.

-
Note the following values from your shoot. These values are required when you configure the authentication:

- The GCP project ID and project number hosting the shoot.

- The Gardener shoot cluster name.

- The OIDC issuer URL of the shoot.

For more information on shoot creation, see the Gardener documentation.

## Configure Authentication​

On GCP, Portworx uses Workload Identity Federation to authenticate to Google Cloud APIs without static service account keys. Portworx pods exchange a projected Kubernetes ServiceAccount token for short-lived Google Cloud credentials.
Before installing Portworx Enterprise, you must create a Google Cloud service account, grant it the required permissions, federate it with the Kubernetes service accounts that Portworx uses, and create the credential `ConfigMap` that the Portworx Operator mounts into the pods. For more information, see Workload identity for cloud operations in Portworx.

Before you begin, ensure you have:

- The `gcloud` CLI installed and authenticated (`gcloud auth login`).

- `kubectl` configured to talk to your Gardener shoot cluster.

- `jq` installed (used to parse OIDC discovery metadata).

- Owner or equivalent IAM permissions on the GCP project.

- Your GCP project ID and project number.

-
Set the following shell variables before running the remaining commands:

```

export PROJECT_ID="<your-gcp-project-id>"

```

Replace `<your-gcp-project-id>` with your actual GCP project ID.

```

# Fetched automatically from GCP — do not change this command

export PROJECT_NUMBER="$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')"

```

-
Create a Google Cloud service account that Portworx uses for Workload Identity authentication, and store its email address in an environment variable:

```

export PX_SA_NAME="portworx-wli-sa"

gcloud iam service-accounts create ${PX_SA_NAME} \

  --project="${PROJECT_ID}" \

  --display-name="Portworx Workload Identity SA"

export PX_SA_EMAIL="$(gcloud iam service-accounts list \

  --project="${PROJECT_ID}" \

  --filter="name:${PX_SA_NAME}" \

  --format='value(email)')"

echo "GSA Email: ${PX_SA_EMAIL}"

```

The `PX_SA_NAME` variable specifies the name of the Google Cloud service account. `portworx-wli-sa` is an example; you can use any valid service account name.

-
Grant the required IAM permissions to the Google Cloud service account that Portworx uses for Workload Identity authentication.

-
Create a custom role with the minimum permissions required for Portworx to manage disks, instances, disk attach and detach operations, and node group operations:

```

gcloud iam roles create portworx_wli_role \

  --project="${PROJECT_ID}" \

  --title="Portworx Workload Identity Role" \

  --description="Minimum permissions required by Portworx for disk and instance management" \

  --permissions="compute.disks.addResourcePolicies,compute.disks.create,compute.disks.createSnapshot,compute.disks.delete,compute.disks.get,compute.disks.getIamPolicy,compute.disks.list,compute.disks.removeResourcePolicies,compute.disks.resize,compute.disks.setIamPolicy,compute.disks.setLabels,compute.disks.update,compute.disks.use,compute.disks.useReadOnly,compute.instances.attachDisk,compute.instances.detachDisk,compute.instances.get,compute.nodeGroups.get,compute.nodeGroups.getIamPolicy,compute.nodeGroups.list,compute.zoneOperations.get,container.clusters.get" \

  --stage="GA"

```

-
Assign the custom role to the Portworx Google Cloud service account:

```

gcloud projects add-iam-policy-binding ${PROJECT_ID} \

  --member="serviceAccount:${PX_SA_EMAIL}" \

  --role="projects/${PROJECT_ID}/roles/portworx_wli_role" \

  --condition=None

```

-
Grant the `roles/iam.serviceAccountUser` role on the worker node service account to the Portworx Google Cloud service account.

important

- Each GCE worker node runs with its own GCP service account (the node SA). When Portworx attaches or detaches disks on a node, Google Cloud requires the Portworx service account to have the `roles/iam.serviceAccountUser` role on that node service account. For more information, see The Service Account User role and Attach disks.

- `CLUSTER_NAME` must match your Gardener shoot cluster name exactly, for example, `my-shoot`. Portworx uses this value to identify the correct worker node service account. If the value is incorrect, you might select a service account from another cluster in the same Google Cloud project.

-
Export the following environment variables:

```

export CLUSTER_NAME="<your-gardener-shoot-name>"

```

-
Get the email address of the node service account:

```

export NODE_SA_EMAIL="$(gcloud compute instances list \

--project="${PROJECT_ID}" \

--filter="name~${CLUSTER_NAME}" \

--format='value(serviceAccounts[0].email)' | sort -u | head -1)"

echo "Node SA: ${NODE_SA_EMAIL}"

```

-
Grant the required role to the Portworx service account on the node service account:

```

gcloud iam service-accounts add-iam-policy-binding ${NODE_SA_EMAIL} \

--project="${PROJECT_ID}" \

--member="serviceAccount:${PX_SA_EMAIL}" \

--role="roles/iam.serviceAccountUser"

```

-
Grant the Portworx Google Cloud service account access to the Google Cloud Storage bucket used for CloudSnap backups.

```

gcloud storage buckets add-iam-policy-binding gs://<your-gcs-bucket-name> \

  --member="serviceAccount:${PX_SA_EMAIL}" \

  --role="roles/storage.objectAdmin"

```

note

Use the same Google Cloud Storage bucket name when creating the `pxctl` credential for CloudSnap backups.

-
Create a Workload Identity Pool to group OIDC providers:

```

export POOL_ID="portworx-wi-pool"

gcloud iam workload-identity-pools create ${POOL_ID} \

  --project="${PROJECT_ID}" \

  --location="global" \

  --display-name="Portworx Workload Identity Pool"

```

The `POOL_ID` variable specifies the Workload Identity Pool name. The name must be unique within your GCP project.

-
Get the Gardener shoot OIDC issuer URL:

```

export OIDC_ISSUER="$(kubectl get --raw /.well-known/openid-configuration | jq -r '.issuer')"

echo "OIDC Issuer: ${OIDC_ISSUER}"

```

-
Create a Workload Identity Provider in the pool to link the cluster OIDC issuer to Google Cloud IAM:

```

export PROVIDER_ID="portworx-wi-provider"

export AUDIENCE="https://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"

gcloud iam workload-identity-pools providers create-oidc ${PROVIDER_ID} \

  --project="${PROJECT_ID}" \

  --location="global" \

  --workload-identity-pool="${POOL_ID}" \

  --issuer-uri="${OIDC_ISSUER}" \

  --allowed-audiences="${AUDIENCE}" \

  --attribute-mapping="google.subject=assertion.sub"

```

- `PROVIDER_ID` specifies the OIDC provider name in the pool. The name must be unique within the pool.

- `--allowed-audiences` must use the `https://iam.googleapis.com/...` format. The Portworx Operator reads this audience from the credential configuration `ConfigMap` and injects it into the projected `ServiceAccount` token using this `https://` format. The provider must allow this exact value.

- `--attribute-mapping="google.subject=assertion.sub"` maps the Kubernetes JWT `sub` claim (`system:serviceaccount:<namespace>:<sa-name>`) to the Google Cloud principal subject used in IAM bindings.

note

If the OIDC endpoint for your Gardener shoot cluster is not publicly reachable, download the JWKS file and add `--jwk-json-path=/tmp/cluster-jwks.json` to the provider creation command:

```

kubectl get --raw /openid/v1/jwks > /tmp/cluster-jwks.json

```

-
Bind the Kubernetes ServiceAccounts used by Portworx to the Google Cloud service account. Each Portworx component runs with a different Kubernetes ServiceAccount, and Google Cloud requires an explicit IAM binding for each one.

```

export K8S_NAMESPACE="portworx"

for SA in portworx stork px-node-wiper; do

  gcloud iam service-accounts add-iam-policy-binding ${PX_SA_EMAIL} \

    --project="${PROJECT_ID}" \

    --role="roles/iam.workloadIdentityUser" \

    --member="principal://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/subject/system:serviceaccount:${K8S_NAMESPACE}:${SA}"

done

```

- `K8S_NAMESPACE` specifies the namespace where Portworx is installed. Use `portworx` unless you installed Portworx in a custom namespace.

- The `portworx` service account is required for Portworx storage, the `stork` service account is required for Stork and Portworx Backup, and the `px-node-wiper` service account is required when uninstalling the `StorageCluster` with the `UninstallAndDelete` strategy.

-
Generate the credential configuration file that Portworx uses for Workload Identity authentication:

```

gcloud iam workload-identity-pools create-cred-config \

  "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}" \

  --service-account="${PX_SA_EMAIL}" \

  --credential-source-file="/var/run/service-account/token" \

  --credential-source-type="text" \

  --output-file="credential-configuration.json"

```

important

The `--credential-source-file` value must be `/var/run/service-account/token`. This is the path where the Portworx Operator mounts the projected ServiceAccount token inside the pods. Do not change this path.

-
Create the credential ConfigMap in the Portworx namespace:

```

kubectl create configmap px-gcp-wli-creds \

  --from-file=credential-configuration.json \

  -n ${K8S_NAMESPACE}

```

note

You can use any valid ConfigMap name. The examples in this topic uses `px-gcp-wli-creds`. When installing Portworx, set the `spec.workloadIdentity.gcp.credentialsConfigMap` field in the `StorageCluster` specification to the name of the ConfigMap you created.

-
Verify that the ConfigMap was created:

```

kubectl -n ${K8S_NAMESPACE} get configmap px-gcp-wli-creds -o yaml

```

Reference the `px-gcp-wli-creds` ConfigMap in the StorageCluster specification when installing Portworx.

## Install Node Packages​

Portworx requires the following operating system packages on every worker node before installation:

- `lvm2`

- `mdadm`

- `parted`

- `augeas-tools`

- `thin-provisioning-tools`

- `dmsetup`

- `nfs-kernel-server`

- `nfs-common`

- `rpcbind`

Portworx does not install operating system packages on Garden Linux worker nodes. If your Gardener cluster uses Garden Linux, ensure that these packages are preinstalled in the worker node image, or provisioned through your supported Gardener or organizational node provisioning process, before you install Portworx. For more information, contact Portworx Support.

## Install Portworx​

You can install Portworx Enterprise on a GCP Gardener cluster either by generating a Kubernetes specification through Portworx Central and applying it, or by deploying the Portworx Helm chart. In both cases, you enable Workload Identity by adding the `spec.workloadIdentity.gcp.credentialsConfigMap` field that references the `px-gcp-wli-creds` ConfigMap you created in the Configure Authentication section. Choose the installation mode that matches your tooling and operational preferences.

- Generate Specification

- Install using Helm

To install Portworx, you must first generate Kubernetes manifests that you will deploy in your GCP Gardener cluster by following these steps.

-
Sign in to the Portworx Central console.
 The system displays the Welcome to Portworx Central! page.

-
In the Portworx Enterprise section, select Generate Cluster Spec.
 The system displays the Generate Portworx Enterprise Spec page.

-
From the Portworx Version dropdown menu, select the Portworx version to install.

note

GCP Gardener is supported on Portworx Enterprise 3.6.2 or later.

-
From the Platform dropdown menu, select Google Cloud.

-
From the Distribution Name dropdown menu, select Gardener.

-
In the Credentials Config Map Name field, enter the name of the Kubernetes ConfigMap that stores the Workload Identity credential mapping used by Portworx components. Enter `px-gcp-wli-creds`, which is the ConfigMap you created in the Configure Authentication section.

-
In the Namespace field, enter the namespace where you plan to install Portworx.
 By default, the namespace is `portworx`. Use the same namespace (`K8S_NAMESPACE`) you used in the Configure Authentication section.

-
(Optional) To customize the configuration options and generate a custom specification, click Customize and perform the following steps:

note

To continue without customizing the default configuration or generating a custom specification, proceed to Step 9.

- Basic tab:

- Select one of the following:

- To use an existing etcd cluster, do the following:

- Select the Your etcd details option.

- In the field provided, enter the host name or IP and port number. For example, `http://test.com.net:1234`.
 To add another etcd cluster, click the + icon.

note

You can add up to three etcd clusters.

- Select one of the following authentication methods:

- Disable HTTPS – To use HTTP for etcd communication.

- Certificate Auth – To use HTTPS with an SSL certificate.
For more information, see Secure your etcd communication.

- Password Auth – To use HTTPS with username and password authentication.

- To use an internal Portworx-managed key-value store (kvdb), do the following:

- Select the Built-in option.

- TLS for internal KVDB is enabled, by default. If Cert-Manager is already running in your Kubernetes cluster, deselect the Deploy Cert-Manager for TLS certificates option to avoid installation failures.

- Click Next.

- Storage tab:

- Select one of the following:

- To enable Portworx to provision drives using a specification, do the following:

- Select the Create Using a Spec option.

- (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- (Optional) Select the Run on Small Node Configuration checkbox if your cluster nodes have limited resources (for example, 4 CPU cores and 8 GB of memory).
Portworx Enterprise requires 8 CPU cores and 8 GB of memory by default. Enabling this option allows Portworx to run on smaller nodes, but it may reduce overall performance compared to the default configuration.

note

This checkbox is available only when you select PX-StoreV2 as the datastore.

- To add one or more cloud storage drive types for Portworx to use, click + Add Drive and select one of the following types of drives:

- Standard

- SSD

- Balanced

note

- To select Standard as the drive type, you must select PX-StoreV1 as the datastore.

- For PX-StoreV2, four drives are recommended for optimal performance.

- Configure the following fields for the drive:

- Size (GB) - Specify the size of the disk in gigabytes.

- Encryption - Choose None to disable encryption or BYOK Encryption to encrypt your GCP cluster data disk using BYOK encryption.
For more information, see Encrypt Google Cloud drives.

- Encryption Key - If you choose BYOK Encryption, specify the key to use for BYOK encryption.
For more information, see Google Cloud KMS.

- Drive Tags - Add labels in `key:value` format to organize and identify drives.
 This is useful for policies and workload mapping.

- Action - Use the trash icon to remove a drive type from the configuration.

- Initial Storage Nodes (Optional): Enter the number of storage nodes that need to be created across zones and node pools.

- From the Default IO Profile dropdown menu, select Auto.
 This enables Portworx to automatically choose the best I/O profile based on detected workload patterns.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
 Enter the path of the journal device in the Journal Device Path field.

- To enable Portworx to use all available, unused, and unmounted drives on the node, do the following:

- Select the Consume Unused option.

- (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- (Optional) Select the Run on Small Node Configuration checkbox if your cluster nodes have limited resources (for example, 4 CPU cores and 8 GB of memory).
Portworx requires 8 CPU cores and 8 GB of memory by default. Enabling this option allows Portworx to run on smaller nodes, but it may reduce overall performance compared to the default configuration.

note

This checkbox is available only when you select PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
 The path must be at least 64 GB in size.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
 Enter the path of the journal device in the Journal Device Path field.

- Select the Use unmounted disks even if they have a partition or filesystem on it. Portworx will never use a drive or partition that is mounted checkbox to use unmounted disks, even if they contain a partition or filesystem.
 Portworx will not use any mounted drive or partition.

- To enable Portworx to use existing drives on a node, do the following:

- Select the Use Existing Drives option.

- (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- (Optional) Select the Run on Small Node Configuration checkbox if your cluster nodes have limited resources (for example, 4 CPU cores and 8 GB of memory).
Portworx requires 8 CPU cores and 8 GB of memory by default. Enabling this option allows Portworx to run on smaller nodes, but it may reduce overall performance compared to the default configuration.

note

This checkbox is available only when you select PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
The path must be at least 64 GB in size.

- In the Drive/Device field, specify the block drive(s) that Portworx uses for data storage.

- In the Pool Label field, assign a custom label in key:value format to identify and categorize storage pools.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
 Enter the path of the journal device in the Journal Device Path field.

- Click Next.

- Network tab:

- In the Interface(s) section, do the following:

- Enter the Data Network Interface to be used for data traffic.

- Enter the Management Network Interface to be used for management traffic.

- In the Advanced Settings section, do the following:

- Enter the Starting port for Portworx services.
 By default, the starting port is `9001`.

- Select Next.

- Deployment tab:

-
In the Kubernetes Distribution section, under Are you running on either of these?, select Gardener.

-
In the Component Settings section:

- (Optional) Select the Enable Stork checkbox to enable Stork.

- (Optional) Select the Remote Fastpath (NVMe-oF/TCP) checkbox to enable Remote Fastpath. For more information, see Remote Fastpath.

- (Optional) Select the Restrict Data Protection RBAC checkbox to restrict RBAC permissions for Stork (if enabled) and Operator. You will not be able to use Backup and DR capabilities with this restriction. For more information, see Restrict Data Protection RBAC.

- (Optional) Select the Enable Monitoring checkbox to enable monitoring of Portworx components and resources.

- To configure the monitoring stack, select one of the following:

- Portworx Managed - To enable Portworx to install and manage Prometheus and Operator automatically.
 Ensure that no other Prometheus Operator instance is already running on the cluster.

- User Managed - To configure and manage your own monitoring stack.

- Select the Enable Autopilot checkbox to enable Portworx Autopilot. For User Managed monitoring stack, Portworx supports the following metrics providers that Autopilot will use to fetch metrics for rule evaluation and automated actions.

- Prometheus - Provide a valid Prometheus URL

- Datadog - Provide a valid Datadog URL, Secret Name and Secret Namespace. To create a Secret, refer to enable Datadog.
 For more information on Autopilot, see Expanding your Storage Pool with Autopilot.

note

This checkbox is available only when you select the Enable Monitoring checkbox.

- (Optional) Select the Enable Telemetry checkbox to enable telemetry in the StorageCluster spec.
For information, see Portworx Telemetry.

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- Select the Secrets Store Type from the dropdown menu to store and manage secure information for features such as CloudSnaps and Encryption.

-
In the Identity and Access Management (IAM) section, select the Enable Workload Identity (WLI) checkbox to use a federated identity with short-lived tokens injected per-pod by the Portworx Operator.
Workload Identity Federation allows the Portworx Operator to configure Portworx components to securely authenticate with cloud services, without storing static cloud credentials. For more information, see Workload identity for cloud operations in Portworx.
When you enable Enable Workload Identity (WLI):

- Select the Enable for Stork (for data protection using Portworx DR or Backup) checkbox to enable workload identity for Stork.
You must select this checkbox to use Portworx Backup or Portworx DR.

- Under Configure Workload Identity Settings, the Cloud Provider (`Google Cloud`) field is pre-populated. In the Credentials Config Map Name field, enter `px-gcp-wli-creds`, the credential ConfigMap you created in the Configure Authentication section.

-
In the Environment Variables section, enter name-value pairs in the respective fields.

- For restricting Portworx services from listening on all network interfaces, set `PX_DISABLE_WILDCARD_LISTENERS` to `"true"`. By default, Portworx services listen on `0.0.0.0` (all interfaces). When this environment variable is set to true, each service listens only on its management IP, data IP or local loopbacks as required. If you do not set `PX_DISABLE_WILDCARD_LISTENERS` to `"true"` during spec generation, you can add it later to the StorageCluster spec as an environment variable.

note

- When you update `PX_DISABLE_WILDCARD_LISTENERS` in StorageCluster, it triggers a rolling update of the cluster. This causes Portworx to restart on each node and it comes up with the new network configuration. We recommend making this change during a planned maintenance window.

- You cannot switch the IP address family (IPv4 to IPv6 or IPv6 to IPv4) using `PX_PREFER_IPV6_NETWORK_IP` while `PX_DISABLE_WILDCARD_LISTENERS` is set to `"true"`. To switch the IP address family, first disable `PX_DISABLE_WILDCARD_LISTENERS`, switch the IP family, and then re-enable `PX_DISABLE_WILDCARD_LISTENERS`.

-
In the Registry and Image Settings section:

- Enter the Custom Container Registry Location to download the Docker images.

- Enter the Kubernetes Docker Registry Secret that serves as the authentication to access the custom container registry.

- From the Image Pull Policy dropdown menu, select Default, Always, IfNotPresent, or Never.
This policy influences how images are managed on the node and when updates are applied.

-
In the Security Settings section, select the Enable Authorization checkbox to enable Role-Based Access Control (RBAC) and secure access to storage resources in your cluster.

-
Click Finish.

-
In the summary page, enter a name for the specification in the Spec Name field, and tags in the Spec Tags field.

-
Click Download .yaml to download the yaml file with the customized specification or Save Spec to save the specification.

- Click Save & Download to generate the specification.

#### Deploy Portworx Operator​

Use the Operator specification you generated to deploy the Portworx Operator:

```

kubectl apply -f 'https://install.portworx.com/<version-number>?comp=pxoperator'

```

```

serviceaccount/portworx-operator created

podsecuritypolicy.policy/px-operator created

clusterrole.rbac.authorization.k8s.io/portworx-operator created

clusterrolebinding.rbac.authorization.k8s.io/portworx-operator created

deployment.apps/portworx-operator created

```

#### Configure Workload Identity in the StorageCluster​

Because you entered the Credentials Config Map Name during spec generation, the generated `StorageCluster` already includes the workload identity configuration that references the credential ConfigMap you created in the Configure Authentication section.

-
Verify that the generated `StorageCluster` specification includes the `spec.workloadIdentity.gcp.credentialsConfigMap` field:

```

spec:

  workloadIdentity:

    gcp:

      credentialsConfigMap: px-gcp-wli-creds   # ConfigMap created in Configure Authentication

```

-
To enable workload identity for Stork (required when running Portworx Backup), add the following to the `StorageCluster` specification:

```

spec:

  stork:

    useWorkloadIdentity: true

```

#### Deploy StorageCluster​

Apply the `StorageCluster` specification:

```

kubectl apply -f px-storagecluster.yaml

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b created

```

The Portworx Operator automatically:

- Mounts the `px-gcp-wli-creds` ConfigMap at `/etc/workload-identity/` in the Portworx and Stork pods.

- Sets `GOOGLE_APPLICATION_CREDENTIALS=/etc/workload-identity/credential-configuration.json` in those pods.

- Projects a Kubernetes ServiceAccount token (audience set to the Workload Identity Provider URI) into the pods at `/var/run/service-account/token`.

If Portworx was already installed and you are adding the `workloadIdentity` section to an existing `StorageCluster`, the Portworx Operator restarts the Portworx and Stork pods automatically for the changes to take effect.

You can install Portworx Enterprise on GCP Gardener using the Portworx Helm chart. This procedure assumes that Portworx is installed in the `portworx` namespace. If you want to install it in a different namespace, use the `-n <px-namespace>` flag.

-
Add the `portworx/helm` repository to your local Helm repository:

```

helm repo add portworx https://raw.githubusercontent.com/portworx/helm/master/stable/

```

```

"portworx" has been added to your repositories

```

-
Verify that the repository has been successfully added:

```

helm repo list

```

```

NAME    	URL

portworx	https://raw.githubusercontent.com/portworx/helm/master/stable/

```

-
Create a `px_install_values.yaml` file. Set `provider` to `gce`, define the GCP disks, and enable workload identity for Stork:

```

clusterName: <unique-cluster-name>

provider: gce

drives: type=pd-ssd,size=150

internalKVDB: true

stork:

  enabled: true

  useWorkloadIdentity: true

```

note

On GCP, workload identity is delivered through the `px-gcp-wli-creds` ConfigMap referenced by the `StorageCluster` field `spec.workloadIdentity.gcp.credentialsConfigMap`. This field is not yet exposed as a Helm chart parameter, so after the chart deploys the `StorageCluster`, add the GCP workload identity configuration as described in Step 5.

-
Install Portworx:

note

To install a specific version of the Helm chart, use the `--version` flag. Example: `helm install <px-release> portworx/portworx --version <helm-chart-version>`.

```

helm install <px-release> portworx/portworx -n portworx -f px_install_values.yaml --debug

```

-
Add the GCP workload identity configuration to the `StorageCluster` that the chart created, so that the Portworx Operator mounts the credential ConfigMap into the pods:

```

kubectl -n portworx patch storagecluster <cluster-name> --type=merge -p '{"spec":{"workloadIdentity":{"gcp":{"credentialsConfigMap":"px-gcp-wli-creds"}}}}'

```

The resulting `StorageCluster` includes:

```

spec:

  workloadIdentity:

    gcp:

      credentialsConfigMap: px-gcp-wli-creds

  stork:

    useWorkloadIdentity: true

```

The Portworx Operator restarts the Portworx and Stork pods automatically so that the credential ConfigMap, the projected token, and the `GOOGLE_APPLICATION_CREDENTIALS` environment variable are injected into the pods.

-
Check the status of your Portworx installation:

```

helm status <px-release> -n portworx

```

```

NAME: px-release

LAST DEPLOYED: Thu Sep 26 05:53:17 2024

NAMESPACE: portworx

STATUS: deployed

REVISION: 1

TEST SUITE: None

NOTES:

Your Release is named "px-release"

Portworx Pods should be running on each node in your cluster.

Portworx would create a unified pool of the disks attached to your Kubernetes nodes.

No further action should be required and you are ready to consume Portworx Volumes as part of your application data requirements.

```

## Monitor Portworx Nodes​

-
Enter the following `kubectl get` command and wait until all Portworx nodes show as `Ready` or `Online` in the output:

```

kubectl -n <px-namespace> get storagenodes -l name=portworx

```

```

NAME                   ID                                     STATUS   VERSION   AGE

gardener-shoot-node0   xxxxxxxx-xxxx-xxxx-xxxx-43cf085e764e   Online   3.6.2     4m52s

gardener-shoot-node1   xxxxxxxx-xxxx-xxxx-xxxx-4597de6fdd32   Online   3.6.2     4m52s

gardener-shoot-node2   xxxxxxxx-xxxx-xxxx-xxxx-e2169ffa111c   Online   3.6.2     4m52s

```

-
Enter the following `kubectl describe` command with the `NAME` of one of the Portworx nodes you retrieved above to show the current installation status for individual nodes:

```

kubectl -n <px-namespace> describe storagenode <portworx-node-name>

```

## Verify Portworx Pod Status​

Enter the following command to list the Portworx pods in the namespace where you deployed Portworx:

```

kubectl get pods -n <px-namespace> -o wide | grep -e portworx -e px

```

```

NAME                                                    READY   STATUS    RESTARTS         AGE     IP                NODE                   NOMINATED NODE   READINESS GATES

portworx-api-774c2                                      1/1     Running   0                2m55s   192.168.121.196   username-k8s1-node0    <none>           <none>

portworx-api-t4lf9                                      1/1     Running   0                2m55s   192.168.121.99    username-k8s1-node1    <none>           <none>

portworx-kvdb-94bpk                                     1/1     Running   0                4s      192.168.121.196   username-k8s1-node0    <none>           <none>

portworx-operator-58967ddd6d-kmz6c                      1/1     Running   0                4m1s    10.244.1.99       username-k8s1-node0    <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-3e9bf3cd834d-9gs79   2/2     Running   0                2m55s   192.168.121.196   username-k8s1-node0    <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-3e9bf3cd834d-vpptx   2/2     Running   0                2m55s   192.168.121.99    username-k8s1-node1    <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-3e9bf3cd834d-bxmpn   2/2     Running   0                2m55s   192.168.121.191   username-k8s1-node2    <none>           <none>

px-csi-ext-868fcb9fc6-54bmc                             4/4     Running   0                3m5s    10.244.1.103      username-k8s1-node0    <none>           <none>

```

Note the name of a `px-cluster` pod. You will run pxctl commands from these pods in Verify Portworx Cluster Status.

Because you configured Workload Identity authentication, perform the following additional checks:

-
Verify that the credential ConfigMap exists in the Portworx namespace:

```

kubectl -n <px-namespace> get configmap px-gcp-wli-creds -o yaml

```

-
Verify that the Portworx and Stork pods include the projected token volume, the credential ConfigMap volume, the volume mounts, and the environment variable injected by the Portworx Operator:

```

kubectl -n <px-namespace> get pod <px-pod-name> -o yaml

```

#### Environment variable​

```

spec:

  containers:

  - env:

    - name: GOOGLE_APPLICATION_CREDENTIALS

      value: /etc/workload-identity/credential-configuration.json

```

#### Token volume and credential ConfigMap volume​

```

volumes:

- name: token

  projected:

    defaultMode: 420

    sources:

    - serviceAccountToken:

        audience: https://iam.googleapis.com/projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/<POOL_ID>/providers/<PROVIDER_ID>

        expirationSeconds: 3600

        path: token

- name: px-gcp-wli-creds

  configMap:

    name: px-gcp-wli-creds

```

#### Volume mounts​

```

volumeMounts:

- mountPath: /var/run/service-account

  name: token

  readOnly: true

- mountPath: /etc/workload-identity

  name: px-gcp-wli-creds

  readOnly: true

```

The Google Cloud SDK inside Portworx uses the projected token and the credential configuration to authenticate to Google Cloud APIs.

## Verify Portworx Cluster Status​

You can find the status of the Portworx cluster by running `pxctl status` from a Portworx pod. Use the pod name you retrieved in Verify Portworx Pod Status:

```

kubectl exec <pod-name> -n <px-namespace> -- /opt/pwx/bin/pxctl status

```

`Status: PX is operational` indicates that the cluster is running as expected. If the cluster is using the PX-StoreV2 datastore, the `StorageNode` entries for each node display `Yes(PX-StoreV2)`.

If nodes do not come online, check the events on a `StorageNode` and the Portworx pod logs for GCP authentication errors:

```

kubectl -n <px-namespace> describe storagenode <node-name>

kubectl -n <px-namespace> logs <px-pod-name> | grep -i "google\|credential\|token\|auth"

```

## Verify Portworx Pool Status​

note

This procedure is applicable for clusters with the PX-StoreV2 datastore.

Run the following command to view the Portworx drive configuration for your pod:

```

kubectl exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl service pool show

```

The output `Type: PX-StoreV2` confirms that the pod uses the PX-StoreV2 datastore.

## Verify pxctl Cluster Provision Status​

-
Run the following command to find the storage cluster:

```

kubectl -n <px-namespace> get storagecluster

```

The status must display the cluster as `Online`.

-
Run the following command to find the storage nodes:

```

kubectl -n <px-namespace> get storagenodes

```

The status must display the nodes as `Online`.

-
Verify the Portworx cluster provision status by running the following command. Specify the pod name you retrieved in Verify Portworx Pod Status:

```

kubectl exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl cluster provision-status

```

## What to do next​

Create a PVC. For more information, see Create your first PVC.

In this topic:
