# Installation on an Azure Gardener Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/azure/azure-gardener (Portworx Enterprise latest)

Installation on an Azure Gardener Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx Enterprise on a Gardener cluster running on Azure. Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

The following collection of tasks describes how to install Portworx Enterprise on an Azure Gardener cluster:

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

Use the Gardener dashboard or the Gardener API to create a shoot cluster on Azure. The shoot specification controls the worker node VMs, networking, and the OIDC issuer that Portworx will federate against when using Workload Identity.

-
Sign in to your Gardener dashboard, or set up `kubectl` access to your Gardener landscape.

-
Create a shoot cluster on the `azure` provider. In the shoot specification, ensure the following fields are set:

- `spec.cloudProfile.name: azure`

- `spec.region` — set to the Azure region where Portworx will run.

- `spec.provider.workers` — define the worker pools. Each worker pool's VMs or VM Scale Sets must reside in a single resource group that Portworx will be granted access to.

-
Once the shoot is reconciled, download its `kubeconfig` from the Gardener dashboard or via `kubectl`, and confirm you can reach the cluster:

```

kubectl get nodes

```

-
Note the following values from your shoot. These values are required when you configure the authentication:

- The Azure subscription ID hosting the shoot.

- The resource group that contains the shoot's worker node VMs or VM Scale Sets.

- The OIDC issuer URL of the shoot (only required for Workload Identity).

For more information on shoot creation, see the Gardener documentation.

## Configure Authentication​

Portworx supports two authentication methods on Gardener:

- Azure Service Principal - static credentials (`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`) stored in a Kubernetes secret.

- Azure Workload Identity - federated identity with short-lived tokens injected per-pod by the Azure Workload Identity webhook. For more information, see Workload identity for cloud operations in Portworx.

Choose the method that matches your security and operational requirements.

- Service Principal

- Workload Identity

With Service Principal authentication, Portworx reads static credentials from a Kubernetes secret named `px-azure` and uses them to authenticate to Azure APIs.

-
Log in to Azure and set the subscription where your Gardener cluster runs:

```

az login

az account set --subscription <your-subscription-id>

```

-
Create a custom Azure role with the permissions Portworx requires:

```

az role definition create --role-definition '{

"Name": "<your-role-name>",

"Description": "",

"AssignableScopes": [

    "/subscriptions/<your-subscription-id>"

],

"Actions": [

    "Microsoft.Compute/disks/delete",

    "Microsoft.Compute/disks/write",

    "Microsoft.Compute/disks/read",

    "Microsoft.Compute/virtualMachines/write",

    "Microsoft.Compute/virtualMachines/read",

    "Microsoft.Compute/virtualMachineScaleSets/virtualMachines/write",

    "Microsoft.Compute/virtualMachineScaleSets/virtualMachines/read"

],

"NotActions": [],

"DataActions": [],

"NotDataActions": []

}'

```

-
Create a service principal for the custom role, scoped to the resource group that contains your shoot's worker node VMs or VM Scale Sets:

```

az ad sp create-for-rbac --role=<your-role-name> \

    --scopes="/subscriptions/<your-subscription-id>/resourceGroups/<worker-node-resource-group>"

```

The output includes `appId`, `password`, and `tenant`. Save these values for the next step.

-
Create the `px-azure` Kubernetes secret in the namespace where you install Portworx:

```

kubectl create secret generic -n <px-namespace> px-azure \

    --from-literal=AZURE_TENANT_ID=<tenant> \

    --from-literal=AZURE_CLIENT_ID=<appId> \

    --from-literal=AZURE_CLIENT_SECRET=<password>

```

Portworx automatically picks up these credentials at startup.

With Workload Identity authentication, Portworx pods exchange a projected service account token for an Azure access token, eliminating the need to store long-lived credentials in the cluster. Before installing Portworx, you must create a user-assigned managed identity, grant it the required Azure permissions, and federate it with the Kubernetes service accounts that Portworx uses.

-
Log in to Azure and set the subscription where your Gardener cluster runs:

```

az login

az account set --subscription <Your-Azure-Subscription-UUID>

```

-
Export the environment variables that the subsequent commands use:

```

export SUBSCRIPTION="$(az account show --query id --output tsv)"

export RESOURCE_GROUP="<gardener-worker-resource-group>"

export LOCATION="<azure-location>"

export USER_ASSIGNED_IDENTITY_NAME="<my-managed-identity-name>"

export OIDC_ISSUER="<gardener-shoot-oidc-issuer-url>"

```

note

`RESOURCE_GROUP` must be the same resource group where the Gardener cluster's worker node VMs or VMSS are created. `OIDC_ISSUER` must be set to the OIDC issuer URL of your Gardener shoot cluster.

-
Create a user-assigned managed identity.
Portworx pods use this identity to authenticate to Azure APIs without secrets.

```

az identity create --name "${USER_ASSIGNED_IDENTITY_NAME}" \

    --resource-group "${RESOURCE_GROUP}" \

    --location "${LOCATION}" \

    --subscription "${SUBSCRIPTION}"

```

-
Save the `clientId` of the managed identity.

```

export USER_ASSIGNED_CLIENT_ID="$(az identity show --resource-group "${RESOURCE_GROUP}" --name "${USER_ASSIGNED_IDENTITY_NAME}" --query 'clientId' --output tsv)"

```

-
Fetch the `principalId` of the managed identity created in Step 3:

```

export IDENTITY_PRINCIPAL_ID="$(az identity show --name "${USER_ASSIGNED_IDENTITY_NAME}" --resource-group "${RESOURCE_GROUP}" --query principalId --output tsv)"

```

-
Create a custom Azure role with the permissions required by Portworx, and assign it to the managed identity:

```

az role definition create --role-definition '{

"Name": "<your-role-name>",

"Description": "",

"AssignableScopes": [

    "/subscriptions/<Your-Azure-Subscription-UUID>"

],

"Actions": [

    "Microsoft.Compute/disks/delete",

    "Microsoft.Compute/disks/write",

    "Microsoft.Compute/disks/read",

    "Microsoft.Compute/virtualMachines/write",

    "Microsoft.Compute/virtualMachines/read",

    "Microsoft.Compute/virtualMachineScaleSets/virtualMachines/write",

    "Microsoft.Compute/virtualMachineScaleSets/virtualMachines/read"

],

"NotActions": [],

"DataActions": [],

"NotDataActions": []

}'

```

```

az role assignment create --assignee-object-id "${IDENTITY_PRINCIPAL_ID}" \

    --role "<your-role-name>" \

    --scope "/subscriptions/<Your-Azure-Subscription-UUID>" \

    --assignee-principal-type ServicePrincipal

```

Replace `<Your-Azure-Subscription-UUID>` with the subscription ID from Step 1.

-
Assign StorageAccount permissions to the managed identity:

```

az role assignment create \

    --assignee-object-id "${IDENTITY_PRINCIPAL_ID}" \

    --role "Storage Blob Data Contributor" \

    --scope "/subscriptions/<your-subscription-id>/resourceGroups/<storage-account-resource-group>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>" \

    --assignee-principal-type ServicePrincipal

```

note

You must use this same Azure Storage account when creating the `pxctl` credential for CloudSnap backups. Portworx Enterprise authenticates to this storage account through the managed identity, so the Storage Blob Data Contributor role assignment and the credential must point to the same account.

-
Create federated identity credentials that link the Kubernetes service accounts used by Portworx to the Azure managed identity.
Repeat the following command for each of the `portworx`, `stork`, and `px-node-wiper` service accounts in the namespace where you install Portworx:

```

export SERVICE_ACCOUNT_NAMESPACE="<px-namespace>"

export SERVICE_ACCOUNT_NAME="portworx"   # repeat for stork and px-node-wiper

export FEDERATED_IDENTITY_CREDENTIAL_NAME="<my-federated-identity-name>"

az identity federated-credential create \

    --name "${FEDERATED_IDENTITY_CREDENTIAL_NAME}" \

    --identity-name "${USER_ASSIGNED_IDENTITY_NAME}" \

    --resource-group "${RESOURCE_GROUP}" \

    --issuer "${OIDC_ISSUER}" \

    --subject "system:serviceaccount:${SERVICE_ACCOUNT_NAMESPACE}:${SERVICE_ACCOUNT_NAME}" \

    --audience api://AzureADTokenExchange

```

The `portworx` service account is required for Portworx, the `stork` service account is required for Stork, and the `px-node-wiper` service account is required when uninstalling the `StorageCluster` with the `UninstallAndDelete` strategy. Each Portworx component uses a different service account, and Azure requires explicit mapping for each one to establish trust and allow authentication.
For more information, see Azure documentation.

-
Install the Azure Workload Identity mutating webhook on the cluster.
Workload identity does not function without this webhook. The webhook injects the workload identity environment variables, mounts the projected service account token, and enables token exchange with Azure.
For information on how to install the webhook, see Azure AD Workload Identity guide.

-
Verify that the webhook is installed:

```

kubectl get mutatingwebhookconfigurations.admissionregistration.k8s.io

```

```

NAME                                              WEBHOOKS   AGE

azure-wi-webhook-mutating-webhook-configuration   1          6h12m

gardener-extension-provider-azure-shoot           1          6h18m

gardener-resource-manager-shoot                   4          6h19m

```

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

You can install Portworx Enterprise on an Azure Gardener cluster either by generating a Kubernetes specification through Portworx Central and applying it, or by deploying the Portworx Helm chart. Choose the installation mode that matches your tooling and operational preferences.

- Generate Specification

- Install using Helm

To install Portworx, you must first generate Kubernetes manifests that you will deploy in your Azure Gardener cluster by following these steps.

-
Sign in to the Portworx Central console.
 The system displays the Welcome to Portworx Central! page.

-
In the Portworx Enterprise section, select Generate Cluster Spec.
 The system displays the Generate Spec page.

-
From the Portworx Version dropdown menu, select the Portworx version to install.

-
From the Platform dropdown menu, select Azure.

-
From the Distribution Name dropdown menu, select Gardener.

-
In the Azure Managed Identity Client ID field, enter the `clientId` of the managed identity you created in the Configure Authentication section.

note

The default Portworx Central workflow for installing Portworx Enterprise on Azure Gardener uses the Azure Managed Identity Client ID field. If you configured Service Principal authentication, leave this field blank and proceed to the Customize step (Step 8) to modify the generated `StorageCluster` specification for Service Principal authentication.

-
In the Namespace field, enter the namespace where you plan to install Portworx.
 By default, the namespace is `portworx`.

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

- Standard SSD

- Premium SSD

- Premium SSD v2

- Ultra disk

note

- To use an Ultra disk, the Azure instance must have the Ultra SSD feature enabled.

- The system automatically selects the minimum number of drives to ensure optimal performance.

- Configure the following fields for the drive:

- Size (GB) - Specify the size of the drive in gigabytes.

- IOPS - Enter the input/output operations per second (IOPS) value for the drive.

note

- IOPS is required when you select Ultra Disk drive type only.

- If you do not specify an IOPS value for Premium SSDv2, Portworx uses the default value of 3000.

- Throughput - Enter the required data transfer rate for the drive.

note

- Throughput is required when you select Ultra Disk drive type.

- If you do not specify a Throughput value for Premium SSDv2, Portworx uses the default value of 125.

- Encryption - Choose None to disable encryption or BYOK Encryption to encrypt your Azure cluster data disk using BYOK encryption.

- Encryption Key - If you choose BYOK Encryption, specify the key to use for BYOK encryption.

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

- (Optional) Select the Restrict Data Protection RBAC to restrict RBAC permissions for Stork (if enabled) and Operator. You will not be able to use Backup and DR capabilities with this restriction. For more information, see Restrict Data Protection RBAC.

- Select the Enable Monitoring checkbox to enable monitoring of Portworx components and resources.

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
In the Identity and Access Management (IAM) section, choose one of the following authentication methods to use for Portworx to access Azure resources.

- Workload Identity (WLI) - To use a federated identity with short-lived tokens injected per-pod by the Azure Workload Identity webhook.
Workload Identity Federation enables the Portworx Operator to configure Portworx components to securely authenticate with cloud services without storing static credentials. For more information, see Workload identity for cloud operations in Portworx.
 When you enable Enable Workload Identity (WLI):

- Select the Enable for Stork (for data protection using Portworx DR or Backup) checkbox to enable workload identity for Stork.
You must select this checkbox to use Portworx Backup or Portworx DR.

- In the Azure Managed Identity Client ID field, enter the `clientId` of the managed identity you created in the Workload Identity tab of Configure Authentication section.

- Service Principal - To use a service principal with static credentials.
 If you selected this option, the spec generator automatically fetches the `px-azure` secret that contains the static credentials (`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`) stored in a Kubernetes secret.

-
In the Environment Variables section, enter name-value pairs in the respective fields.

note

For deploying Portworx on an Azure Sovereign cloud, specify the value of the `AZURE_ENVIRONMENT` variable in the Name and Value fields.

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

#### Deploy StorageCluster​

Apply the `StorageCluster` specification you generated:

```

kubectl apply -f px-storagecluster.yaml

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b created

```

You can install Portworx Enterprise on Azure Gardener using the Portworx Helm chart. This procedure assumes that Portworx is installed in the `portworx` namespace. If you want to install it in a different namespace, use the `-n <px-namespace>` flag.

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
Create a `px_install_values.yaml` file using the template that matches the authentication method you configured in the Configure Authentication section.

- Service Principal

- Workload Identity

Portworx reads the `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` values from the `px-azure` Kubernetes secret you created. Reference them as environment variables in `px_install_values.yaml`:

```

clusterName: <unique-cluster-name>

provider: azure

drives: type=Premium_LRS,size=150

internalKVDB: true

envs:

  - name: AZURE_TENANT_ID

    valueFrom:

      secretKeyRef:

        name: px-azure

        key: AZURE_TENANT_ID

  - name: AZURE_CLIENT_ID

    valueFrom:

      secretKeyRef:

        name: px-azure

        key: AZURE_CLIENT_ID

  - name: AZURE_CLIENT_SECRET

    valueFrom:

      secretKeyRef:

        name: px-azure

        key: AZURE_CLIENT_SECRET

```

With Workload Identity, the Azure Workload Identity webhook injects credentials into Portworx pods based on annotations on the Portworx service accounts. Use the `workloadIdentity.credentials` parameter to instruct the Helm chart to annotate the service accounts with the `clientId` of the user-assigned managed identity you created.

```

clusterName: <unique-cluster-name>

provider: azure

drives: type=Premium_LRS,size=150

internalKVDB: true

workloadIdentity:

  credentials:

    - cloudProvider: azure

      key: azure.workload.identity/client-id

      value: <USER_ASSIGNED_CLIENT_ID>

stork:

  enabled: true

  useWorkloadIdentity: true

```

Replace `<USER_ASSIGNED_CLIENT_ID>` with the `clientId` of the managed identity you created in the Configure Authentication section. Set `stork.useWorkloadIdentity` to `true` to apply the same workload identity credentials to Stork.

-
(Optional) In many cases, you may want to customize Portworx configurations, such as enabling monitoring or specifying specific storage devices. You can pass the custom configuration to the `px_install_values.yaml` file.

note

- You can refer to the Portworx Helm chart parameters for a list of configurable parameters and the values.yaml file for the configuration file template.

- The default `clusterName` is `mycluster`. However, it is recommended to change it to a unique identifier to avoid conflicts in multi-cluster environments.

-
Install Portworx:

note

To install a specific version of the Helm chart, use the `--version` flag. Example: `helm install <px-release> portworx/portworx --version <helm-chart-version>`.

```

helm install <px-release> portworx/portworx -n portworx -f px_install_values.yaml --debug

```

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

gardener-shoot-node0   xxxxxxxx-xxxx-xxxx-xxxx-43cf085e764e   Online   3.6.1     4m52s

gardener-shoot-node1   xxxxxxxx-xxxx-xxxx-xxxx-4597de6fdd32   Online   3.6.1     4m52s

gardener-shoot-node2   xxxxxxxx-xxxx-xxxx-xxxx-e2169ffa111c   Online   3.6.1     4m52s

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

portworx-api-dvw64                                      1/1     Running   0                2m55s   192.168.121.99    username-k8s1-node2    <none>           <none>

portworx-kvdb-94bpk                                     1/1     Running   0                4s      192.168.121.196   username-k8s1-node0    <none>           <none>

portworx-kvdb-8b67l                                     1/1     Running   0                10s     192.168.121.196   username-k8s1-node1    <none>           <none>

portworx-kvdb-fj72p                                     1/1     Running   0                30s     192.168.121.196   username-k8s1-node2    <none>           <none>

portworx-operator-58967ddd6d-kmz6c                      1/1     Running   0                4m1s    10.244.1.99       username-k8s1-node0    <none>           <none>

prometheus-px-prometheus-0                              2/2     Running   0                2m41s   10.244.1.105      username-k8s1-node0    <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-3e9bf3cd834d-9gs79   2/2     Running   0                2m55s   192.168.121.196   username-k8s1-node0    <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-3e9bf3cd834d-vpptx   2/2     Running   0                2m55s   192.168.121.99    username-k8s1-node1    <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-3e9bf3cd834d-bxmpn   2/2     Running   0                2m55s   192.168.121.191   username-k8s1-node2    <none>           <none>

px-csi-ext-868fcb9fc6-54bmc                             4/4     Running   0                3m5s    10.244.1.103      username-k8s1-node0    <none>           <none>

px-csi-ext-868fcb9fc6-8tk79                             4/4     Running   0                3m5s    10.244.1.102      username-k8s1-node2    <none>           <none>

px-csi-ext-868fcb9fc6-vbqzk                             4/4     Running   0                3m5s    10.244.3.107      username-k8s1-node1    <none>           <none>

px-prometheus-operator-59b98b5897-9nwfv                 1/1     Running   0                3m3s    10.244.1.104      username-k8s1-node0    <none>           <none>

```

Note the name of a `px-cluster` pod. You will run pxctl commands from these pods in Verify Portworx Cluster Status.

If you configured Workload Identity authentication, perform the following additional checks:

-
Confirm that Portworx Operator has labeled the Portworx pods:

```

kubectl -n <px-namespace> get pods -l name=portworx --show-labels | grep "azure.workload.identity/use=true"

```

-
Verify that Portworx Operator added the workload identity annotation on the `portworx` service account:

```

kubectl -n <px-namespace> get sa portworx -o yaml

```

The output should include the following annotation:

```

metadata:

annotations:

    azure.workload.identity/client-id: <USER_ASSIGNED_CLIENT_ID>

```

-
After the configuration is applied, the Portworx Operator restarts the pods as needed.
Verify that the Portworx pods include the projected token volume, volume mount, and environment variables injected by the Azure Workload Identity webhook:

```

kubectl -n <px-namespace> get pods <px-pod> -o yaml

```

#### Token volume​

```

volumes:

- name: azure-identity-token

projected:

    defaultMode: 420

    sources:

    - serviceAccountToken:

        audience: api://AzureADTokenExchange

        expirationSeconds: 3600

        path: azure-identity-token

```

#### Volume mount​

```

volumeMounts:

- mountPath: /var/run/secrets/azure/tokens

name: azure-identity-token

readOnly: true

```

#### Environment variables​

```

spec:

containers:

- env:

    - name: AZURE_CLIENT_ID

    value: <client-id>

    - name: AZURE_TENANT_ID

    value: <tenant-id>

    - name: AZURE_FEDERATED_TOKEN_FILE

    value: /var/run/secrets/azure/tokens/azure-identity-token

    - name: AZURE_AUTHORITY_HOST

    value: https://login.microsoftonline.com/

```

The Azure cloud SDK uses these to authenticate with Azure AD and access Azure resources.

## Verify Portworx Cluster Status​

You can find the status of the Portworx cluster by running `pxctl status` from a Portworx pod. Use the pod name you retrieved in Verify Portworx Pod Status:

```

kubectl exec <pod-name> -n <px-namespace> -- /opt/pwx/bin/pxctl status

```

`Status: PX is operational` indicates that the cluster is running as expected. If the cluster is using the PX-StoreV2 datastore, the `StorageNode` entries for each node display `Yes(PX-StoreV2)`.

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

- Create a PVC. For more information, see Create your first PVC.

- You can enable disk locking on Azure disks to prevent accidental or external deletion of the disks. For more information, see Azure Disk Locking.

In this topic:
