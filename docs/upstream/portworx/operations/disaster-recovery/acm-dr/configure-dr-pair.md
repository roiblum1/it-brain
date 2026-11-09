# Manage a Disaster Recovery Pair

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/acm-dr/configure-dr-pair (Portworx Enterprise latest)

Manage a Disaster Recovery Pair | Portworx Enterprise Documentation

This topic explains how to create, update, and delete a disaster recovery (DR) pair by using the OpenShift console.

important

Only one DR pair can exist between the same source and destination clusters for a specific backup location. For example, if a pair already exists between cluster A and cluster B, you cannot create another A-to-B pair. However, you can create pairs between A and C or A and D.

## Prerequisites​

Ensure that your environment meets the prerequisites for ACM-based DR.

## Create a DR pair​

To create a DR pair, complete the following steps:

- Sign in to the OpenShift web console.

- Switch to the multicluster management view (All Clusters on OpenShift 4.18 and 4.19, or Fleet management on 4.20 and later), and from the left navigation pane, select the Portworx option.

- Select Disaster Recovery Pairs.
 The system displays the Disaster Recovery Pairs page that lists all existing DR pairs.

- Click Create Disaster Recovery Pair.
The system displays the Create a Disaster Recovery Pair window.

- In the Basic Information page of the Create a Disaster Recovery Pair window, do the following:

- In the Disaster Recovery Pair Name field, enter a name for the DR pair.

- In the Disaster Recovery Type section, select Asynchronous.

- In the Pair Type section, select Unidirectional or Bidirectional.

- Click Next.

- In the Select Clusters page that opens, do the following:

- From the Primary Cluster (Source) dropdown, select the source cluster.
 The Cluster capacity section displays the cluster's total and available capacity.

- From the Disaster Recovery Cluster (Destination) dropdown, select the destination cluster.
 The Cluster capacity section displays the cluster's total and available capacity.

- Click Next.

- In the Backup Location page that opens, do the following:

- From the Type dropdown, select the type of the backup location.
The available options are AWS S3, Azure Storage, Google Cloud Storage, and NFS.

- Based on the type of the backup location, enter the following information:

- AWS S3

- Azure Storage

- Google Cloud Storage

- Network File System (NFS)

- In the Storage Location section, enter the following information to configure the AWS S3 bucket that stores backup data:

- Bucket Name: Enter the name of the bucket where Portworx stores data.

- Region: Enter the region where the bucket resides.

- Endpoint: Enter the S3 endpoint based on your storage type:

- For AWS S3, enter only the hostname without a protocol prefix. For example, `s3.amazonaws.com`.

- For S3-compatible storage such as MinIO, enter the complete URL including the protocol. For example, `https://minio.portworx.com`.

- In the Authentication section, configure the authentication settings:

- Use IAM role for authentication: Toggle the option to enable or disable IAM authentication.
When enabled, Portworx uses the IAM role associated with the cluster or nodes instead of access keys.

note

If IAM role authentication is enabled, Portworx uses the assigned IAM permissions to access the bucket. Ensure that the IAM role has the required permissions for backup and snapshot operations.

- Access Key: Enter the access key for the storage account when IAM authentication is disabled.

- Secret Key: Enter the secret access key associated with the access key.

- In the Advanced Settings section, configure the optional storage and encryption parameters:

- Encryption Key: Enter the encryption key used to encrypt data stored in the bucket, if required by your environment.

- S3 Storage Class: Specify the storage class to use for uploaded objects.
Examples include STANDARD, STANDARD_IA, ONEZONE_IA, or storage classes supported by your S3-compatible provider.

- Server-side Encryption: From the dropdown menu, select the server-side encryption method to apply to objects stored in the bucket.

- SSL: Enables encrypted communication between Portworx and the storage endpoint. Disable this option only if the endpoint does not support SSL/TLS.

- In the Storage Location section, enter the following information to configure the Azure Storage container that stores backup data:

- Container Name: Enter the name of the Azure Blob Storage container where backups are stored.

- In the Authentication section, configure the authentication settings:

- Storage Account Name: Enter the name of the Azure Storage account that contains the backup container.

- Storage Account Key: Enter the access key for the Azure Storage account.

- In the Advanced Settings section, provide additional Azure configuration details when required:

- Environment: Enter the Azure cloud environment.

- Resource Group Name: Enter the name of the Azure resource group associated with the storage account.

- Tenant ID: Enter the Microsoft Entra tenant ID used for authentication.

- Client ID: Enter the application (service principal) client ID.

- Subscription ID: Enter the Azure subscription ID associated with the storage account.

- In the Storage Location section, enter the following information to configure the Google Cloud Storage bucket that stores backup data:

- Bucket Name: Enter the name of the Google Cloud Storage bucket where backups and replicated data will be stored.

- In the Authentication section, configure the authentication settings:

- Project ID: Enter the Google Cloud project ID associated with the storage bucket.

- Account Key: Paste the JSON service account key for a service account that has the required permissions to access the bucket.

- In the Storage Location section, enter the following information to configure the NFS server that stores replicated data:

- NFS Server Address: Enter the IP address or hostname of the NFS server.

- NFS Sub Path: Enter the directory path on the NFS export that Portworx uses to store backup and replication data.

- In the Connection Settings section, configure the following:

- Timeout in Seconds: Specifies the maximum time the system waits for a response from the NFS server before timing out. Increase this value for higher-latency environments.

- In the Advanced Settings section, provide additional NFS configuration details when required:

- NFS Mount Options: Enter any mount options required for the NFS share.

- NFS Export Path: Enter the full export path configured on the NFS server. This path must be accessible from all participating clusters.

- Click Next.

- In the Review page that opens, do the following:

- Review the DR pair configuration details.

- Click Create Disaster Recovery Pair.
The system creates the DR pair and displays the Disaster Recovery Pairs page that lists the DR pair.

After the DR pair is created, you can create a protection group to begin replicating namespaces between the paired clusters.

important

When you create a DR pair, the Portworx MultiCluster Operator automatically discovers the endpoints where the Portworx API is reachable on the source and destination clusters. If the clusters cannot connect to each other directly, this automatic discovery does not succeed. In this case, override the endpoint discovery by adding the following annotations to the `DisasterRecoveryPair` resource. These annotations specify the endpoints where the Portworx API is reachable, along with the authentication token for each cluster.

AnnotationDescription

`multicluster.purestorage.com/source-endpoint`Specifies the endpoint where the Portworx API is reachable on the source cluster.

`multicluster.purestorage.com/destination-endpoint`Specifies the endpoint where the Portworx API is reachable on the destination cluster.

`multicluster.purestorage.com/source-token`Specifies the authentication token for the Portworx API on the source cluster.

`multicluster.purestorage.com/destination-token`Specifies the authentication token for the Portworx API on the destination cluster.

The following example shows these annotations on a `DisasterRecoveryPair` resource:

```

metadata:

  annotations:

    multicluster.purestorage.com/source-endpoint: "<source-portworx-api-endpoint>"

    multicluster.purestorage.com/destination-endpoint: "<destination-portworx-api-endpoint>"

    multicluster.purestorage.com/source-token: "<source-portworx-api-token>"

    multicluster.purestorage.com/destination-token: "<destination-portworx-api-token>"

```

When you set these annotations, the operator uses the specified endpoints and tokens instead of the automatically discovered values.

note

If you remove all the connectivity override annotations from the `DisasterRecoveryPair`, the operator does not reconcile the underlying `ClusterPair` resources, and the clusters continue to use the previously configured endpoints and tokens. To change the connectivity configuration, update the annotation values instead of removing them.

## Update a DR pair​

To update a DR pair, complete the following steps:

note

You can update only the account key and the associated secret used to authenticate with the backup location.

- Sign in to the OpenShift web console.

- Switch to the multicluster management view, and from the left navigation pane, select the Portworx option.

- Select Disaster Recovery Pairs.
 The system displays the Disaster Recovery Pairs page that lists all existing DR pairs.

- From the DR pair that you want to update, click the vertical ellipsis menu and select Edit.

- On the Edit Disaster Recovery Pair page that opens, update the account key and click Update Disaster Recovery Pair.
The system updates the DR pair.

## Delete a DR pair​

To delete a DR pair, complete the following steps:

note

You cannot delete a DR pair if one or more protection groups use it.

- Sign in to the OpenShift web console.

- Switch to the multicluster management view, and from the left navigation pane, select the Portworx option.

- Select Disaster Recovery Pairs.
 The system displays the Disaster Recovery Pairs page that lists all existing DR pairs.

- Click the vertical ellipsis menu associated with the DR pair to delete, and select Remove Disaster Recovery Pair.

- Confirm the deletion by clicking Remove Disaster Recovery Pair.
The system deletes the DR pair.

In this topic:
