# Installation on OpenShift Two-Node with Arbiter Bare Metal Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/bare-metal/openshift-two-node-arbiter (Portworx Enterprise latest)

Installation on OpenShift Two-Node with Arbiter Bare Metal Cluster | Portworx Enterprise Documentation

A Portworx cluster on a Red Hat OpenShift two-node with arbiter (TNA) cluster is a compact, cost-effective topology designed for edge environments. The cluster consists of two control plane nodes and one arbiter node. The arbiter node stores the Portworx KVDB data, maintaining quorum and preventing split-brain. The arbiter node does not store application data or run workloads.

note

If your deployment requires more than three nodes, configure it as a regular Portworx cluster rather than a TNA cluster.

The following tasks describe how to install Portworx on a TNA cluster:

Complete all the tasks to install Portworx.

## Prerequisites​

Before installing Portworx on a TNA cluster, ensure you meet the following requirements:

- Portworx version: 3.5.2 or later

- Portworx Operator version: 25.6.0 or later

- OpenShift version: 4.20.11 or later

- PX-Store version: Only PX-StoreV2 is supported for TNA clusters.

- Control plane nodes: Ensure that your control plane nodes meet all the System Requirements

- Arbiter node: The arbiter node must meet the generic System Requirements with the following TNA-specific overrides:

CategoryTNA-Specific Requirement

CPU Cores (Physical)4 cores

Network Latency200ms maximum

## Create a monitoring ConfigMap​

Enable monitoring for user-defined projects before installing the Portworx Operator. Use the instructions in this section to configure the OpenShift Prometheus deployment to monitor Portworx metrics.

To integrate OpenShift's monitoring and alerting system with Portworx, create a `cluster-monitoring-config` ConfigMap in the `openshift-monitoring` namespace:

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

The `enableUserWorkload` parameter enables monitoring for user-defined projects in the OpenShift cluster. This creates a prometheus-operated service in the openshift-user-workload-monitoring namespace.

## Generate Portworx Enterprise Specification​

To install Portworx, you must first generate Kubernetes manifests that you will deploy in your bare metal OpenShift cluster by following these steps.

important

When generating the specification for TNA, you must select PX-StoreV2 in the Storage tab. TNA is not supported with PX-StoreV1.

-
Sign in to the Portworx Central console.
 The system displays the Welcome to Portworx Central! page.

-
In the Portworx Enterprise section, select Generate Cluster Spec.
 The system displays the Generate Spec page.

-
From the Portworx Version dropdown menu, select the Portworx version to install.

-
From the Platform dropdown menu, select DAS/SAN.

-
From the Distribution Name dropdown menu, select OpenShift 4+.

-
To customize the configuration options, click Customize and perform the following steps:

- Basic tab:

-
To use an existing etcd cluster, do the following:

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

-
To use an internal Portworx-managed key-value store (kvdb), do the following:

- Select the Built-in option.

- TLS for internal KVDB is enabled by default. If Cert-Manager is already running in your Kubernetes cluster, deselect the Deploy Cert-Manager for TLS certificates option to avoid installation failures.

-
Click Next.

- Storage tab:

- To enable Portworx to use all available, unused, and unmounted drives on the node, do the following:

- Select the Automatically scan disks option.

- From the Default IO Profile dropdown menu, select Auto.
 This enables Portworx to automatically choose the best I/O profile based on detected workload patterns.

- Ensure that PX-Store V2 is selected in the Select PX-Store Version list because the TNA setup is supported only with PX-Store V2.

- Turn on the toggle: Enable Two Node Arbiter (TNA) Setup.

- For master nodes 1 and 2, enter the following details:

- Node Name: Node name from `oc get nodes` output.

- System Metadata Device: Enter the path of the system metadata device (for example, `/dev/sdb`).

- (Optional) Cluster Domain: Enter the cluster domain name.

- For the arbiter node, enter the following details:

- Node Name: Node name from `oc get nodes` output.

- KVDB Device: Enter the path of the KVDB device (for example, `/dev/sdb`).

- Cluster Domain: The cluster domain name must be `witness`. This value is set by default.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path (applicable only for master nodes).
Enter the path of the journal device in the Journal Device Path field.

- Click Next.

- Network tab:

- In the Interface(s) section, do the following:

- Enter the Data Network Interface to be used for data traffic.

- Enter the Management Network Interface to be used for management traffic.

- In the Advanced Settings section, do the following:

- Enter the Starting port for Portworx services.

- Click Next.

- Deployment tab:

-
In the Kubernetes Distribution section, select OpenShift 4+.

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
For more information, see Enable Pure1 integration for upgrades on bare metal.

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- Select the Secrets Store Type from the dropdown menu to store and manage secure information for features such as CloudSnaps and Encryption.

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

-
Click Save & Download to generate the specification.

The generated StorageCluster resource for a TNA cluster automatically includes:

- `spec.nodes`: entries for the two master nodes and the arbiter node, mapping each node to its `systemMetadataDevice` or `kvdbDevice` and `clusterDomain`.

- `spec.nodes.storage.useAll`: set to `true` for the master nodes.

- `annotations.portworx.io/misc-args`: a misc arg set to `-rt_opts small_conf=1 -T px-storev2`.

note

To use unmounted drives even if they have a partition or file system, configure this by using the `spec.nodes.storage.useAllWithPartitions` field in the master node configuration.

Example:

StorageCluster

```

    - selector:

        nodeName: "master-node1"

      storage:

        systemMetadataDevice: /dev/sda1

        useAllWithPartitions: true

```

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

## Deploying Portworx using OpenShift Console​

-
Click Create StorageCluster.
The system displays the Create StorageCluster page.

-
Select YAML view.

-
Copy and paste the specification that you generated in Generate Portworx Enterprise Specification section into the text editor.

-
Click Create.
 The system deploys Portworx, and displays the Portworx instance in the Storage Cluster tab of the Installed Operators page.

## Verify Portworx Pod Status​

Run the following command to list and filter the results for Portworx pods and specify the namespace where you have deployed Portworx:

```

oc get pods -n <px-namespace> -o wide | grep -e portworx -e px

```

```

cert-manager-bfcb97f5d-fpxjp                            1/1     Running   1 (59m ago)    83m   10.X.X.X        master-node-1   <none>           <none>

portworx-api-7bk95                                      2/2     Running   8 (59m ago)    83m   10.X.X.X        master-node-1   <none>           <none>

portworx-api-j5pdx                                      2/2     Running   10 (71m ago)   83m   10.X.X.X        master-node-2   <none>           <none>

portworx-api-mpzwc                                      2/2     Running   7 (81m ago)    83m   10.X.X.X        arbiter-node    <none>           <none>

portworx-kvdb-6zq27                                     1/1     Running   0              74m   10.X.X.X        master-node-1   <none>           <none>

portworx-kvdb-hbnb4                                     1/1     Running   0              73m   10.X.X.X        master-node-2   <none>           <none>

portworx-kvdb-qhfxz                                     1/1     Running   0              75m   10.X.X.X        arbiter-node    <none>           <none>

portworx-operator-847745484c-8crmr                      1/1     Running   5 (73m ago)    90m   10.X.X.X        master-node-1   <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-972a4b8978ab-94d4k   1/1     Running   0              83m   10.X.X.X        master-node-2   <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-972a4b8978ab-frgkg   1/1     Running   1 (59m ago)    83m   10.X.X.X        master-node-1   <none>           <none>

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-972a4b8978ab-jh6q5   1/1     Running   0              83m   10.X.X.X        arbiter-node    <none>           <none>

px-csi-ext-5fb89dfd95-9k5wb                             4/4     Running   3 (59m ago)    71m   10.X.X.X        master-node-1   <none>           <none>

px-csi-ext-5fb89dfd95-nrrf7                             4/4     Running   1 (59m ago)    72m   10.X.X.X        master-node-1   <none>           <none>

px-telemetry-metrics-collector-67cc96cf6d-tp5vn         2/2     Running   0              71m   10.X.X.X        master-node-2   <none>           <none>

px-telemetry-phonehome-pgf5k                            2/2     Running   0              71m   10.X.X.X        master-node-2   <none>           <none>

px-telemetry-phonehome-wtn8w                            2/2     Running   0              71m   10.X.X.X        master-node-1   <none>           <none>

px-telemetry-registration-6ffcc7794b-sfb7s              2/2     Running   0              71m   10.X.X.X        master-node-2   <none>           <none>

```

note

In a TNA deployment, you will see different pods running on different nodes:

- Control-plane nodes (2 nodes): Run the full set of Portworx pods including `portworx-api`, `px-cluster`, `portworx-kvdb`, `stork`, and other Portworx components.

- Arbiter node (1 node): Runs only three Portworx pods: `portworx-api`, `px-cluster`, and `portworx-kvdb`. The arbiter node does not run storage-related pods since it is a storageless node.

Note the name of a `px-cluster` pod. You will run `pxctl` commands from these pods in Verify Portworx Cluster Status.

## Verify Portworx Cluster Status​

You can find the status of the Portworx cluster by running `pxctl status` commands from a pod.
Enter the following `oc exec` command, specifying the pod name you retrieved in Verify Portworx Pod Status:

```

oc exec <px-pod-name>  -n <px-namespace> -- /opt/pwx/bin/pxctl status

```

```

Status: PX is operational

Telemetry: Healthy

Metering: Disabled or Unhealthy

License: Trial (expires in 31 days)

Node ID: xxxxxxxx-xxxx-xxxx-xxxx-065b52c92f87

	IP: 10.X.X.X

 	Local Storage Pool: 1 pool

	POOL	IO_PRIORITY	RAID_LEVEL	USABLE	USED	STATUS	ZONE	REGION

	0	HIGH		raid0		111 GiB	34 MiB	Online	default	default

	Local Storage Devices: 1 device

	Device	Path		Media Type		Size		Last-Scan

	0:0	/dev/sdc	STORAGE_MEDIUM_SSD	128 GiB		16 Feb 26 09:11 UTC

	total			-			128 GiB

	Cache Devices:

	 * No cache devices

	Metadata Device:

	1	/dev/sdb	STORAGE_MEDIUM_SSD	64 GiB

	* Internal kvdb on this node is using this dedicated metadata device to store its data.

Cluster Summary

	Cluster ID: px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-972a4b8978ab

	Cluster UUID: xxxxxxxx-xxxx-xxxx-xxxx-1c4d08c9d709

	Scheduler: kubernetes

	Total Nodes: 3 node(s) with storage (3 online)

	IP		ID					SchedulerNodeName	Auth		StorageNode	Used	Capacity	Status	StorageStatus	Version		Kernel				OS

	10.X.X.X	xxxxxxxx-xxxx-xxxx-xxxx-065b52c92f87	master-node-2		Disabled	Yes(PX-StoreV2)	34 MiB	111 GiB		Online	Up (This node)	3.X.X		5.14.0-570.78.1.el9_6.x86_64	Red Hat Enterprise Linux CoreOS 9.6.20260112-0 (Plow)

	10.X.X.X	xxxxxxxx-xxxx-xxxx-xxxx-d5cfe8192510	master-node-1		Disabled	Yes(PX-StoreV2)	34 MiB	111 GiB		Online	Up		3.X.X		5.14.0-570.78.1.el9_6.x86_64	Red Hat Enterprise Linux CoreOS 9.6.20260112-0 (Plow)

	10.X.X.X	xxxxxxxx-xxxx-xxxx-xxxx-055e42c84c8b	arbiter-node		Disabled	Yes(PX-StoreV2)	0 B	0 B		Online	No Storage	3.X.X		5.14.0-570.78.1.el9_6.x86_64	Red Hat Enterprise Linux CoreOS 9.6.20260112-0 (Plow)

Global Storage Pool

	Total Used    	:  68 MiB

	Total Capacity	:  222 GiB

```

For TNA clusters, verify the following in the output:

- Status displays `PX is operational` when the cluster is running as expected.

- Total Nodes: Shows 2 nodes with storage and 1 node without storage.

- The arbiter node displays No Storage with a KVDB device only.

- Global storage pool capacity is reported correctly from the two control-plane nodes.

## Verify Portworx Pool Status​

note

This procedure is applicable for clusters with PX-StoreV2 datastore.

Run the following command to view the Portworx drive configurations for your pod:

```

oc exec <px-pod>  -n <px-namespace> -- /opt/pwx/bin/pxctl service pool show

```

```

PX drive configuration:

Pool ID: 0

	Type:  PX-StoreV2

	UUID:  xxxxxxxx-xxxx-xxxx-xxxx-15dc838a383b

	IO Priority:  HIGH

	Labels:  beta.kubernetes.io/arch=amd64,node-role.kubernetes.io/master,iopriority=HIGH,node.openshift.io/os_id=rhel,beta.kubernetes.io/os=linux,node-role.kubernetes.io/worker,node-role.kubernetes.io/control-plane,kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=master-node-2,medium=STORAGE_MEDIUM_SSD

	Size: 111 GiB

	MaxPoolSize: 15 TiB

	Status: Online

	Has metadata:  No

	Drives:

	0: /dev/sdc, Total size 128 GiB, Online

	Cache Drives:

	No Cache drives found in this pool

Metadata  Device:

	1: /dev/sdb, STORAGE_MEDIUM_SSD

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

NAME                    ID                                     STATUS   VERSION           AGE

master-node-1           xxxxxxxx-xxxx-xxxx-xxxx-d5cfe8192510   Online   3.X.X-xxxxxxxx    20h

master-node-2           xxxxxxxx-xxxx-xxxx-xxxx-065b52c92f87   Online   3.X.X-xxxxxxxx    20h

arbiter-node            xxxxxxxx-xxxx-xxxx-xxxx-055e42c84c8b   Online   3.X.X-xxxxxxxx    20h

```

The status must display the nodes are `Online`.

-
Verify the Portworx cluster provision status by running the following command.
 Specify the pod name you retrieved in Verify Portworx Pod Status.

```

oc exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl cluster provision-status

```

```

NODE ID					IP		HOSTNAME		NODE STATUS	POOL						POOL STATUS	IO_PRIORITY	SIZE	AVAILABLE	USED	PROVISIONED	ZONE	REGION	RACK

xxxxxxxx-xxxx-xxxx-xxxx-d5cfe8192510	10.X.X.X	master-node-1		Up		0 ( xxxxxxxx-xxxx-xxxx-xxxx-808948089ed8 )	Online		HIGH		128 GiB	128 GiB		34 MiB	0 B		default	default	default

xxxxxxxx-xxxx-xxxx-xxxx-065b52c92f87	10.X.X.X	master-node-2		Up		0 ( xxxxxxxx-xxxx-xxxx-xxxx-15dc838a383b )	Online		HIGH		128 GiB	128 GiB		34 MiB	0 B		default	default	default

```

## What to do next​

Create a PVC. For more information, see Create your first PVC.

In this topic:
