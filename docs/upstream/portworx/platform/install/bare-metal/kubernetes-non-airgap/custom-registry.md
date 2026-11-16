# Installation on a Bare Metal Kubernetes Cluster using Custom Container Registry

Source: https://docs.portworx.com/portworx-enterprise/platform/install/bare-metal/kubernetes-non-airgap/custom-registry (Portworx Enterprise latest)

Installation on a Bare Metal Kubernetes Cluster using Custom Container Registry | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx on a bare metal Kubernetes cluster using a custom container registry.

note

The steps in this document use the air-gapped-install bootstrap script to create a custom registry for internet connected clusters. For information on how to install Portworx on an air-gapped bare metal cluster, see Installation on Air-Gapped Bare Metal Kubernetes Cluster.

Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

The following collection of tasks describe how to install Portworx on a bare metal Kubernetes cluster using Portworx Central:

- Create a version manifest configmap for the Portworx Operator

- Generate Portworx Specification

- Deploy Portworx Operator

- Deploy StorageCluster

- Verify Portworx Pod Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx.

## Create a version manifest configmap for the Portworx Operator​

-
Set an environment variable for your Kubernetes version:

```

KBVER=$(kubectl version --short | awk -F'[v+_-]' '/Server Version: / {print $3}')

```

-
Set an environment variable to specify the latest major version of Portworx:

```

PXVER=<portworx-version>

```

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
(Optional) If your installation uses images from multiple custom registries, update the version manifest with the custom registry location details. You can use a DNS hostname and domain, or IP addresses (IPv4 or IPv6), to specify the container registry server in the following format:

```

<dns-host.domain or IPv4 or IPv6>[:<port>]/repository/image:tag

```

The following example demonstrates registries using a custom DNS hostname + domain, IPv4, and IPv6:

version-config.yaml

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

kubeScheduler: custom-registry.acme.org/k8s/kube-scheduler-amd64:v$KBVER

kubeControllerManager: custom-registry.acme.org/k8s/kube-controller-manager-amd64:v$KBVER

pause: custom-registry.acme.org/k8s/pause:3.1

```

-
Create a configmap from the downloaded or updated version manifest:

```

kubectl -n <px-namespace> create configmap px-versions --from-file=versions.yaml

```

## Generate Portworx Specification​

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

- From the Portworx version dropdown, select the same value that you have set as your Portworx version in the Create a version manifest configmap section.

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
To add another block drive, click the + icon.

- In the Pool Label field, assign a custom label in `key:value` format to identify and categorize storage pools.

- (Optional) To designate PX-StoreV1 as the datastore, clear the PX-StoreV2 checkbox. By default, the system selects PX-StoreV2 as the datastore.

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
In the Registry and Image Settings section, do one of the following:

- If you use a single private registry, enter the internal registry path and the details for how to connect to your private registry in the Custom Container Registry Location field.

- If you use multiple private registries, leave the Custom Container Registry Location field blank.

-
In the Security Settings section, select the Enable Authorization checkbox to enable Role-Based Access Control (RBAC) and secure access to storage resources in your cluster.

-
Click Finish to generate the specs.

-
Log in to the custom container registry using your JFrog credentials.

-
Use the config.json file, and create a registry secret to pull container images from the custom container registry:

```

kubectl create secret generic regcred -n portworx \

--from-file=.dockerconfigjson=/root/.docker/config.json \

--type=kubernetes.io/dockerconfigjson

```

After creating the `regcred` registry secret, add the registry secret in the Kubernetes Docker Registry Secret field.

-
Configure the STC configuration file to pull OCI monitor component images from the custom container registry:

```

env:

- name: REGISTRY_USER

    value: <repository user credentials>

- name: REGISTRY_PASS

    value: <repository token>

spec:

image: registry.portworx.io/portworx/oci-monitor:3.3.0.1

```

Replace `repository user credentials` with the actual username used to authenticate with the registry.

## Deploy Portworx Operator​

Use the Operator specifications you generated in the Generate Portworx Specification section, and deploy Portworx Operator by running the following command.

```

kubectl apply -f 'https://install.portworx.com/<PX-version-number>?comp=pxoperator'

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

kubectl apply -f 'https://install.portworx.com/<PX-version-number>?operator=true&mc=false&kbver=&b=true&c=px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b&stork=true&csi=true&mon=true&tel=false&st=k8s&promop=true'

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b created

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

Note the name of a `px-cluster` pod. You will run `pxctl` commands from these pods in Verify pxctl Cluster Provision Status.

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

Create a PVC. For more information, see Create your first PVC.

In this topic:
