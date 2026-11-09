# DisasterRecoveryPair CRD reference

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/acm-dr/crd-reference/disaster-recovery-pair (Portworx Enterprise latest)

DisasterRecoveryPair CRD reference | Portworx Enterprise Documentation

The `DisasterRecoveryPair` CRD represents a DR relationship between clusters.

## Example​

```

apiVersion: multicluster.portworx.com/v1alpha1

kind: DisasterRecoveryPair

metadata:

  name: <dr-pair-name>

  namespace: <namespace>

spec:

  sourceCluster: <source-cluster-name>

  destinationCluster: <destination-cluster-name>

  disasterRecoveryType: ASYNC        # SYNC | ASYNC

  pairType: BI-DIRECTIONAL           # UNI-DIRECTIONAL | BI-DIRECTIONAL

  backupLocation:

    type: s3                         # s3 | azure | google | nfs

    s3Config:

      bucketName: <bucket-name>

      endpoint: <s3-endpoint>        # e.g. s3.amazonaws.com

      region: <region>              # e.g. us-east-1

      accessKeyID: <access-key-id>

      secretAccessKey: <secret-access-key>

```

## DisasterRecoveryPair​

FieldDescriptionType

`apiVersion`APIVersion defines the versioned schema of this representation of an object.
Servers should convert recognized schemas to the latest internal value, and
may reject unrecognized values.
More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources`string`

`kind`Kind is a string value representing the REST resource this object represents.
Servers may infer this from the endpoint the client submits requests to.
Cannot be updated.
In CamelCase.
More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds`string`

`spec`DisasterRecoveryPairSpec defines the desired state of DisasterRecoveryPair`object`

`status`DisasterRecoveryPairStatus stores the current status of the Disaster Recovery Pair`object`

### spec fields​

FieldDescriptionType

`spec.backupLocation`BackupLocation specifies the object storage configuration for disaster recovery replication;
defines where backup data and application manifests are stored for cross-cluster recovery operations.`object`

`spec.backupLocation.azureConfig`Azure Blob Storage backup location configuration for disaster recovery pair`object`

`spec.backupLocation.azureConfig.clientID`ClientID is the Azure service principal application/client ID;
optional; required only for Service Principal authentication used in Azure management operations
(object lock, immutability policies); pairs with ClientSecret and TenantID; not required for basic blob storage access.`string`

`spec.backupLocation.azureConfig.clientSecret`ClientSecret is the Azure service principal client secret (password);
optional; required only for Service Principal authentication used in Azure management operations
(object lock, immutability policies); pairs with ClientID and TenantID; not required for basic blob storage access using StorageAccountKey.`string`

`spec.backupLocation.azureConfig.containerName`ContainerName is the name of the storage location.
Stork will try to create the container if it does not exist.
Backup snapshot will be successful but won't be uploaded to storage location if container creation fails.`string`

`spec.backupLocation.azureConfig.environment`Environment specifies the Azure cloud environment type for blob storage;
defaults to empty (uses AzurePublicCloud);
supported values: "AzurePublicCloud" (default), "AzureChinaCloud".`string`

`spec.backupLocation.azureConfig.resourceGroupName`ResourceGroupName is the Azure resource group name where storage resources are located;
optional; used for resource organization and management operations.`string`

`spec.backupLocation.azureConfig.storageAccountKey`StorageAccountKey is the Azure Storage account access key for authentication;
pairs with StorageAccountName for credential-based blob storage access;
required for basic backup/restore operations when not using Service Principal.`string`

`spec.backupLocation.azureConfig.storageAccountName`StorageAccountName is the Azure Storage account name where the backup container is located;
required for accessing Azure Blob Storage; pairs with StorageAccountKey for credential-based authentication.`string`

`spec.backupLocation.azureConfig.subscriptionID`SubscriptionID is the Azure subscription ID where cluster resources are located;
optional; required only for Service Principal authentication used in Azure management operations
(object lock, immutability policies); not required for basic blob storage access.`string`

`spec.backupLocation.azureConfig.tenantID`TenantID is the Azure Active Directory (AAD) tenant ID;
optional; required only for Service Principal authentication used in Azure management operations
(object lock, immutability policies); not required for basic blob storage access.`string`

`spec.backupLocation.googleConfig`Google Cloud Storage backup location configuration for disaster recovery pair`object`

`spec.backupLocation.googleConfig.accountKey`AccountKey is the Google Cloud service account JSON key;
required for authentication to Google Cloud Storage;
contains the JWT credentials used to generate OAuth2 tokens for GCS access.`string`

`spec.backupLocation.googleConfig.bucketName`BucketName is the name of the storage bucket.
Stork will try to create the bucket if it does not exist.
Backup snapshot will be successful but won't be uploaded to storage location if bucket creation fails.`string`

`spec.backupLocation.googleConfig.projectID`ProjectID is the Google Cloud Platform (GCP) project ID;
required for creating GCS buckets and managing GCP compute snapshots;
used for both object storage operations and volume snapshot operations.`string`

`spec.backupLocation.nfsConfig`NFS backup location configuration for disaster recovery pair`object`

`spec.backupLocation.nfsConfig.exportPath`ExportPath is an optional sub-directory within the NFS export for organizing backups;
full NFS path: ServerAddress:SubPath/ExportPath;`string`

`spec.backupLocation.nfsConfig.ioTimeoutInSecs`IOTimeoutInSecs specifies the NFS I/O timeout in seconds (e.g., 24);
optional; used to configure timeout for NFS operations; stored in backup location configuration.`integer`

`spec.backupLocation.nfsConfig.mountOptions`MountOptions specifies NFS mount options (e.g., "--vers=4.0", "nfsvers=4.1");
optional; passed to the NFS PersistentVolume mount for controlling NFS protocol version and behavior.`string`

`spec.backupLocation.nfsConfig.serverAddress`ServerAddress is the NFS server address (hostname or IP);
required for NFS backup location; used to mount the NFS share for backup/restore operations.`string`

`spec.backupLocation.nfsConfig.subPath`SubPath is the export path on the NFS server (e.g., "/stork-nfs");
required; specifies the NFS export directory to mount for backup/restore operations.`string`

`spec.backupLocation.s3Config`AWS S3 backup location configuration for disaster recovery pair`object`

`spec.backupLocation.s3Config.accessKeyID`AccessKeyID is the AWS access key ID credential used for S3 authentication;
required when useIam is false or not set; ignored when useIam is true (uses EC2 instance IAM roles instead).`string`

`spec.backupLocation.s3Config.bucketName`BucketName is the S3 bucket name for the backup location.
Stork will try to create the bucket if it does not exist.
Backup snapshot will be successful but won't be uploaded to storage location if bucket creation fails.`string`

`spec.backupLocation.s3Config.disableSSL`DisableSSL when true, uses HTTP instead of HTTPS; defaults to false; set to true to use HTTP for S3-compatible stores without SSL enabled.`boolean`

`spec.backupLocation.s3Config.encryptionKey`EncryptionKey is used for client-side encryption of application resource manifests (Kubernetes YAMLs) before uploading to S3.`string`

`spec.backupLocation.s3Config.endpoint`Endpoint is the S3 API endpoint URL; required; for AWS S3, set to `s3.amazonaws.com` without a protocol prefix; for S3-compatible stores (MinIO, Ceph, etc.), include the protocol (for example, `https://minio.example.com`).`string`

`spec.backupLocation.s3Config.region`Region is the AWS region for the S3 bucket; required; set to appropriate AWS region (e.g., "us-east-1") or region for S3-compatible stores.`string`

`spec.backupLocation.s3Config.secretAccessKey`SecretAccessKey is the AWS secret access key credential that pairs with AccessKeyID for S3 authentication;
required when useIam is false or not set; ignored when useIam is true.`string`

`spec.backupLocation.s3Config.sse`SSE (Server Side Encryption) type for the S3 bucket; optional.`string`

`spec.backupLocation.s3Config.storageClass`StorageClass specifies the S3 storage class for uploaded objects (e.g., STANDARD, STANDARD_IA); defaults to empty (uses bucket default); Glacier classes not supported.`string`

`spec.backupLocation.s3Config.useIam`UseIam when true, uses the IAM role attached to the node where Stork pods run instead of AccessKeyID/SecretAccessKey; defaults to false.`boolean`

`spec.backupLocation.type`Type of backup location`string`

`spec.destinationCluster`DestinationCluster defines the destination cluster name`string`

`spec.disasterRecoveryType`DisasterRecoveryType defines the type of disaster recovery is desired`string`

`spec.pairType`PairType defines the type of cluster pairing is desired`string`

`spec.sourceCluster`SourceCluster defines the source cluster name`string`

### status fields​

FieldDescriptionType

`status.compliant`Compliant represents the compliance status of the disaster recovery pair.`object`

`status.compliant.reason`Reason is short description of why the resource is in non compliant state.`string`

`status.compliant.status`Status: is true then resource is compliant and operational.`boolean`

`status.conditions`Conditions represent the latest available observations of the DisasterRecoveryPair's state`array`

`status.conditions.lastTransitionTime`lastTransitionTime is the last time the condition transitioned from one status to another.
This should be when the underlying condition changed. If that is not known, then using the time when the API field changed is acceptable.`string`

`status.conditions.message`message is a human readable message indicating details about the transition.
This may be an empty string.`string`

`status.conditions.observedGeneration`observedGeneration represents the .metadata.generation that the condition was set based upon.
For instance, if .metadata.generation is currently 12, but the .status.conditions[x].observedGeneration is 9, the condition is out of date
with respect to the current state of the instance.`integer`

`status.conditions.reason`reason contains a programmatic identifier indicating the reason for the condition's last transition.
Producers of specific condition types may define expected values and meanings for this field,
and whether the values are considered a guaranteed API.
The value should be a CamelCase string.
This field may not be empty.`string`

`status.conditions.status`status of the condition, one of True, False, Unknown.`string`

`status.conditions.type`type of condition in CamelCase or in foo.example.com/CamelCase.`string`

`status.destinationCluster`Destination Clusters DisasterRecovery Pair status`object`

`status.destinationCluster.references`Cluster's DisasterRecovery Pair Created Object Details
Map of Kubernetes resource kind to array of object references in format: <uid>#<name>#<namespace>`object`

`status.destinationCluster.schedulerStatus`Status of the pairing with the scheduler`string`

`status.destinationCluster.storageStatus`Status of pairing with the storage driver`string`

`status.lastAgentUpdateTimestamp`LastAgentUpdateTimestamp is the time when the disaster recovery pair status was last updated by the agent`string`

`status.sourceCluster`Source Cluster's DisasterRecovery Pair status`object`

`status.sourceCluster.references`Cluster's DisasterRecovery Pair Created Object Details
Map of Kubernetes resource kind to array of object references in format: <uid>#<name>#<namespace>`object`

`status.sourceCluster.schedulerStatus`Status of the pairing with the scheduler`string`

`status.sourceCluster.storageStatus`Status of pairing with the storage driver`string`

In this topic:
