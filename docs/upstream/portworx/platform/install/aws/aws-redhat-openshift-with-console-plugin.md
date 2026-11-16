# Installation on Red Hat OpenShift Service on AWS (ROSA) Cluster

Source: https://docs.portworx.com/portworx-enterprise/platform/install/aws/aws-redhat-openshift-with-console-plugin (Portworx Enterprise latest)

Installation on Red Hat OpenShift Service on AWS (ROSA) Cluster | Portworx Enterprise Documentation

This topic provides instructions for installing Portworx on Red Hat OpenShift Service on AWS (ROSA) cluster with console plugin. Ensure that your cluster meets all the prerequisites before installing Portworx Enterprise.

The following collection of tasks describes how to install Portworx on a Red Hat OpenShift cluster:

- Configure authentication

- Generate Portworx Specification

- Install Portworx Operator using OpenShift console

- Deploy Portworx using the OpenShift console

- Verify Portworx cluster status

- Verify Portworx pod status

- Verify Portworx pool status

- Verify pxctl cluster provision status

Complete all the tasks to install Portworx.

## Configure authentication​

Portworx supports two authentication methods on Red Hat OpenShift Service on AWS (ROSA):

- IAM User credentials — create an AWS IAM user with the required permissions, generate an access key, and store the key in a Kubernetes secret that Portworx reads at runtime.

- Workload Identity (IRSA) — federated identity using AWS IAM Roles for Service Accounts (IRSA). The `eks-pod-identity-webhook` (included by default on ROSA) injects a projected service account token and the environment variables required by the AWS SDK into Portworx pods, so no static credentials are stored in the cluster. For an overview, see Workload identity for cloud operations in Portworx.

LIMITATION

Portworx Enterprise does not support AWS KMS grants.

Choose the method that matches your security and operational requirements.

- IAM User credentials

- Workload Identity

#### Create an AWS user​

Create an AWS user with the required permissions for Portworx to work.

-
Sign in to the AWS Management Console.

-
Go to the IAM Console Home page, select Users in the left pane.

-
On the Users page, select Create user in the upper-right corner to create a new user.

-
Specify your user details and select Next.

-
On the Set permissions page, select Attach policies directly, and then select Create policy.

-
In the policy editor, open the JSON tab, paste the following policy, and select Next:

```

{

  "Version": "2012-10-17",

  "Statement": [

    {

      "Sid": "",

      "Effect": "Allow",

      "Action": [

        "ec2:AttachVolume",

        "ec2:ModifyVolume",

        "ec2:DetachVolume",

        "ec2:CreateTags",

        "ec2:CreateVolume",

        "ec2:DeleteTags",

        "ec2:DeleteVolume",

        "ec2:DescribeTags",

        "ec2:DescribeVolumeAttribute",

        "ec2:DescribeVolumesModifications",

        "ec2:DescribeVolumeStatus",

        "ec2:DescribeVolumes",

        "ec2:DescribeInstances",

        "autoscaling:DescribeAutoScalingGroups"

      ],

      "Resource": ["*"]

    }

  ]

}

```

-
Provide a name for the policy and select Create policy. After the policy is created and attached to your user account, it appears in the Permissions policies section.

-
Select your policy in the Permissions policies section and select Next.

-
Review your user details and permissions, and then select Create user.

#### Create AWS secure credentials​

After you create the policy in the previous section, create credentials for secure access to your AWS account.

-
From the User page, find the user you created in the previous section using the search bar, and then select the user name.

-
On the user information page, select the Security credentials tab under Summary.

-
In the Access keys section, select Create access key.

-
Select Application running on an AWS compute service, and then select Next.

-
Provide a description tag value and select Create access key.

-
Select Download .csv file to save your credentials.

-
Use the values from the CSV file to create an AWS secret in OpenShift:

```

oc create secret generic -n portworx aws-creds \

  --from-literal=aws-key=XXXXXXXXXXXXXX \

  --from-literal=aws-secret=XXXXXXXXXXXX

```

#### Open ports for worker nodes​

Add inbound rules so that the AWS EC2 instances in your worker security group allow the required incoming traffic.

-
From the EC2 page of the AWS console, select Security Groups under Network & Security in the left pane.

-
On the Security Groups page, enter your ROSA cluster name in the search bar and press Enter. A list of security groups associated with your cluster appears. Select the link under Security group ID for the worker security group.

-
On the security group page, select Actions, and then select Edit inbound rules.

-
Select Add rule to add each of the following rules:

- Allow inbound Custom TCP traffic with Protocol: TCP on ports 17001–17022.

- Allow inbound Custom TCP traffic with Protocol: TCP on port 20048.

- Allow inbound Custom TCP traffic with Protocol: TCP on port 111.

- Allow inbound Custom UDP traffic with Protocol: UDP on port 17002.

- Allow inbound NFS traffic with Protocol: TCP on port 2049.

Make sure to specify the security group ID of the same worker security group mentioned in step 2.

-
Select Save.

#### Create a monitoring ConfigMap​

Recent OpenShift versions don’t support the Portworx Prometheus deployment. You must enable monitoring for user-defined projects before installing the Portworx Operator. Use this section to configure the OpenShift Prometheus deployment to monitor Portworx metrics.

To integrate OpenShift monitoring and alerting with Portworx, create a `cluster-monitoring-config` ConfigMap in the `openshift-monitoring` namespace:

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

With Workload Identity, Portworx pods assume an AWS IAM role through the cluster's OIDC provider, and the `eks-pod-identity-webhook` (included by default on ROSA) injects short-lived credentials at runtime. No static AWS access keys are stored in the cluster.

Before installing Portworx, create an IAM role with the required permissions and a trust policy that federates it with the Portworx service accounts. You will provide the role ARN during spec generation.

#### Prerequisites​

See Prerequisites.

#### Create an IAM role​

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

                    "<oidc-provider-url>:aud": "openshift"

                },

                "StringLike": {

                    "<oidc-provider-url>:sub": [

                        "system:serviceaccount:<namespace>:portworx",

                        "system:serviceaccount:<namespace>:px-node-wiper"

                    ]

                }

            }

        }

    ]

}

```

Replace `<account-id>`, `<oidc-provider-url>`, and `<namespace>` (the namespace where Portworx is installed) with the values from your ROSA cluster.

For more information, see Create a role for OpenID Connect federation (console).

-
Note the ARN of the IAM role. You will enter it as the AWS Workload Identity IAM Role ARN when generating the Portworx specification.

## Generate Portworx specification​

-
Sign in to the Portworx Central console.
 The system displays the Welcome to Portworx Central! page.

-
In the Portworx Enterprise section, select Generate Cluster Spec.
 The system displays the Generate Spec page.

-
From the Portworx Version drop-down menu, select the Portworx version to install.

-
From the Platform drop-down menu, select AWS.

-
From the Distribution Name drop-down menu, select Red Hat OpenShift Service on AWS (ROSA).

-
In the Namespace field, enter the namespace where you plan to install Portworx.
 By default, the namespace is `portworx`.

-
(Optional) To customize the configuration options and generate a custom specification, click Customize and perform the following steps:

note

To continue without customizing the default configuration or generating a custom specification, proceed to Step 8.

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

important

The selection between PX-StoreV2 and PX-StoreV1 is automatic. The default datastore is determined by a preflight check that runs across the cluster to assess whether it can deploy Portworx with the PX-StoreV2 datastore. If the preflight check passes for all nodes, PX-StoreV2 is selected as the default.

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

note

If you do not specify a Throughput value for Premium SSDv2, Portworx uses the default value of 125.

- Encryption - Choose None to disable encryption or BYOK Encryption to encrypt your ROSA cluster data disk using BYOK encryption.

- Encryption Key - If you choose BYOK Encryption, specify the key to use for BYOK encryption.
For more information, see AWS KMS.

- Drive Tags - Add labels in `key:value` format to organize and identify drives.
 This is useful for policies and workload mapping.
For more information, see How to assign custom labels to device pools.

- Action - Use the trash icon to remove a drive type from the configuration. You can add multiple drive types by selecting Add Drive Type, remove a drive type by selecting Remove, or add the same drive type with different configurations using + Add Drive.

- Initial Storage Nodes (Optional) - Enter the number of storage nodes that need to be created across zones and node pools.

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

important

The selection between PX-StoreV2 and PX-StoreV1 is automatic. The default datastore is determined by a preflight check that runs across the cluster to assess whether it can deploy Portworx with the PX-StoreV2 datastore. If the preflight check passes for all nodes, PX-StoreV2 is selected as the default.

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

important

The selection between PX-StoreV2 and PX-StoreV1 is automatic. The default datastore is determined by a preflight check that runs across the cluster to assess whether it can deploy Portworx with the PX-StoreV2 datastore. If the preflight check passes for all nodes, PX-StoreV2 is selected as the default.

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
 Set the starting port as `17001`.

- Select Next.

- Deployment tab:

-
In the Kubernetes Distribution section, under Are you running on either of these?, select Red Hat OpenShift Service on AWS (ROSA).

-
In the Component Settings section:

- (Optional) Select the Enable Stork checkbox to enable Stork.

- (Optional) Select the Remote Fastpath (NVMe-oF/TCP) checkbox to enable Remote Fastpath. For more information, see Remote Fastpath.

- (Optional) Select Restrict Data Protection RBAC to restrict RBAC permissions for Stork (if enabled) and Operator.
You will not be able to use Backup and DR capabilities with this restriction.
For more information, see Restrict Data Protection RBAC.

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

- In the Identity and Access Management (IAM) section, select the Enable Workload Identity (WLI) checkbox to use a federated identity with short-lived tokens injected per-pod by the `eks-pod-identity-webhook`.
Workload Identity Federation allows the Portworx Operator to configure Portworx components to securely authenticate with cloud services, without storing static cloud credentials. For more information, see Workload identity for cloud operations in Portworx.
When you enable Enable Workload Identity (WLI):

- Select the Enable for Stork (for data protection using Portworx DR or Backup) checkbox to enable workload identity for Stork.
You must select this checkbox to use Portworx Backup or Portworx DR.

- Under Configure Workload Identity Settings, the Cloud Provider (`AWS`) and Key (`eks.amazonaws.com/role-arn`) fields are pre-populated. In the AWS Role ARN field, enter the ARN of the IAM role you created in the Configure Authentication section.

-
In the Environment Variables section, enter name-value pairs in the respective fields.

- For a disaggregated installation, set node labels and set the `ENABLE_ASG_STORAGE_PARTITIONING` environment variable to `true`. For more information, see Deployment planning.

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
In Security Settings, select the Enable Authorization checkbox to enable Role-Based Access Control (RBAC) and secure access to storage resources in your cluster.

-
Click Finish.

-
In the summary page, enter a name for the specification in the Spec Name field, and tags in the Spec Tags field.

-
Click Download .yaml to download the yaml file with the customized specification or Save Spec to save the specification.

- Click Save & Download to generate the specification.

## Install Portworx Operator using OpenShift console​

-
Sign in to the OpenShift console by following the quick access instructions on the Accessing your cluster quickly page in the Red Hat OpenShift Service on AWS documentation.

-
Search for the Portworx Operator:

- OCP version 4.20 or later:
 From the OpenShift UI, go to Ecosystem > Software Catalog. From Project dropdown, select Create Project to create a new project. Enter a name for new project and select that project. Search for Portworx Operator, and the Portworx Operator page appears.

- OCP version 4.19 or earlier:
 From the OpenShift UI, go to OperatorHub, search for Portworx Operator, and the Portworx Operator page appears.

-
Select Install. The Install Operator page appears.

-
In Installation mode, select A specific namespace on the cluster.

-
From Installed Namespace, choose Create Project. The Create Project window appears.

-
Enter `portworx` and select Create to create a namespace named `portworx`.

-
In Console plugin, select Enable to manage your Portworx cluster using the Portworx dashboard within the OpenShift console.

note

If the Portworx Operator is installed but the OpenShift Console plugin is not enabled, or was previously disabled, you can re-enable it by running the following command.

```

oc patch console.operator cluster --type=json -p='[{"op":"add","path":"/spec/plugins/-","value":"portworx"}]'

```

-
Select Install to deploy the Portworx Operator in the `portworx` namespace.
After installation, the Create StorageCluster option appears.

-
Click Install to deploy Portworx Operator in the `portworx` namespace.
After you successfully install Portworx Operator, the system displays the Create StorageCluster option.

## Deploy Portworx using the OpenShift console​

-
Click Create StorageCluster.
The system displays the Create StorageCluster page.

-
Select YAML view. If you chose IAM User credentials in Configure authentication, reference the `aws-creds` secret in the `env` section:

```

env:

  - name: AWS_ACCESS_KEY_ID

    valueFrom:

      secretKeyRef:

        key: aws-key

        name: aws-creds

  - name: AWS_SECRET_ACCESS_KEY

    valueFrom:

      secretKeyRef:

        key: aws-secret

        name: aws-creds

```

note

If you chose Workload Identity in Configure authentication, skip the `env` section above. The generated specification already includes the `spec.workloadIdentity.credentials` block with your IAM role ARN, and Portworx pods receive AWS credentials through the `eks-pod-identity-webhook` at runtime.

-
Click Create.
 The system deploys Portworx, and displays the Portworx instance in the Storage Cluster tab of the Installed Operators page.

## Verify Portworx cluster status​

- After you create the `StorageCluster`, a Portworx option appears in the left pane of the OpenShift UI. Select the Cluster sub-tab to view the Portworx dashboard.

- If Portworx is installed successfully, the cluster status is Running. The dashboard also shows details about telemetry, monitoring, and the versions of Portworx and its components installed in your cluster.

- In Node Summary, verify that all Portworx nodes show Online.

Alternatively, you can verify Portworx cluster status using the command line. For more information, see Verify Portworx cluster status.

## Verify Portworx pod status​

-
Perform the following steps to verify Portworx pod status using the OpenShift console:

- From the left navigation pane of the OpenShift console, select Workloads, and then select Pods.

- In the Project drop-down, choose portworx.

- The list of pods in the `portworx` namespace appears.

- If Portworx is installed successfully, all pods show Running.

-
Alternatively, you can verify Portworx pod status using the command line.

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

-
(Optional) If you configured Workload Identity authentication, perform the following additional checks:

-
Verify that Portworx Operator added the IRSA annotation on the `portworx` service account:

```

kubectl -n <px-namespace> get sa portworx -o yaml

```

The output should include the following annotation, where the value matches the ARN of the IAM role you created in Configure authentication:

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

## Verify Portworx pool status​

Run the following command to view the Portworx drive configuration for your pod:

```

oc exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl service pool show

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

The output `Type: PX-StoreV2` indicates that the pod uses the PX-StoreV2 datastore.

## Verify pxctl cluster provision status​

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

The status must be `Online`.

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

The nodes must be `Online`.

-
Verify the Portworx cluster provision status by running the following command. Specify the pod name you retrieved in Verify Portworx pod status.

```

oc exec <px-pod> -n <px-namespace> -- /opt/pwx/bin/pxctl cluster provision-status

```

```

NODE                                NODE STATUS  POOL                                   POOL STATUS  IO_PRIORITY  SIZE   AVAILABLE  USED   PROVISIONED  ZONE    REGION  RACK

0c99e1f2-9d49-xxxx-xxxx-xxxxxxxxxxxx Up           0 ( 8ec9e6aa-7726-xxxx-xxxx-xxxxxxxxxxxx ) Online         HIGH         32 GiB 32 GiB      33 MiB 0 B          default default default

1e89102f-0510-xxxx-xxxx-xxxxxxxxxxxx Up           0 ( 06fcc73a-7e2f-xxxx-xxxx-xxxxxxxxxxxx ) Online         HIGH         32 GiB 32 GiB      33 MiB 0 B          default default default

24508311-e2fe-xxxx-xxxx-xxxxxxxxxxxx Up           0 ( 58ab2e3f-a22e-xxxx-xxxx-xxxxxxxxxxxx ) Online         HIGH         32 GiB 32 GiB      33 MiB 0 B          default default default

```

## What to do next​

Create a PVC. For more information, see Create your first PVC.

In this topic:
