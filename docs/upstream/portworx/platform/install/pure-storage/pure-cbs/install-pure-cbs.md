# Installation of Portworx with Everpure Cloud Dedicated for Azure and AWS using Portworx Central

Source: https://docs.portworx.com/portworx-enterprise/platform/install/pure-storage/pure-cbs/install-pure-cbs (Portworx Enterprise latest)

Installation of Portworx with Everpure Cloud Dedicated for Azure and AWS using Portworx Central | Portworx Enterprise Documentation

After preparing your environment, deploy the Portworx Operator first, followed by the Portworx StorageCluster. The Portworx Operator automates the deployment, configuration, upgrades, and integration of Portworx with your Kubernetes cluster.

To install Portworx with Everpure Cloud Dedicated, complete the following collection of tasks:

Complete all the tasks to install Portworx.

## Prerequisites​

- Ensure that system requirements are met.

- Ensure your Kubernetes cluster is configured to use Everpure Cloud Dedicated with Azure or AWS. For more information, see Prepare your Environment for Installation of Portworx with Everpure Cloud Dedicated

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

To continue without customizing the default configuration, proceed to Step 7.

- Basic tab (etcd cluster details):

- Select Your etcd details to use an existing etcd cluster and enter the host name or IP and port number.

- Select one of the following authentication methods:

- Disable HTTPS – Use HTTP for etcd communication.

- Certificate Auth – Use HTTPS with an SSL certificate.
For more information, see Secure your etcd communication.

- Password Auth – Use HTTPS with username and password authentication.

- To use an internal Portworx-managed key-value store (KVDB), do the following:

- Select the Built-in option.

- TLS for internal KVDB is enabled, by default. If Cert-Manager is already running in your Kubernetes cluster, deselect the Deploy Cert-Manager for TLS certificates option to avoid installation failures.

- Select Next.

- Storage tab (storage and multitenancy configuration):

- Select type of drive as Create Using a Spec to create Everpure Cloud Dedicated managed disks using the following spec.

- Select backend store based on your infrastructure as PX-StoreV1 or PX-StoreV2.

- From the Select type of storage area network dropdown, choose one of the following:

- iSCSI(Default)

- NVMe-oF TCP
Using the above SAN type, the volumes from Everpure Cloud Dedicated will be connected to the Portworx nodes.

- Enter the size of the pool drive(s) in GB.

- Select Default IO Profile for Portworx volumes.

- Under Journal Device, select one of the following:

- None – Use the default journaling setting.

- Auto – Automatically allocate journal devices.

- Custom – Manually enter a journal device path.
Enter the path of the journal device in the Journal Device Path field.

- Select Next.

- Network tab (network settings):

- Enter the Data Network Interface used by Portworx nodes for exchanging data. This setting does not apply to Everpure Cloud Dedicated connections.

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

- Select the Enable Fusion Controller checkbox to enable Portworx Fusion Controller (Early Access release) for OpenShift Distribution types. For more information on Portworx Fusion Controller, see Portworx Fusion Controller documentation.

- Select the Enable Telemetry checkbox to enable telemetry in the StorageCluster spec.
For more information, see Enable Pure1 integration for upgrades on an Azure Red Hat OpenShift cluster.

-
In the Configure Secret Details section:

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- To use a key management service (KMS) to store encryption keys, secrets, or credentials for features such as CloudSnap, volume encryption, or cloud provider integrations, select the appropriate KMS from the Default Secrets Store Type dropdown menu. For more information, see Set Up Key Management and Encrypt Portworx Volumes.

- Click the toggle button to Configure Secrets Store Type per Feature. Configure multiple secret providers and assign a different secret store to each feature. If you enable the toggle and do not select the secrets store for the features, Portworx Enterprise uses Default Secret Store Type for cloud provider credentials. For more information, see Configure multiple secrets providers.

- Select the Secret Store Type for Cloud Provider Credentials feature from the dropdown menu.

- Select the Secret Store Type for Volume Encryption feature from the dropdown menu.

- Select the Secret Store Type for Cloud Snap feature from the dropdown menu.

-
(Optional) In Environment Variables, enter name-value pairs in the respective fields.

- If you are using multiple NICs for iSCSI host, then add the following environment variable to your StorageCluster spec. Replace `<nic-interface-names>` with comma-separated names of NICs such as `"eth1,eth2"`:

```

env:

- name: PURE_ISCSI_ALLOWED_IFACES

  value: "<nic-interface-names>"

```

note

If you have multiple NICs on your virtual machine, then Everpure Cloud Dedicated does not distinguish the NICs that include iSCSI and the others without iSCSI. This list must be provided, otherwise Portworx may potentially use only one of the provided interfaces.

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

Once deployed, Portworx detects that the Everpure Cloud Dedicated secret is present when it starts up and can use the specified Everpure Cloud Dedicated as a storage provider.

## What to do next​

Create a PVC. For more information, see Create your first PVC.

In this topic:
