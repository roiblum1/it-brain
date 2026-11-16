# Installation on Google Cloud Openshift Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/google-cloud/install-on-ocp-gcp (Portworx Enterprise latest)

Installation on Google Cloud Openshift Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx on an OpenShift cluster running on Google Cloud Platform (GCP). Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

The following collection of tasks describe how to install Portworx on an OpenShift GCP cluster:

- Grant the necessary permissions to Portworx

- Create a custom Google IAM role

- Create a Service Account

- Create a secret

- Create a monitoring ConfigMap

- Generate Portworx Enterprise Specification

- Install Portworx Operator using OpenShift Console

- Deploying Portworx using OpenShift Console

- Verify Portworx Pod Status

- Verify Portworx Cluster Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx on OpenShift GCP.

## Grant the necessary permissions to Portworx​

Create the following default roles for Portworx to manage GCP disks:

- Compute Admin / custom IAM role

- Service Account User

### Create a custom Google IAM role​

If you prefer that Portworx has minimal access required, then create a custom IAM role providing the compute permissions. This role allows Portworx to have set of permissions to create, attach, or manage disks on VM instances.

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

 Once you have created the custom IAM role, you need to bind it with a service account using which you can manage GCP disks.

### Create a Service Account​

Create a service account with the appropriate permissions. This account is required to interact with GCP services.

-
Run the following command to create a Service account:

```

gcloud iam service-accounts create <your-service-account-name>

```

-
Grant the required permissions to the Service Account using your custom role created previously:

```

gcloud projects add-iam-policy-binding <your-gcp-project> \

--member="serviceAccount:<your-custom-role>@<your-gcp-project>.iam.gserviceaccount.com" \

--role=projects/<your-gcp-project>/roles/portworx_role

```

This command grants the service account the permissions defined in the `portworx_role` file.

-
Grant your service account the Service account user permissions:

```

gcloud projects add-iam-policy-binding <your-gcp-project> \

--member="serviceAccount:<your-custom-role>@<your-gcp-project>.iam.gserviceaccount.com" \

--role="roles/iam.serviceAccountUser"

```

- Run the following command to get the JSON output of your service account:

```

gcloud iam service-accounts keys create gcloud.json \

--iam-account=<your-custom-role>@<your-gcp-project>.iam.gserviceaccount.com

```

### Create a secret​

Create a secret called `px-gcloud` in the Portworx namespace (namespace where you will deploy Portworx) using the previously generated JSON file. This will be used for authenticating your service account:

```

oc -n portworx create secret generic px-gcloud --from-file=gcloud.json

```

## Create a monitoring ConfigMap​

Newer OpenShift versions do not support the Portworx Prometheus deployment. As a result, you must enable monitoring for user-defined projects before installing the Portworx Operator. Use the instructions in this section to configure the OpenShift Prometheus deployment to monitor Portworx metrics.

To integrate OpenShift’s monitoring and alerting system with Portworx, create a `cluster-monitoring-config` ConfigMap in the `openshift-monitoring` namespace:

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
For Distribution Name, select OpenShift 4+.

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

- Drive Tags – Enter multiple tags as key-value pairs to be applied to the disks created by Portworx.

- Consume Unused – To enable Portworx to use all available, unused, and unmounted drives on the node.

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

- If using a secure registry, provide Kubernetes Docker Registry Secret a customized Kubernetes secret that will serve as authentication for a container registry. Ensure the secret should exist within the same namespace as the StorageCluster object.

-
Under Component Settings section

- Select the Enable Stork checkbox to enable Stork.

- Select the Restrict Data Protection RBAC to restrict RBAC permissions for Stork. You will not be able to use Backup and DR capabilities with this restriction. For more information, see Restrict Data Protection RBAC.

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
Click Download .yaml to download the yaml file with the customized specification or Save Spec to save the specification.

- Click Save & Download to generate the specification.

## Install Portworx Operator using OpenShift Console​

Before you can install Portworx on your OpenShift cluster, you must first install the Portworx Operator. Perform the following steps to prepare your OpenShift cluster by installing the Operator.

-
Sign in to the OpenShift Container Platform web console.

-
From the left navigation pane, select OperatorHub.
The system displays the OperatorHub page.

-
Search for Portworx and select Portworx Operator.
The system displays the Portworx Operator page.

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
Add the following to your StorageCluster Spec, and click Create. This will ensure that Portworx has the proper authorization to manage GCP disks:

```

volumes:

  - name: gcloud

    mountPath: /etc/pwx/gce

    secret:

      secretName: px-gcloud

env:

  - name: GOOGLE_APPLICATION_CREDENTIALS

    value: "/etc/pwx/gce/gcloud.json"

```

Example spec with the above addition:

```

....

kind: StorageCluster

apiVersion: core.libopenstorage.org/v1

....

spec:

  image: portworx/oci-monitor:3.4.0.1

  imagePullPolicy: Always

....

  volumes:

    - name: gcloud

      mountPath: /etc/pwx/gce

      secret:

        secretName: px-gcloud

  env:

    - name: GOOGLE_APPLICATION_CREDENTIALS

      value: "/etc/pwx/gce/gcloud.json"

```

-
The system deploys Portworx, and displays the Portworx instance in the Storage Cluster tab of the Installed Operators page. Once Portworx has fully deployed, the status will show as Online:

## Verify Portworx Pod Status​

Run the following command to list and filter the results for Portworx pods and specify the namespace where you have deployed Portworx:

```

oc get pods -n portworx -o wide | grep -e portworx -e px

```

```

portworx-api-774c2                                      1/1     Running   0                2m55s   192.168.121.196   username-k8s1-node0    <none>           <none>

portworx-api-t4lf9                                      1/1     Running   0                2m55s   192.168.121.99    username-k8s1-node1    <none>           <none>

portworx-kvdb-94bpk                                     1/1     Running   0                4s      192.168.121.196   username-k8s1-node0    <none>           <none>

portworx-operator-xxxx-xxxxxxxxxxxxx                    1/1     Running   0                4m1s    10.244.1.99       username-k8s1-node0    <none>           <none>

prometheus-px-prometheus-0                              2/2     Running   0                2m41s   10.244.1.105      username-k8s1-node0    <none>           <none>

px-cluster-1c3edc42-4541-48fc-b173-xxxx-xxxxxxxxxxxxx   2/2     Running   0                2m55s   192.168.121.196   username-k8s1-node0    <none>           <none>

px-cluster-1c3edc42-4541-48fc-b173-xxxx-xxxxxxxxxxxxx   1/2     Running   0                2m55s   192.168.121.99    username-k8s1-node1    <none>           <none>

px-csi-ext-868fcb9fc6-xxxxx                             4/4     Running   0                3m5s    10.244.1.103      username-k8s1-node0    <none>           <none>

px-csi-ext-868fcb9fc6-xxxxx                             4/4     Running   0                3m5s    10.244.1.102      username-k8s1-node0    <none>           <none>

px-csi-ext-868fcb9fc6-xxxxx                             4/4     Running   0                3m5s    10.244.3.107      username-k8s1-node1    <none>           <none>

px-prometheus-operator-59b98b5897-xxxxx                 1/1     Running   0                3m3s    10.244.1.104      username-k8s1-node0    <none>           <none>

```

Note the name of a `px-cluster` pod. You will run `pxctl` commands from these pods in Verify Portworx Cluster Status.

## Verify Portworx Cluster Status​

You can find the status of the Portworx cluster by running `pxctl status` commands from a pod.
Enter the following `oc exec` command, specifying the pod name you retrieved in Verify Portworx Pod Status:

```

oc exec px-cluster-1c3edc42-4541-48fc-b173-xxxx-xxxxxxxxxxxxx -n portworx -- /opt/pwx/bin/pxctl status

```

```

Defaulted container "portworx" out of: portworx, csi-node-driver-registrar

Status: PX is operational

Telemetry: Disabled or Unhealthy

Metering: Disabled or Unhealthy

License: Trial (expires in 31 days)

Node ID: 788bf810-57c4-4df1-xxxx-xxxxxxxxxxxxx

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

        Cluster ID: px-cluster-1c3edc42-xxxx-xxxxxxxxxxxxx

        Cluster UUID: 33a82fe9-d93b-435b-xxxx-xxxxxxxxxxxxx

        Scheduler: kubernetes

        Nodes: 2 node(s) with storage (2 online)

        IP              ID                                      SchedulerNodeName       Auth            StorageNode     Used    Capacity        Status  StorageStatus       Version         Kernel                  OS

        192.168.121.196 f6d87392-81f4-459a-xxxx-xxxxxxxxxxxxx    username-k8s1-node0      Disabled        Yes             10 GiB  3.0 TiB         Online  Up 2.11.0-81faacc   3.10.0-1127.el7.x86_64  CentOS Linux 7 (Core)

        192.168.121.99  788bf810-57c4-4df1-xxxx-xxxxxxxxxxxxx    username-k8s1-node1      Disabled        Yes             10 GiB  3.0 TiB         Online  Up (This node)      2.11.0-81faacc  3.10.0-1127.el7.x86_64  CentOS Linux 7 (Core)

Global Storage Pool

        Total Used      :  20 GiB

        Total Capacity  :  6.0 TiB

```

Status displays `PX is operational` when the cluster is running as expected.

## Verify pxctl Cluster Provision Status​

-
Access the Portworx CLI.

-
Run the following command to find the storage cluster:

```

oc -n portworx get storagecluster

```

```

NAME                                              CLUSTER UUID                           STATUS   VERSION   AGE

px-cluster-1c3edc42-4541-48fc-xxxx-xxxxxxxxxxxxx   33a82fe9-d93b-435b-xxxx-xxxxxxxxxxxx   Online   2.11.0    10m

```

The status must display the cluster is `Online`.

-
Run the following command to find the storage nodes:

```

oc -n portworx get storagenodes

```

```

NAME                  ID                                      STATUS   VERSION          AGE

username-k8s1-node0   f6d87392-81f4-459a-xxxx-xxxxxxxxxxxxx   Online   2.11.0-81faacc   11m

username-k8s1-node1   788bf810-57c4-4df1-xxxx-xxxxxxxxxxxxx   Online   2.11.0-81faacc   11m

```

The status must display the nodes are `Online`.

-
Verify the Portworx cluster provision status by running the following command.
 Specify the pod name you retrieved in Verify Portworx Pod Status.

```

oc exec px-cluster-1c3edc42-4541-48fc-b173-xxxx-xxxxxxxxxxxxx -n portworx -- /opt/pwx/bin/pxctl cluster provision-status

```

```

Defaulted container "portworx" out of: portworx, csi-node-driver-registrar

NODE                                    NODE STATUS     POOL                                            POOL STATUS     IO_PRIORITY     SIZE    AVAILABLE   USED   PROVISIONED          ZONE    REGION  RACK

788bf810-57c4-4df1-xxxx-xxxxxxxxxxxx    Up              0 ( 96e7ff01-fcff-4715-xxxx-xxxxxxxxxxxx )      Online          HIGH            3.0 TiB 3.0 TiB    10 GiB       0 B             default default default

f6d87392-81f4-459a-xxxx-xxxxxxxxx       Up              0 ( e06386e7-b769-xxxx-xxxxxxxxxxxxx )          Online          HIGH            3.0 TiB 3.0 TiB    10 GiB       0 B             default default default

```

## What to do next​

Create a PVC. For more information, see Create your first PVC.

In this topic:
