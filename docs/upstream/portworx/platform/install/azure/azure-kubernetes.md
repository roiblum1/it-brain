# Installation on an Azure Kubernetes Service Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/azure/azure-kubernetes (Portworx Enterprise latest)

Installation on an Azure Kubernetes Service Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx on an Azure Kubernetes Service (AKS) cluster. Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

The following collection of tasks describe how to install Portworx on an AKS cluster:

- Create an AKS Cluster

- Configure Authentication

- Generate Portworx Specification

- Deploy Portworx Operator

- Deploy StorageCluster

- Monitor Portworx Nodes

- Verify Portworx Pod Status

- Verify Portworx Cluster Status

- Verify Portworx Pool Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx.

## Create an AKS Cluster​

To set up the Azure Kubernetes Service (AKS) to use Portworx, follow these steps:

-
Log in to Azure and save your `az login` subscription ID (`"id"`) for future reference:

```

az login

```

```

[

    {

        "cloudName": "AzureCloud",

        "homeTenantId": "xxxxxxxx-xxxx-xxxx-xxxx-1234567890ab",

        "id": "xxxxxxxx-xxxx-xxxx-xxxx-1234567890ab",

        "isDefault": true,

        "managedByTenants": [],

        "name": "Example name",

        "state": "Enabled",

        "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-1234567890ab",

        "user": {

        "name": "user@example.com",

        "type": "user"

        }

    }

]

```

-
Set the subscription:

```

az account set --subscription <Your-Azure-Subscription-UUID>

```

-
Get the Azure locations using the Azure CLI command:

```

az account list-locations

```

-
Create an Azure Resource Group by specifying its name and the location in which you will be deploying your AKS cluster:

```

az group create --name <resource-group-name> --location <location>

```

-
Create an AKS cluster in the resource group, with the flags that match the authentication method you intend to use for Portworx:

-
Service Principal — create the cluster without managed identity or workload identity flags:

```

az aks create -g <resource-group-name> -n <cluster-name>

```

-
Managed Identity — add the `--enable-managed-identity` flag:

```

az aks create -g <resource-group-name> -n <cluster-name> --enable-managed-identity

```

-
Workload Identity — enable the OIDC issuer and the workload identity feature so that AKS exposes a stable issuer URL and installs the Azure Workload Identity mutating webhook:

```

az aks create -g <resource-group-name> -n <cluster-name> \

    --enable-oidc-issuer --enable-workload-identity

```

note

If you have an existing AKS cluster, enable these features by running `az aks update --resource-group <resource-group-name> --name <cluster-name> --enable-oidc-issuer --enable-workload-identity`.

For more information on `az aks create`, see the Microsoft documentation. To use Azure ultra disks, add the `--enable-ultra-ssd` parameter; see the Azure documentation.

## Configure Authentication​

Portworx supports three authentication methods on AKS:

- Azure Service Principal - static credentials (`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`) stored in a Kubernetes secret.

- Azure Managed Identity - a managed identity attached to the AKS node pool VM Scale Sets; Portworx reads the identity's client ID from a Kubernetes secret and authenticates through the Azure Instance Metadata Service.

- Azure Workload Identity - federated identity with short-lived tokens injected per-pod by the Azure Workload Identity webhook.

Choose the method that matches your security and operational requirements.

- Service Principal

- Managed Identity

- Workload Identity

With Service Principal authentication, Portworx reads static credentials from a Kubernetes secret named `px-azure` and uses them to authenticate to Azure APIs.

-
Create a custom role for Portworx. Enter the subscription ID using the value you saved in Create an AKS Cluster, and specify a role name:

```

az role definition create --role-definition '{

"Name": "<your-role-name>",

"Description": "",

"AssignableScopes": [

    "/subscriptions/<your-subscription-id>"

],

"Actions": [

    "Microsoft.ContainerService/managedClusters/agentPools/read",

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
Find the AKS cluster Infrastructure Resource Group. The following command shows the Infrastructure Resource Group for a given cluster name and AKS resource group:

```

az aks show -n <aks-cluster-name> -g <aks-resource-group> | jq -r '.nodeResourceGroup'

```

-
Create a service principal for the Portworx custom role, scoped to the AKS Infrastructure Resource Group. Replace the following with your cluster's values:

- Your subscription ID

- The Infrastructure Resource Group name from the previous step

- The name of the custom role that you created in step 1

```

az ad sp create-for-rbac --role=<your-role-name> --scopes="/subscriptions/<your-subscription-id>/resourceGroups/<aks-infrastructure-resource-group>"

```

```

{

  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-1234567890ab",

  "displayName": "azure-cli-2020-10-10-10-10-10",

  "name": "http://azure-cli-2020-10-10-10-10-10",

  "password": "xxxxxxxx-xxxx-xxxx-xxxx-1234567890ab",

  "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-1234567890ab"

}

```

-
Create a secret called `px-azure` to give Portworx access to Azure APIs. Take the following fields from the previous output and use them in the following command:

- Set `AZURE_TENANT_ID` to the value for `tenant`

- Set `AZURE_CLIENT_ID` to the value for `appId`

- Set `AZURE_CLIENT_SECRET` to the value for `password`

```

kubectl create secret generic -n kube-system px-azure --from-literal=AZURE_TENANT_ID=<tenant> \

                                                      --from-literal=AZURE_CLIENT_ID=<appId> \

                                                      --from-literal=AZURE_CLIENT_SECRET=<password>

```

```

secret/px-azure created

```

After you create the secret, the spec generator automatically incorporates it, and Portworx fetches the secret to authenticate.

With Managed Identity authentication, Portworx uses the managed identity attached to the AKS node pool VM Scale Sets. The `px-azure` Kubernetes secret stores only the identity's client ID, and Portworx obtains access tokens from the Azure Instance Metadata Service at runtime.

-
Identify the object and client IDs of the kubelet managed identity:

```

az aks show -g <resource-group-name> -n <cluster-name> --query identityProfile

```

For example:

```

az aks show -g cass-rg -n msi-test --query identityProfile

```

```

{

  "kubeletidentity": {

    "clientId": "68XXXXXX-f3a5-459d-9b57-XXXXXXXXXX70",

    "objectId": "c0XXXXXX-ba91-4c13-9456-XXXXXXXXXX35",

    "resourceId": "/subscriptions/72XXXXXX-a431-4b8e-80ef-685510XXXXXX/resourcegroups/MC_cass-rg_msi-test_eastus/providers/Microsoft.ManagedIdentity/userAssignedIdentities/msi-test-agentpool"

  }

}

```

-
Assign the Contributor role to the managed identity:

```

az role assignment create --assignee <objectId> --role "Contributor" --scope <resourceId>

```

note

The `objectId` is the value returned in the previous step. The `resourceId` is also returned in the previous step, but you must trim it after the resource group name `/subscriptions/<subscription-id>/resourcegroups/MC_<resource-group>_<cluster-name>_<location>`, right before `providers`.

For example:

```

az role assignment create --assignee "c0XXXXXX-ba91-4c13-9456-XXXXXXXXXX35" --role "Contributor" --scope "/subscriptions/72XXXXXX-a431-4b8e-80ef-685510XXXXXX/resourcegroups/MC_cass-rg_msi-test_eastus"

```

-
Create a Kubernetes secret based on the `clientId` you retrieved in step 1:

```

kubectl create secret generic -n <px-namespace> px-azure --from-literal=AZURE_CLIENT_ID="<clientId>"

```

For example:

```

kubectl create secret generic -n portworx px-azure --from-literal=AZURE_CLIENT_ID="68XXXXXX-f3a5-459d-9b57-XXXXXXXXXX70"

```

With Workload Identity authentication, Portworx pods exchange a projected service account token for an Azure access token, so no long-lived credentials are stored in the cluster. Before installing Portworx, you must capture the cluster's OIDC issuer URL, create a user-assigned managed identity, grant it the required Azure permissions, and federate it with the Kubernetes service accounts that Portworx uses.

-
Retrieve the OIDC issuer URL of your AKS cluster. You enabled the issuer in Create an AKS Cluster:

```

az aks show --resource-group <resource-group-name> --name <cluster-name> --query "oidcIssuerProfile.issuerUrl" --output tsv

```

-
Find the AKS cluster Infrastructure Resource Group. Portworx requires permissions on the AKS node pool VMs and managed disks, which live in this resource group:

```

az aks show -n <cluster-name> -g <resource-group-name> | jq -r '.nodeResourceGroup'

```

-
Export the environment variables that the subsequent commands use:

```

export SUBSCRIPTION="$(az account show --query id --output tsv)"

export RESOURCE_GROUP="<resource-group-name>"

export INFRA_RESOURCE_GROUP="<aks-infrastructure-resource-group>"

export LOCATION="<azure-location>"

export USER_ASSIGNED_IDENTITY_NAME="<my-managed-identity-name>"

export AKS_OIDC_ISSUER="<aks-oidc-issuer-url>"

```

note

`INFRA_RESOURCE_GROUP` is the `MC_*` resource group returned in step 2; it contains the AKS node pool VMs and managed disks. `AKS_OIDC_ISSUER` is the URL returned in step 1.

-
Create a user-assigned managed identity. Portworx pods use this identity to authenticate to Azure APIs without secrets:

```

az identity create --name "${USER_ASSIGNED_IDENTITY_NAME}" \

    --resource-group "${RESOURCE_GROUP}" \

    --location "${LOCATION}" \

    --subscription "${SUBSCRIPTION}"

```

-
Save the `clientId` and `principalId` of the managed identity:

```

export USER_ASSIGNED_CLIENT_ID="$(az identity show --resource-group "${RESOURCE_GROUP}" --name "${USER_ASSIGNED_IDENTITY_NAME}" --query 'clientId' --output tsv)"

export IDENTITY_PRINCIPAL_ID="$(az identity show --name "${USER_ASSIGNED_IDENTITY_NAME}" --resource-group "${RESOURCE_GROUP}" --query principalId --output tsv)"

```

-
Create a custom Azure role with the permissions required by Portworx, and assign it to the managed identity, scoped to the AKS infrastructure resource group:

```

az role definition create --role-definition '{

"Name": "<your-role-name>",

"Description": "",

"AssignableScopes": [

    "/subscriptions/<your-subscription-id>"

],

"Actions": [

    "Microsoft.ContainerService/managedClusters/agentPools/read",

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

    --scope "/subscriptions/${SUBSCRIPTION}/resourceGroups/${INFRA_RESOURCE_GROUP}" \

    --assignee-principal-type ServicePrincipal

```

-
Assign Storage Account permissions to the managed identity. This is required for CloudSnap backups:

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
Create federated identity credentials that link the Kubernetes service accounts used by Portworx to the Azure managed identity. Repeat the following command for each of the `portworx`, `stork`, and `px-node-wiper` service accounts in the namespace where you install Portworx:

```

export SERVICE_ACCOUNT_NAMESPACE="<px-namespace>"

export SERVICE_ACCOUNT_NAME="portworx"   # repeat for stork and px-node-wiper

export FEDERATED_IDENTITY_CREDENTIAL_NAME="<my-federated-identity-name>"

az identity federated-credential create \

    --name "${FEDERATED_IDENTITY_CREDENTIAL_NAME}" \

    --identity-name "${USER_ASSIGNED_IDENTITY_NAME}" \

    --resource-group "${RESOURCE_GROUP}" \

    --issuer "${AKS_OIDC_ISSUER}" \

    --subject "system:serviceaccount:${SERVICE_ACCOUNT_NAMESPACE}:${SERVICE_ACCOUNT_NAME}" \

    --audience api://AzureADTokenExchange

```

The `portworx` service account is required for Portworx, the `stork` service account is required for Stork, and the `px-node-wiper` service account is required when uninstalling the `StorageCluster` with the `UninstallAndDelete` strategy. Each Portworx component uses a different service account, and Azure requires explicit mapping for each one to establish trust and allow authentication. For more information, see the Azure documentation.

-
Verify that the Azure Workload Identity mutating webhook is installed on the cluster. AKS installs this webhook automatically when you create or update the cluster with `--enable-workload-identity`:

```

kubectl get mutatingwebhookconfigurations.admissionregistration.k8s.io

```

The output should include an entry similar to `azure-wi-webhook-mutating-webhook-configuration`.

## Generate Portworx Specification​

To install Portworx, you must first generate Kubernetes manifests that you will deploy in your Azure Kubernetes cluster by following these steps.

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
From the Distribution Name dropdown menu, select Azure Kubernetes Service (AKS).

-
In the Namespace field, enter the namespace where you plan to install Portworx.
 By default, the namespace is `portworx`.

-
(Optional) To customize the configuration options and generate a custom specification, click Customize and perform the following steps:

note

To continue without customizing the default configuration or generating a custom specification, proceed to Step 8.

-
Basic tab:

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

- Select Next.

-
Storage tab:

- Select one of the following:

- To enable Portworx to provision drives using a specification, do the following:

- Select the Create Using a Spec option.

- Select PX-Store Version: (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- To add one or more cloud storage drive types for Portworx to use, click + Add Drive and select one of the following types of drives:

- Standard HDD

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

- IOPS is required when you select Ultra Disk drive type.

- If you do not specify an IOPS value for Premium SSDv2, Portworx uses the default value of 3000.

- Throughput - Enter the required data transfer rate for the drive.

note

- Throughput is required when you select Ultra Disk drive type.

- If you do not specify a Throughput value for Premium SSDv2, Portworx uses the default value of 125.

- Encryption - Choose None to disable encryption or BYOK Encryption to encrypt your Azure cluster data disk using BYOK encryption.

- Encryption Key - If you choose BYOK Encryption, specify the key to use for BYOK encryption.

- Drive Tags - Add labels in key:value format to organize and identify drives.
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

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
 Enter the path of the journal device in the Journal Device Path field.

- (Optional) To designate PX-StoreV1 as the datastore, clear the PX-StoreV2 checkbox. By default, the system selects PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
 The path must be at least 64 GB in size.

- Select the Use unmounted disks even if they have a partition or filesystem on it. Portworx will never use a drive or partition that is mounted checkbox to use unmounted disks, even if they contain a partition or filesystem.
 Portworx will not use any mounted drive or partition.

- To enable Portworx to use existing drives on a node, do the following:

- Select the Use Existing Drives option.

- In the Drive/Device field, specify the block drive(s) that Portworx uses for data storage.

- In the Pool Label field, assign a custom label in key:value format to identify and categorize storage pools.

- (Optional) To designate PX-StoreV1 as the datastore, clear the PX-StoreV2 checkbox. By default, the system selects PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
The path must be at least 64 GB in size.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
 Enter the path of the journal device in the Journal Device Path field.

- Select Next.

-
Network tab:

- In the Interface(s) section, do the following:

- Enter the Data Network Interface to be used for data traffic.

- Enter the Management Network Interface to be used for management traffic.

- In the Advanced Settings section, do the following:

- Enter the Starting port for Portworx services.

- Select Next.

-
Deployment tab:

-
In the Kubernetes Distribution section, under Are you running on either of these?, select Azure Kubernetes Service (AKS).

-
In the Component Settings section:

- Select the Enable Stork checkbox to enable Stork.

- (Optional) Select the Remote Fastpath (NVMe-oF/TCP) checkbox to enable Remote Fastpath. For more information, see Remote Fastpath.

- Select the Restrict Data Protection RBAC to restrict RBAC permissions for Stork (if enabled) and Operator. You will not be able to use Backup and DR capabilities with this restriction. For more information, see Restrict Data Protection RBAC.

- Select the Enable Monitoring checkbox to enable monitoring of Portworx components and resources.

- To configure the monitoring stack, select one of the following:

- Portworx Managed - To enable Portworx to install and manage Prometheus and Operator automatically.
 Ensure that no other Prometheus Operator instance already running on the cluster.

- User Managed - To configure and manage your own monitoring stack.

- Select the Enable Autopilot checkbox to enable Portworx Autopilot. For User Managed monitoring stack, Portworx supports the following metrics providers that Autopilot will use to fetch metrics for rule evaluation and automated actions.

- Prometheus - Provide a valid Prometheus URL

- Datadog - Provide a valid Datadog URL, Secret Name and Secret Namespace. To create a Secret, refer to enable Datadog.
 For more information on Autopilot, see Expanding your Storage Pool with Autopilot.

- Select the Enable Telemetry checkbox to enable telemetry in the StorageCluster spec.
For more information, see Enable Pure1 integration for upgrades on an Azure cluster.

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- Select the Secrets Store Type from the dropdown menu to store and manage secure information for features such as CloudSnaps and Encryption.

-
In the Identity and Access Management (IAM) section, choose one of the following authentication methods to use for Portworx to access Azure resources.

- Workload Identity (WLI) - Select this checkbox to use a federated identity with short-lived tokens injected per-pod by the Azure Workload Identity webhook.
Workload Identity Federation enables the Portworx Operator to configure Portworx components to securely authenticate with cloud services without storing static credentials. For more information, see Workload identity for cloud operations in Portworx.
 When you enable Enable Workload Identity (WLI):

- Select the Enable for Stork (for data protection using Portworx DR or Backup) checkbox to enable workload identity for Stork.
You must select this checkbox to use Portworx Backup or Portworx DR.

- In the Azure Managed Identity Client ID field, enter the `clientId` of the managed identity you created in the Workload Identity tab of Configure Authentication section.

- Managed Identity - To use a user-assigned managed identity attached to the Gardener worker node VM Scale Sets.
If you selected this option, the spec generator automatically fetches the `px-azure` secret that contains the managed identity's client ID (`AZURE_CLIENT_ID`) stored in a Kubernetes secret.

- Service Principal - To use a service principal with static credentials.
 If you selected this option, the spec generator automatically fetches the `px-azure` secret that contains the static credentials (`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`) stored in a Kubernetes secret.

-
In the Environment Variables section, enter name-value pairs in the respective fields.

- For deploying Portworx on an Azure Sovereign cloud, specify the value of the `AZURE_ENVIRONMENT` variable in the Name and Value fields.

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

## Deploy Portworx Operator​

-
Use the Operator specifications you generated in the Generate Portworx Specification section, and deploy Portworx Operator by running the following command.

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

-
(Optional) If you have a disaggregated setup, after you generate the StorageCluster spec in the Generate Portworx Specification section, add the following environment variable in the env section:

```

spec:

env:

- name: ENABLE_ASG_STORAGE_PARTITIONING

value: "true"

```

You can also add the environment variables from the spec generator using the Environment Variables dropdown menu.
 After you add the variable, Portworx runs nodes labeled `portworx.io/node-type=storage` as storage nodes and nodes labeled `portworx.io/node-type=storageless` as storageless nodes.

## Deploy StorageCluster​

Use the StorageCluster specifications you generated in the Generate Portworx Specification section, and deploy StorageCluster by running the following command.

```

kubectl apply -f 'https://install.portworx.com/<version-number>?operator=true&mc=false&kbver=&b=true&c=px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b&stork=true&csi=true&mon=true&tel=false&st=k8s&promop=true'

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b created

```

## Monitor Portworx Nodes​

-
Enter the following `kubectl get` command and wait until all Portworx nodes show as `Ready` or `Online` in the output:

```

kubectl -n <px-namespace> get storagenodes -l name=portworx

```

```

NAME                 ID                                     STATUS   VERSION          AGE

username-k8s1-node0   xxxxxxxx-xxxx-xxxx-xxxx-43cf085e764e   Online   2.11.1-3a5f406   4m52s

username-k8s1-node1   xxxxxxxx-xxxx-xxxx-xxxx-4597de6fdd32   Online   2.11.1-3a5f406   4m52s

username-k8s1-node2   xxxxxxxx-xxxx-xxxx-xxxx-e2169ffa111c   Online   2.11.1-3a5f406   4m52s

```

-
Enter the following `kubectl describe` command with the `NAME` of one of the Portworx nodes you retrieved above to show the current installation status for individual nodes:

```

kubectl -n <px-namespace> describe storagenode <portworx-node-name>

```

```

...

Events:

    Type     Reason                             Age                     From                  Message

    ----     ------                             ----                    ----                  -------

    Normal   PortworxMonitorImagePullInPrgress  7m48s                   portworx, k8s-node-2  Portworx image portworx/px-enterprise:2.10.1.1 pull and extraction in progress

    Warning  NodeStateChange                    5m26s                   portworx, k8s-node-2  Node is not in quorum. Waiting to connect to peer nodes on port 9002.

    Normal   NodeStartSuccess                   5m7s                    portworx, k8s-node-2  PX is ready on this node

```

note

- The image pulled in the output differs based on the Portworx license type and version.

- For Portworx Enterprise, the default license activated on the cluster is a 30 day trial, that you can convert to a SaaS-based model or a generic fixed license.

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

kubectl -n <portworx_namespace> get pods <px_pod> -oyaml

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

You can find the status of the Portworx cluster by running `pxctl status` commands from a pod.
Enter the following `kubectl exec` command, specifying the pod name you retrieved in Verify Portworx Pod Status:

```

kubectl exec <pod-name> -n <px-namespace> -- /opt/pwx/bin/pxctl status

```

```

Defaulted container "portworx" out of: portworx, csi-node-driver-registrar

Status: PX is operational

Telemetry: Disabled or Unhealthy

Metering: Disabled or Unhealthy

License: Trial (expires in 31 days)

Node ID: xxxxxxxx-xxxx-xxxx-xxxx-70c31d0f478e

    IP: 192.168.121.99

    Local Storage Pool: 1 pool

    POOL    IO_PRIORITY     RAID_LEVEL      USABLE  USED    STATUS  ZONE    REGION

    0       HIGH            raid0           3.0 TiB 10 GiB  Online  default default

    Local Storage Devices: 3 devices

    Device  Path            Media Type              Size            Last-Scan

    0:1     /dev/vdb        STORAGE_MEDIUM_MAGNETIC 1.0 TiB         14 Jul 22 22:03 UTC

    0:2     /dev/vdc        STORAGE_MEDIUM_MAGNETIC 1.0 TiB         14 Jul 22 22:03 UTC

    0:3     /dev/vdd        STORAGE_MEDIUM_MAGNETIC 1.0 TiB         14 Jul 22 22:03 UTC

    * Internal kvdb on this node is sharing this storage device /dev/vdc  to store its data.

    total           -       3.0 TiB

    Cache Devices:

        * No cache devices

Cluster Summary

    Cluster ID: px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-3e9bf3cd834d

    Cluster UUID: xxxxxxxx-xxxx-xxxx-xxxx-6f3fd5522eae

    Scheduler: kubernetes

    Nodes: 3 node(s) with storage (3 online)

    IP              ID                                      SchedulerNodeName       Auth            StorageNode     Used    Capacity        Status  StorageStatus       Version         Kernel                  OS

    192.168.121.196 xxxxxxxx-xxxx-xxxx-xxxx-fad8c65b8edc    username-k8s1-node0      Disabled        Yes             10 GiB  3.0 TiB         Online  Up 2.11.0-81faacc   3.10.0-1127.el7.x86_64  CentOS Linux 7 (Core)

    192.168.121.99  xxxxxxxx-xxxx-xxxx-xxxx-70c31d0f478e    username-k8s1-node1      Disabled        Yes             10 GiB  3.0 TiB         Online  Up (This node)      2.11.0-81faacc  3.10.0-1127.el7.x86_64  CentOS Linux 7 (Core)

    192.168.121.191 xxxxxxxx-xxxx-xxxx-xxxx-19d45b4c541a    username-k8s1-node2      Disabled        Yes             10 GiB  3.0 TiB         Online  Up  2.11.0-81faacc  3.10.0-1127.el7.x86_64  CentOS Linux 7 (Core)

Global Storage Pool

    Total Used      :  30 GiB

    Total Capacity  :  9.0 TiB

```

Status displays `PX is operational` when the cluster is running as expected. If the cluster is using the PX-StoreV2 datastore, the `StorageNode` entries for each node displays `Yes(PX-StoreV2)`.

## Verify Portworx Pool Status​

note

This procedure is applicable for clusters with PX-StoreV2 datastore.

Run the following command to view the Portworx drive configurations for your pod:

```

kubectl exec <px-pod>  -n <px-namespace> -- /opt/pwx/bin/pxctl service pool show

```

```

Defaulted container "portworx" out of: portworx, csi-node-driver-registrar

PX drive configuration:

Pool ID: 0

    Type:  PX-StoreV2

    UUID:  58ab2e3f-a22e-xxxx-xxxx-xxxxxxxxxxxx

    IO Priority:  HIGH

    Labels:  kubernetes.io/arch=amd64,kubernetes.io/hostname=username-vms-silver-sight-3,kubernetes.io/os=linux,medium=STORAGE_MEDIUM_SSD,beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,iopriority=HIGH

    Size: 25 GiB

    Status: Online

    Has metadata:  No

    Balanced:  Yes

    Drives:

    0: /dev/sda, Total size 32 GiB, Online

    Cache Drives:

    No Cache drives found in this pool

Metadata  Device:

    1: /dev/sdd, STORAGE_MEDIUM_SSD

```

The output `Type: PX-StoreV2` ensures that the pod uses the PX-StoreV2 datastore.

## Verify pxctl Cluster Provision Status​

-
Access the Portworx CLI.

-
Run the following command to find the storage cluster:

```

kubectl -n <px-namespace> get storagecluster

```

```

NAME                                              CLUSTER UUID                           STATUS   VERSION   AGE

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-3e9bf3cd834d   xxxxxxxx-xxxx-xxxx-xxxx-6f3fd5522eae   Online   2.11.0    10m

```

The status must display the cluster is `Online`.

-
Run the following command to find the storage nodes:

```

kubectl -n <px-namespace> get storagenodes

```

```

NAME                  ID                                     STATUS   VERSION          AGE

username-k8s1-node0   xxxxxxxx-xxxx-xxxx-xxxx-fad8c65b8edc   Online   2.11.0-81faacc   11m

username-k8s1-node1   xxxxxxxx-xxxx-xxxx-xxxx-70c31d0f478e   Online   2.11.0-81faacc   11m

username-k8s1-node2   xxxxxxxx-xxxx-xxxx-xxxx-19d45b4c541a   Online   2.11.0-81faacc   11m

```

The status must display the nodes are `Online`.

-
Verify the Portworx cluster provision status by running the following command.
 Specify the pod name you retrieved in Verify Portworx Pod Status.

```

kubectl exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl cluster provision-status

```

```

NODE					                NODE STATUS	 POOL						              POOL STATUS  IO_PRIORITY	SIZE	AVAILABLE	USED   PROVISIONED ZONE REGION	RACK

0c99e1f2-9d49-xxxx-xxxx-xxxxxxxxxxxx	Up		    0 ( 8ec9e6aa-7726-xxxx-xxxx-xxxxxxxxxxxx )	Online		HIGH		32 GiB	32 GiB		33 MiB	0 B		default	default	default

1e89102f-0510-xxxx-xxxx-xxxxxxxxxxxx	Up		    0 ( 06fcc73a-7e2f-xxxx-xxxx-xxxxxxxxxxxx )	Online		HIGH		32 GiB	32 GiB		33 MiB	0 B		default	default	default

24508311-e2fe-xxxx-xxxx-xxxxxxxxxxxx	Up		    0 ( 58ab2e3f-a22e-xxxx-xxxx-xxxxxxxxxxxx )	Online		HIGH		32 GiB	32 GiB		33 MiB	0 B		default	default	default

```

## What to do next​

- Create a PVC. For more information, see Create your first PVC.

- You can enable disk locking on Azure disks to prevent accidental or external deletion of the disks. For more information, see Azure Disk Locking.

In this topic:
