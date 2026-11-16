# Installation on Non-Air-Gapped vSphere OpenShift Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/vsphere/ocp-vsphere-non-airgap (Portworx Enterprise latest)

Installation on Non-Air-Gapped vSphere OpenShift Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx on a non-air-gapped VMware vSphere OpenShift cluster using the OpenShift Container Platform web console.

The following collection of tasks describe how to install Portworx on a non-air-gapped VMware vSphere OpenShift cluster:

- Create a Monitoring ConfigMap

- Create a vCenter user account for Portworx

- Create a secret with your vCenter user credentials

- Generate Portworx Enterprise Specification

- Install Portworx Operator using OpenShift Console

- Deploy Portworx using OpenShift Console

- Verify Portworx Cluster Status

- Verify Portworx Pod Status

Complete all the tasks to install Portworx.

## Create a Monitoring ConfigMap​

Enable monitoring for user-defined projects before installing the Portworx Operator. Use the instructions in this section to configure the OpenShift Prometheus deployment to monitor Portworx metrics.

To integrate OpenShift’s monitoring and alerting system with Portworx, create a cluster-monitoring-config ConfigMap in the openshift-monitoring namespace:

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

The `enableUserWorkload` parameter enables monitoring for user-defined projects in the OpenShift cluster. This creates a `prometheus-operated` service in the `openshift-user-workload-monitoring` namespace.

## Create a vCenter user account for Portworx​

Using your vSphere console, provide Portworx with a vCenter server user account that has the following minimum vSphere privileges at vCenter datacenter level:

-
Datastore

- Allocate space

- Browse datastore

- Low level file operations

- Remove file

-
Host

- Local operations

- Reconfigure virtual machine

-
Virtual machine

- Change Configuration

- Add existing disk

- Add new disk

- Add or remove device

- Advanced configuration

- Change Settings

- Extend virtual disk

- Modify device settings

- Remove disk

If you create a custom role as above, make sure to select Propagate to children when assigning the user to the role.

Why select `Propagate to Children` ?

In vSphere, resources are organized hierarchically. Select Propagate to children to ensure that the permissions granted to the custom role are automatically applied not just to the targeted object, but also to all objects within its sub-tree. This includes VMs, datastores, networks, and other resources nested under the selected resource.

## Create a secret with your vCenter user credentials​

Create a secret using the following steps.

- Kubernetes Secret

- Vault Secret

-
Get the vCenter user and password by running the following commands:

- For `VSPHERE_USER`: `echo '<vcenter-server-user>' | base64`

- For `VSPHERE_PASSWORD`: `echo '<vcenter-server-password>' | base64`

-
Update the following Kubernetes Secret template by using the values obtained in step 1 for `VSPHERE_USER` and `VSPHERE_PASSWORD`.

```

apiVersion: v1

kind: Secret

metadata:

  name: px-vsphere-secret

  namespace: <px-namespace>

type: Opaque

data:

  VSPHERE_USER: XXXX

  VSPHERE_PASSWORD: XXXX

```

-
Apply the above spec to update the spec with your VCenter username and password:

```

oc apply -f <updated-secret-template.yaml>

```

tip

To enable TLS certificate verification for vCenter, add the CA certificate used to verify the vCenter certificate to this secret with the `VSPHERE_CA_CERT` key. For more information, see Enable TLS Certificate Verification for vCenter.

important

Ensure that the ports 17001-17020 on worker nodes are reachable from the control plane node and other worker nodes.

When using Portworx with vSphere, you can supply the vSphere credentials by creating a secret in Vault. Follow the steps below to properly create and verify the secret.

#### Step 1: Create the Secret​

Store vSphere credentials (username and password) as key-value pairs at the path `secret/vsphereCredentials`. If you are not using a custom backend path, use `secret` as shown. If you are using a custom secret path, replace `secret` with your custom path.

Run the following command, substituting the placeholder values with your actual credentials:

```

vault kv put secret/vsphereCredentials VSPHERE_PASSWORD=<vsphere_password> VSPHERE_USER=<vsphere_user>

```

If your custom secret path is, for example, customPath:

```

vault kv put customPath/vsphereCredentials VSPHERE_PASSWORD=<vsphere_password> VSPHERE_USER=<vsphere_user>

```

#### Step 2: Retrieve and Verify the Secret​

To ensure that the secret was created correctly, use this command:

```

vault kv get secret/vsphereCredentials

```

The command should return an output similar to the following:

```

========== Data ==========

Key                 Value

---                 -----

VSPHERE_PASSWORD    <vsphere_password>

VSPHERE_USER        <vsphere_user>

```

important

- Ensure that the correct vSphere credentials are securely stored in Vault before Portworx installation.

- Ensure that the ports 17001-17020 on worker nodes are reachable from the control plane node and other worker nodes.

## Generate Portworx Enterprise Specification​

To install Portworx, you must first generate Kubernetes manifests that you will deploy in your vSphere Openshift cluster by following these steps.

-
Sign in to the Portworx Central console.
 The system displays the Welcome to Portworx Central! page.

-
In the Portworx Enterprise section, select Generate Cluster Spec.
 The system displays the Generate Spec page.

-
From the Portworx Version dropdown menu, select the Portworx version to install.

-
From the Platform dropdown menu, select vSphere.

-
In the vCenter Endpoint field, specify the hostname or the IP address of the vSphere server.

-
In the vCenter Datastore Prefix field, specify the datastore name(s) or datastore cluster name(s) available for Portworx.
To specify multiple datastore names or datastore cluster names, enter a generic prefix common to all the datastores or datastore clusters. For example, if you want Portworx to use three datastores named `px-datastore-01`, `px-datastore-02`, and `px-datastore-03`, specify `px` or `px-datastore`.

-
From the Distribution Name dropdown menu, select Openshift 4+.

-
(Optional) To customize the configuration options and generate a custom specification, click Customize and perform the following steps:

note

To continue without customizing the default configuration or generating a custom specification, proceed to Step 9.

- Basic tab:

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

- Storage tab:

- To enable Portworx to provision drives using a specification, do the following:

- Select the Create Using a Spec option.

- Select PX-Store Version: (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- To add one or more storage drive types for Portworx to use, click + Add Drive and select one of the following types of drives:

- Lazy-Zeroed Thick

- Eager-Zeroed Thick

- Thin

note

The system automatically selects the minimum number of drives to ensure optimal performance.

- Configure the following fields for the drive:

- Size (GB) - Specify the size of the drive in gigabytes.

- Action - Use the trash icon to remove a drive type from the configuration.

- (Optional) To add more storage drives, click one of the following options based on the drive type:

- + Add Lazy-Zeroed Thick Drives

- + Add Eager-Zeroed Thick Drives

- + Add Thin Drives

- Initial Storage Nodes (Optional): Enter the number of storage nodes that need to be created across zones and node pools.

- From the Default IO Profile dropdown menu, select Auto.
This enables Portworx to automatically choose the best I/O profile based on detected workload patterns.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually choose a volume type for the journal device.

- To enable Portworx to use all available, unused, and unmounted drives on the node, do the following:

- Select the Consume Unused option.

- (Optional) To designate PX-StoreV1 as the datastore, clear the PX-StoreV2 checkbox. By default, the system selects PX-StoreV2 as the datastore.

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

- (Optional) To designate PX-StoreV1 as the datastore, clear the PX-StoreV2 checkbox. By default, the system selects PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
The path must be at least 64 GB in size.

- In the Drive/Device field, specify the block drive(s) that Portworx uses for data storage.
To add another block drive, click the + icon.

- (Optional) In the Pool Label field, assign a custom label in key:value format to identify and categorize storage pools.
 For more information refer to How to assign custom labels to device pools.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
Enter the path of the journal device in the Journal Device Path field.

- Select Next.

- Network tab:

- In the Interface(s) section, do the following:

- Enter the Data Network Interface to be used for data traffic.

- Enter the Management Network Interface to be used for management traffic.

- In the Advanced Settings section, do the following:

- Enter the Starting port for Portworx services.

- Select Next.

- Deployment tab:

-
In the Kubernetes Distribution section, under Are you running on either of these?, select Openshift 4+.

-
In the Component Settings section:

- Select the Enable Stork checkbox to enable Stork.

- Select the Restrict Data Protection RBAC to restrict RBAC permissions for Stork (if enabled). You will not be able to use Backup and DR capabilities with this restriction. For more information, see Restrict Data Protection RBAC.

- (Optional) Select the Remote Fastpath (NVMe-oF/TCP) checkbox to enable Remote Fastpath. For more information, see Remote Fastpath.

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
For more information, see Enable Pure1 integration for upgrades on a VMware vSphere cluster.

-
In the Configure Secret Details section:

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- To use a key management service (KMS) to store encryption keys, secrets, or credentials for features such as CloudSnap, volume encryption, or cloud provider integrations, select the appropriate KMS from the Default Secrets Store Type dropdown menu. For more information, see Set Up Key Management and Encrypt Portworx Volumes.

- Click the toggle button to Configure Secrets Store Type per Feature. Configure multiple secret providers and assign a different secret store to each feature. If you enable the toggle and do not select the secrets store for the features, Portworx Enterprise uses Default Secret Store Type for cloud provider credentials. For more information, see Configure multiple secrets providers.

- Select the Secret Store Type for Cloud Provider Credentials feature from the dropdown menu.

- Select the Secret Store Type for Volume Encryption feature from the dropdown menu.

- Select the Secret Store Type for Cloud Snap feature from the dropdown menu.

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

## Install Portworx Operator using OpenShift Console​

-
Sign in to the OpenShift Container Platform web console.

-
Search for the Portworx Operator:

- OCP version 4.20 or later:
 From the OpenShift UI, go to Ecosystem > Software Catalog. From Project dropdown, select Create Project to create a new project. Enter a name for new project and select that project. Search for Portworx Operator, and the Portworx Operator page appears.

- OCP version 4.19 or earlier:
 From the OpenShift UI, go to OperatorHub, search for Portworx Operator, and the Portworx Operator page appears.

-
Click Install.
The system initiates the Portworx Operator installation and displays the Install Operator page.

-
In the Installation mode section, select A specific namespace on the cluster.

-
From the Installed Namespace dropdown, choose Create Project.
The system displays the Create Project window.

-
Provide the name `portworx` and click Create to create a namespace called portworx.

-
In the Console plugin section, select Enable to manage your Portworx cluster using the Portworx dashboard within the OpenShift console.

note

If the Portworx Operator is installed but the OpenShift Console plugin is not enabled, or was previously disabled, you can re-enable it by running the following command.

```

oc patch console.operator cluster --type=json -p='[{"op":"add","path":"/spec/plugins/-","value":"portworx"}]'

```

-
Click Install to deploy Portworx Operator in the `portworx` namespace.
 After you successfully install Portworx Operator, the system displays the Create StorageCluster option.

## Deploy Portworx using OpenShift Console​

-
Click Create StorageCluster.
The system displays the Create StorageCluster page.

-
Select YAML view.

-
Copy and paste the specification that you generated in the Generate Portworx Enterprise Specification section into the text editor.

-
Click Create.
 The system deploys Portworx, and displays the Portworx instance in the Storage Cluster tab of the Installed Operators page. Refresh your browser to see the Portworx option in the left navigation pane. Click the Cluster tab to access the Portworx dashboard.

note

For clusters with PX-StoreV2 datastores, after you deploy Portworx, the Portworx Operator performs a pre-flight check across the cluster, and the check must pass on each node. This check determines whether each node in the cluster is compatible with the PX-StoreV2 datastore. If each node meets the minimum requirements for PX-StoreV2, PX-StoreV2 is automatically set as the default datastore during Portworx installation.

## Verify Portworx Cluster Status​

After you install Portworx Operator and create the StorageCluster, you can see the Portworx option in the left pane of the OpenShift UI.

- Click the Cluster sub-tab to view the Portworx dashboard. If Portworx is installed correctly, the status will be displayed as Running. You can also see the information about the status of Telemetry, Monitoring, and the version of Portworx and its components installed in your cluster.

- Navigate to the Node Summary section. If your cluster is running as intended, the status of all Portworx nodes displays Online.

## Verify Portworx Pod Status​

- From the left pane of the OpenShift UI, click Pods under the Workload option.

- To check the status of all pods in the `portworx` namespace, select portworx from the Project drop-down. If Portworx is installed correctly, then all pods should be in Running status.

## What to do next​

Create a PVC. For more information, see Create your first PVC.

In this topic:
