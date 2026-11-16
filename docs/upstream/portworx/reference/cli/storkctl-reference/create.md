# storkctl create

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/storkctl-reference/create (Portworx Enterprise latest)

storkctl create | Portworx Enterprise Documentation

Create stork resources

Example: `storkctl create <resource> <flags>`

note

The following commands support a set of global flags that can be used across all `storkctl` commands. For details, see the Global Flags section.

## storkctl create applicationclones​

Start an applicationClone

Aliases: `applicationclone`, `clone`, `clones`

Example: `storkctl create applicationclone <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--destinationNamespace``string`The namespace to where the applications should be cloned-Optional

`--postExecRule``string`Rule to run after executing applicationclone-Optional

`--preExecRule``string`Rule to run before executing applicationclone-Optional

`--replacePolicy`, `-r``string`Policy to use if resources being cloned already exist in destination namespace (Retain or Delete).`Retain`Optional

`--sourceNamespace``string`The namespace from where applications should be cloned-Optional

`--wait``bool`Wait for applicationclone to complete`false`Optional

## storkctl create clusterpair​

Create ClusterPair on source and destination cluster

Example: `storkctl create clusterpair <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--annotations``stringToString`Add required annotations to the resource in comma-separated key value pairs. key1=value1,key2=value2,...`[]`Optional

`--azure-account-key``string`Account key for Azure-Optional

`--azure-account-name``string`Account name for Azure-Optional

`--bucket``string`Bucket name-Optional

`--dest-ep``string`(Optional)Endpoint of portworx-api service in destination cluster-Optional

`--dest-kube-file``string`Path to the kubeconfig of destination cluster-Yes

`--dest-token``string`(Optional)Destination cluster token for cluster pairing-Optional

`--disable-ssl``bool`Set to true to disable ssl when using S3`false`Optional

`--encryption-key``string`Encryption key for encrypting the data stored in the objectstore.-Optional

`--google-key-file-path``string`Json key file path for Google-Optional

`--google-project-id``string`Project ID for Google-Optional

`--mode``string`Mode of DR. [async-dr, sync-dr, migration]`async-dr`Optional

`--nfs-export-path``string`mount path exported by the NFS server-Optional

`--nfs-mount-opts``string`optional NFS mount options-Optional

`--nfs-server``string`NFS server address-Optional

`--nfs-sub-path``string`sub-path to use in mount-Optional

`--nfs-timeout-seconds``int`optional nfs IO timeout in seconds (Valid Range: [1 30]) (default 5)`5`Optional

`--project-mappings``string`Project mappings between source and destination clusters (currently supported only for Rancher).
Use comma-separated <source-project-id>=<dest-project-id> pairs.
For the project-id, you can also have a cluster-id field added as a prefix to the project-id.
It is recommended to include both one-to-one mappings of the project-id and Rancher cluster-id prefixed project-id as follows:
<source-project-id>=<dest-project-id>,<source-cluster-id>:<source-project-id>=<dest-cluster-id>:<dest-project-id>-Optional

`--provider`, `-p``string`External objectstore provider name. [s3, azure, google, nfs]-Yes

`--s3-access-key``string`Access Key for S3-Optional

`--s3-endpoint``string`EndPoint for S3-Optional

`--s3-region``string`Region for S3-Optional

`--s3-secret-key``string`Secret Key for S3-Optional

`--s3-storage-class``string`Storage Class for S3-Optional

`--skip-validation``bool`Skip validation of objectstorelocation credentials`false`Optional

`--src-ep``string`(Optional)Endpoint of portworx-api service in source cluster-Optional

`--src-kube-file``string`Path to the kubeconfig of source cluster-Yes

`--src-token``string`(Optional)Source cluster token for cluster pairing-Optional

`--unidirectional`, `-u``bool`(Optional) to create Clusterpair from source -> dest only`false`Optional

`--use-existing-objectstorelocation``string`(Optional) Objectstorelocation with the provided name should be present in both source and destination cluster-Optional

`--use-workload-identity``bool`Use cloud provider workload identity for objectstore authentication instead of static credentials (supported for s3, azure, google)`false`Optional

## storkctl create groupsnapshots​

Create a group volume snapshot

Aliases: `groupsnapshot`

Example: `storkctl create groupsnapshot <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--maxRetries``int`Number of times to retry the groupvolumesnapshot on failure`0`Optional

`--opts``stringSlice`Comma-separated list of options to provide to the storage driver. These are in the format key1=value1,key2=value2. e.g portworx/snapshot-type=cloud`[]`Optional

`--postExecRule``string`Rule to run after triggering group volume snapshot-Optional

`--preExecRule``string`Rule to run before triggering group volume snapshot-Optional

`--pvcSelectors``stringSlice`Comma-separated list of PVC selectors in the format key1=value1,key2=value2. e.g app=mysql,tier=db`[]`Yes

`--restoreNamespaces``stringSlice`List of namespaces to which the snapshots can be restored to`[]`Optional

## storkctl create migrations​

Start a migration

Aliases: `migration`

Example: `storkctl create migration <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--admin-cluster-pair``string`Specify the name of the admin ClusterPair (in the admin/kube-system namespace). If provided, it takes precedence over --clusterPair and may be used alone.-Optional

`--annotations``stringToString`Add required annotations to the resource in comma-separated key value pairs. key1=value1,key2=value2,...`[]`Optional

`--clusterPair`, `-c``string`ClusterPair name for migration. If omitted, you must specify --admin-cluster-pair.-Optional

`--dry-run``bool`Validate migration params before starting migration`false`Optional

`--enforce-primary-kind``string`Workload-class mode: "" (legacy), "true" (primaries-only), "false" (non-primaries-only).-Optional

`--file`, `-f``string`file to run migration-Optional

`--include-names``stringSlice`Comma-separated primary names. Mutually exclusive with --selectors / --exclude-selectors.`[]`Optional

`--includeResources`, `-r``bool`Include resources in the migration`true`Optional

`--includeVolumes``bool`Include volumees in the migration`true`Optional

`--namespaces``stringSlice`Comma separated list of namespaces to migrate`[]`Yes

`--postExecRule``string`Rule to run after executing migration-Optional

`--preExecRule``string`Rule to run before executing migration-Optional

`--preview``bool`Preview resources that will be migrated`false`Optional

`--previewFile``string`file where migration preview will be saved-Optional

`--primary-kind``string`Canonical group/version/kind for a primary (e.g. kubevirt.io/v1/VirtualMachine). Required when --enforce-primary-kind=true.-Optional

`--startApplications`, `-a``bool`Start applications on the destination cluster after migration`true`Optional

`--wait``bool`Wait for migration to complete`false`Optional

## storkctl create migrationschedules​

Create a migration schedule

Aliases: `migrationschedule`

Example: `storkctl create migrationschedule <name> <flags> -n <migrationschedule-namespace>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--admin-cluster-pair``string`Specify the name of the admin ClusterPair (in the admin/kube-system namespace). If provided, it takes precedence over --cluster-pair and may be used alone.-Optional

`--annotations``stringToString`Add required annotations to the resource in comma-separated key value pairs. key1=value1,key2=value2,...`[]`Optional

`--cluster-pair`, `-c``string`Specify the name of the ClusterPair in the same namespace to be used for the migration. If omitted, you must specify --admin-cluster-pair.-Optional

`--disable-auto-suspend``bool`Prevent automatic suspension of DR migration schedules on the source cluster in case of a disaster`false`Optional

`--disable-skip-deleted-namespaces``bool`If present, Stork will fail the migration when it encounters a namespace that is deleted but specified in the namespaces field. By default, Stork ignores deleted namespaces during migration`false`Optional

`--enforce-primary-kind``string`Workload-class mode: "" (legacy), "true" (primaries-only), "false" (non-primaries-only).-Optional

`--exclude-resource-types``stringSlice`Comma-separated list of the specific resource types which need to be excluded from migration, ex: Deployment,PersistentVolumeClaim`[]`Optional

`--exclude-resources``bool`If present, Kubernetes resources will not be migrated`false`Optional

`--exclude-selectors``stringToString`Resources with the provided labels will be excluded from the migration. All the labels provided in this option will be OR'ed`[]`Optional

`--exclude-volumes``bool`If present, the underlying Portworx volumes will not be migrated. This is the only allowed and default behaviour in sync-dr use-cases or when storage options are not provided in the cluster pair`false`Optional

`--ignore-owner-references-check``bool`If set, resources with ownerReferences will also be migrated, even if the corresponding owners are getting migrated`false`Optional

`--include-jobs``bool`Set this flag to ensure that K8s Job resources are migrated. By default, the Job resources are not migrated`false`Optional

`--include-names``stringSlice`Comma-separated primary names. Mutually exclusive with --selectors / --exclude-selectors.`[]`Optional

`--include-network-policy-with-cidr``bool`If set, the underlying network policies will be migrated even if a fixed CIDR is present on them`false`Optional

`--interval`, `-i``int`Specify the time interval, in minutes, at which Stork should trigger migrations`30`Optional

`--namespace-selectors``stringToString`Resources in the namespaces with the specified namespace labels will be migrated. All the labels provided in this option will be OR'ed`[]`Optional

`--namespaces``stringSlice`Specify the comma-separated list of namespaces to be included in the migration`[]`Yes

`--post-exec-rule``string`Specify the name of the rule to be executed after every migration is triggered-Optional

`--pre-exec-rule``string`Specify the name of the rule to be executed before every migration is triggered-Optional

`--preview``bool`Preview resources that will be migrated`false`Optional

`--preview-file``string`file where migration preview will be saved-Optional

`--primary-kind``string`Canonical group/version/kind for a primary (e.g. kubevirt.io/v1/VirtualMachine). Required when --enforce-primary-kind=true.-Optional

`--purge-deleted-resources``bool`Set this flag to automatically delete Kubernetes resources in the target cluster when they are removed from the source cluster`false`Optional

`--schedule-policy-name`, `-s``string`Name of the schedule policy to use. If you want to create a new interval policy, use the --interval flag instead`default-migration-policy`Optional

`--selectors``stringToString`Only resources that have all of the provided labels will be migrated (the labels are AND'ed). This is a key=value map, so the same label key cannot be provided with multiple values`[]`Optional

`--skip-service-update``bool`If set, service objects will be skipped during migration`false`Optional

`--start-applications`, `-a``bool`If present, the applications will be scaled up on the target cluster after a successful migration`false`Optional

`--suspend``bool`Flag to denote whether schedule should be suspended on creation`false`Optional

`--transform-spec``string`Specify the ResourceTransformation spec to be applied during migration-Optional

## storkctl create persistentvolumeclaims​

Create persistent volume claims (PVCs) from snapshots

Aliases: `persistentvolumeclaim`, `volume`, `pvc`

Example: `storkctl create pvc <pvc-name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--acccess-mode`, `-a``string`Access mode for the new PVC`ReadWriteOnce`Optional

`--size``string`Size for the new PVC (example 2Gi)-Yes

`--snapshot`, `-s``string`Name of the snapshot to use to create the PVC-Yes

`--source-ns``string`The source namespace if the snapshot was created in a different namespace-Optional

## storkctl create schedulepolicy​

Create schedule policy

Aliases: `sp`

Example: `storkctl create schedulepolicy <name>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--date-of-month``int`Specify the date of the month when Stork should trigger the operation.`1`Optional

`--day-of-week``string`Specify the day of the week when Stork should trigger the operation. You can use both the abbreviated or the full name of the day of the week.`Sunday`Optional

`--force-full-snapshot-day``string`For daily scheduled backup operations, specify on which day to trigger a full backup.`Monday`Optional

`--interval-minutes`, `-i``int`Specify the interval, in minutes, after which Stork should trigger the operation.`30`Optional

`--policy-type`, `-t``string`Select Type of schedule policy to apply. Interval / Daily / Weekly / Monthly.`Interval`Optional

`--retain``int`For backup operations,specify how many backups triggered as part of this schedule should be retained.`0`Optional

`--time``string`Specify the time of the day in the 12 hour AM/PM format, when Stork should trigger the operation.`12:00AM`Optional

## storkctl create volumesnapshotrestore​

Restore snapshot to source PVC

Aliases: `volumesnapshotrestores`, `snapshotrestore`, `snapshotrestore`, `snaprestore`, `snapsrestores`

Example: `storkctl create volumesnapshotrestore <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--groupsnapshot`, `-g``bool`True if snapshot is group, default false`false`Optional

`--snapname``string`Snapshot name to be restored-Optional

`--sourcenamepace``string`Namespace of snapshot`default`Optional

## storkctl create volumesnapshots​

Create snapshot resources

Aliases: `volumesnapshot`, `snapshots`, `snapshot`, `snap`

Example: `storkctl create volumesnapshot <snapshot-name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--annotations``stringToString`Add required annotations to the resource in comma-separated key value pairs. key1=value1,key2=value2,...`[]`Optional

`--pvc`, `-p``string`Name of the PVC which should be used to create a snapshot-Yes

## storkctl create volumesnapshotschedules​

Create a snapshot schedule

Aliases: `volumesnapshotschedule`, `snapshotschedule`, `snapshotschedules`

Example: `storkctl create volumesnapshotschedule <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--annotations``stringToString`Add required annotations to the resource in comma-separated key value pairs. key1=value1,key2=value2,...`[]`Optional

`--postExecRule``string`Rule to run after executing snapshot-Optional

`--preExecRule``string`Rule to run before executing snapshot-Optional

`--pvc`, `-p``string`Name of the PVC for which to create a snapshot schedule-Optional

`--reclaimPolicy``string`Reclaim policy for the created snapshots (Retain or Delete)`Retain`Optional

`--schedulePolicyName`, `-s``string`Name of the schedule policy to use-Yes

`--suspend``bool`Flag to denote whether schedule should be suspended on creation`false`Optional

`--volume-snapshot-class-name``string`Name of the VolumeSnapshotClass to use for CSI snapshots-Optional

In this topic:
