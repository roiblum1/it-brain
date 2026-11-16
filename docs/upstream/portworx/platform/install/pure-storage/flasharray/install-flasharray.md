# Installation of Portworx with FlashArray using Portworx Central

Source: https://docs.portworx.com/portworx-enterprise/platform/install/pure-storage/flasharray/install-flasharray (Portworx Enterprise latest)

Installation of Portworx with FlashArray using Portworx Central | Portworx Enterprise Documentation

After preparing your environment, deploy the Portworx Operator first, followed by the Portworx StorageCluster. The Portworx Operator automates the deployment, configuration, upgrades, and integration of Portworx with your Kubernetes cluster.

The following collection of tasks describes how to install Portworx with FlashArray:

Complete all the tasks to install Portworx.

## Prerequisites​

- Ensure that system requirements are met.

- Ensure your Kubernetes cluster is configured to use FlashArray. For more information, see Prepare your Environment for Installing Portworx Enterprise with FlashArray

## Generate Portworx Specification​

- Sign in to the Portworx Central console.
 The system displays the Welcome to Portworx Central! page.

- In the Portworx Enterprise section, select Generate Cluster Spec.
 The system displays the Generate Spec page.

- From the Portworx Version dropdown menu, select the Portworx version to install.

- From the Platform dropdown menu, select Pure FlashArray.

- From the Distribution Name dropdown menu, select a Kubernetes distribution.

- (Optional) To customize the configuration options and generate a custom specification with multi-tenancy, click Customize and perform the following steps:

note

To continue without customizing the default configuration and install Portworx with standard FlashArray, proceed to Step 7.

- Basic tab (etcd cluster details):

- Select Your etcd details to use an existing etcd cluster and enter the host name or IP and port number.

- Select one of the following authentication methods:

- Disable HTTPS – Use HTTP for etcd communication.

- Certificate Auth – Use HTTPS with an SSL certificate.
For more information, see Secure your etcd communication.

- Password Auth – Use HTTPS with username and password authentication.

- To use an internal Portworx-managed key-value store (KVDB), do the following:

- Select the Built-in option.

- TLS for internal KVDB is enabled by default. If Cert-Manager is already running in your Kubernetes cluster, deselect the Deploy Cert-Manager for TLS certificates option to avoid installation failures.

- Select Next.

- Storage tab (storage and multitenancy configuration):

- Select type of drive as Create Using a Spec to create Pure FlashArray managed disks using the following spec.

- Select backend store based on your infrastructure as PX-StoreV1 or PX-StoreV2. By default, the system selects PX-StoreV2 as the datastore.

- (Optional) Select the Run on Small Node Configuration checkbox if your cluster nodes have limited resources (for example, 4 CPU cores and 8 GB of memory).
Portworx requires 8 CPU cores and 8 GB of memory by default. Enabling this option allows Portworx to run on smaller nodes, but it may reduce overall performance compared to the default configuration.

note

This checkbox is available only when you select PX-StoreV2 as the datastore.

- (Optional) Select the Enable Dynamic Pool checkbox to enable dynamic pools. For more information, see Dynamic Pools.

- From the Select type of storage area network dropdown, choose one of the following:

- iSCSI(Default)

- NVMe-oF RDMA

- NVMe-oF TCP

- Fibre Channel.
Using the above SAN type, the volumes from FlashArray will be connected to the Portworx nodes.

- Select the checkbox for Enable multitenancy.
Enter a FlashArray pod name in the Pure FA Pod Name field.

- In Selected Drives:

- Enter Size of the pool drive(s) in GB.

- Add Drive Tags to add custom disk tags in key:value format to organize and identify drives.
 This is useful for policies and workload mapping. For more information, refer Custom Disk Tags

- Select Default IO Profile for Portworx volumes.

- Under Journal Device, select one of the following:

- None – Use the default journaling setting.

- Auto – Automatically allocate journal devices.

- Custom – Manually enter a journal device path.
Enter the path of the journal device in the Journal Device Path field.

- Select Next.

- Network tab (network settings):

- Enter the Data Network Interface used by Portworx nodes for exchanging data. This setting does not apply to FlashArray connections.

- Enter the Management Network Interface to be used for management traffic.

- Enter the Starting port for Portworx services.

- Select Next.

- Deployment tab (advanced settings):

-
In the Kubernetes Distribution section, under Are you running on either of these?, select a Kubernetes distribution or None.

-
In the Component Settings section:

- Select the Enable Stork checkbox to enable Stork.

- (Optional) Select the Remote Fastpath (NVMe-oF/TCP) checkbox to enable Remote Fastpath. For more information, see Remote Fastpath.

- Select the Restrict Data Protection RBAC to restrict RBAC permissions for Stork (if enabled) and Operator (not supported for OpenShift 4+). You will not be able to use Backup and DR capabilities with this restriction. For OpenShift 4+, selecting Enable Stork is required to enable Restrict Data Protection RBAC. For more information, see Restrict Data Protection RBAC.

- Select the Enable Monitoring checkbox to enable monitoring of Portworx components and resources.

- To configure the monitoring stack, select one of the following:

- Portworx Managed - To enable Portworx to install and manage Prometheus and Operator automatically.
 Ensure that no other Prometheus Operator instance is already running on the cluster.

- User Managed - To configure and manage your own monitoring stack.

- Select the Enable Autopilot checkbox to enable Portworx Autopilot. For User Managed monitoring stack, Portworx supports the following metrics providers that Autopilot will use to fetch metrics for rule evaluation and automated actions.

- Prometheus - Provide a valid Prometheus URL

- Datadog - Provide a valid Datadog URL, Secret Name and Secret Namespace. To create a Secret, refer to enable Datadog.
 For more information on Autopilot, see Expanding your Storage Pool with Autopilot.

- Select the Enable Fusion Controller checkbox to enable Portworx Fusion Controller (Early Access release) for OpenShift Distribution types. For more information on Portworx Fusion Controller, see Portworx Fusion Controller documentation.

- Select the Enable Telemetry checkbox to enable telemetry in the StorageCluster spec.
For more information, see Enable Pure1 integration for upgrades on an Azure Red Hat OpenShift cluster.

- Select the Enhanced FA/FB Driver checkbox to enable the FA/FB driver. For more information, see FlashArray/FlashBlade Driver.

-
In the Configure Secret Details section:

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- To use a key management service (KMS) to store encryption keys, secrets, or credentials for features such as CloudSnap, volume encryption, or cloud provider integrations, select the appropriate KMS from the Default Secrets Store Type dropdown menu. For more information, see Set Up Key Management and Encrypt Portworx Volumes.

- Click the toggle button to Configure Secrets Store Type per Feature. Configure multiple secret providers and assign a different secret store to each feature. If you enable the toggle and do not select the secrets store for the features, Portworx Enterprise uses Default Secret Store Type for cloud provider credentials. For more information, see Configure multiple secrets providers.

- Select the Secret Store Type for Cloud Provider Credentials feature from the dropdown menu.

- Select the Secret Store Type for Volume Encryption feature from the dropdown menu.

- Select the Secret Store Type for Cloud Snap feature from the dropdown menu.

-
(Optional) In Environment Variables section, enter name-value pairs in the respective fields.

- If you are using multiple NICs for iSCSI host, then add the following environment variable to your StorageCluster spec. Replace `<nic-interface-names>` with comma-separated names of NICs such as `"eth1,eth2"`:

```

env:

- name: PURE_ISCSI_ALLOWED_IFACES

  value: "<nic-interface-names>"

```

note

If you have multiple NICs on your virtual machine, then FlashArray does not distinguish between the NICs that include iSCSI and those without iSCSI. This list must be provided, otherwise Portworx may potentially use only one of the provided interfaces.

- For restricting Portworx services from listening on all network interfaces, set `PX_DISABLE_WILDCARD_LISTENERS` to `"true"`. By default, Portworx services listen on `0.0.0.0` (all interfaces). When this environment variable is set to true, each service listens only on its management IP, data IP or local loopbacks as required. If you do not set `PX_DISABLE_WILDCARD_LISTENERS` to `"true"` during spec generation, you can add it later to the StorageCluster spec as an environment variable.

note

- When you update `PX_DISABLE_WILDCARD_LISTENERS` in StorageCluster, it triggers a rolling update of the cluster. This causes Portworx to restart on each node and it comes up with the new network configuration. We recommend making this change during a planned maintenance window.

- You cannot switch the IP address family (IPv4 to IPv6 or IPv6 to IPv4) using `PX_PREFER_IPV6_NETWORK_IP` while `PX_DISABLE_WILDCARD_LISTENERS` is set to `"true"`. To switch the IP address family, first disable `PX_DISABLE_WILDCARD_LISTENERS`, switch the IP family, and then re-enable `PX_DISABLE_WILDCARD_LISTENERS`.

-
In Registry and Image Settings:

- Enter the Custom Container Registry Location to download the Docker images.

- Enter the Kubernetes Docker Registry Secret that serves as the authentication to access the custom container registry.

- From the Image Pull Policy dropdown menu, select Default, Always, IfNotPresent, or Never.
This policy influences how images are managed on the node and when updates are applied.

-
In Security Settings, select the Enable Authorization checkbox to enable Role-Based Access Control (RBAC) and secure access to storage resources in your cluster.

-
Click Finish.

-
In the summary page, enter a name for the specification in the Spec Name field, and tags in the Spec Tags field.

-
Click Download .yaml to download the yaml file with the customized specification or Save Spec to save the specification.

- Click Save & Download to generate the specification.

note

You can either copy the `kubectl apply` command from the Central UI and apply it to your Kubernetes cluster, or download the YAML file and apply it using the file name.

## Provision storage pools from a specific FlashArray​

If your environment includes multiple FlashArrays, you can control which FlashArray Portworx uses for each storage pool by specifying the `storage_backend` field in the device specification. Set the value to the FlashArray name or management endpoint.

The following `cloudStorage` configuration provisions one storage pool from each of three FlashArrays on every storage node:

```

cloudStorage:

  deviceSpecs:

    - size=100,storage_backend=<fa1-name>

    - size=100,storage_backend=<fa2-management-endpoint>

    - size=200,storage_backend=<fa3-name>

```

This configuration creates three storage pools on each storage node, one from each FlashArray. Portworx creates a separate KDS for each FlashArray when its first pool is provisioned.

Pool provisioning also follows CSI topology. If a device specification includes the `pod` field, Portworx uses the specified FlashArray pod placement.

note

Portworx applies `deviceSpecs` only when provisioning new storage nodes. Changes to this field do not affect existing storage nodes. Similarly, changes made to storage pools on an existing node by using `pxctl` are not reflected in the `StorageCluster` specification.

Portworx Enterprise creates a Kube Datastore for each FlashArray when the first storage pool is provisioned on that array. For more information, see Select the KDS for storage pools.

## (Optional) Customize Portworx system volumes for secure multi-tenancy​

If you're deploying Portworx with Pure FlashArray and the Secure Multi-Tenancy (SMT) feature, you can assign either the same pod that is used for `deviceSpecs` or assign each system volume to a different FlashArray pod within the same realm, based on your requirements.

To place system volumes, such as journal, key-value database (KVDB), and system metadata, in specific FlashArray pods, customize the `cloudStorage` section in your StorageCluster specification:

```

cloudStorage:

  deviceSpecs:

    - size=2000,pod=<fa-pod-name>               # volume for storage pool

  journalDeviceSpec: size=3,pod=<fa-pod-name>   # Journal volume

  kvdbDeviceSpec: size=32,pod=<fa-pod-name>     # Internal KVDB volume

  systemMetadataDeviceSpec: size=32,pod=<fa-pod-name> # System metadata volume

```

important

If you are also using FACD CSI topology, you must use the same `pod` name across all FlashArrays in your `pure.json` configuration. The Portworx Operator applies the `pod` value from the first matching `deviceSpecs` entry cluster-wide as the system metadata device spec. Nodes in zones where that pod does not exist will fail to provision storage.

For more information about `cloudStorage` fields, see Cloud storage configuration.

## Apply Portworx Specification​

Apply the Operator and StorageCluster specs you generated in the section above using the `oc apply` command:

note

- If you have downloaded and modified the specification, use that in the `kubectl apply` command below, instead of the specification URL generated from Portworx Central.

- OpenShift Container Platform

- Other Kubernetes platforms

-
From the OpenShift UI, go to OperatorHub, search for Portworx Operator, and click Install to deploy the Portworx Operator in a desired namespace.

-
Deploy the StorageCluster:

```

oc apply -f '<url-generated-from-portworx-central-spec-gen>'

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-5db83030471e created

```

-
Deploy the Operator:

```

kubectl apply -f '<url-generated-from-portworx-central-spec-gen>'

```

```

serviceaccount/portworx-operator created

podsecuritypolicy.policy/px-operator created

clusterrole.rbac.authorization.k8s.io/portworx-operator created

clusterrolebinding.rbac.authorization.k8s.io/portworx-operator created

deployment.apps/portworx-operator created

```

-
Deploy the StorageCluster:

```

kubectl apply -f '<url-generated-from-portworx-central-spec-gen>'

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-5db83030471e created

```

Once deployed, Portworx detects that the FlashArray secret is present when it starts up and can use the specified FlashArray as a storage provider.

## What to do next​

Create a PVC:

- For FlashArray cloud drives, see Create your first PVC.

- For FlashArray Direct Access volumes, see Configure FlashArray as a Direct Access volume.

In this topic:
