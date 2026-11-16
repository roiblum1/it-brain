# Installation on Anthos Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/google-cloud/anthos (Portworx Enterprise latest)

Installation on Anthos Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx on an Anthos cluster. Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

- Generate Portworx Enterprise Specification

- Deploy Portworx Operator and StorageCluster

- Verify Portworx Pod Status

- Verify Portworx Cluster Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx on Google Anthos Cluster.

## Generate Portworx Enterprise Specification​

-
Sign in to the Portworx Central console.
 The system displays the Welcome to Portworx Central! page.

-
In the Portworx Enterprise section, select Generate Cluster Spec.
 The system displays the Generate Spec page.

-
From the Portworx Version dropdown menu, select the Portworx version to install.

-
For Platform, select your Google Cloud as your cloud environment.

-
From the Distribution Name dropdown menu, select Anthos as your distribution.

-
In the Cluster Selector Label field, enter the suitable label for a cluster. This helps you specify configurations or software installations that should only be applied to clusters matching the label criteria. For example, when installing Portworx on an Anthos cluster, you might want to target only those clusters designated for storage-intensive applications. For instance, label your target cluster with a specific selector:

```

metadata:

labels:

  configmanagement.gke.io/cluster-selector: storage-intensive

```

This ensures that Portworx is only installed on clusters designated for storage-heavy workloads, optimizing resource usage and deployment strategies across your Anthos environment.

-
In the Namespace field, enter `portworx` (or the namespace where you will deploy Portworx).

-
(Optional) To customize the configuration options and generate a custom specification, click Customize and perform the following steps:

note

To continue without customizing the default configuration or generating a custom specification, proceed to Step 9.

- Basic tab:

- To use an existing etcd cluster, do the following:

- Select the Your etcd details option.

- In the field provided, enter the host name or IP and port number.
 For example, `http://test.com.net:1234`.

- Select one of the following authentication methods:

- Disable HTTPS – To use HTTP for etcd communication.

- Certificate Auth – To use HTTPS with an SSL certificate.
For more information, see Secure your etcd communication.

- Password Auth – To use HTTPS with username and password authentication.

- To use an internal Portworx-managed key-value store (kvdb), do the following:

- Select the Built-in option.

note

To restrict Portworx to run internal KVDB only on specific nodes, label those nodes with:

```

kubectl label nodes node1 node2 node3 px/metadata-node=true

```

- TLS for internal KVDB is enabled, by default. If Cert-Manager is already running in your Kubernetes cluster, deselect the Deploy Cert-Manager for TLS certificates option to avoid installation failures.

- Select Next.

- Storage tab (storage configuration):

- Select one of the following:

- Create Using a Spec – Select this option to create a spec that Portworx will use to create GCP disks.

- Select PX-Store Version - (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- Add the following details for spec block:

- Select Volume Type – Select the type of disk to be created from the dropdown menu.

- Size (GB) – Enter the size of the disk to be created.

- Encryption – Select one of the following encryption options from the dropdown menu:

- None – Do not encrypt the disks.

- BYOK Encryption – Use your own encryption key to encrypt the disks.

- If you select this option, enter the Encryption Key in the respective field, which will be used for BYOK encryption.

- If you select Separate KMS Account checkbox, you must provide a name KMS Account field.

 Follow instructions in Create a Disk Encryption Key and Create and Configure a KMS Service Account, then return to this installation guide.

- Drive Tags – Enter multiple tags as key-value pairs to be applied to the disks created by Portworx.

- Add/Delete spec entered using the Delete icon and + icon respectively, at the end of the spec line.

- Initial Storage Nodes (Optional): Enter the number of storage nodes that need to be created across zones and node pools.

 Details

See more about initial storage nodes Anthos cluster management operations, such as upgrades, recycle cluster nodes by deleting and recreating them. During this process, the cluster momentarily scales up to more nodes than initially installed. For example, a 3-node cluster may increase to a 4-node cluster. To prevent Portworx from creating storage on these additional nodes, you must cap the number of Portworx nodes that will act as storage nodes. You can set this value in the Initial Storage Nodes field according to the following requirements:

- If your Anthos cluster does not have zones configured, this number should be your initial number of cluster nodes,

- If your Anthos cluster has zones configured, this number should be an initial number of cluster nodes per zone.

- Under Default IO Profile, select one of the following:

- Auto – Automatically select the IO profile based on the underlying storage media.

- None

- Under Journal Device, select one of the following:

- None – Use the default journaling setting.

- Auto – Dynamically allocates journal device.

- Custom – Manually specify a journal device.

- Select Volume Type – Select the type of disk to be created from the dropdown menu.

- Encryption – Select one of the following encryption options from the dropdown menu:

- None – Do not encrypt the disks.

- BYOK Encryption – Use your own encryption key to encrypt the disks.

- If you select this option, enter the Encryption Key in the respective field, which will be used for BYOK encryption.

- If you select Separate KMS Account checkbox, you must provide a name KMS Account field.

 Follow instructions in Create a Disk Encryption Key and Create and Configure a KMS Service Account, then return to this installation guide.

- Drive Tags – Enter multiple tags as key-value pairs to be applied to the disks created by Portworx.

- Consume Unused – To enable Portworx to use all available, unused, and unmounted drives on the node

- (Optional) To designate PX-StoreV1 as the datastore, clear the PX-StoreV2 checkbox. By default, the system selects PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
The path must be at least 64 GB in size.

- Under Journal Device, select one of the following:

- None – Use the default journaling setting.

- Auto – Automatically allocate journal devices.

- Custom – Manually enter a journal device path.
Enter the path of the journal device in the Journal Device Path field.

- Select the Use unmounted disks even if they have a partition or filesystem on it. Portworx will never use a drive or partition that is mounted checkbox to use unmounted disks, even if they contain a partition or filesystem.
Portworx will not use any mounted drive or partition.

- Use Existing Disks - Select this option to provide a list of existing drives on the node for Portworx to use. To manually specify the drives on the node for Portworx to use, and in the Drive/Device field, enter the path of the block drive.

- Use Pool Label field given in each Drive/Device row to control the placement of volumes. For more information refer to How to assign custom labels to device pools. Pool label must follow key:value format. Keys and values must not be empty, contain colons (:) or whitespace. Reserved keys "medium" and "iopriority" are not allowed. Only one label per device is supported during installation.

- (Optional) To designate PX-StoreV1 as the datastore, clear the PX-StoreV2 checkbox. By default, the system selects PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
The path must be at least 64 GB in size.

- Under Journal Device, select one of the following:

- None – Use the default journaling setting.

- Auto – Automatically allocate journal devices.

- Custom – Manually enter a journal device path.
Enter the path of the journal device in the Journal Device Path field.

- Select Next.

- Network tab (network settings):

- Enter the Data Network Interface to be used for data traffic, or leave the default value of `auto`.

- Enter the Management Network Interface to be used for management traffic, or leave the default value of `auto`.

- Enter the Starting port for Portworx services, or leave the default value of `9001`.

- Select Next.

- Deployment tab (advanced settings):

-
Under Kubernetes Distribution section

- Choose Are you running on either of these?

- Define the Cluster Selector Label to target specific clusters for Portworx installation.

-
Under Component Settings section

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
 This should not be enabled for air-gapped environments.

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- Select the Secrets Store Type from the dropdown menu to store and manage secure information for features such as CloudSnaps and Encryption.

-
In Environment Variables, enter name-value pairs in the respective fields.

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
Click Download to download the zip file containing the customized specifications files or Save Spec to save the specification.

-
Click Save & Download to generate zip file containing specification YAMLs files.

-
Extract the .zip file you download in previous step 10, as shown below. Replace the zip file name with your downloaded .zip file name:

```

unzip <portworx-anthos-label-2025-09-19-11-07-32.zip>

```

```

px-operator-portworx-label-2025-09-19-11-07-32.yaml

storage-cluster-portworx-label-2025-09-19-11-07-32.yaml

```

You will get the `px-operator` and `storage-cluster` YAML files.

## Deploy Portworx Operator and StorageCluster​

Deploy the Portworx Operator and StorageCluster specs YAML files downloaded in the previous section:

-
Run the following command to deploy the Portworx Operator. Replace the Portworx Enterprise Operator file name with your downloaded file name:

```

kubectl create -f <px-operator-namespace-label-2025-09-19-11-07-32.yaml>

```

```

serviceaccount/portworx-operator created

clusterrole.rbac.authorization.k8s.io/portworx-operator created

clusterrolebinding.rbac.authorization.k8s.io/portworx-operator created

deployment.apps/portworx-operator created

```

-
(Optional) If you have a disaggregated setup, after you generate the StorageCluster spec in the Generate Portworx Enterprise Specification section, add the following environment variable in the env section:

```

spec:

env:

- name: ENABLE_ASG_STORAGE_PARTITIONING

value: "true"

```

You can also add the environment variables from the spec generator using the Environment Variables dropdown menu.
 After you add the variable, Portworx runs nodes labeled `portworx.io/node-type=storage` as storage nodes and nodes labeled `portworx.io/node-type=storageless` as storageless nodes.

-
Run the following command to deploy the StorageCluster. Replace the Portworx Enterprise StorageCluster file name with your downloaded file name:

```

kubectl create -f <storage-cluster-namespace-label-2025-09-19-11-07-32.yaml >

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-f50775cb041b created

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

- For Portworx Enterprise, the default license activated on the cluster is a 30-day trial that you can convert to a SaaS-based model or a generic fixed license.

## Verify Portworx Pod Status​

Run the following command to list and filter the results for Portworx pods and specify the namespace where you have deployed Portworx:

```

kubectl get pods -n <px-namespace> -o wide | grep -e portworx -e px

```

```

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

Note the name of a `px-cluster` pod. You will run `pxctl` commands from these pods in Verify Portworx Cluster Status.

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

kubectl exec <pod-name> -n <px-namespace> -- /opt/pwx/bin/pxctl cluster provision-status

```

```

Defaulted container "portworx" out of: portworx, csi-node-driver-registrar

NODE                                    NODE STATUS     POOL                                            POOL STATUS     IO_PRIORITY     SIZE    AVAILABLE  USED     PROVISIONED     ZONE    REGION  RACK

xxxxxxxx-xxxx-xxxx-xxxx-70c31d0f478e    Up              0 ( xxxxxxxx-xxxx-xxxx-xxxx-4d74ecc7e159 )      Online          HIGH            3.0 TiB 3.0 TiB    10 GiB   0 B             default default default

xxxxxxxx-xxxx-xxxx-xxxx-fad8c65b8edc    Up              0 ( xxxxxxxx-xxxx-xxxx-xxxx-97e4359e57c0 )      Online          HIGH            3.0 TiB 3.0 TiB    10 GiB   0 B             default default default

xxxxxxxx-xxxx-xxxx-xxxx-19d45b4c541a    Up              0 ( xxxxxxxx-xxxx-xxxx-xxxx-8904cab0e019 )      Online          HIGH            3.0 TiB 3.0 TiB    10 GiB   0 B             default default default

```

## What to do next​

Create a PVC. For more information, see Create your first PVC.

In this topic:
