# Installation on Air-Gapped Bare Metal Kubernetes Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/bare-metal/kubernetes-airgap (Portworx Enterprise latest)

Installation on Air-Gapped Bare Metal Kubernetes Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx on an air-gapped bare metal Kubernetes cluster. You can deploy Portworx and the required packages using a private container registry.

Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

The following collection of tasks describes how to install Portworx on an air-gapped bare metal Kubernetes cluster:

- Get Portworx Container Images

- Install NFS Packages for Sharedv4

- Generate Portworx Specification

- Deploy Portworx Operator

- Deploy StorageCluster

- Verify Portworx Pod Status

- Verify Portworx Cluster Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx.

## Get Portworx container images​

note

The bootstrap script pulls images that match the CPU architecture of the host machine running it. Run the script on a host that has the same architecture as your destination cluster nodes. For example, if you run the script on an Apple Silicon Mac (arm64) and your destination cluster nodes are x86_64 (amd64), the script will pull arm64 images that are incompatible with your cluster.

-
Set an environment variable for your Kubernetes version:

```

KBVER=$(kubectl version | awk -F'[v+_-]' '/Server/ {print $3}')

```

-
Set an environment variable to specify the latest major version of Portworx:

```

PXVER=<portworx-version>

```

-
Run the following command to download a list of the released images:

```

curl -o images "https://install.portworx.com/$PXVER/images?kbver=$KBVER"

```

-
On an internet-connected host that matches the architecture and OS version of the Kubernetes cluster nodes intended for Portworx installation, download the air-gapped installation bootstrap script for the Kubernetes and Portworx versions:

```

curl -o px-ag-install.sh -L "https://install.portworx.com/$PXVER/air-gapped?kbver=$KBVER"

```

-
Pull the container images for the Kubernetes and Portworx versions:

```

sh px-ag-install.sh pull

```

-
Log in to Docker:

```

docker login <your-private-registry>

```

-
Push the container images to a private registry that is accessible to your air-gapped nodes. Do not include `http://` in your private registry path:

```

sh px-ag-install.sh push <your-registry-path>

```

For example:

```

sh px-ag-install.sh push myregistry.net:5443

```

Example for pushing image to a specific repo:

```

sh px-ag-install.sh push myregistry.net:5443/px-images

```

### Create a version manifest ConfigMap for the Portworx Operator​

-
Download the Portworx version manifest:

```

curl -o versions.yaml "https://install.portworx.com/$PXVER/version?kbver=$KBVER&opver=<operator-version>"

```

Replace `<operator-version>` with the Operator version you want to use.

-
(Optional) If your installation uses images from multiple custom registries, update the version manifest with the custom registry location details. You can use a DNS hostname and domain, or IP addresses (IPv4 or IPv6), to specify the container registry server in the following format:

```

<dns-host.domain or IPv4 or IPv6>[:<port>]/repository/image:tag

```

The following example demonstrates registries using a custom DNS hostname + domain, IPv4, and IPv6:

```

version: 2.13.3

components:

  stork: custom-registry.acme.org/portworx/backup/stork:23.2.1

  autopilot: 192.168.1.2:5433/tools/autopilot:1.3.7

  nodeWiper: [2001:db8:3333:4444:5555:6666:7777:8888]:5443/portworx/px-node-wiper:2.13.2

```

note

-
Ensure that the Custom Container Registry location field is empty for any specs you generate in the spec generator.

-
`kubeScheduler`, `kubeControllerManager`, and `pause` may not appear in the version manifest, but you can include them in the `px-version` configmap:

```

...

kubeScheduler: custom-registry.acme.org/k8s/kube-scheduler-amd64:v1.26.4

kubeControllerManager: custom-registry.acme.org/k8s/kube-controller-manager-amd64:v1.26.4

pause: custom-registry.acme.org/k8s/pause:3.1

```

-
Create a configmap from the downloaded or updated version manifest in the namespace `<px-namespace>`, where you deploy Portworx:

```

kubectl -n <px-namespace> create configmap px-versions --from-file=versions.yaml

```

## Install NFS packages for Sharedv4​

To install the NFS package on your host systems so that Portworx can use the sharedv4 feature, follow these steps:

-
Start the repository container as a standalone service in Docker by running the following command:

```

docker run -p 8080:8080 docker.io/portworx/px-repo:1.2.0

```

-
Using a browser within your air-gapped environment, navigate to your host IP address where the above docker image is running (For example, `http://<ip-address>:8080`), and follow the instructions for your Linux distribution provided by the container to configure your host to use the package repository service, and install the NFS packages.

## Generate Portworx specification​

To install Portworx, you must first generate Kubernetes manifests that you will deploy in your bare metal Kubernetes cluster by following these steps.

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
From the Distribution Name dropdown menu, select None.

important

The deployment process for Kubernetes distributions such as Google Anthos, Rancher Kubernetes Engine (RKE2), or VMware Tanzu Kubernetes Grid Integrated Edition (TKGI) is identical to deploying Portworx on a vSphere Kubernetes cluster. However, you must select Anthos, Rancher Kubernetes Engine (RKE2), or VMware Tanzu Kubernetes Grid Integrated Edition (TKGI) from the Distribution Name dropdown, based on your Kubernetes environment and deployment requirements. This ensures that the deployment manifest is correctly tailored for Anthos, RKE2, or TKGI.

-
Click Customize.

-
On the Basic tab:

- From the Portworx version dropdown, select the Portworx version to install.

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

-
On the Storage tab:

- To enable Portworx to use all available, unused, and unmounted drives on the node, do the following:

- Select the Automatically scan disks option.

- From the Default IO Profile dropdown menu, select Auto.
 This enables Portworx to automatically choose the best I/O profile based on detected workload patterns.

- Select the Use unmounted disks even if they have a partition or filesystem on it. Portworx will never use a drive or partition that is mounted checkbox to use unmounted disks, even if they contain a partition or filesystem.
Portworx will not use any mounted drive or partition.

- To manually specify the drives on the node for Portworx to use, do the following:

- Select the Manually specify disks option.

- In the Drive/Device field, specify the block drive(s) that Portworx uses for data storage.

- In the Pool Label field, assign a custom label in `key:value` format to identify and categorize storage pools.

- (Optional) To designate PX-StoreV1 as the datastore, clear the PX-StoreV2 checkbox.
By default, the system selects PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
The path must be at least 64 GB in size.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
Enter the path of the journal device in the Journal Device Path field.

- Skip KVDB device - This checkbox is selected by default and appears only if you choose the Built-in option in the Basic tab.
Keep it selected to use the same device for KVDB and storage I/O. This configuration is suitable for test or development clusters but not recommended for production clusters. For production clusters, clear the checkbox and provide a separate device to store internal KVDB data. This separates KVDB I/O from storage I/O and improves performance.

- KVDB device - Enter the block device path to be used exclusively for KVDB data.
This field appears only if you clear the Skip KVDB device checkbox. The KVDB device must be present on at least three nodes in the cluster to ensure high availability.

note

To restrict Portworx to run internal KVDB only on specific nodes, label those nodes with:

```

kubectl label nodes node1 node2 node3 px/metadata-node=true

```

- Click Next.

-
On the Network tab:

- In the Interface(s) section, do the following:

- Enter the Data Network Interface to be used for data traffic.

- Enter the Management Network Interface to be used for management traffic.

- In the Advanced Settings section, do the following:

- Enter the Starting port for Portworx services.

- Click Next.

-
On the Deployment tab:

-
In the Kubernetes Distribution section, under Are you running on either of these?, select None.

-
In the Component Settings section:

- Select the Enable Stork checkbox to enable Stork.

- (Optional) Select the Remote Fastpath (NVMe-oF/TCP) checkbox to enable Remote Fastpath. For more information, see Remote Fastpath.

- Select the Restrict Data Protection RBAC to restrict RBAC permissions for Stork (if enabled) and Operator. You will not be able to use Backup and DR capabilities with this restriction. For more information, see Restrict Data Protection RBAC.

- Select the Enable Monitoring checkbox to enable monitoring of Portworx components and resources.

- To configure the monitoring stack, select one of the following:

- Portworx Managed - To enable Portworx to install and manage Prometheus and Operator automatically.
 Ensure that no other Prometheus Operator instance is already running on the cluster.

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
In the Registry and Image Settings section, do one of the following:

- If you use a single private registry, enter the internal registry path and the details for how to connect to your private registry in the Custom Container Registry Location field.

- If you use multiple private registries, leave the Custom Container Registry Location field blank.

-
In the Security Settings section, select the Enable Authorization checkbox to enable Role-Based Access Control (RBAC) and secure access to storage resources in your cluster.

-
Click Finish to generate the specs.

## Deploy Portworx Operator​

Use the Operator specifications you generated in the Generate Portworx Specification section, and deploy Portworx Operator by running the following command.

```

kubectl apply -f 'https://install.portworx.com/<PXVER>?comp=pxoperator'

```

```

serviceaccount/portworx-operator created

podsecuritypolicy.policy/px-operator created

clusterrole.rbac.authorization.k8s.io/portworx-operator created

clusterrolebinding.rbac.authorization.k8s.io/portworx-operator created

deployment.apps/portworx-operator created

```

## Deploy StorageCluster​

Use the StorageCluster specifications you generated in the Generate Portworx Specification section, and deploy StorageCluster by running the following command.

```

kubectl apply -f 'https://install.portworx.com/<PXVER>?operator=true&mc=false&kbver=&b=true&c=px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b&stork=true&csi=true&mon=true&tel=false&st=k8s&promop=true'

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b created

```

## Verify Portworx Pod status​

Enter the following command to list and filter the results for Portworx pods and specify the namespace where you have deployed Portworx:

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

Note the name of a `px-cluster` pod. You can run `pxctl` commands from these pods in Verify pxctl Cluster Provision Status.

## Verify Portworx Cluster status​

You can find the status of the Portworx cluster by running `pxctl status` commands from a pod.
Enter the following `kubectl exec` command, specifying the pod name you retrieved in Verify Portworx Pod status:

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

Status displays `PX is operational` when the cluster is running as expected. If the cluster is using the PX-StoreV2 datastore, the `StorageNode` entries for each node display `Yes(PX-StoreV2)`.

## Verify pxctl Cluster provision status​

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

The status must show the cluster is `Online`.

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

The status must show the nodes are `Online`.

-
Verify the Portworx cluster provision status by running the following command.
 Specify the pod name you retrieved in Verify Portworx Pod status.

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

Create a PVC. For more information, see Create your first PVC.

In this topic:
