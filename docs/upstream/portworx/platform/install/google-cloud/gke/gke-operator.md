# Installation on Google Kubernetes Engine Cluster using Portworx Central

Source: https://docs.portworx.com/portworx-enterprise/platform/install/google-cloud/gke/gke-operator (Portworx Enterprise latest)

Installation on Google Kubernetes Engine Cluster using Portworx Central | Portworx Enterprise Documentation

This document provides instructions for installing Portworx with Google Kubernetes Engine (GKE) cluster using Portworx Central. Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

The following collection of tasks describes how to install Portworx on a GKE cluster:

- Grant the necessary permissions to Portworx

- Create a custom Google IAM role

- Create a ClusterRoleBinding

- Generate Portworx Enterprise Specification

- Deploy Portworx Operator

- Deploy StorageCluster

- Verify Portworx Pod Status

- Verify Portworx Cluster Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx on Google Kubernetes Engine.

## Grant the necessary permissions to Portworx​

Portworx requires access to the Google Cloud APIs to provision and manage disks. Ensure that the service account for Portworx has the following roles:

- Compute Admin / custom IAM role

- Service Account User

- Kubernetes Engine Cluster Viewer

### Create a custom Google IAM role​

If you prefer Portworx to have minimal access, create a custom IAM role providing the compute permissions. This role allows Portworx to have a set of permissions to create, attach, or manage disks on VM instances.

- Create the following `portworx-role.yaml` file with the following minimum permissions:

```

title: "Portworx role"

description: "Portworx role for managed disks"

stage: "GA"

includedPermissions:

- compute.disks.addResourcePolicies

- compute.disks.create

- compute.disks.createSnapshot

- compute.disks.delete

- compute.disks.get

- compute.disks.getIamPolicy

- compute.disks.list

- compute.disks.removeResourcePolicies

- compute.disks.resize

- compute.disks.setIamPolicy

- compute.disks.setLabels

- compute.disks.update

- compute.disks.use

- compute.disks.useReadOnly

- compute.instances.attachDisk

- compute.instances.detachDisk

- compute.instances.get

- compute.nodeGroups.get

- compute.nodeGroups.getIamPolicy

- compute.nodeGroups.list

- compute.zoneOperations.get

- container.clusters.get

```

- Create your custom role for Portworx using the `portworx-role.yaml` file:

```

gcloud iam roles create portworx_role --project=<your-gcp-project> \

--file=portworx-role.yaml

```

 Once you have created the custom IAM role, you need to assign that role to the GKE cluster nodes that will run Portworx.

### Create a ClusterRoleBinding​

Portworx requires a ClusterRoleBinding for your user to deploy the specs. Create a ClusterRoleBinding using the following `kubectl` command:

```

kubectl create clusterrolebinding myname-cluster-admin-binding \

    --clusterrole=cluster-admin --user=`gcloud info --format='value(config.account)'`

```

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
For Platform, select your K8s Google Cloud as your cloud environment.

-
For Distribution Name, select Google Kubernetes Engine (GKE).

-
In Namespace field enter `portworx` (or the namespace where you will deploy Portworx).

-
(Optional) To customize the configuration options and generate a custom specification, click Customize and perform the following steps:

note

To continue without customizing the default configuration or generating a custom specification, proceed to Step 8.

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

- Enter the Starting port for Portworx services, or leave the default value of `17001`.

- Select Next.

- Deployment tab (advanced settings):

-
Under Kubernetes Distribution section

- Choose Are you running on either of these?

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
For more information, see Enable Pure1 integration for upgrades on GKE cluster.

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- Select the Secrets Store Type from the dropdown menu to store and manage secure information for features such as CloudSnaps and Encryption.

-
In Environment Variables, enter name-value pairs in the respective fields.

- For Disaggregated installation you need to set node labels and `ENABLE_ASG_STORAGE_PARTITIONING` environment variable to `true`. For more information, see Deployment planning.

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

## Deploy Portworx Operator​

Use the Operator specifications you generated in the Generate Portworx Enterprise Specification section, and deploy Portworx Operator by running the following command.

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

## Deploy StorageCluster​

Use the StorageCluster specifications you generated in the Generate Portworx Enterprise Specification section, and deploy StorageCluster by running the following command.

```

kubectl apply -f 'https://install.portworx.com/<version-number>?operator=true&mc=false&kbver=&b=true&c=px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b&stork=true&csi=true&mon=true&tel=false&st=k8s&promop=true'

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b created

```

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

Status displays `PX is operational` when the cluster is running as expected.

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
