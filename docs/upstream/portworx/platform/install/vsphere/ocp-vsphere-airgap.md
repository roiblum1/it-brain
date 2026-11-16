# Installation on Air-Gapped vSphere OpenShift Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/vsphere/ocp-vsphere-airgap (Portworx Enterprise latest)

Installation on Air-Gapped vSphere OpenShift Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx on an air-gapped VMware vSphere OpenShift cluster using the internal OpenShift cluster registry.

The following collection of tasks describe how to install Portworx Enterprise on an air-gapped VMware vSphere OpenShift cluster:

- Configure your Environment

- Create a version manifest configmap for Portworx Operator

- Generate Portworx Specification

- Deploy Portworx Operator

- Deploy StorageCluster

- Verify Portworx Pod Status

- Verify Portworx Cluster Status

- Verify Portworx Pool Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx.

## Configure your Environment​

-
On your internet-connected host, set an environment variable for the Kubernetes version that you are using:

```

KBVER=$(oc version | awk -F'[v+_-]' '/Kubernetes/ {print $2}')

```

-
Set an environment variable to the latest major version of Portworx:

```

PXVER=<portworx-version>

```

-
On an internet-connected host with the same architecture and OS version as the Kubernetes cluster nodes intended for Portworx installation, download the air-gapped installation bootstrap script for the specified Kubernetes and Portworx versions:

```

curl -o px-ag-install.sh -L "https://install.portworx.com/$PXVER/air-gapped?kbver=$KBVER"

```

-
Pull the container images required for the specified versions:

```

sh px-ag-install.sh pull

```

-
Authenticate to the OpenShift internal registry.

For example:

```

oc login -u admin -p password https://api.lab.ocp.lan:6443

```

```

Login successful.

[...]

Using project "default".

```

-
Log in to your registry, substituting `docker` for `podman` if you are not using Podman.

For example:

```

podman login -u admin -p $(oc whoami -t) default-route-openshift-image-registry.apps.lab.ocp.lan

```

```

Login Succeeded!

```

note

If the host you're running Podman from does not have the cluster's certificate authority in its trusted-stores, you will need to pass the `--tls-verify=false` flag to the login command.

-
Push the container images to your internal OpenShift cluster registry.

For example:

```

sh px-ag-install.sh push default-route-openshift-image-registry.apps.lab.ocp.lan/kube-system

```

-
Create a secret for the Operator to use that contains the registry credentials.

For example:

```

oc -n portworx create secret docker-registry px-image-repository \

    --docker-server=image-registry.openshift-image-registry.svc:5000 \

    --docker-username=admin \

    --docker-password=$(oc whoami -t)

```

```

Login Succeeded!

```

## Create a version manifest configmap for Portworx Operator​

-
Download the Portworx version manifest:

```

curl -o versions.yaml "https://install.portworx.com/$<portworx-version>/version?kbver=$<kubernetes-version>&opver=$<operator-version>"

```

Replace:

- `<portworx_version>` with the Portworx version you want to use.

- `<kubernetes-version>` with the Kubernetes version you want to use.

- `<operator-version>` with the Operator version you want to use.

-
Create a configmap from the downloaded `versions.yaml`:

```

oc -n portworx create configmap px-versions --from-file=versions.yaml

```

## Create a vCenter user account for Portworx​

- Using your vSphere console, provide Portworx with a vCenter Server user account that has the following minimum vSphere privileges at vCenter Server datacenter level:

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

In vSphere, resources are organized hierarchically. By selecting "Propagate to Children," you ensure that the permissions granted to the custom role are automatically applied not just to the targeted object, but also to all objects within its sub-tree. This includes VMs, datastores, networks, and other resources nested under the selected resource.

## Provide the vCenter user credentials​

In order to grant Portworx the necessary permissions for managing the storage block devices that the storage nodes require, create a secret with user credentials.

- Kubernetes Secret

- Vault Secret

-
Get the vCenter Server username and password by running the following commands:

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
Apply the above spec to update the spec with your vCenter Server username and password:

```

oc apply -f <updated-secret-template.yaml>

```

tip

To enable TLS certificate verification for vCenter, add the CA certificate used to verify the vCenter certificate to this secret with the `VSPHERE_CA_CERT` key. For more information, see Enable TLS Certificate Verification for vCenter.

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

## Generate Portworx Specification​

To install Portworx, you must first generate Kubernetes manifests that you will deploy in your vSphere OpenShift cluster by following these steps.

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
From the Distribution Name dropdown menu, select OpenShift 4+.

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

- TLS for internal KVDB is enabled by default. If Cert-Manager is already running in your Kubernetes cluster, deselect the Deploy Cert-Manager for TLS certificates option to avoid installation failures.

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
In the Kubernetes Distribution section, under Are you running on either of these?, select OpenShift 4+.

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

## Deploy Portworx Operator​

Use the Operator specifications you generated in the Generate Portworx Specification section, and deploy Portworx Operator by running the following command:

```

oc apply -f 'https://install.portworx.com/<PXVER>?comp=pxoperator&reg=image-registry.openshift-image-registry.svc:5000/kube-system'

```

## Deploy StorageCluster​

-
Use the StorageCluster specifications you generated in the Generate Portworx Specification section, and deploy StorageCluster by running the following command:

```

oc apply -f '<storagecluster-deployment-URL>'

```

```

storagecluster.core.libopenstorage.org/px-cluster-<randomUUID> created

```

note

If you installed the Portworx Operator manually, run the following command to annotate the newly created StorageCluster and identify it as an OpenShift environment:

```

 oc -n kube-system annotate stc $(oc -n kube-system get stc -o jsonpath='{.items[0].metadata.name}') 'portworx.io/is-openshift=true'

```

-
(Optional) If you have a disaggregated setup, after you generate the StorageCluster spec, you must create two separate node sections in the spec to define the device settings for the storage and storageless (compute) nodes.
 Here is a sample StorageCluster spec that uses node-specific overrides:

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:2.10.1

  storage:

    devices:

      - /dev/sda

      - /dev/sdb

  nodes:

    - selector:

        labelSelector:

          matchLabels:

            portworx.io/node-type: "storage"

      storage:

        devices:

          - /dev/nvme1

          - /dev/nvme2

    - selector:

        labelSelector:

          matchLabels:

            portworx.io/node-type: "storageless"

      storage:

        devices: []

```

In this example, Portworx on the nodes labeled as `portworx.io/node-type=storage` expects two disks, `/dev/nvme1` and `/dev/nvme2`, and it runs them as storage nodes. On the other hand, Portworx on the nodes labeled as `portworx.io/node-type=storageless` ignores any disks that might be found on the node and run as storageless nodes.

## Verify Portworx Pod Status​

Run the following command to list and filter the results for Portworx pods and specify the namespace where you have deployed Portworx:

```

oc get pods -n <px-namespace> -o wide | grep -e portworx -e px

```

```

NAME                                                    READY   STATUS    RESTARTS         AGE     IP              NODE                         NOMINATED NODE   READINESS GATES

portworx-api-8scq2                                      1/1     Running   0                5h1m    xx.xx.xxx.xxx   username-vms-silver-sight-0   <none>           <none>

portworx-api-f24b9                                      1/1     Running   0                5h1m    xx.xx.xxx.xxx   username-vms-silver-sight-3   <none>           <none>

portworx-api-f95z5                                      1/1     Running   0                5h1m    xx.xx.xxx.xxx   username-vms-silver-sight-2   <none>           <none>

portworx-kvdb-558g5                                     1/1     Running   0                3m46s   xx.xx.xxx.xxx   username-vms-silver-sight-2   <none>           <none>

portworx-kvdb-9tfjd                                     1/1     Running   0                2m57s   xx.xx.xxx.xxx   username-vms-silver-sight-0   <none>           <none>

portworx-kvdb-cjcxg                                     1/1     Running   0                3m7s    xx.xx.xxx.xxx   username-vms-silver-sight-3   <none>           <none>

portworx-operator-548b8d4ccc-qgnkc                      1/1     Running   0                5h2m    xx.xx.xxx.xxx   username-vms-silver-sight-0   <none>           <none>

portworx-pvc-controller-ff669698-62ngd                  1/1     Running   0                5h1m    xx.xx.xxx.xxx   username-vms-silver-sight-3   <none>           <none>

portworx-pvc-controller-ff669698-6b4zj                  1/1     Running   0                5h1m    xx.xx.xxx.xxx   username-vms-silver-sight-2   <none>           <none>

portworx-pvc-controller-ff669698-pffvl                  1/1     Running   0                5h1m    xx.xx.xxx.xxx   username-vms-silver-sight-0   <none>           <none>

prometheus-px-prometheus-0                              2/2     Running   0                5h      xx.xx.xxx.xxx   username-vms-silver-sight-0   <none>           <none>

px-cluster-378d7ae1-f4ca-xxxx-xxxx-xxxxxxxxxxxx-2qsp4   2/2     Running   0                3h20m   xx.xx.xxx.xxx   username-vms-silver-sight-3   <none>           <none>

px-cluster-378d7ae1-f4ca-xxxx-xxxx-xxxxxxxxxxxx-5vnzv   2/2     Running   0                3h20m   xx.xx.xxx.xxx   username-vms-silver-sight-0   <none>           <none>

px-cluster-378d7ae1-f4ca-xxxx-xxxx-xxxxxxxxxxxx-lxzd5   2/2     Running   0                3h20m   xx.xx.xxx.xxx   username-vms-silver-sight-2   <none>           <none>

px-csi-ext-77fbdcdcc9-7hkpm                             4/4     Running   0                3h19m   xx.xx.xxx.xxx   username-vms-silver-sight-3   <none>           <none>

px-csi-ext-77fbdcdcc9-9ck26                             4/4     Running   0                3h18m   xx.xx.xxx.xxx   username-vms-silver-sight-0   <none>           <none>

px-csi-ext-77fbdcdcc9-ddmjr                             4/4     Running   0                3h20m   xx.xx.xxx.xxx   username-vms-silver-sight-2   <none>           <none>

px-prometheus-operator-7d884bc8bc-5sv9r                 1/1     Running   0                5h1m    xx.xx.xxx.xxx   username-vms-silver-sight-0   <none>           <none>

```

Note the name of a `px-cluster` pod. You will run `pxctl` commands from these pods in Verify Portworx Cluster Status.

## Verify Portworx Cluster Status​

You can find the status of the Portworx cluster by running `pxctl status` commands from a pod.
Enter the following `oc exec` command, specifying the pod name you retrieved in Verify Portworx Pod Status:

```

oc exec <px-pod-name>  -n <px-namespace> -- /opt/pwx/bin/pxctl status

```

```

Defaulted container "portworx" out of: portworx, csi-node-driver-registrar

Status: PX is operational

Telemetry: Disabled or Unhealthy

Metering: Disabled or Unhealthy

License: Trial (expires in 31 days)

Node ID: 24508311-e2fe-xxxx-xxxx-xxxxxxxxxxxx

    IP: xx.xx.xxx.xxx

    Local Storage Pool: 1 pool

    POOL	IO_PRIORITY	RAID_LEVEL	USABLE	USED	STATUS	ZONE	REGION

    0	HIGH		raid0		25 GiB	33 MiB	Online	default	default

    Local Storage Devices: 1 device

    Device	Path		Media Type		Size		Last-Scan

    0:0	/dev/sda	STORAGE_MEDIUM_SSD	32 GiB		10 Oct 22 23:45 UTC

    total			-			32 GiB

    Cache Devices:

     * No cache devices

    Kvdb Device:

    Device Path	Size

    /dev/sdc	1024 GiB

     * Internal kvdb on this node is using this dedicated kvdb device to store its data.

    Metadata Device:

    1	/dev/sdd	STORAGE_MEDIUM_SSD	64 GiB

Cluster Summary

    Cluster ID: px-cluster-378d7ae1-f4ca-xxxx-xxxx-xxxxxxxxxxxx

    Cluster UUID: 482b18b1-2a8b-xxxx-xxxx-xxxxxxxxxxxx

    Scheduler: kubernetes

    Nodes: 3 node(s) with storage (3 online)

    IP		ID					SchedulerNodeName		Auth		StorageNode		Used	Capacity	Status	StorageStatus	Version		Kernel				OS

    xx.xx.xxx.xxx	24508311-e2fe-xxxx-xxxx-xxxxxxxxxxxx	username-vms-silver-sight-3	Disabled	Yes(PX-StoreV2)	33 MiB	25 GiB		Online	Up (This node)	3.2.0-28944c8	5.4.217-1.el7.elrepo.x86_64	CentOS Linux 7 (Core)

    xx.xx.xxx.xxx	1e89102f-0510-xxxx-xxxx-xxxxxxxxxxxx	username-vms-silver-sight-0	Disabled	Yes(PX-StoreV2)	33 MiB	25 GiB		Online	Up		3.2.0-28944c8	5.4.217-1.el7.elrepo.x86_64	CentOS Linux 7 (Core)

    xx.xx.xxx.xxx	0c99e1f2-9d49-xxxx-xxxx-xxxxxxxxxxxx	username-vms-silver-sight-2	Disabled	Yes(PX-StoreV2)	33 MiB	25 GiB		Online	Up		3.2.0-28944c8	5.4.217-1.el7.elrepo.x86_64	CentOS Linux 7 (Core)

Global Storage Pool

    Total Used    	:  99 MiB

    Total Capacity	:  74 GiB

```

Status displays `PX is operational` when the cluster is running as expected. If the cluster is using the PX-StoreV2 datastore, the `StorageNode` entries for each node displays `Yes(PX-StoreV2)`.

## Verify Portworx Pool Status​

note

This procedure is applicable for clusters with PX-StoreV2 datastore.

Run the following command to view the Portworx drive configurations for your pod:

```

oc exec <px-pod>  -n <px-namespace> -- /opt/pwx/bin/pxctl service pool show

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

oc -n <px-namespace> get storagecluster

```

```

NAME                                              CLUSTER UUID                           STATUS   VERSION          AGE

px-cluster-378d7ae1-f4ca-xxxx-xxxx-xxxxxxxxxxxx   482b18b1-2a8b-xxxx-xxxx-xxxxxxxxxxxx   Online   3.2.0-dev-rc1   5h6m

```

The status must display the cluster is `Online`.

-
Run the following command to find the storage nodes:

```

oc -n <px-namespace> get storagenodes

```

```

NAME                          ID                                     STATUS   VERSION          AGE

username-vms-silver-sight-0   1e89102f-0510-xxxx-xxxx-xxxxxxxxxxxx   Online   3.2.0-28944c8   3h25m

username-vms-silver-sight-2   0c99e1f2-9d49-xxxx-xxxx-xxxxxxxxxxxx   Online   3.2.0-28944c8   3h25m

username-vms-silver-sight-3   24508311-e2fe-xxxx-xxxx-xxxxxxxxxxxx   Online   3.2.0-28944c8   3h25m

```

The status must display the nodes are `Online`.

-
Verify the Portworx cluster provision status by running the following command.
 Specify the pod name you retrieved in Verify Portworx Pod Status.

```

oc exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl cluster provision-status

```

```

NODE					                NODE STATUS	 POOL						              POOL STATUS  IO_PRIORITY	SIZE	AVAILABLE	USED   PROVISIONED ZONE REGION	RACK

0c99e1f2-9d49-xxxx-xxxx-xxxxxxxxxxxx	Up		    0 ( 8ec9e6aa-7726-xxxx-xxxx-xxxxxxxxxxxx )	Online		HIGH		32 GiB	32 GiB		33 MiB	0 B		default	default	default

1e89102f-0510-xxxx-xxxx-xxxxxxxxxxxx	Up		    0 ( 06fcc73a-7e2f-xxxx-xxxx-xxxxxxxxxxxx )	Online		HIGH		32 GiB	32 GiB		33 MiB	0 B		default	default	default

24508311-e2fe-xxxx-xxxx-xxxxxxxxxxxx	Up		    0 ( 58ab2e3f-a22e-xxxx-xxxx-xxxxxxxxxxxx )	Online		HIGH		32 GiB	32 GiB		33 MiB	0 B		default	default	default

```

## What to do next​

Create a PVC. For more information, see Create your first PVC.

In this topic:
