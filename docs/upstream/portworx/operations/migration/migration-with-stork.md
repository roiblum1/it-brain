# Migration with Stork

Source: https://docs.portworx.com/portworx-enterprise/operations/migration/migration-with-stork (Portworx Enterprise latest)

Migration with Stork | Portworx Enterprise Documentation

This topic describes how to migrate your Portworx volumes and your Kubernetes/OpenShift resources one time between clusters using Stork. If you want to set up disaster recovery instead, see Set up Disaster Recovery.

note

Migration from a cluster with PX-Security enabled to a cluster without PX-Security is not supported.

Starting with Stork 26.5.0, you can migrate applications and volumes from an unsecured cluster to a PX-Security enabled destination cluster. This is supported on both Kubernetes and OpenShift clusters. During migration, Stork detects whether PX-Security is enabled on the destination cluster and automatically retrieves the authentication information required to access the migrated volumes. No additional authentication configuration is required in the ClusterPair or the Migration specification.

The following collection of tasks describes how to migrate your applications and volumes using Stork:

- Create a ClusterPair object

- Start your migration

- Monitoring a migration

Ensure that all the prerequisites are met and then proceed to complete all the tasks to migrate your applications and volumes.

## Prerequisites​

Before you migrate with Stork, ensure that the following requirements are met on both the source and destination clusters:

- Secret store: A secret store is configured on both clusters. The secret store holds the credentials for the objectstore.

- Objectstore: An AWS S3-compatible objectstore, AWS S3, GCP Object Storage, or Azure Blob Storage is available.

- NFS storage: If you use NFS to migrate volume data, ensure Stork 24.4.0 or later is installed. The supported NFS version is limited to NFSv4.

- Network connectivity:

- Cluster API access: All worker nodes can reach the API endpoints on both clusters, for example, on port 6443 or 443. On Kubernetes, these are the Kubernetes API endpoints. On OpenShift 4 and later, these are the OpenShift API endpoints.

- Portworx ports: On Kubernetes, ports 9001-9020 are open so that Portworx worker nodes can communicate with each other. On OpenShift, ports 17001-17020 are open so that you can reach the Portworx API endpoints. For the ports specific to your environment, see the Network table on the Prerequisites page.

- Default StorageClass: At most one StorageClass object is configured as the default. Having multiple default StorageClasses causes PVC migrations to fail.

- Cloud environment: If you use a cloud provider, you have completed the destination cluster setup, for more information refer to cloud provider specific guides: EKS, GKE, AAD-enabled AKS, or OKE.

- Custom container images: On OpenShift, if you use custom container images, the images are available from a registry that both the source and destination clusters can access.

- `storkctl`: `storkctl` is installed on both clusters. Always use the latest `storkctl` binary by downloading it from the running Stork container.

### Prerequisites when migrating from an unsecured cluster to a PX-Security enabled cluster​

To migrate application and volumes from an unsecured cluster to PX-Security enabled cluster, ensure that the following additional requirements are met:

-
Stork version: Stork 26.5.0 or later is installed on the source cluster.

-
Kubernetes version: If you use in-tree Portworx volumes and the destination cluster runs Kubernetes 1.31 or later, the destination cluster must run at least Kubernetes 1.31.6, 1.32.2, or 1.33.0.

-
Guest access (recommended): Guest access is disabled on the destination cluster so that PX-Security enforces authentication for access to migrated volumes.

-
Destination cluster: Verify that the `px-user-token` secret exists on the PX-Security enabled destination cluster, by using the following command:

```

kubectl get secrets --all-namespaces --field-selector metadata.name=px-user-token

```

Verify that the output lists the `px-user-token` Secret. If the Secret is missing, Stork treats the destination cluster as unsecured and does not add the authentication information during migration. For more information, see Enable authorization in Portworx.

-
Kubeconfig access: The destination kubeconfig used to create the ClusterPair has permission to list Secrets across all namespaces.

note

-
The default admin namespace is `kube-system`. In all examples, `<migrationnamespace>` is the admin namespace that migrates all namespaces from your source cluster to the destination cluster. Alternatively, you can specify a non-admin namespace. In that case, Portworx migrates only that namespace. To learn how to set up an admin namespace, see Set up a Cluster Admin namespace for Migration.

-
Migration is not supported for FlashArray Direct Access and FlashBlade Direct Access volumes. Avoid configuring migration schedules for namespaces that contain these volumes.

## Create a ClusterPair object​

To migrate with Stork, you must first pair the two clusters so that Portworx can migrate data and resources between them. To do this, you create a trust object, called a ClusterPair object, on the source cluster. Portworx uses this object to establish a communication channel between the two clusters.

### Pair your clusters​

Use the `storkctl create clusterpair` command to create a unidirectional ClusterPair, with the command options for your environment as described in the following sections. A unidirectional ClusterPair establishes authentication from the source cluster to the destination cluster, so you can migrate resources and data in one direction.

The command creates the ClusterPair object on the source cluster, using the source kubeconfig file (`<source-kubeconfig-file>`) and the destination kubeconfig file (`<destination-kubeconfig-file>`) in the specified namespace (`<migrationnamespace>`). This object establishes and authenticates the connection between the two clusters for migrating resources and volumes within that namespace.

note

If you configured the `portworx-api` service to be accessible externally through ingresses or routes, add the following command options when you create the ClusterPair:

- `--dest-ep string`: Endpoint of the `portworx-api` service in the destination cluster.

- `--src-ep string`: Endpoint of the `portworx-api` service in the source cluster.

If you do not specify these endpoints, the storage status of the ClusterPair shows as `failed`.

#### Create a unidirectional ClusterPair​

Select the tab for your objectstore, and then run the command to create a unidirectional ClusterPair named `migration-cluster-pair`:

- Amazon S3 or S3 compatible

- Microsoft Azure

- GCP

- NFS

Run the following command:

```

storkctl create clusterpair migration-cluster-pair \

--namespace <migrationnamespace> \

--dest-kube-file <destination-kubeconfig-file> \

--src-kube-file <source-kubeconfig-file> \

--provider s3 \

--s3-endpoint s3.amazonaws.com \

--s3-access-key <s3-access-key> \

--s3-secret-key <s3-secret-key> \

--s3-region <s3-region> \

--mode migration \

--unidirectional

```

Portworx uses AWS S3 or S3-compatible object storage to migrate volume data between the two clusters. The credentials in the command authenticate you with your cloud platform. The access key, secret key, and region identify the S3 bucket that Portworx uses for the data transfer.

Run the following command:

```

storkctl create clusterpair migration-cluster-pair \

--namespace <migrationnamespace> \

--dest-kube-file <destination-kubeconfig-file> \

--src-kube-file <source-kubeconfig-file> \

--provider azure \

--azure-account-name <azure-account-name> \

--azure-account-key <azure-account-key> \

--mode migration \

--unidirectional

```

Portworx uses Azure Blob Storage to migrate volume data between the two clusters. The Azure credentials in the command authenticate you with Azure.

Run the following command:

```

storkctl create clusterpair migration-cluster-pair \

--namespace <migrationnamespace> \

--dest-kube-file <destination-kubeconfig-file> \

--src-kube-file <source-kubeconfig-file> \

--provider google \

--google-project-id <gcp-project-ID> \

--google-json-key <gcp-json-auth-key> \

--mode migration \

--unidirectional

```

Portworx uses Google Cloud Storage to migrate volume data between the two clusters. The Google Cloud credentials in the command authenticate you with Google Cloud.

Run the following command:

```

storkctl create clusterpair migration-cluster-pair \

  --src-kube-file </tmp/kubeconfig> \

  --dest-kube-file </tmp/kubeconfig2> \

  --provider nfs \

  --nfs-server <nfs-server-address> \

  --nfs-export-path <nfs-export-path> \

  --nfs-sub-path <nfs-sub-path> \

  --nfs-mount-opts <mount-options> \

  --nfs-timeout-seconds <timeout-seconds> \

  --unidirectional

```

The command uses the following parameters:

- `--provider nfs`: Specifies the provider as NFS.

- `--nfs-server`: Specifies the address of the NFS server (hostname or IP address).

- `--nfs-export-path`: Specifies the exported path on the NFS server.

- `--nfs-sub-path`: Specifies the subpath within the export path to use. If you do not specify a subpath, Portworx creates one automatically.

- `--nfs-mount-opts`: (Optional) Specifies NFS mount options, for example, `vers=4.0`.

- `--nfs-timeout-seconds`: (Optional) Specifies the NFS IO timeout in seconds (default is 5, valid range is 1-30).

Portworx uses the specified NFS storage to migrate volume data between the two clusters.

#### Verify the status of your unidirectional ClusterPair​

To check the status of the ClusterPair, run the following `storkctl` command, which lists the ClusterPairs in the namespace `<migrationnamespace>`:

```

storkctl get clusterpair -n <migrationnamespace>

```

The command displays the name and status of each ClusterPair in that namespace. For example, the output on the source cluster looks like this:

```

NAME                     STORAGE-STATUS  SCHEDULER-STATUS  CREATED

migration-cluster-pair   Ready           Ready             10 Mar 23 17:16 PST

```

After a successful pairing, both `STORAGE-STATUS` and `SCHEDULER-STATUS` show `Ready`.
 Encountered an error?

If you see an error, run the following command to get more information:

`kubectl describe clusterpair <your-clusterpair-name> -n <migrationnamespace>`

### Use Rancher Projects with ClusterPair​

If you use Rancher projects, follow the instructions in Use Rancher Projects with ClusterPair. Otherwise, skip to the next section.

## Start your migration​

After you configure the pairing, you can migrate applications to the destination cluster as many times as you need.

To start a migration, use the `storkctl create migration` command, or create a migration object and apply it manually.

You can also use `pre-exec` and `post-exec` rules to run custom actions before or after each migration. For more information, see Configure pre-exec and post-exec rules for Stork migrations.

If you migrate from an unsecured cluster to a destination cluster with PX-Security enabled, you do not need to add authentication annotations to the Migration specification or the MigrationSchedule specification. Stork checks whether PX-Security is enabled on the destination cluster, including during each scheduled migration, and handles the required authentication information automatically. For more information about scheduled migrations, see Schedule migrations.

note

Starting with Stork 25.5.0, you can use the admin ClusterPair to create migration schedules in any namespace instead of creating a local ClusterPair and referencing it in the migration schedule. For more information, see Use the admin ClusterPair for migrations in any namespace.

- Using storkctl

- Using CRD

To start the migration, run the `storkctl create migration` command with the required flags. For more information, see `storkctl create migration`.

note

If you created an admin ClusterPair, you can use it instead of a local ClusterPair. Use the `--admin-cluster-pair` flag instead of `--clusterPair`.

The following example creates a migration:

```

storkctl create migration <your-migration-object-name> \

  --clusterPair migration-cluster-pair \

  --namespaces <app-namespace1>,<app-namespace2> \

  --includeResources=true \

  --startApplications=true \

  --namespace <migrationNamespace>

```

### Preview resources before starting migration​

To check which resources a migration includes before you create it, use the `--preview` or `--previewFile` flag with the `storkctl create migration` command:

- Use `--preview` to display the resources that the migration includes, without starting it.

- Use `--previewFile <filename>` to save the preview output to a file.

The preview confirms which resources Portworx migrates, including non-namespaced resources such as `ClusterRole` and `ClusterRoleBinding`.

To migrate your cluster resources and volumes using a custom resource definition, complete the following steps.

### Define your migration object​

To define your migration object, paste the following Migration specification into a `migration.yaml` file:

note

If you created an admin ClusterPair, you can use it instead of a local ClusterPair. Use the `spec.adminClusterPair` field instead of `spec.clusterPair`.

```

apiVersion: stork.libopenstorage.org/v1alpha1

kind: Migration

metadata:

  name: <your-migration-object-name>

  namespace: <migrationnamespace>

spec:

  clusterPair: migration-cluster-pair

  includeResources: true

  startApplications: true

  namespaces:

  - <app-namespace1>

  - <app-namespace2>

  purgeDeletedResources: false

```

In the specification:

- `apiVersion`: Set to `stork.libopenstorage.org/v1alpha1`.

- `kind`: Set to `Migration`.

- `metadata.name`: The name of the object that performs the migration.

- `metadata.namespace`: The namespace in which you want to create the object.

- `spec.clusterPair`: The name of the ClusterPair object that you created in Pair your clusters.

- `spec.includeResources`: A boolean value that specifies whether the migration includes PVCs and other application specifications. If you set this field to `false`, Portworx migrates only your volumes.

- `spec.startApplications`: A boolean value that specifies whether Portworx automatically starts applications on the destination cluster. If you set this field to `false`, Portworx sets the replicas of the `Deployment` and `StatefulSet` objects on the destination cluster to zero. On the destination cluster, Portworx stores the number of replicas from the source cluster in the `stork.openstorage.org/migrationReplicas` annotation.

- `spec.namespaces`: The list of namespaces that you want to migrate.

- `spec.purgeDeletedResources`: A boolean value that specifies whether Stork automatically purges a resource from the destination cluster when you delete it from the source cluster. The default value is `false`.

### (Optional) Customize your migration​

You can customize your migration by specifying pre-exec and post-exec rules in your Migration specification. The pre-exec rule runs before the migration is triggered, and the post-exec rule runs after the migration is triggered.

If you use an admin namespace to migrate multiple namespaces and want to customize the migration with pre-exec or post-exec rules, create the rules in the admin namespace.

The following example shows how to specify the rules in your migration object:

```

apiVersion: stork.libopenstorage.org/v1alpha1

kind: Migration

metadata:

  name: <your-migration-object-name>

  namespace: <migrationnamespace>

spec:

  clusterPair: migration-cluster-pair

  includeResources: true

  startApplications: true

  preExecRule: <your-pre-rule>

  postExecRule: <your-post-rule>

  namespaces:

  - <app-namespace1>

  - <app-namespace2>

  purgeDeletedResources: false

```

If the rules do not exist, you see an event and the migration stops.

The following behavior applies when a rule fails:

- PreExec rule failure: If the PreExec rule fails for any reason, Stork logs an event against the object and retries. Stork does not mark the migration as failed.

- PostExec rule failure: If the PostExec rule fails for any reason, Stork logs an event and marks the migration as failed. Stork also tries to cancel the migration that the underlying storage driver started.

### Apply the specification​

To start the migration, apply the Migration specification:

- Kubernetes

- OpenShift

```

kubectl apply -f migration.yaml

```

```

oc apply -f migration.yaml

```

## Monitoring a migration​

After you start the migration, check its status using `storkctl`:

```

storkctl get migration -n <migrationnamespace>

```

The following example shows the output when the migration is first triggered:

```

NAME                                            CLUSTERPAIR              STAGE     STATUS       VOLUMES   RESOURCES   CREATED

<your-migration-object-name>-2022-12-12-200210  migration-cluster-pair   Volumes   InProgress   0/3       0/0         12 Dec 22 11:45 PST

```

If the migration succeeds, the `STAGE` changes from `Volumes` to `Application` to `Final`.

The following example shows the output of a successful migration:

```

NAME                                             CLUSTERPAIR            STAGE   STATUS       VOLUMES   RESOURCES   CREATED               ELAPSED

<your-migration-object-name>-2022-12-12-200210   migration-cluster-pair Final   Successful   3/3       10/10       12 Dec 22 12:02 PST   1m23s

```

 Need to see more details?

If you see an error, or you want more details about your migration, run the following command:

`kubectl describe clusterpair <your-clusterpair-name> -n <migrationnamespace>`

If you migrated applications and volumes from an unsecured cluster to a destination cluster with PX-Security enabled, a migration status of `Successful` indicates that Stork created the objects on the destination. However, this status does not confirm that the migrated applications can successfully mount their volumes.

To verify that Stork added the authentication information to the migrated objects, run the following commands on the destination cluster. The `kubectl get pvc -n <application-namespace>` command shows the name of the PersistentVolume behind each claim.

For a CSI volume, verify that the secret reference is set:

```

kubectl get pv <pv-name> -o jsonpath='{.spec.csi.nodePublishSecretRef}'

```

For an in-tree volume, verify that the annotation is set:

```

kubectl get pv <pv-name> -o jsonpath='{.metadata.annotations.openstorage\.io/auth-secret-name}'

```

For a StorageClass that the migration created, verify that the authentication parameters are set:

```

kubectl get storageclass <storageclass-name> -o jsonpath='{.parameters}'

```

If you set `startApplications` to `true` in the Migration specification, also confirm that the application pods reach the `Running` state:

```

kubectl get pods -n <application-namespace>

```

If a pod stays in `ContainerCreating`, check the pod events for volume mount or authentication errors. For troubleshooting guidance, see Troubleshooting.

## Limitations​

Migration from a cluster with PX-Security enabled to a cluster without PX-Security is not supported. In addition, the following limitations apply when you migrate applications and volumes from an unsecured cluster to a cluster with PX-Security enabled:

-
Existing StorageClasses: Stork adds the required authentication parameters only to StorageClasses created during migration. If a StorageClass with the same name already exists on the destination cluster, Stork does not update it.

Kubernetes does not allow you to change the parameters of an existing StorageClass. To use the authentication parameters, recreate the StorageClass with the parameters, or create a new StorageClass that includes them. Otherwise, new PVCs that use the StorageClass might fail to authenticate. For more information, see PVCs and Stork with authorization.

-
Volumes migrated before enabling PX-Security: Volumes migrated to the destination cluster before PX-Security was enabled might fail to mount, even if the migration status is `Successful`. Contact Portworx Support (support@everpuredata.com) for assistance in this case.

## Troubleshooting​

If you migrate applications and volumes from an unsecured cluster to a cluster with PX-Security enabled and encounter issues, use the following table to identify the symptom and the action to take:

SymptomWhat to do

A pod stays in `ContainerCreating` with the error `Access denied without authentication token`Confirm that the source cluster runs Stork 26.5.0 or later and that the `px-user-token` Secret exists on the destination cluster. After you fix either, run the migration again and delete the pod so that Kubernetes recreates it. Running the migration again fixes in-tree volumes only. If the pod uses a CSI volume that already exists on the destination cluster, contact Portworx Support (support@everpuredata.com) for assistance.

A new PVC on the destination fails with `ProvisioningFailed` and `Access denied without authentication token`The StorageClass does not have the authentication parameters. This happens with StorageClasses that already existed on the destination cluster before the migration. For more information, see Existing StorageClasses limitation.

The Migration shows a `SecuredDestinationDetectionFailed` warningStork could not read Secrets on the destination. Check connectivity and that the destination kubeconfig can list Secrets in all namespaces, and then run the migration again.

In this topic:
