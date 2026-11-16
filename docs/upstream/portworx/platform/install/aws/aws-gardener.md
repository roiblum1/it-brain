# Installation on an AWS Gardener Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/aws/aws-gardener (Portworx Enterprise latest)

Installation on an AWS Gardener Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx Enterprise on a Gardener cluster running on AWS. Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

The following collection of tasks describes how to install Portworx Enterprise on an AWS Gardener cluster:

- Create a Shoot Cluster

- Configure Authentication

- Install Node Packages

- Install Portworx

- Monitor Portworx Nodes

- Verify Portworx Pod Status

- Verify Portworx Cluster Status

- Verify Portworx Pool Status

- Verify pxctl Cluster Provision Status

Complete all the tasks to install Portworx.

## Create a Shoot Cluster​

Use the Gardener dashboard or the Gardener API to create a shoot cluster on AWS. The shoot specification controls the worker node EC2 instances, networking, and the OIDC issuer that Portworx will federate against when using Workload Identity.

-
Sign in to your Gardener dashboard, or set up `kubectl` access to your Gardener landscape.

-
Create a shoot cluster on the `aws` provider. In the shoot specification, ensure the following fields are set:

- `spec.cloudProfile.name: aws`

- `spec.region` — set to the AWS region where Portworx will run.

- `spec.provider.workers` — define the worker pools. Each worker pool's EC2 instances are launched through Auto Scaling groups that Portworx will be granted access to.

-
Once the shoot is reconciled, download its `kubeconfig` from the Gardener dashboard or via `kubectl`, and confirm you can reach the cluster:

```

kubectl get nodes

```

-
Note the following values from your shoot. These values are required when you configure the authentication:

- The AWS account ID hosting the shoot.

- The IAM role (instance profile) attached to the shoot's worker node EC2 instances.

- The OIDC issuer URL of the shoot (only required for Workload Identity).

For more information on shoot creation, see the Gardener documentation.

## Configure Authentication​

Portworx supports two authentication methods on Gardener:

- IAM Policy - attach an IAM policy with the required permissions to the Gardener worker nodes' instance role. Portworx uses these node-level credentials at runtime.

- Workload Identity (IRSA) - federated identity using AWS IAM Roles for Service Accounts (IRSA). The `eks-pod-identity-webhook` injects a projected service account token and the environment variables required by the AWS SDK into Portworx pods, so no static credentials are stored in the cluster. For more information, see Workload identity for cloud operations in Portworx.

LIMITATION

Portworx Enterprise does not support AWS KMS grants.

Choose the method that matches your security and operational requirements.

- IAM Policy

- Workload Identity

With IAM Policy authentication, Portworx uses the credentials of the IAM role attached to the Gardener worker node EC2 instances. Create an IAM policy with the permissions Portworx requires and attach it to the worker node instance role.

-
In the AWS Management Console, go to IAM > Policies and select Create policy.

-
Choose the JSON tab, and then paste the following permissions into the editor:

note

These are the minimum permissions required for storage operations for a Portworx cluster. For the complete set of permissions for all Portworx storage operations, see the credentials reference.

```

{

    "Version": "2012-10-17",

    "Statement": [

        {

            "Sid": "EBSVolumeManagement",

            "Effect": "Allow",

            "Action": [

                "ec2:CreateVolume",

                "ec2:DeleteVolume",

                "ec2:AttachVolume",

                "ec2:DetachVolume",

                "ec2:DescribeVolumes",

                "ec2:ModifyVolume",

                "ec2:DescribeVolumeStatus",

                "ec2:CreateSnapshot",

                "ec2:DeleteSnapshot",

                "ec2:DescribeSnapshots",

                "ec2:CreateTags",

                "ec2:DeleteTags",

                "ec2:DescribeTags",

                "ec2:DescribeVolumeAttribute",

                "ec2:DescribeVolumesModifications",

                "autoscaling:DescribeAutoScalingGroups"

            ],

            "Resource": "*"

        },

        {

            "Sid": "InstanceDescription",

            "Effect": "Allow",

            "Action": [

                "ec2:DescribeInstances"

            ],

            "Resource": "*"

        }

    ]

}

```

-
Name the policy and create it.

-
Attach the policy to the IAM role (instance profile) of your Gardener worker nodes:

- From the IAM page, select Roles in the left pane.

- Search for and select the worker node instance role of your shoot cluster.

- From the Add permissions dropdown, select Attach policies.

- Search for the policy you created, select it, and then select Attach policies.

note

Gardener may recreate worker nodes during shoot reconciliation (for example, after a worker pool update). The IAM policy remains attached because it is bound to the worker node instance role, not to individual instances.

With Workload Identity authentication, Portworx pods assume an AWS IAM role through the shoot's OIDC provider, eliminating the need to store long-lived credentials in the cluster. Before installing Portworx, create an IAM role with the required permissions and a trust policy that federates it with the Kubernetes service accounts that Portworx uses. You will provide the role ARN during spec generation.

-
In the AWS Management Console, go to IAM > Policies and create a policy with the permissions required for the AWS services that Portworx uses for CloudSnap and CloudDrive.

```

{

    "Version": "2012-10-17",

    "Statement": [

        {

            "Sid": "EBSVolumeManagement",

            "Effect": "Allow",

            "Action": [

                "ec2:CreateVolume",

                "ec2:DeleteVolume",

                "ec2:AttachVolume",

                "ec2:DetachVolume",

                "ec2:DescribeVolumes",

                "ec2:ModifyVolume",

                "ec2:DescribeVolumeStatus",

                "ec2:CreateSnapshot",

                "ec2:DeleteSnapshot",

                "ec2:DescribeSnapshots",

                "ec2:CreateTags",

                "ec2:DeleteTags",

                "ec2:DescribeTags",

                "ec2:DescribeVolumeAttribute",

                "ec2:DescribeVolumesModifications",

                "autoscaling:DescribeAutoScalingGroups"

            ],

            "Resource": "*"

        },

        {

            "Sid": "InstanceDescription",

            "Effect": "Allow",

            "Action": [

                "ec2:DescribeInstances"

            ],

            "Resource": "*"

        },

        {

            "Sid": "S3BucketManagement",

            "Effect": "Allow",

            "Action": [

                "s3:CreateBucket",

                "s3:ListAllMyBuckets",

                "s3:GetBucketLocation",

                "s3:ListBucket",

                "s3:PutObject",

                "s3:GetObject",

                "s3:DeleteObject"

            ],

            "Resource": [

                "*"

            ]

        }

    ]

}

```

-
Create an IAM role and attach the policy you created in the previous step.

-
Edit the role's Trust relationships and replace the trust policy with the following:

```

{

    "Version": "2012-10-17",

    "Statement": [

        {

            "Effect": "Allow",

            "Principal": {

                "Federated": "arn:aws:iam::<account-id>:oidc-provider/<oidc-provider-url>"

            },

            "Action": "sts:AssumeRoleWithWebIdentity",

            "Condition": {

                "StringEquals": {

                    "<oidc-provider-url>:aud": "sts.amazonaws.com"

                },

                "StringLike": {

                    "<oidc-provider-url>:sub": [

                        "system:serviceaccount:<namespace>:portworx",

                        "system:serviceaccount:<namespace>:stork",

                        "system:serviceaccount:<namespace>:px-node-wiper"

                    ]

                }

            }

        }

    ]

}

```

Replace `<account-id>` with the AWS account ID hosting the shoot, `<oidc-provider-url>` with the OIDC issuer URL of your Gardener shoot cluster (without the `https://` prefix), and `<namespace>` with the namespace where you install Portworx.

The `portworx` service account is required for Portworx, the `stork` service account is required for Stork, and the `px-node-wiper` service account is required when uninstalling the `StorageCluster` with the `UninstallAndDelete` strategy.
For more information, see Create a role for OpenID Connect federation (console).

-
Ensure the `eks-pod-identity-webhook` is deployed on the cluster.
Workload identity does not function without this webhook. The webhook injects the projected service account token, the AWS SDK environment variables, and enables token exchange with AWS. On Gardener worker nodes running on EC2, you must deploy the webhook manually. For more information, see Amazon EKS Pod Identity Webhook.

important

After cloning the repository, edit the deployment-base.yaml file to include the `--aws-default-region <aws-region>` flag in the `spec.template.spec.containers.command` field before deploying the webhook.

-
Note the ARN of the IAM role. You will enter it in the AWS Role ARN field when generating the Portworx specification.

## Install Node Packages​

Portworx requires the following operating system packages on every worker node before installation:

- `lvm2`

- `mdadm`

- `parted`

- `augeas-tools`

- `thin-provisioning-tools`

- `dmsetup`

- `nfs-kernel-server`

- `nfs-common`

- `rpcbind`

Portworx does not install operating system packages on Garden Linux worker nodes. If your Gardener cluster uses Garden Linux, ensure that these packages are preinstalled in the worker node image, or provisioned through your supported Gardener or organizational node provisioning process, before you install Portworx. For more information, contact Portworx Support.

## Install Portworx​

You can install Portworx Enterprise on an AWS Gardener cluster either by generating a Kubernetes specification through Portworx Central and applying it, or by deploying the Portworx Helm chart. Choose the installation mode that matches your tooling and operational preferences.

- Generate Specification

- Install using Helm

To install Portworx, you must first generate Kubernetes manifests that you will deploy in your AWS Gardener cluster by following these steps.

-
Sign in to the Portworx Central console.
 The system displays the Welcome to Portworx Central! page.

-
In the Portworx Enterprise section, select Generate Cluster Spec.
 The system displays the Generate Spec page.

-
From the Portworx Version dropdown menu, select the Portworx version to install.

-
From the Platform dropdown menu, select AWS.

-
From the Distribution Name dropdown menu, select Gardener.

-
In the AWS Role ARN field, enter the ARN of the IAM role you created in the Configure Authentication section, in the format `arn:aws:iam::<account-id>:role/<role-name>`.
Portworx Enterprise uses this role to access AWS services through IRSA.

note

The default Portworx Central workflow for installing Portworx Enterprise on an AWS Gardener cluster uses workload identity (IRSA). If you configured IAM Policy authentication instead, leave this field blank and proceed to the Customize step (Step 8) to modify the generated `StorageCluster` specification for IAM Policy authentication.

-
In the Namespace field, enter the namespace where you plan to install Portworx.
 By default, the namespace is `portworx`.

-
(Optional) To customize the configuration options and generate a custom specification, click Customize and perform the following steps:

note

To continue without customizing the default configuration or generating a custom specification, proceed to Step 9.

- Basic tab:

- Select one of the following:

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

- Storage tab:

warning

Do not add volumes of different types when configuring storage devices. For example, do not add both GP2 and GP3 or IO1. This can cause performance issues or errors.

- Select one of the following:

- To enable Portworx to provision drives using a specification, do the following:

- Select the Create Using a Spec option.

- (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- (Optional) Select the Run on Small Node Configuration checkbox if your cluster nodes have limited resources (for example, 4 CPU cores and 8 GB of memory).
Portworx Enterprise requires 8 CPU cores and 8 GB of memory by default. Enabling this option allows Portworx to run on smaller nodes, but it may reduce overall performance compared to the default configuration.

note

This checkbox is available only when you select PX-StoreV2 as the datastore.

- To add one or more cloud storage drive types for Portworx to use, click + Add Drive and select one of the following types of drives:

- GP2

- GP3

- IO1

note

- To select GP2 as the drive type, you must select PX-StoreV1 as the datastore.

- For PX-StoreV2, four drives are recommended for optimal performance.

- Configure the following fields for the drive:

- Size (GB) - Specify the size of the drive in gigabytes.

- IOPS required from EBS volume - Enter the input/output operations per second (IOPS) value for the drive.

note

- IOPS is required when you select IO1 drive type only.

- If you do not specify an IOPS value for GP3, Portworx uses the default value of 3000.

- Throughput for EBS volume - Enter the required data transfer rate for the drive.

- Encryption - Choose None to disable encryption or BYOK Encryption to encrypt your AWS cluster data disk using BYOK encryption.

- Encryption Key - If you choose BYOK Encryption, specify the key to use for BYOK encryption.
For more information, see AWS KMS.

- Drive Tags - Add labels in `key:value` format to organize and identify drives.
 This is useful for policies and workload mapping.

- Action - Use the trash icon to remove a drive type from the configuration.

- Initial Storage Nodes (Optional): Enter the number of storage nodes that need to be created across zones and node pools.

- From the Default IO Profile dropdown menu, select Auto.
 This enables Portworx to automatically choose the best I/O profile based on detected workload patterns.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
 Enter the path of the journal device in the Journal Device Path field.

- To enable Portworx to use all available, unused, and unmounted drives on the node, do the following:

- Select the Consume Unused option.

- (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- (Optional) Select the Run on Small Node Configuration checkbox if your cluster nodes have limited resources (for example, 4 CPU cores and 8 GB of memory).
Portworx requires 8 CPU cores and 8 GB of memory by default. Enabling this option allows Portworx to run on smaller nodes, but it may reduce overall performance compared to the default configuration.

note

This checkbox is available only when you select PX-StoreV2 as the datastore.

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

- (Optional) To designate PX-StoreV1 as the datastore, select PX-StoreV1. By default, the system selects PX-StoreV2 as the datastore.

- (Optional) Select the Run on Small Node Configuration checkbox if your cluster nodes have limited resources (for example, 4 CPU cores and 8 GB of memory).
Portworx requires 8 CPU cores and 8 GB of memory by default. Enabling this option allows Portworx to run on smaller nodes, but it may reduce overall performance compared to the default configuration.

note

This checkbox is available only when you select PX-StoreV2 as the datastore.

- For PX-StoreV2, in the Metadata Path field, enter a pre-provisioned path for storing the Portworx metadata.
The path must be at least 64 GB in size.

- In the Drive/Device field, specify the block drive(s) that Portworx uses for data storage.

- In the Pool Label field, assign a custom label in key:value format to identify and categorize storage pools.

- From the Journal Device dropdown menu, select one of the following:

- None – To use the default journaling setting.

- Auto – To automatically allocate journal devices.

- Custom – To manually enter a journal device path.
 Enter the path of the journal device in the Journal Device Path field.

- Click Next.

- Network tab:

- In the Interface(s) section, do the following:

- Enter the Data Network Interface to be used for data traffic.

- Enter the Management Network Interface to be used for management traffic.

- In the Advanced Settings section, do the following:

- Enter the Starting port for Portworx services.
 By default, the starting port is `9001`.

- Select Next.

- Deployment tab:

-
In the Kubernetes Distribution section, under Are you running on either of these?, select Gardener.

-
In the Component Settings section:

- (Optional) Select the Enable Stork checkbox to enable Stork.

- (Optional) Select the Remote Fastpath (NVMe-oF/TCP) checkbox to enable Remote Fastpath. For more information, see Remote Fastpath.

- (Optional) Select the Restrict Data Protection RBAC checkbox to restrict RBAC permissions for Stork (if enabled) and Operator. You will not be able to use Backup and DR capabilities with this restriction. For more information, see Restrict Data Protection RBAC.

- (Optional) Select the Enable Monitoring checkbox to enable monitoring of Portworx components and resources.

- To configure the monitoring stack, select one of the following:

- Portworx Managed - To enable Portworx to install and manage Prometheus and Operator automatically.
 Ensure that no other Prometheus Operator instance is already running on the cluster.

- User Managed - To configure and manage your own monitoring stack.

- Select the Enable Autopilot checkbox to enable Portworx Autopilot. For User Managed monitoring stack, Portworx supports the following metrics providers that Autopilot will use to fetch metrics for rule evaluation and automated actions.

- Prometheus - Provide a valid Prometheus URL

- Datadog - Provide a valid Datadog URL, Secret Name and Secret Namespace. To create a Secret, refer to enable Datadog.
 For more information on Autopilot, see Expanding your Storage Pool with Autopilot.

note

This checkbox is available only when you select the Enable Monitoring checkbox.

- (Optional) Select the Enable Telemetry checkbox to enable telemetry in the StorageCluster spec.
For information, see Portworx Telemetry.

- Enter the prefix for the Portworx cluster name in the Cluster Name Prefix field.

- Select the Secrets Store Type from the dropdown menu to store and manage secure information for features such as CloudSnaps and Encryption.

-
In the Identity and Access Management (IAM) section, select the Enable Workload Identity (WLI) checkbox to use a federated identity with short-lived tokens injected per-pod by the `eks-pod-identity-webhook`.
Workload Identity Federation allows the Portworx Operator to configure Portworx components to securely authenticate with cloud services, without storing static cloud credentials. For more information, see Workload identity for cloud operations in Portworx.
When you enable Enable Workload Identity (WLI):

- Select the Enable for Stork (for data protection using Portworx DR or Backup) checkbox to enable workload identity for Stork.
You must select this checkbox to use Portworx Backup or Portworx DR.

- Under Configure Workload Identity Settings, the Cloud Provider (`AWS`) and Key (`eks.amazonaws.com/role-arn`) fields are pre-populated. In the AWS Role ARN field, enter the ARN of the IAM role you created in the Configure Authentication section.

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

#### Deploy Portworx Operator​

Use the Operator specification you generated to deploy the Portworx Operator:

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

#### Deploy StorageCluster​

Apply the `StorageCluster` specification you generated:

```

kubectl apply -f px-storagecluster.yaml

```

```

storagecluster.core.libopenstorage.org/px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-8dfd338e915b created

```

You can install Portworx Enterprise on AWS Gardener using the Portworx Helm chart. This procedure assumes that Portworx is installed in the `portworx` namespace. If you want to install it in a different namespace, use the `-n <px-namespace>` flag.

-
Add the `portworx/helm` repository to your local Helm repository:

```

helm repo add portworx https://raw.githubusercontent.com/portworx/helm/master/stable/

```

```

"portworx" has been added to your repositories

```

-
Verify that the repository has been successfully added:

```

helm repo list

```

```

NAME    	URL

portworx	https://raw.githubusercontent.com/portworx/helm/master/stable/

```

-
Create a `px_install_values.yaml` file using the template that matches the authentication method you configured in the Configure Authentication section.

- IAM Policy

- Workload Identity

Portworx uses the credentials of the IAM role attached to the Gardener worker node EC2 instances at runtime, so no credentials are referenced in `px_install_values.yaml`:

```

clusterName: <unique-cluster-name>

provider: aws

drives: type=gp3,size=150

internalKVDB: true

```

With Workload Identity, the `eks-pod-identity-webhook` injects credentials into Portworx pods based on annotations on the Portworx service accounts. Use the `workloadIdentity.credentials` parameter to instruct the Helm chart to annotate the service accounts with the ARN of the IAM role you created.

```

clusterName: <unique-cluster-name>

provider: aws

drives: type=gp3,size=150

internalKVDB: true

workloadIdentity:

  credentials:

    - cloudProvider: aws

      key: eks.amazonaws.com/role-arn

      value: <IAM_ROLE_ARN>

stork:

  enabled: true

  useWorkloadIdentity: true

```

Replace `<IAM_ROLE_ARN>` with the ARN of the IAM role you created in the Configure Authentication section. Set `stork.useWorkloadIdentity` to `true` to apply the same workload identity credentials to Stork.

-
(Optional) In many cases, you may want to customize Portworx configurations, such as enabling monitoring or specifying specific storage devices. You can pass the custom configuration to the `px_install_values.yaml` file.

note

- You can refer to the Portworx Helm chart parameters for a list of configurable parameters and the values.yaml file for the configuration file template.

- The default `clusterName` is `mycluster`. However, it is recommended to change it to a unique identifier to avoid conflicts in multi-cluster environments.

-
Install Portworx:

note

To install a specific version of the Helm chart, use the `--version` flag. Example: `helm install <px-release> portworx/portworx --version <helm-chart-version>`.

```

helm install <px-release> portworx/portworx -n portworx -f px_install_values.yaml --debug

```

-
Check the status of your Portworx installation:

```

helm status <px-release> -n portworx

```

```

NAME: px-release

LAST DEPLOYED: Thu Sep 26 05:53:17 2024

NAMESPACE: portworx

STATUS: deployed

REVISION: 1

TEST SUITE: None

NOTES:

Your Release is named "px-release"

Portworx Pods should be running on each node in your cluster.

Portworx would create a unified pool of the disks attached to your Kubernetes nodes.

No further action should be required and you are ready to consume Portworx Volumes as part of your application data requirements.

```

## Monitor Portworx Nodes​

-
Enter the following `kubectl get` command and wait until all Portworx nodes show as `Ready` or `Online` in the output:

```

kubectl -n <px-namespace> get storagenodes -l name=portworx

```

```

NAME                   ID                                     STATUS   VERSION   AGE

gardener-shoot-node0   xxxxxxxx-xxxx-xxxx-xxxx-43cf085e764e   Online   3.6.2     4m52s

gardener-shoot-node1   xxxxxxxx-xxxx-xxxx-xxxx-4597de6fdd32   Online   3.6.2     4m52s

gardener-shoot-node2   xxxxxxxx-xxxx-xxxx-xxxx-e2169ffa111c   Online   3.6.2     4m52s

```

-
Enter the following `kubectl describe` command with the `NAME` of one of the Portworx nodes you retrieved above to show the current installation status for individual nodes:

```

kubectl -n <px-namespace> describe storagenode <portworx-node-name>

```

## Verify Portworx Pod Status​

Enter the following command to list the Portworx pods in the namespace where you deployed Portworx:

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

Note the name of a `px-cluster` pod. You will run pxctl commands from these pods in Verify Portworx Cluster Status.

If you configured Workload Identity authentication, perform the following additional checks:

-
Verify that Portworx Operator added the IRSA annotation on the `portworx` service account:

```

kubectl -n <px-namespace> get sa portworx -o yaml

```

The output should include the following annotation, where the value matches the ARN of the IAM role you created in Configure Authentication:

```

metadata:

  annotations:

    eks.amazonaws.com/role-arn: arn:aws:iam::<account-id>:role/<role-name>

```

-
After the configuration is applied, the Portworx Operator restarts the pods as needed.
Verify that the Portworx pods include the projected token volume, volume mount, and environment variables injected by the `eks-pod-identity-webhook`:

```

kubectl -n <px-namespace> get pods <px-pod> -oyaml

```

#### Token volume​

```

volumes:

- name: aws-iam-token

  projected:

    defaultMode: 420

    sources:

    - serviceAccountToken:

        audience: sts.amazonaws.com

        expirationSeconds: 86400

        path: token

```

#### Volume mount​

```

volumeMounts:

- mountPath: /var/run/secrets/eks.amazonaws.com/serviceaccount

  name: aws-iam-token

  readOnly: true

```

#### Environment variables​

```

spec:

  containers:

  - env:

    - name: AWS_ROLE_ARN

      value: arn:aws:iam::<account-id>:role/<role-name>

    - name: AWS_WEB_IDENTITY_TOKEN_FILE

      value: /var/run/secrets/eks.amazonaws.com/serviceaccount/token

    - name: AWS_DEFAULT_REGION

      value: <region>

    - name: AWS_STS_REGIONAL_ENDPOINTS

      value: regional

```

These are used by the AWS SDK to authenticate and make API calls.

## Verify Portworx Cluster Status​

You can find the status of the Portworx cluster by running `pxctl status` from a Portworx pod. Use the pod name you retrieved in Verify Portworx Pod Status:

```

kubectl exec <pod-name> -n <px-namespace> -- /opt/pwx/bin/pxctl status

```

`Status: PX is operational` indicates that the cluster is running as expected. If the cluster is using the PX-StoreV2 datastore, the `StorageNode` entries for each node display `Yes(PX-StoreV2)`.

## Verify Portworx Pool Status​

note

This procedure is applicable for clusters with the PX-StoreV2 datastore.

Run the following command to view the Portworx drive configuration for your pod:

```

kubectl exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl service pool show

```

The output `Type: PX-StoreV2` confirms that the pod uses the PX-StoreV2 datastore.

## Verify pxctl Cluster Provision Status​

-
Run the following command to find the storage cluster:

```

kubectl -n <px-namespace> get storagecluster

```

The status must display the cluster as `Online`.

-
Run the following command to find the storage nodes:

```

kubectl -n <px-namespace> get storagenodes

```

The status must display the nodes as `Online`.

-
Verify the Portworx cluster provision status by running the following command. Specify the pod name you retrieved in Verify Portworx Pod Status:

```

kubectl exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl cluster provision-status

```

## What to do next​

- Create a PVC. For more information, see Create your first PVC.

In this topic:
