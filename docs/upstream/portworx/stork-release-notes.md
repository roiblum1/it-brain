# Portworx Stork Release Notes

Source: https://docs.portworx.com/portworx-enterprise/stork-release-notes (Portworx Enterprise latest)

Portworx Stork Release Notes | Portworx Enterprise Documentation

## 26.5.0​

November 12, 2026

This release addresses security vulnerabilities and provides new features and fixes:

### New Features​

-
Migrate applications and volumes from an unsecured to a secured Portworx cluster: Starting with Stork 26.5.0, you can migrate applications and volumes from a Portworx cluster without PX-Security enabled to a destination cluster with PX-Security enabled. For more information, see Migration with Stork.

-
Granular migration of KubeVirt VMs by name or label: Portworx Disaster Recovery now supports name-based selection of KubeVirt virtual machines (VMs), providing precise control over which VMs a schedule migrates. Stork automatically includes the resources that a selected VM depends on, such as its PVCs and DataVolumes, which removes the need to label each dependency.

To select VMs by name, use the new `--enforce-primary-kind`, `--primary-kind`, and `--include-names` flags. To add or remove VMs on an existing schedule without rewriting it, use the new `storkctl update migrationschedule` command with the `--add-names` and `--remove-names` flags. For more information, see Migrate specific VMs with a migration schedule.

### Improvements​

Improvement NumberImprovement Description

PWX-30984Application pods can now continue running on the same node during Portworx upgrades. You can configure this behavior by adding `disable-pod-failover:true` to the Stork arguments in the `spec.stork.args` field of the `StorageCluster` custom resource. When you configure this argument, Stork does not delete these pods or reschedule them to a different node during a Portworx upgrade.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-61496Stork stopped supporting directly created `ApplicationBackup`, `ApplicationRestore`, and `ApplicationBackupSchedule` objects in 26.4.1, and accepts these objects only when Portworx Backup creates them. However, `storkctl` still included commands that create these objects directly.

User Impact: An object that you created by using `storkctl` failed immediately with the reason `NotSupported`.

Resolution: The `storkctl` CLI no longer includes the commands that create, get, and delete application backups, application restores, and application backup schedules, or the commands that suspend and resume application backup schedules. Use Portworx Backup to create and manage these objects.

Affected Versions: 26.4.1 and laterMinor

PWX-59511Stork could schedule pods on a node that had already reached the Portworx limit of 1024 volume attachments (`LocalVolumeAttaches`).

User Impact: Pods and virtual machines (VMs) placed on such a node stayed in the `Scheduling` state, and volume mounts failed with the error `Licensed maximum reached for 'LocalVolumeAttaches' feature (allowed 1024, requested 1025)`.

Resolution: The Stork scheduler extender now filters out nodes where the existing Portworx attachments plus the new volumes of the pod would exceed the 1024 limit. Stork counts only external attachments, because Portworx does not count internal attachments toward this limit.

Affected Versions: All versionsMinor

PWX-57663An in-place restore of a FlashArray Direct Access (FADA) or FlashBlade Direct Access (FBDA) volume from a cloud snapshot ran for a while and then failed with a misleading backend error: `Volume name must be between 1 and 63 characters`.

User Impact: The restore failed after a delay, and the error did not tell you the actual cause, which is that in-place restore is not supported for these volumes.

Resolution: The in-place restore now fails immediately and returns a `not supported` message. To restore a FADA volume, restore the cloud snapshot to a new PVC.

Affected Versions: 25.4.1Minor

PWX-56934The warning that Stork logged when it failed to list resources did not include the resource type, namespace, or error.

User Impact: You could not easily tell why a migration failed to list resources, for example, when a permission was missing.

Resolution: The warning now includes the GroupVersionResource, namespace, and error.

Affected Versions: 26.1.0 and laterMinor

### Known issues (Errata)​

Issue NumberIssue DescriptionSeverity

PWX-63026After an OpenShift Virtualization storage-class migration, Stork does not create a `VolumeSnapshotSchedule` for the migrated PVCs. The OCP storage migration controller copies all source PVC annotations to the target PVC, including the `stork.libopenstorage.org/snapshot-schedule-created: "yes"` annotation that Stork sets when it creates a schedule. When Stork reconciles the migrated PVC, it reads this annotation and skips creating a new schedule, leaving the migrated PVC without snapshot protection even when the target StorageClass has a snapshot schedule policy configured.

Workaround: For each affected PVC, remove the annotation so that Stork creates a `VolumeSnapshotSchedule` on its next reconcile:

`kubectl annotate pvc <pvc-name> -n <namespace> stork.libopenstorage.org/snapshot-schedule-created-`

Affected versions: 26.5.0 and laterMinor

## 26.4.2​

September 29, 2026

This release addresses security vulnerabilities and provides new features and fixes:

### New Features​

-
Normalized and tunable scoring for scheduling pods: Stork now includes the `spec.stork.args.normalize-stork-scores` parameter, which is enabled by default to normalize hyperconvergence scores during pod scheduling. This normalization allows factors such as node load, CPU utilization, memory consumption, and other scheduling policy settings to influence the final score assigned to feasible nodes.

You can further tune the normalized hyperconvergence scoring using the newly added `spec.stork.args.replica-score`, `spec.stork.args.rack-score`, `spec.stork.args.zone-score`, `spec.stork.args.region-score`, and `spec.stork.args.remote-score` parameters. For more information, see Tuning hyperconvergence scoring.

Note: Portworx Operator 26.4 or later and Portworx Enterprise 3.6.2 or later are needed for this normalization and tunable scoring feature that is available with Stork 26.4.2.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-59101The Metro DR `witness-install.sh` script required the `btrfs` kernel module on the witness node even when the Metro cluster pair used PX-StoreV2, which doesn't need it.

User Impact: In air-gapped environments without the `btrfs` module, the script failed to install the witness node, even for PX-StoreV2 cluster pairs that don't require `btrfs`.

Resolution: The script now defaults to PX-StoreV2 and only requires `btrfs` when you pass `--store-version=px-storev1` for a PX-StoreV1 cluster pair. For more information, see Set up a witness node.

Affected Versions: All versionsMinor

## 26.4.1​

September 8, 2026

### New Features​

- FADA backup and restore on Portworx clusters with FA/FB driver enabled: Stork now enables Portworx Backup to back up and restore FADA (FlashArray Direct Access) volumes on Portworx Enterprise clusters configured with FA/FB driver enabled. Stork resolves backup requests issued by Portworx Backup from any node in the cluster, and provisions the restore destination PVC. This requires Stork 26.4.1, Portworx Enterprise 3.7.0 or later, and Portworx Backup 3.1.1. For prerequisites and behavior, see Backup and Restore FADA Volumes.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-57233The Stork leader pod deletes the cluster-scoped `stork-webhooks-cfg` MutatingWebhookConfiguration during shutdown, even though the surviving Stork replicas still need it to serve admission requests.

User Impact: During a routine drain of the node running the Stork leader, all pod admission mutations were interrupted for 15–40 seconds until a new leader was elected and recreated the configuration. In KubeVirt environments, this window could cause active live VM migrations to abort.

Resolution: Stork no longer deletes `stork-webhooks-cfg` on pod shutdown. For Operator-managed deployments, the Portworx Operator handles cleanup when Stork is disabled or uninstalled. For operator-less deployments, delete the `stork-webhooks-cfg` MutatingWebhookConfiguration and the `stork-webhook-secret` Secret manually after the Stork pods are removed.

Affected Versions: 26.4.0 and earlierMajor

PB-16693When restoring a RoleBinding whose subjects referenced ServiceAccounts from a namespace not included in the restore namespace mapping, those subjects were dropped from the restored RoleBinding.

User Impact: Restored RoleBindings were missing cross-namespace ServiceAccount subjects, breaking RBAC configurations that granted permissions to service accounts in other namespaces.

Resolution: Stork now preserves all `RoleBinding` subjects during restore. Subjects whose source namespace is included in the namespace mapping have their namespace replaced with the corresponding destination namespace; all other subjects are applied unchanged. Stork does not validate subjects in either case.

Affected Versions: All versionsMinor

## 26.4.0​

July 29, 2026

### New Features​

-
CSI VolumeSnapshot support for VolumeSnapshotSchedules: VolumeSnapshotSchedules for PVCs provisioned by the Portworx CSI driver (`pxd.portworx.com`) now automatically use CSI VolumeSnapshots (`snapshot.storage.k8s.io/v1`) instead of the legacy external-storage VolumeSnapshot API. PVCs on the in-tree Portworx driver continue to use the legacy path. For more information, see Associate a schedule policy using a CSI VolumeSnapshotClass.

-
Granular failover and failback by object name: The `storkctl perform failover` and `storkctl perform failback` commands now support name-based inclusion and exclusion of specific Kubernetes resources, providing precise control over which workloads are activated or deactivated during a DR operation. New flags available on both commands: `--include-objects` and `--exclude-objects`. For more information, see Failover an application and Failback an application.

-
Skip last-mile migration on failover/failback: A new `--skip-last-mile-migration` flag on `storkctl perform failover` and `storkctl perform failback` skips the last-mile migration before workloads are activated. For more information, see Failover an application and Failback an application.

-
Workload identity for ClusterPair authentication: The `storkctl create clusterpair` command now supports the `--use-workload-identity` flag, letting Stork authenticate with the backup location using your cloud provider's workload identity instead of static credentials. Supported only in Gardener clusters provisioned in Amazon Web Services (AWS), Azure, and Google Cloud Platform (GCP). For more information, see storkctl create clusterpair and Prerequisites for Asynchronous Disaster Recovery.

-
Forced full-backup cadence supported on CSI cloud snapshots: The Portworx CSI driver now reads `csi.openstorage.org/snapshot-incremental-count` from `VolumeSnapshotClass.Parameters` and propagates it to the full-backup frequency of the cloud backup request, forcing a full backup when the value is "0". This restores the legacy portworx.io/cloudsnap-incremental-count cadence control on the CSI snapshotter path. Supported values:

- Integer N >= 1 implies 1 full backup followed by N incremental backups per cycle.

- "0" implies every backup is a full backup.

- Absent implies cluster default value 7 as full backup frequency.

For more information, see Create a VolumeSnapshotClass.

### Improvements​

Improvement NumberImprovement Description

PWX-50016Stork's scheduler extender now serves a `/healthz` endpoint. Portworx Operator 26.2.0 and later configures readiness and liveness probes on the Stork deployment using this endpoint, so application pods using `schedulerName: stork-scheduler` no longer fall back to the default scheduler while Stork is restarting.

PWX-44985Creating a `MigrationSchedule` or `Migration` object using `storkctl` on a security-enabled cluster with guest access disabled no longer requires you to manually provide auth annotations. `storkctl` now automatically adds the `openstorage.io/auth-secret-name` and `openstorage.io/auth-secret-namespace` annotations, defaulting to `px-admin-token` and the target namespace, so migrations no longer fail with an `Access denied without authentication token` error.

## 26.3.1​

June 16, 2026

### Improvements​

Improvement NumberImprovement Description

PWX-54863Stork's scheduler extender now applies hyperconvergence-aware scoring (hyperconvergence or anti-hyperconvergence) for pods whose PVCs are sourced from VolumeSnapshots, PVC clones, or local snapshots when the StorageClass uses `volumeBindingMode: WaitForFirstConsumer`. This improves I/O locality and reduces east-west network traffic for workloads such as backup restore jobs that create PVCs from VolumeSnapshots.

## 26.3.0​

June 1, 2026

### New Features​

Stork log telemetry

Portworx Enterprise telemetry now supports collecting and uploading Stork logs to Pure1. These logs assist in troubleshooting and observability of Stork operations. For more information, see Enable Stork telemetry.

### Improvements​

Improvement NumberImprovement Description

PB-14672The BackupSync controller now uses origin markers for the ApplicationBackup and ApplicationRestore resources it creates, preventing unauthorized resource creation from bypassing Portworx Backup access controls.

## 26.2.0​

March 18, 2026

This release addresses security vulnerabilities and provides the following fixes:

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-51331Reverse migration of forklifted VMs to SUSE Virtualization cluster was not supported

User Impact: Incomplete disaster recovery cycle of forklifted VM workloads in SUSE Virtualization cluster.

Resolution: Reverse migration, failover, and failback have been validated for forklifted VMs in SUSE Virtualization cluster.

Affected Version: 26.1.0Minor

PWX-51522VM Pods using Portworx RAW Volumes after being live migrated might not end up in a hyperconverged setup

User Impact: The issue might lead to IO performance degradation.

Resolution: VMs with Portworx RAW volumes will be hyperconverged after live migration.

Affected Version: 26.1.0 and earlierMinor

## 26.1.0​

March 03, 2026

This release addresses security vulnerabilities and provides new features, improvements, and fixes:

### New Features​

-
Disaster Recovery support for SUSE Virtualization: Stork now supports disaster recovery (DR) for SUSE Virtualization with Portworx Enterprise 3.5.2 or later. This includes Asynchronous and Synchronous Disaster Recovery support. For more information, see SUSE Virtualization installation.

-
Selective resource filtering for failover and failback operations: The `storkctl` CLI now supports `--selectors`, `--exclude-selectors`, and `--resource-types` flags for greater control over resource filtering during failover and failback operations. For more information, see the storkctl perform.

### Improvements​

Improvement NumberImprovement Description

PWX-50808Added support for configuring the Stork log level using the `--log-level` flag. You can set the desired log level in the `spec.stork.args` field of the `StorageCluster` custom resource. For more information, see the StorageCluster – Stork Configuration.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-49064Stork cached and monitored only pods that were scheduled using the Stork scheduler. Pods that used Portworx volumes but were scheduled with the default Kubernetes scheduler were not included in the Stork cache and were not monitored by the Pod health monitoring workflow

User Impact: When Stork was unavailable and Pods were scheduled using the default Kubernetes scheduler, Pods that used Portworx volumes could become stuck on nodes in an `Unreachable` or `Unknown` state without being detected or cleaned up. This left the Pods and their associated storage attachments in a stale state, impacting application recovery and cluster health.

Resolution: Stork now caches and monitors all pods that use Portworx volumes, regardless of which scheduler was used. This ensures that the health monitoring workflow tracks all relevant pods, including those scheduled by the default Kubernetes scheduler.

Affected Version: All versions from 25.2.2 to 25.6.1Minor

PWX-49010Stork did not honor the include (`--selectors`) and exclude (`--exclude-selectors`) filters defined in MigrationSchedule during failover and failback.

User Impact: In DR scenarios, if you recreated a MigrationSchedule with selector filters to limit the migration scope, failover and failback still scaled up or scaled down all migrated resources in the namespace. This caused unintended applications to start on the destination cluster and stop on the source cluster.

Resolution: Stork now correctly applies the include and exclude selector filters defined in MigrationSchedule during failover and failback, ensuring that only the intended resources are migrated.

Affected Version: 25.6.0Minor

### Known issues (Errata)​

Issue NumberIssue Description

PWX-45435Migrations that complete within 10 seconds would have a field showing the value of total bytes that have been migrated set as 0 in the Migration specification, even after the data was migrated successfully.

Affected versions: 25.6.0 and later

## 25.6.1​

February 02, 2026

### New Features​

Load handling controls for CloudSnap

Delivers the ability to cap concurrent CloudSnaps per VM and the number of volumes per VM with active CloudSnap operations using safe, configurable defaults, so backup operations can run within system and environmental constraints without I/O or resource bottlenecks. The controls are set by default and configurable via standard mechanisms. For more information, see Configure CloudSnap load handling parameters.

## 25.6.0​

December 10, 2025

note

This release also addresses security vulnerabilities.

### Improvements​

Improvement NumberImprovement Description

PWX-46541Added new Prometheus metrics for monitoring disaster recovery (DR) operations, including migrations, migration schedules, failover and failback actions, and protected namespaces. Improved the existing metrics and introduced a new Portworx DR Grafana dashboard built on these metrics. For information about the dashboard, see Portworx DR dashboard. For the list of Stork metrics, see Portworx DR and Stork metrics.

## 25.5.0​

November 24, 2025

note

This release also addresses security vulnerabilities.

### New Features​

-
Admin ClusterPair supports migration of namespace-scoped resources: Stork now supports a cross-namespace disaster recovery (DR) capability that enables reuse of a centrally managed ClusterPair. Cluster administrators can define one secure DR connection in an admin namespace, while application teams manage MigrationSchedule objects and trigger failover or failback from their own namespaces by referencing the centralized ClusterPair.

This enhancement removes the previous constraint that ClusterPair, MigrationSchedule, and Migration objects must reside in the same namespace and avoids duplicating DR credentials across application namespaces.

-
A single admin-scoped AdminClusterPair object can now be referenced by namespaced DR resources (MigrationSchedule, Migration, and others). When specified, it takes precedence for all operations. For more information, see Set up an admin ClusterPair.

-
Existing specifications remain backward compatible. If an AdminClusterPair is not specified, behavior remains unchanged, and the local, same-namespace ClusterPair is used.

-
The `storkctl` CLI supports cross-namespace usage with the existing `--admin-cluster-pair` flag. For more information, see the storkctl create migrations and storkctl create migrationschedules.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-46543Previously, Stork failed a migration early if any single volume migration failed, leaving other volume migrations in progress.

User impact: In asynchronous DR scenarios, if a volume migration failed and a new migration was scheduled quickly, the previous incomplete migration could cause the new one to fail with a `Restore InProgress` error.

Resolution: Stork now waits for all volume migrations to finish before completing the migration, even if some fail.

Affected versions: 25.4.1 and earlierMinor

PB-12474Namespace label backup includes the namespace in the list even after the volume stage, which results in only PVC resources being included in the resource stage for the new namespace.

User impact: This causes the restore to fail because the volume backup did not happen for the newly included namespace.

Resolution: Update the namespace list only once during the start of the backup.

Affected versions: 25.4.1 and earlierMinor

PB-10321VM backups using the `filesystem-consistent Backup` method could incorrectly succeed without the `qemu-guest-agent` due to inconsistent behavior across Linux distributions.

User impact: On some Linux Distributions, this resulted in crash-consistent backups instead of filesystem-consistent backup.

Resolution: Stork now properly detects the absence of the guest agent and fails the backup as expected.

Affected versions: 25.4.1 and earlierMinor

## 25.4.1​

September 22, 2025

### Improvements​

Improvement NumberImprovement Description

PWX-46812Added the `--skip-validation` flag to the `storkctl create clusterpair` command to skip `ObjectStoreLocation` credential validation. For more information, see storkctl create clusterpair command reference.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-46831When creating a `ClusterPair` with the `portworx-api` Service of type `NodePort` and specifying the `--src-ep` and `--dest-ep` flags, `ObjectStoreLocation` validation failed.

User impact: `ClusterPair` creation failed, impacting the workflow to set up disaster recovery (DR).

Resolution: `ObjectStoreLocation` validation is now skipped if custom endpoints are specified in the `storkctl create clusterpair` command.

Affected versions: 25.4.0Minor

PWX-46943During `ClusterPair` creation in an OpenShift cluster with the `portworx-api` Service of type `LoadBalancer`, the step that fetched the Portworx cluster pairing token from the destination cluster failed.

User impact: `ClusterPair` creation failed, impacting the workflow to set up disaster recovery (DR).

Resolution: When creating a `ClusterPair` and the `portworx-api` Service is of type `LoadBalancer`, use the Service port instead of the `targetPort` from the Service specification.

Affected versions: 25.4.0Minor

## 25.4.0​

September 01, 2025

### Improvements​

Improvement NumberImprovement Description

PWX-39882Added a new `storkctl validate` command with the `backuplocation` subcommand to verify backup location credentials and connectivity using the Portworx API. You can now validate a backup location by running `storkctl validate backuplocation <name> -n <namespace>`. Replace `<name>` with the backup location name and `<namespace>` with its namespace. For more information, see storkctl validate command refence.

PWX-43926Added a user confirmation prompt when creating failover or failback if the last migration in the referenced `MigrationSchedule` is in `PartialSuccess`. This prompt can be bypassed using the new `--force` flag.

PWX-38076Added support for skipping only the source cluster domain deactivation during Synchronous (Metro) DR failover. Introduced a new custom resource field and the `--skip-source-cluster-domain-deactivation` flag in the `storkctl failover` command. This allows scaling down apps on the source without deactivating the source cluster domain. For more information, see the Controlled Failover tab in the Perform failover.

PWX-33029You can now improve pod startup performance by enabling Stork to set `fsGroupChangePolicy=OnRootMismatch` for pods that use `ReadWriteMany` or `ReadOnlyMany` volumes with `fsGroup` configured, by setting `spec.stork.args.enable-fsgroup-optimization` to `true` in the `StorageCluster` custom resource.

PWX-43928Stork now supports array indexing in ResourceTransformation paths to modify fields within specific elements of arrays. For example, to modify the image of the first container in a Pod object, use the path `spec.containers[0].image`. For more information, see ResourceTransformation.

PWX-44332Improved handling of pre-exec and post-exec rules for pods and virtual machines to minimize application freeze time while ensuring data consistency during disaster recovery (DR).

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-43835Failover failed for apps using the boolean `suspend` option when no value was provided.

User Impact: Failover operations failed due to parsing an empty string in the `suspend` field of app configurations.

Resolution: Failover logic now defaults empty `suspend` values to `true`, avoiding failures caused by invalid boolean parsing.

Affected Versions: 25.3.2 and earlierMinor

PWX-45513`ImageStreamTag` resources were not included in migrations, causing failures when associated with `ImageStream` resources.

User Impact: Migrations failed when apps used `ImageStream` resources that referenced `ImageStreamTag` resources that were not migrated.

Resolution: Stork now collects and migrates both `ImageStream` and `ImageStreamTag` resources on OpenShift.

Affected Versions: 25.3.2 and earlierMinor

PWX-45601KubeVirt virtual machine resources such as `VirtualMachine`, `DataVolume`, and associated `PersistentVolumeClaim` objects were re-created on the target cluster for each migration.

User Impact: These resources were redundantly re-created on every migration, even when unchanged, increasing migration time and resource usage.

Resolution: Fixed the hash check logic to prevent re-creation of KubeVirt resources when they have not changed since the last migration.

Affected Versions: 25.3.2 and earlierMinor

PWX-44830Reverse migrations were incorrectly marked as `PartialSuccess` when resources already existed at the source cluster.

User Impact: Migrations appeared partially successful when certain resources failed to apply because they were already present. This commonly occurred when operator-managed resources were created on the destination cluster before Stork attempted to migrate them, leading to confusion about the actual resource state.

Resolution: Stork now treats already existing resources on the destination as successfully migrated and excludes them from failure evaluation during reverse migration.

Affected Versions: 25.3.2 and earlierMinor

PWX-44535PVC creation failed on the destination cluster during asynchronous disaster recovery (DR) operations for forklifted virtual machines.

User Impact: These operations failed because PVCs owned by the virtual machine were not handled correctly during migration.

Resolution: Updated the DR workflow to support cases where the virtual machine is the owner of the PVCs.

Affected Versions: 25.3.2 and earlierMinor

PWX-44460Migration of forklifted Windows virtual machines failed because the associated `ControllerRevision` for `VirtualMachineClusterPreference` was not migrated to the destination cluster.

User Impact: Windows VMs failed to start after asynchronous DR.

Resolution: Stork now migrates the `ControllerRevision` associated with `VirtualMachineClusterPreference`, allowing Windows VMs to start successfully on the destination.

Affected Versions: 25.3.2 and earlierMinor

PWX-44593Unnecessary `GET` calls to PersistentVolumes were made when the `StorageClass` had no snapshot policy and the PVC lacked a `StorageClass` reference.

User Impact: Excessive `GET PV` calls could cause Kubernetes API throttling, leading to delays in backup operations.

Resolution: Stork now skips `GET PV` calls when the `StorageClass` does not define a snapshot policy.

Affected Versions: 25.3.2 and earlierMinor

PB-11551At scale, KDMP offload backups/restores hit PVC binding issues, as Kubernetes or the storage layer could not keep up with multiple and simultaneous volume claims, causing PVC bound timeouts.

User Impact: Users experienced backup/restore failures with PVC bound timeout issues.

Resolution: Fixed PVC bound timeouts that occurred during large-scale operations to ensure KDMP backups and restores complete successfully at scale.

Affected Versions: 25.3.2 and earlierMajor

PB-11723FADA volume backups used to fail during snapshot creation for CSI+Offload backups due to transient errors in FA environments with high IOPS.

User Impact: FADA volume backups used to fail, as a result user was unable to offload the CSI backup to the backup location.

Resolution: Stork ignores such transient errors and completes snapshot creation successfully and these backups are later uploaded to the chosen backup location.

Affected Versions: 25.3.2 and earlierMajor

PWX-45854The command executor Pod failed to run when the command targeted a specific container in a multi-container Pod object.

 User Impact: Rules with background actions failed to run during volume snapshots.

Resolution: Volume snapshots with rules targeting a specific container in a multi-container Pod object now run successfully.

Affected Versions: 25.3.2 and earlierMinor

PWX-45820When more than one Portworx SharedV4 volume is used by a KubeVirt VM, a race condition can occur between the termination of the CDI uploader pod and the startup of the VM’s `virt-launcher` pod. This can cause the root disk volume to remain attached to a node while the `virt-launcher` pod is being scheduled. If Kubernetes determines that this node is unsuitable for scheduling the pod, the pod starts on a different node, resulting in non-optimal scheduling. A VM scheduled this way may shut down unexpectedly during a future planned node maintenance event. This issue affects the VM only once and does not recur after it has been restarted.

Resolution: Fixed the race condition. VMs with multiple SharedV4 volumes now start correctly without suboptimal scheduling.

Affected Versions: 25.3.2 and earlierMinor

PWX-39881`ClusterPair` creation succeeds even when the object store `BackupLocation` credentials are invalid. As a result, users might assume that migrations will succeed. However, migrations later fail because Portworx cannot connect to the object store due to incorrect credentials or configuration.

Resolution: Added validation to `storkctl` to check `BackupLocation` credentials before creating a `ClusterPair`. If validation fails, the `ClusterPair` is not created. This validation is supported in Portworx version 3.4.0 and later.

Affected Versions: 25.3.2 and earlierMinor

PWX-42891If the webhook is enabled (which it is by default) and the user later disables it, the mutating webhook remains in the cluster.

User Impact: This may confuse users, as the webhook remains in the cluster even when it is disabled in the Portworx `StorageCluster` specification.

Resolution: The mutating webhook is now automatically removed when it is disabled in the Portworx `StorageCluster` specification.

Affected Versions: 25.3.2 and earlierMinor

PWX-44460Migration of forklifted Windows VMs to the destination was failing.

User Impact: Asynchronous disaster recovery (DR) for these forklifted Windows VMs fails.

Resolution: Migrating the `VirtualMachineClusterPreference` `ControllerRevision` to the destination ensures the VM starts successfully after migration.

Affected Versions: 25.3.2 and earlierMinor

### Known issues (Errata)​

Issue NumberIssue Description

PWX-46831When creating a `ClusterPair` that uses a `portworx-api` Service of type `NodePort` and includes the `--src-ep` and `--dest-ep` flags, `ObjectStoreLocation` validation fails. This causes `ClusterPair` creation to fail, which prevents disaster recovery (DR) setup.

Affected versions: 25.4.0

PWX-46943When creating a `ClusterPair` in an OpenShift cluster that uses a `portworx-api` Service of type `LoadBalancer`, the step to fetch the Portworx cluster pairing token from the destination cluster fails. This causes `ClusterPair` creation to fail, which prevents disaster recovery (DR) setup.

Affected versions: 25.4.0

## 25.3.2​

August 13, 2025

### Fixes​

Issue NumberIssue DescriptionSeverity

PB-11492Issue: When backing up Portworx volumes from a PX-Security enabled cluster with Stork version 25.3.1 or 25.3.0, PXB used to back up only the resources, leaving out the volumes.

User Impact: User was able to back up only Portworx volume resources but not volume data in the specified environment.

Resolution: Upgrade to Stork version 25.3.2 on your PX-Security enabled application cluster to ensure successful backups of Portworx volumes (and resources).

Affected Versions: 25.3.0, 25.3.1Major

## 25.3.1​

July 22, 2025

### Fixes​

Issue NumberIssue DescriptionSeverity

PB-11673Issue:
Case 1: Stork < 25.3.0
Deleting the associated StorageClass (SC) causes backups of FADA and FBDA volumes to fail. Without the SC, Stork can't identify the volume as FADA and incorrectly sends the snapshot request to PXE, (which does not support cloud snapshots), resulting in a partial success backup. Non-FADA volume backups succeed in this scenario.
Case 2: Stork = 25.3.0
FADA, FBDA, and PXE volume backups fail if SC is not present.

User Impact: User will experience backup failures of FADA, FBDA and/or PXE volumes if Stork version is 25.3.0 and below.

Resolution: Upgrade to Stork version 25.3.1 for your backups of PXE volumes (that are not FADA/FBDA) to succeed even if the corresponding SC is deleted.

Note: Stork 25.3.1 does not resolve failures that occur with FADA volumes lacking an associated SC. This issue will be resolved when PXE supports FADA volume backups.

Affected Versions: 25.3.0 and earlierMajor

### Known issues (Errata)​

Issue NumberIssue Description

PWX-45820When more than one Portworx SharedV4 volume is used by a KubeVirt VM, a race condition can occur between the termination of the CDI uploader pod and the startup of the VM’s `virt-launcher` pod. This can cause the root disk volume to remain attached to a node while the `virt-launcher` pod is being scheduled. If Kubernetes determines that this node is unsuitable for scheduling the pod, the pod starts on a different node, resulting in non-optimal scheduling. A VM scheduled this way may shut down unexpectedly during a future planned node maintenance event. This issue affects the VM only once and does not recur after it has been restarted.

Workaround: Restart the VM once after creation and after the uploader pod has terminated. This typically completes within a few minutes.

Components: SharedV4, KubeVirt
Affected Versions: All

## 25.3.0​

July 08, 2025

note

This release addresses security vulnerabilities.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-44567Live migration failed for virtual machines (VMs) with volumes that had device minor numbers greater than `255`.

User Impact: Operations such as Portworx upgrades failed when KubeVirt VMs were in use.

Resolution: Stork now correctly identifies Portworx devices with minor numbers greater than `255`, allowing live migration to succeed in these cases.

Affected Versions: 25.2.2 and earlierMinor

PWX-44456The webhook controller failed to find the PVC in the cache.

User Impact: This could result in a Stork panic in the mutating webhook path if PVC caching is delayed.

Resolution: Stork now handles missing PVCs in the cache by adding a nil check, allowing pod scheduling to proceed using the default scheduling path.

Affected Versions: 25.2.2, 25.2.1, and 25.2.0Minor

PWX-43584DataVolumes were not being migrated along with KubeVirt VirtualMachines.

User Impact: The OpenShift UI showed `DataVolumesReady=False` for the VirtualMachines on the destination cluster. Reverse migration was delayed when `storage.usePopulators` was enabled in the DataVolume.

Resolution: Stork now migrates DataVolumes and uses the DataVolume claim adoption utility to adopt PVCs created during migration, instead of creating new ones.

Affected Versions: 25.2.2 and earlierMinor

PB-11415Issue: When you initiate a KDMP backup with a large number of volumes with Offload option enabled, backup used to fail.

 User Impact: Such backups used to fail with time-out issue.

Resolution: KDMP backup with a large number of volumes with Offload option enabled succeeds without any hassles.

Affected versions: 25.2.2 and 25.2.1Minor

PB-11212Issue: During a CSI backup with offload to S3 and an NFS backup location, failure in backing up a single volume caused the entire backup to be marked as `Failed`, making it unusable for restore—even though snapshots of other volumes were successfully backed up. Also, this process left uncleaned snapshot copies.

User Impact: Backups with only a single failed volume were rendered completely unusable, preventing users from restoring any successful data.

Resolution: Such backups are now marked as `Partial Success`, allowing users to restore the successfully backed-up volumes. In addition, snapshot copies created during backup process are cleaned up.

Affected versions: 25.2.2 and earlierMinor

PB-11077Issue: When you trigger parallel scheduled backups for namespaces that contain secrets, PXB was also backing up its internal secrets and those associated with NFS backup jobs.

 User Impact: Unintended system-generated secrets were also getting backed up along with user-created secrets.

Resolution: PXB only backs up user-created secrets now.

Affected versions: 25.2.1Minor

PB-10584Issue: Backup uploads to the backup location were failing immediately upon encountering transient issues such as network interruptions or backup location unavailability, due to the absence of retry logic.

 User Impact: Users faced backup failures in situations where a retry might have resolved the issue, resulting in reduced reliability of the backup process.

Resolution: Stork has introduced configurable retry options for backup uploads using `DoRetryWithTimeout`. The retry behavior can be customized through the `stork-config` ConfigMap by setting `uploadMaxRetries` and `uploadRetryInterval`. Transient upload errors are now automatically retried based on these settings.

Affected versions: 25.2.2 and earlier

### Known issues (Errata)​

Issue NumberIssue DescriptionSeverity

PB-11551For backups that use CSI with offload and an NFS location, backups might fail with the error `PVC restore timed out after 30m0s`. This occurs because the binding job for WaitForFirstConsumer PVCs is created only in the SnapshotRestoreInProgress stage. In large-scale setups, delays in reaching this stage can cause the backup to time out.

Workaround: Disable the PVC watcher by setting `spec.stork.args.pvc-watcher` to `false` in the `StorageCluster` custom resource object.

Affected versions: 25.3.0Minor

## 25.2.2​

May 14, 2025

### Improvements​

Improvement NumberImprovement Description

PWX-42977Stork now reduces memory consumption by removing caching of:

- Pods not managed by Stork.

- Pod container specifications.

- PersistentVolumeClaim (PVC) resource requirements.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-43167When multiple `AppRegistration` (appreg) objects existed for the same CRD GVK, those with empty `suspendOptions` could overwrite valid configurations on others. This caused KubeVirt virtual machines (VMs) to fail to scale automatically during disaster recovery (DR) failover or failback.

User Impact: VMs did not scale down or up automatically during DR events, requiring manual intervention by operators.

Resolution: Stork now populates default `suspendOptions` only when missing, and only for supported GVKs. Existing custom settings are preserved, and unused GVKs are excluded from registration. This update also resolves a PVC migration race condition that previously led to recreated PVCs being incorrectly treated as errors.

Affected Versions: 25.2.1 and earlierMinor

### Known issues (Errata)​

Issue NumberIssue DescriptionSeverity

PWX-43584Stork currently does not support KubeVirt VM Disaster Recovery workflows when the `cdi.kubevirt.io/storage.usePopulator` annotation is set to `"true"` in the DataVolume spec. During failback, the CDI controller may recreate the PVC before Stork can, leading to the new PVC pointing to a fresh volume instead of the migrated one. This can cause the VM to use an unintended volume after failback.
The DR workflow functions as expected when `storage.usePopulator` is explicitly set to `"false"`.

Affected versions: AllMinor

## 25.2.1​

April 14, 2025

### Improvements​

Improvement NumberImprovement Description

PB-9573Portworx Backup now handles CSI snapshot reconciliation more robustly. It ignores revision mismatch errors that occur when the external snapshotter updates the persistent volume claim (PVC) spec during finalizer updates. This prevents snapshot failures and ensures backup success for CSI, KDMP, and local snapshot volumes.

PB-9989Portworx Backup now supports scheduling backups using the time zone configured on the Stork instance running in the application cluster. This change reduces confusion and helps ensure that backup schedules align with the cluster’s local time settings.

PB-9990Portworx Backup improves resilience in virtual machine (VM) backup workflows. If a `preExec` rule fails for one VM, backups for other VMs in the same schedule can still continue.

Recommendation: If you're using Stork versions earlier than 25.2.1 and Portworx Backup versions earlier than 2.8.4, configure a separate schedule for each VM to help isolate backup failures.

PB-9988Previously, restoring a VM with a static IP in the same cluster could fail due to network conflicts. This enhancement adds support for such workflows through two annotations:

- `px-backup/skip-vm-start` – Prevents the VM from starting automatically after it's restored. This allows users to manually configure the static IP before VM startup.

- `px-backup/skip-mac-masking` – Disables MAC address masking during restore and preserves the original MAC address.

PB-10126Added the `advancedResourceLabelSelector` parameter to all `resourceCollector` APIs. This new string-based field allows users to define advanced label selector expressions compatible with `kubectl` filtering, including support for logical operators such as `in`, `notin`, and set-based matching. This enhancement provides greater flexibility and precision in resource selection by aligning behavior with native Kubernetes label filtering.

Example: `advancedResourceLabelSelector: "env in (dev, prod), tier != frontend"`

## 25.2.0​

April 3, 2025

note

- If you are using Portworx Backup and planning to install or upgrade your Stork version to 25.2.0 in your air-gapped environment, ensure that you pull the following `kopiaexecutor` and `nfsexecutor` images from the following Docker image paths and push them to your custom image registry.
 `docker.io/openstorage/kopiaexecutor:master-latest`
 `docker.io/openstorage/nfsexecutor:master-latest`

- The following status field names in the `GroupVolumeSnapshots` custom resource definition (CRD) are updated from PascalCase to camelCase. Update these field names in automation scripts, if applicable. For more information, see GroupVolumeSnapshot.

- `dataSource`

- `conditions`

- `parentVolumeID`

- `taskID`

- `volumeSnapshotName`

### New Features​

Migration Preview: Added support for migration previews in `storkctl create migration` and `storkctl create migrationschedule`.

-
For `storkctl create migration`: Use the `--preview` flag to display the resources that would be included in the migration without running it. Use `--previewFile <filename>` to save the preview output to a file. For more information, see Preview resources before starting migration.

-
For `storkctl create migrationschedule`: Similarly, use the `--preview` and `--preview-file` flags to view and save the resources that would be migrated as part of the schedule. For more information, see Preview resources before creating migration schedule.

This feature helps confirm which resources will be migrated before execution, including non-namespaced resources such as `ClusterRoles` and `ClusterRoleBindings`.

### Improvements​

Improvement NumberImprovement Description

PWX-35523The `MigrationSchedule` controller now prunes old failed `Migration` custom resources, retaining only the five most recent failures. This prevents accumulation and reduces unnecessary Kubernetes API calls during reconciliation.

PWX-37807Stork health monitoring now includes Pods using Portworx volumes as ephemeral volumes, ensuring they are properly evicted if the underlying Portworx node becomes unavailable.

PWX-41385Stork scheduling now considers Pods that use Portworx volumes as ephemeral volumes. This enables placement decisions based on storage availability.

PWX-41617Improved performance of `storkctl get <resource> --all-namespaces` by replacing per-namespace iteration with a single API call that retrieves resources across all namespaces, significantly reducing wait time in clusters with many namespaces.

PWX-42338Pod scheduling is now faster when multiple pods are scheduled in parallel on a heavily loaded cluster. The volume listing process has been optimized, reducing delays and improving workload deployment times.

## 25.1.0​

February 12, 2025

### Improvements​

Improvement NumberImprovement Description

PB-9039Portworx Backup now supports storing and restoring the status of Custom Resources (CR) during backup and restore operations. This feature ensures that CRs retain their status upon restoration, improving consistency and recovery reliability. To enable this feature in the UI, you must set the corresponding flag in the ConfigMap.
Note: Only create and delete operations are supported for this flag in both manual and scheduled backups.

PB-8121Portworx Backup includes `virtualMachineInstancetype` and `VirtualMachinePreference` resources when backing up KubeVirt VMs. This ensures that these resources can be restored successfully.

PB-8466Portworx Backup now captures `NetworkAttachmentDefinition` resources during KubeVirt VM backups. This ensures that `NetworkAttachmentDefinition` resources can be restored successfully.

### Fixes​

Issue NumberIssue DescriptionSeverity

PB-6688Backup failed for Portworx volumes encrypted at the storage class level using CSI and Kubernetes Secrets on non-secure clusters.

User Impact: Users had to rely on alternative encryption methods to secure their Portworx volumes.

Resolution: Portworx Backup now successfully backs up volumes encrypted at the storage class level using CSI and Kubernetes Secrets on non-secure clusters.

Affected Versions: 24.4.0 and earlierMinor

PB-9267In PX-Security enabled clusters, if the required user token is unavailable or misconfigured, backups for encrypted volumes fail. However, the system incorrectly marks the partial backup status as successful.

User Impact: Users might assume that backups completed successfully, even if one or more volumes failed to back up.

Resolution: Now, `volumeInfo` correctly marks volumes as failed when token retrieval fails and skips reconciliation for these volumes. This ensures that the partial backup status accurately reflects the backup state.

Affected Versions: 24.4.0 and earlierMinor

## 24.4.0​

January 28, 2025

### New Features​

Added support for using NFS locations in asynchronous disaster recovery. For more information on how to create a cluster pair for NFS location, refer to the following pages:

- Create a unidirectional ClusterPair for NFS

- Create a bidirectional ClusterPair for NFS

### Improvements​

Improvement NumberImprovement Description

PWX-37386Added support for listing the failover/failback actions for all namespaces using the `--all-namespaces` flag. Users can now track failover and failback actions across all namespaces using the `storkctl get failover --all-namespaces` and `storkctl get failback --all-namespaces` commands.

PWX-40683Improved the snapshot data garbage collection (GC) workflow to reduce the volume of deletions and PX API calls. Added sub-batch deletions and verification checks. Stork now periodically cleans stale volumsnapshotdata and driver snapshots. The following Stork arguments can be used to control this task:

- `snapshotdata-gc-interval`: Period in which the task should run (default: 24h).

- `snapshotdata-gc-batch-size`: Deletion will be in batches. This specifies the batch size of snapshotdata to be deleted at one go (default: 50).

- `snapshotdata-gc-min-age`: Minimum age of snapshotdata to qualify for being garbage collected (default: 24h). In this default case, even if a snapshotdata is stale and doesn't have a corresponding volumesnapshot in the cluster which makes it eligible for garbage collection, if it is created within 24 hours, it won't be deleted.

- `snapshotdata-gc-start-time`: Start time window of the GC task in which it is allowed in 24-hour time format (default: 00:00).

- `snapshotdata-gc-end-time`: End time window of the GC task in which it is allowed in 24-hour time format (default: 00:00). You can add these arguments to control the task.

PWX-40163Added the `retain-external-schedulers` argument in Stork to prevent Stork from replacing external schedulers, ensuring that only the default scheduler is replaced. When set to true, external schedulers are preserved. By default, the value is false.

PWX-36876Added the `storkctl update volumesnapshotschedule` command to update the PVC name in the specified `volumesnapshotschedule`. Users can now update PVC names in volumesnapshotschedules.

PWX-22735Scheduled snapshots are now supported in PX-Security enabled clusters. Snapshot schedules created with StorageClass annotations now work in auth-enabled clusters.

PWX-41089Added an option to disable caching of pod data with the `disable-pod-caching: true` argument in the StorageCluster configuration. By default, pod caching is enabled. This helps reduce memory consumption when the cluster is used at scale with respect to the number of pods.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-38924Failover operation was failing due to a pod in the `Succeeded` phase but still in a Bound state with a PVC, causing Stork to wait indefinitely.

User Impact: Stork was unable to complete failover as it waited for the pod to terminate, which never happened.

Resolution: Stork now skips considering pods in the Completed state for waiting for source deactivation in failover.

Affected Versions: 24.3.0–24.3.4Minor

PWX-38925Migration of Job resources failed with a status of `partially successful`.

User Impact: Users encountered migration failures for Job resources.

Resolution: Fixed the error in the migration process for Job resources.

Affected Versions: 24.3.0–24.3.4Minor

PWX-37027Pods showed an event `Unable to schedule pod using volumes [*] in a hyperconverged fashion` when using direct access volumes.

User Impact: Pods received the event and were deleted if scheduled on a storage node that went offline.

Resolution: Node prioritizing is skipped for pods using direct access volumes, preventing eviction if the storage node goes offline.

Affected Versions: 23.11.1-24.3.4Minor

PWX-38905Migrations were stuck in a loop if the StorageClass for a migrated PVC was not present in the source cluster.

User Impact: Migrations appeared to be stuck.

Resolution: Migrations now continue and complete even if the StorageClasses are not present in the source cluster.

Affected Versions: 24.3.0–24.3.4Minor

## 24.3.4​

December 12, 2024

### Fixes​

Issue NumberIssue DescriptionSeverity

PB-8630In IBM environments, backups or restores of Persistent Volume Claims (PVCs) fail when using certain CSI provisioners (e.g., IBM File). These provisioners do not invoke the kubelet ownership and permission change functions, causing `kopia` to fail due to insufficient read permissions.

User Impact: Users with IBM File provisioners cannot perform KDMP backups because KDMP job pods lack the required read permissions.

Resolution: KDMP job pods now support the anyuid annotation to address permission issues. To enable this:

- Add the `PROVISIONERS_TO_USE_ANYUID: openshift-storage.cephfs.csi.ceph.com,provisioner2` entry to the KDMP ConfigMap.

- Apply this ConfigMap on both the backup and restore clusters.

This ensures KDMP job pods run with the necessary permissions, resolving backup and restore failures.

Affected Versions: 24.3.3 and earlierMinor

## 24.3.3.1​

December 11, 2024

### Fixes​

Issue NumberIssue DescriptionSeverity

PB-7868The NFS backup location PVC failed when the NFS version was not specified in the mount option.

User impact: KDMP restore failed with an NFSv4 backup location.

Resolution: You can now restore KDMP backups taken on an NFSv4 backup location.

Affected versions: 24.3.3 and earlierMajor

PWX-40984Previously, in Stork version 24.3.3, live migration of VMs with bind-mounted Portworx volumes failed with the following error: `Unsafe migration: Migration without shared storage is unsafe`.

User Impact: Users encountered migration failures for such VMs.

Resolution: This issue has been fixed in Stork version 24.3.3.1. To successfully live migrate the impacted VMs, restart the impacted VMs after upgrading.

Affected Versions: 24.3.3Major

PB-7944For large resources, the resources are fetched twice, increasing the backup completion time.

User Impact: Large resource backups take longer to complete.

Resolution: Resources are now fetched only once and uploaded in the same reconciler context. Note: This fix is applicable only for S3 object store.

Affected Versions: 24.3.3 and earlierMinor

PB-8394If a smaller pxd volume of a few MB and a larger volume of, let's say, 500 GB, are backed up, the status of the smaller backup throws a false error: `Backup failed for volume: rpc error: code = Internal desc = Failed to get status of backup: Key not found`.

User Impact: The backup appears to be in a failed state with the `key not found` error, but the backup was actually successful and uploaded to the cloud.

Resolution: Once the backup reaches a successful state, we stop checking its status.

Affected Versions: 24.3.2 and earlierMinor

PB-7476Node affinity was not set up in the kopia/NFS backup and restore job pods, allowing these job pods to be scheduled on nodes where the applications to be backed up were not running. This led to backup failures.

User Impact: If there are network restrictions on certain nodes and applications are not running on those nodes, there's a risk that the backup job pods may get scheduled on these restricted nodes, causing the backup to fail.

Resolution: Added node affinity for the job pods to ensure they are scheduled on the desired nodes where the application pods are running.

Affected Versions: 24.3.2 and earlierMinor

### Known issues (Errata)​

Issue NumberIssue DescriptionSeverity

PWX-38905If a StorageClass is deleted on the source and an asynchronous DR operation is performed for resources (PV/PVC) that use the deleted StorageClass, the migration fails with the following error:
`Error updating StorageClass on PV: StorageClass.storage.k8s.io <storageClassName> not found`

Workaround: You need to recreate the deleted StorageClass to proceed with the DR operation.

Affected versions: 24.3.0, 24.3.1, 24.3.2, and 24.3.3Major

## 24.3.2​

October 14, 2024

### Fixes​

Issue NumberIssue DescriptionSeverity

PB-4394KDMP restore failed when the snapshot size exceeded the PVC size.

User Impact: Users experienced failures during KDMP restore for filesystem-based storage provisions when the PVC content was larger than the PVC size.

Resolution: Modified the PVC size to match the snapshot size.
Affected Versions: 24.3.1 and earlierMajor

PB-8316Backups were incorrectly marked as successful, not partial, even when some volume backups failed.

User Impact: Users were led to assume that all PVCs were successfully backed up, even when some had failed.

Resolution: Updated the `in-memory` value of `failedVolCount` and the backup object to accurately reflect the number of failed backups.
Affected Versions: 24.3.0 and 24.3.1Major

PB-8360Addition of IBM COS backup location failed with an `UnsupportedOperation` error when the bucket was unlocked.

User Impact: Users could not add an IBM COS backup location if it was unlocked.

Resolution: The `UnsupportedOperation` error is now ignored for unlocked IBM COS buckets, indicating the bucket is not locked.
Affected Versions: 24.3.1Major

PB-7726VM Backup failed while executing auto exec rules if the `virt-launcher` pod of the VMs was not in a running state.

User Impact: VM Backups failed when auto exec rules were applied.

Resolution: Auto exec rules are now only executed on running `virt-launcher` pods.
Affected Versions: 24.3.0 and 24.3.1Major

### Known issues (Errata)​

Issue NumberIssue DescriptionSeverity

PWX-38905If a StorageClass is deleted on the source and an asynchronous DR operation is performed for resources (PV/PVC) that use the deleted StorageClass, the migration fails with the following error:
`Error updating StorageClass on PV: StorageClass.storage.k8s.io <storageClassName> not found`

Workaround: You need to recreate the deleted StorageClass to proceed with the DR operation.

Affected versions: 24.3.0, 24.3.1, and 24.3.2.Major

## 24.3.1​

October 07, 2024

### Improvements​

Improvement NumberImprovement Description

PWX-39128If the AWS init gets stuck for a long time and prevents Stork from starting up, you can skip the AWS driver init from the Stork imports by adding the environment variable `SKIP_AWS_DRIVER_INIT="true"` to the stork pod.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-38383In certain scenarios, `Kubernetes etcd` was overloaded, and stork pods went into CrashLoopBackOff state with the following error:
`Controller manager: failed to wait for snapshot-schedule-controller caches to sync: timed out waiting for cache to be synced`.

 User Impact: Stork failed and restarted multiple times due to the overloading of `Kubernetes etcd`.

 Resolution: We've added a `--controller-cache-sync-timeout` flag, using which you can tweak the value of the cache sync timeout based on your requirements. The default value is 2 minutes.
Example: `--controller-cache-sync-timeout=10` - sets the controller cache sync timeout as 10 minutes instead of the default 2 minutes.
 Affected Versions: 24.3.0 and earlierMinor

PWX-36167The Stork health monitor was incorrectly considering stale node entries with an offline status for pod eviction.

 User Impact: If a node was repaired and returned with a different IP address, pods were inadvertently evicted from this online node due to the presence of stale node entries.

 Resolution: If a node entry with an 'online' storage status shares the same scheduler ID as an 'offline' node entry, the system will disregard the offline node entry when considering pod evictions. This change ensures that pods are not inadvertently evicted from nodes that have been repaired and are now online.
 Affected Versions: 24.3.0 and earlierMinor

## 24.3.0​

September 11, 2024

### Improvements​

- Stork now supports partial backups. If backup fails for any of the PVCs, the successful backups of other PVCs are still saved, and the status is displayed as `partial success`.

note

A partial backup requires at least one successful PVC backup.

- Updated `golang`, `aws-iam-authenticator`, `google-cloud-cli`, and `google-cloud-sdk` versions to resolve security vulnerabilities.

### Fixes​

- Issue: In a Synchronous DR setup, when you perform a failover operation using the `storkctl perform failover` command, the witness node might be deactivated instead of the source cluster.
User Impact: After failover, the source cluster might remain in active state, and the PX volumes can still be mounted and used from the source cluster.
Resolution: After failover, now the source cluster is deactivated by default, and the witness node remains unaffected.

## 24.2.5​

August 05, 2024

### Fixes​

- Issue: Strong hyperconvergence for pods is not working when using `stork.libopenstorage.org/preferLocalNodeOnly` annotation.
User Impact: Pods remain in a pending state.
Resolution: When the `stork.libopenstorage.org/preferLocalNodeOnly` annotation is used, the pods are now scheduled in the node where the volume replica lies, and the strong hyperconvergence works as expected.

## 24.2.4​

July 17, 2024

### Fixes​

- Issue: During an OCP upgrade in a 3-node cluster, the MutatingWebhookConfiguration `stork-webhooks-cfg` is deleted if the leader Stork pod is evicted.
User Impact: Applications that require Stork as the scheduler will experience disruptions, and OCP upgrades will get stuck on a 3-node cluster.
Resolution: The MutatingWebhookConfiguration is now created after the leader election, ensuring `stork-webhooks-cfg` is always available.
Affected Versions: All

## 24.2.3​

July 02, 2024

note

For users currently on Stork versions 24.2.0, 24.2.1, or 24.2.2, Portworx by Everpure recommends upgrading to Stork 24.2.3.

### Fixes​

- Issue: If the VolumeSnapshotSchedule has more status entries than the retain policy limit, Stork may continue creating new VolumeSnapshots, ignoring the retain policy. This can happen if the retain limit was lowered or if there was an error during snapshot creation.
User Impact: Users saw more VolumeSnapshots than their retain policy was configured to allow.
Resolution: Upgrade to Stork version 24.2.3. #1800

note

This fix doesn’t clean up the snapshots that were created before the upgrade. If required, you need to delete the old snapshots manually.

Affected Versions: 24.2.0, 24.2.1, and 24.2.2.

## 24.2.2​

June 14, 2024

### Improvements​

- Stork now uses the shared informer cache event handling mechanism instead of the watch API to reschedule unhealthy pods that are using Portworx volumes.

## 24.2.1​

June 06, 2024

### Improvements​

- Stork now supports Azure China environment for Azure backup locations. For more information, see Add Azure backup location.

### Fixes​

-
Issue: If you were running Portworx Backup version 2.6.0 and upgraded the Stork version to 24.1.0, selecting the default VSC in the Create Backup window resulted in a `VSC Not Found` error.
User Impact: Experienced failures during backup operations.
Resolution: You can now choose the default VSC in the Create Backup window and create successful backups.

-
Issue: If you deploy Portworx Enterprise with PX-Security enabled and take a backup to an NFS backup location and then restore, restore used to fail.
User Impact: Unable to restore backups from the NFS backup location for PX security-enabled Portworx volumes.
Resolution: This issue is now fixed.

## 24.2.0​

May 29, 2024

### Improvements​

-
Enhanced Disaster Recovery User Experience

In this latest Stork release, the user experience has been improved significantly, with a particular focus on performing failover and failback operations. These improvements provide a smoother and more intuitive user experience by simplifying the process while ensuring efficiency and reliability.

Now, you can perform a failover or failback operation using the following `storkctl` commands:

- To perform a failover operation, use the following command: `storkctl perform failover -m <migration-schedule> -n <migration-schedule-namespace>`

- To perform a failback operation, use the following command: `storkctl perform failback -m <migration-schedule> -n <migration-schedule-namespace>`

See the following pages for more information on the enhanced approach:

- Failover an application in an asynchronous DR setup.

- Failback an application in an asynchronous DR setup.

- Failover an application in a synchronous DR setup.

- Failback an application in a synchronous DR setup.

- The Portworx driver is updated to optimize the API calls it makes to reduce the time taken for scheduling pods and monitoring pods if they need to be rescheduled when Portworx is down on nodes.

### Fixes​

-
Issue: Migration schedules in the `admin` namespace were updated with true or false for the `applicationActivated` field when activating or deactivating a namespace, even if they did not migrate the particular namespace.
User Impact: Unrelated migration schedules were getting suspended.
Resolution: Stork now updates the `applicationActivated` field only for migration schedules that are migrating at least one of the namespaces being activated or deactivated.

-
Issue: Updating the VolumeSnapshotSchedule resulted in a version mismatch error from Kubernetes when the update happened on a previous version of the resource.
User Impact: When the VolumeSnapshotSchedule is high, Stork logs are flooded with these warning messages.
Resolution: Fixed the VolumeSnapshotSchedule update with a patch to avoid the version mismatch error.

-
Issue: Similar volume snapshot names were created when the VolumeSnapshotSchedule frequency matched and aftertrimming produced similar substrings.
User Impact: For one volume, a snapshot may not be taken but can be marked as successful.
Resolution: A 4 digit randomness is now added to the name to avoid name collisions for volumesnapshots resulting from different volumesnapshot schedules.

-
Issue: Stork relies on Kubernetes DNS to locate services, but it also assumes the `.svc.cluster.local` domain for Kubernetes services.
User Impact: The clusters that modified Kubernetes DNS domains were not able to use Stork.
Resolution: Stork now works on clusters with a modified Kubernetes DNS domain.

-
Issue: Resource transformation for CR was not supported.
User Impact: It was blocking some of the necessary transformations for resources that were required at the destination site.
Resolution: Now, resource transformation for CR is supported.

### Known issues (Errata)​

- Issue: If you use the `storkctl perform failover` command to perform a failover operation, Stork might not be able to scale down the KubeVirt pods, which could cause the operation to fail. Workaround: Perform the failover operation by following the procedure on the below pages:

- Asynchronous DR

- Synchronous DR

## 24.1.0​

May 20, 2024

### Improvements​

- Stork now supports Kubevirt VMs for Portworx backup and restore operations. You can now initiate VM-specific backups by setting the `backupObjectType` to `VirtualMachine`. Stork automatically includes associated resources, such as PVCs, secrets, and ConfigMaps used as volumes and user data in VM backups. Also, Stork applies default freeze/thaw rules during VM backup operations to ensure consistent filesystem backups.

- Cloud Native backups will now automatically default to CSI or KDMP with LocalSnapshot, depending on the type of schedules they create.

- Previously in Stork, for CSI backups, you were limited to selecting a single VSC from the dropdown under the `CSISnapshotClassName` field. Now you can select a VSC for each provisioner via the `CSISnapshotClassMap`.

- Now, the creation of a default VSC from Stork is optional.

### Fixes​

-
Issue: Canceling an ongoing backup initiated by PX-Backup results in the halting of the post-execution rule.
User Impact: This interruption causes the I/O processes on the application to stop or the post-execution rule execution to cease.
Resolution: To address this, Stork executes and removes the post-execution rule CR as part of the cleanup procedure for the application backup CR.

-
Issue: Generic KDMP backup/restore pods become unresponsive in environments where Istio is enabled.
User Impact: Generic KDMP backup and restore fails in the Istio enabled environments.
Resolution: Relaxed the Istio webhook checks for the stork created KDMP generic backup/restore pods. Additionally, the underlying issue causing job pod freezes has been resolved in Kubernetes version 1.28 and Istio version 1.19.

## 23.11.0​

January 22, 2024

### New Features​

-
You can now create and delete schedule policies and migration schedules using the new `storkctl` CLI feature. This enables you to seamlessly create and delete SchedulePolicy and MigrationSchedule resources, enhancing the DR setup process. In addition to the existing support for clusterPairs, you can now efficiently manage all necessary resources through `storkctl`. This update ensures a faster and simpler setup process, with built-in validations. By eliminating the need for manual YAML file edits, the feature significantly reduces the likelihood of errors, providing a more robust and user-friendly experience for DR resource management in Kubernetes clusters.

-
The new Storage Class parameter `preferRemoteNode` enhances scheduling flexibility for SharedV4 Service Volumes. By setting this parameter to `false`, you can now disable anti-hyperconvergence during scheduling. This provides an increased flexibility to tailor Stork's scheduling behavior according to your specific application needs.

### Improvements​

- Updated golang and `google-cloud-sdk` versions to resolve security vulnerabilities.

### Fixes​

-
Issue: Exclusion of Kubernetes resources such as deployments, statefulsets, and so on was not successful during migration.
User Impact: The use of labels to exclude selectors proved ineffective in scenarios where the resource was managed by an operator that reset user-defined labels.
Resolution: The introduction of the `excludeResourceTypes` feature now allows users to exclude certain types of resources from migration, providing a more effective solution compared to using [labels].

-
Issue: The `applicationrestore` function created using `storkctl` consistently restored to a namespace with the identical name as the source, causing users to be unable to restore to a different namespace.
User Impact: Users faced limitations as they were unable to restore applications to a namespace other than the one with the same name as the source.
Resolution: `storkctl` has been updated to address this issue by introducing support for accepting namespace mapping as a parameter, allowing users to restore to a different namespace as needed.

-
Issue: The `storkctl` create `clusterpair` command was not functioning properly with `HTTPS PX` endpoints.
User Impact: Migrations between clusters with SSL-enabled PX endpoints were not successful.
Resolution: The issue has been addressed, and now both HTTPS and HTTP endpoints are accepted as source (`src-ep`) and destination (`dest-ep`) when using `storkctl create clusterpair`.

-
Issue: The PostgreSQL operator generates an error related to the pre-existence of service account, role, and role bindings following a migration.
User Impact: Users are unable to scale up a PostgreSQL application installed via OpenShift Operator Hub after completing the migration.
Resolution: Excluded migration of service account, role, and role bindings if they have owner reference set to allow PostgreSQL pods to come up successfully.

-
Issue: Real-Time Custom Resource (RT CR) enters a failed state when a transform rule includes either int or bool as a data type.
User Impact: Migration involving resource transformation will not succeed.
Resolution: Resolved the issue by addressing the parsing problem associated with `int` and `bool` types.

-
Issue: Continuous crashes occur in Stork pods when the cluster contains a RT CR with a rule type set as slice and the operation is add.
User Impact: Stork service experiences ongoing disruptions.
Resolution: Implemented a solution by using type assertion to prevent the panic. Additionally, the problematic `SetNestedField` method is replaced with `SetNestedStringSlice` to avoid panics in such scenarios. You can also temporarily resolve the problem by removing the RT CR from the application cluster.

-
Issue: Stork crashes when attempting to clone an application with CSI volumes using Portworx.
User Impact: Users are unable to clone applications if PVCs in the namespaces utilize Portworx CSI volumes.
Resolution: Now, a patch is included to manage CSI volumes with Portworx, which ensures the stability of application cloning functionality.

-
Issue: When setting up a migration schedule in the `admin` namespace with pre/post-execution rules, these rules must be established in both the `admin` namespace and every namespace undergoing migration.
User Impact: The user experience is less intuitive as it requires creating identical rules across multiple namespaces.
Resolution: The process is now simplified as rules only require addition within the migration schedule's namespace.

-
Issue: Stork was not honoring locator volume labels correctly when scheduling pods.
User Impact: In cases where `preferRemoteNodeOnly` was initially set to `true`, pods sometimes failed to schedule. This issue was particularly noticeable when the Portworx volume setting `preferRemoteNodeOnly` was later changed to `false`, and there were no remote nodes available for scheduling.
Resolution: Now, even in scenarios where remote nodes are not available for scheduling, pods can be successfully scheduled on a node that holds a replica of the volume.

### Known issues (Errata)​

-
Issue: In Portworx version 3.0.4, several migration tests fail in an auth-enabled environment. This issue occurs specifically when running these tests in environments where authentication is enabled.
User Impact: You may experience failed migrations, which will impact data transfer and management processes.
Resolution: The issue has been resolved in Portworx version 3.1.0. Users experiencing this problem are advised to upgrade to version 3.1.0 to ensure smooth migration operations and avoid permission-related errors during data migration processes.

-
Issue: When using the `storkctl create clusterpair` command, the HTTPS endpoints for Portworx were not functioning properly.
User Impact: This issue affects when you attempt migrations between clusters where `px` endpoints were secured with SSL. As a result, migrations could not be carried out successfully in environments using secure HTTPS connections.
Resolution: In the upcoming Portworx 3.1.0 release, the `storkctl create clusterpair` command will be updated to accept both HTTP and HTTPS endpoints, allowing the specification of either `src-ep` or `dest-ep` with the appropriate scheme. This update ensures successful cluster pairing and migration in environments with SSL-secured `px` endpoints.

## 23.9.1​

December 15, 2023

### Fixes​

-
Issue: The generic backup of some PVCs in kdmp was failing due to the inclusion of certain read-only directories and files.
User Impact: Difficulties restoring the snapshot as the restoration of these read-only directories and files resulted in permission denied errors.
Resolution: Introduced the --ignore-file option in kdmp backup, enabling you to specify a list of files and directories to be excluded during snapshot creation. This ensures that during restoration, these excluded files and directories will not be restored.

Format for adding the ignore file list:

```

KDMP_EXCLUDE_FILE_LIST: |

    <storageClassName1>=<dir-list>,<file-list1>,....

    <storageClassName2>=<dir-list>,<file-list1>,....

```

Sample for adding the ignore file list:

```

KDMP_EXCLUDE_FILE_LIST: |

    px-db=dir1,file1,dir2

    mysql=dir1,file1,dir2

```

-
Issue: The backup process does not terminate when an invalid post-execution rule is applied, leading to occasional failures in updating the failure status to the application backup CR.
User Impact: Backups with invalid post-execution rules were not failing as expected.
Resolution: Implemented a thorough check to ensure that backups with invalid post-execution rules are appropriately marked as failed, accompanied by a clear error message.

## 23.9.0​

December 07, 2023

### New Features​

#### Enhanced support for Kubevirt VMs in Portworx Backup​

This feature facilitates the backup and restoration of Kubevirt VMs through Portworx Backup. When Kubevirt VMs are included in the backup object, the restoration process from this backup ensures successful transformation of VMs, incorporating `DataVolumeTemplate` and adjusting masquerade interface configurations to ensure a successful completion of the restore operation.

### Fixes​

-
Issue: Occasionally, the restoration process encounters an error stating `resourceBackup CR already exists` when the reconciler attempts to re-enter.
User Impact: The restore operation is unsuccessful due to this error.
Resolution: The issue has been resolved by addressing the issue of the already-existing `resourceBackup CR` error. The fix involves handling the error by ignoring it during the creation of the `ResourceBackup` CR. https://github.com/libopenstorage/stork/pull/1482

-
Issue: The attempt to add Tencent Cloud object storage fails during the objectlock support check due to a discrepancy in error reporting when object lock is not supported.
User Impact: Users are unable to utilize Tencent Cloud object storage as a backup location for backup and restore operations.
Resolution: A solution has been implemented by incorporating appropriate error handling checks during the verification of objectlock support for buckets in Tencent Cloud object storage. https://github.com/libopenstorage/stork/pull/1478

-
Issue: A warning event is recorded in the applicationbackup CR when the S3 bucket already exists.
User Impact: The warning event is causing confusion for users.
Resolution: To address this, the system now refrains from generating a warning event if the S3 object store indicates the `ErrCodeBucketAlreadyExists` code. https://github.com/libopenstorage/stork/pull/1481

-
Issue: Backing up the `kube-system` namespace is not a supported feature. However, in the case of `all-namespace` backups or backups based on namespace labels, the `kube-system` namespace is inadvertently included.
User Impact: This inclusion of the `kube-system` namespace in backups causes complications during the restore process.
Resolution: This issue has been resolved by excluding the `kube-system` namespace from `all-namespace` backups and backups based on namespace labels. https://github.com/libopenstorage/stork/pull/1506

-
Issue: The restore process based on CSI encounters failures in setups with the `csi-snapshot-webhook` admin webhook. This failure is attributed to a distinct error related to existing resources, specifically when creating the `volumesnapshotclass` resource.
User Impact: Users are affected by the inability to perform CSI-based restores on setups featuring the `csi-snapshot-webhook` admin webhook.
Resolution: The issue has been addressed by incorporating a pre-check through a `get` call before the `create` call. Now, the `create` call occurs only if the `get` call fails with a `NotFound` error, preventing conflicts related to existing resources. https://github.com/libopenstorage/stork/pull/1567

## 23.8.0​

October 12, 2023

### New Features​

-
Stork now supports both asynchronous and synchronous DR migration for applications managed by operators. When `startApplications` is set to `false` for migrations, Stork ensures that application pods remain inactive in the destination cluster after migration. Additionally, Stork provides the flexibility to scale down applications by modifying Custom Resource (CR) specifications, using the `suspend options` feature. For applications controlled by clusterwide operators that do not support scaling down via CR spec modifications, Stork offers a "stash strategy" to prevent application pods from becoming active prematurely during migration, ensuring a seamless transition to the destination cluster. https://github.com/libopenstorage/stork/pull/1451

-
Stork now supports import workflows using the DataExport CRs. This means you can now seamlessly transfer data from one PVC to another within the same cluster using rsync.

### Improvements​

- Stork now enables you to optimize resource utilization and ensure a more efficient and targeted restoration of applications. You can now specify `resourceTypes` during the application backup process, allowing for a more granular selection of resources to be included in the backup. Moreover, when initiating an application restore, you can also choose specific resources to restore, providing greater flexibility in the recovery process.

### Fixes​

-
Issue: `ReplicaSets` that had been migrated and were not under the management of deployments were unable to be activated or deactivated using `storkctl`.
User Impact: Users should manually scale up or down the `ReplicaSet` using `kubectl`.
Resolution: As part of the activation or deactivation process, `storkctl` is now capable of scaling up or down the migrated `ReplicaSet`. https://github.com/libopenstorage/stork/pull/1471

-
Issue: When using Stork 23.7, KubeVirt pods encounter a `CrashLoopBackoff` state, accompanied by the following error messages within the pod logs:

```

/usr/bin/virt-launcher-monitor: /lib64/libc.so.6: version GLIBC_2.34' not found (required by /etc/px_statfs.so)

/usr/bin/virt-launcher-monitor: /lib64/libc.so.6: version GLIBC_2.33' not found (required by /etc/px_statfs.so)

```

User Impact: KubeVirt VMs become unusable.
Resolution: This issue has been resolved in Stork version 23.8. For any existing virt-launcher pods experiencing the CrashLoopBackOff state due to this bug, follow these steps after upgrading to Stork 23.8:

- Stop the KubeVirt VM.

- Restart the KubeVirt VM. https://github.com/libopenstorage/stork/pull/1493

-
Issue: Following migration, an ECK application installed using an operator demands all associated Custom Resource Definitions (CRDs) to be present to initiate successfully.
User Impact: Users experiences difficulties in scaling up the Elasticsearch application due to the absence of essential CRDs after the migration.
Resolution: To address this issue, the migration process will include the migration of associated CRDs for a Custom Resource, thereby preventing any obstacles in scaling up the ECK application post-migration. https://github.com/libopenstorage/stork/pull/1494

-
Issue: Following migration, applications controlled by Custom Resources (CRs) are automatically initiated if the operator is already operational in a distinct namespace.
User Impact: This results in applications in the destination cluster starting unexpectedly, contrary to the desired behavior where they should remain inactive with `startApplication: false`.
Resolution: To rectify this, a stashing strategy has been implemented for the CR content, storing it in a configmap. This ensures that the CR specification is applied only after activating the migration, allowing the applications to start as intended. https://github.com/libopenstorage/stork/pull/1451

## 23.7.3​

September 26, 2023

### Fixes​

Issue: Migrations using a cluster pair created using `--unidirectional` option fail due to the absence of object store information in the destination cluster.
User Impact: Users couldn't run migrations with unidirectional cluster pair.
Resolution: Create object store information in the destination cluster for the migrations to succeed. https://github.com/libopenstorage/stork/pull/1501, https://github.com/libopenstorage/stork/pull/1507, https://github.com/libopenstorage/stork/pull/1510

## 23.7.2​

September 01, 2023

### Fixes​

Issue: If the status is larger than the maximum `etcd` request size (1.5M), the update of the `kdmp` generic backup status in the `Volumebackup` CR will fail.
User Impact: At times, the failure of the update to the `Volumebackup` CR causes the `kdmp` backup to also fail.
Resolution: Currently, the practice involves refraining from updating the actual status in the `Volumebackup` CR if it is large. Instead, the update is made within the log of the job pod.

## 23.7.1​

August 22, 2023

### Fixes​

-
Issue: The `aws-iam-authenticator` binary size was zero in the Stork container.
User Impact: If kubeconfig is used with `aws-iam-authenticator`, then users will encounter failure when creating a cluster pair on Amazon EKS.
Resolution: Updated the `aws-iam-authenticator` and the curl options to make sure binary gets downloaded successfully.

-
Issue: Updates made to the parameter associated with large resources in the `stork-controller-config` configmap are not preserved when the Stork pod is restarted.
User Impact: Whenever Stork pods restart, user needs to update the parameter related to large resources in the `stork-controller-config` configmap.
Resolution: Ensure that updated value of the large-resource related parameter in the `stork-controller-config` configmap persists across Stork pod restarts. #1473

-
Issue: The backup object has an empty volume size for the Portworx volume, when you use a Stork version that is newer than 23.6.0 but Portworx version is older than 3.0.0.
User Impact: Portworx volumes with a version below 3.0.0 will display a volume size of zero.
Resolution: Retrieval of volume size has been handled regardless of the versions of Stork and Portworx.

## 23.7.0​

August 02, 2023

### New Features​

- Stork has introduced an enhanced workflow for creating a ClusterPair, enabling you to create a ClusterPair using a single storkctl command in both synchronous and asynchronous Disaster Recovery (DR) scenarios. See Create a synchronous DR ClusterPair and Create an asynchronous DR ClusterPair for more information.

note

You need to update the storkctl binary for this change to take effect.

### Improvements​

-
Updated golang, aws-iam-authenticator and google-cloud-sdk versions to resolve 20 Critical and 105 High vulnerabilities reported by the JFrog scanner.

-
Added kubelogin utility in Stork container.

### Fixes​

-
Issue: Due to occasional delays in bound pod deletion, the current timeout setting of 30 seconds proves insufficient, resulting in backup failures.
User Impact: At times, the backup process for a volume, which is bound with the "WaitForFirstConsumer" mode, encounters timeout errors and fails.
Resolution: The timeout value has been extended to five minutes to ensure that the deletion of the bound pod, created for binding the volume with "WaitForFirstConsumer," will not encounter timeout errors.

-
Issue: During the cleanup process, when the KDMP/Localsnapshot backup fails, the volumesnapshot/volumesnapshotcontent were not being removed.
User Impact: Unnecessary accumulation of the stale volumesnapshot/volumesnapshotcontent was occurring.
Resolution: Volumesnapshot/volumesnapshotcontent cleanup is now performed, even in the case of failed KDMP/localsnapshot backups.

-
Issue: When the native CSI backup fails with a timeout error, the volumesnapshotcontent is not being deleted.
User Impact: In the event of native CSI backup failures, the volumesnapshotcontent will accumulate.
Resolution: Proper handling includes deleting the volumesnapshotcontent in case of failure as well.

## 23.6.0​

June 27, 2023

### New Features​

- Added support for Portworx Backup created ApplicationBackup and ApplicationRestore for Stork, to work with NFS share backup location.

### Fixes​

-
Issue: Update calls were happening to the volumesnapshotschedule in each 10 seconds even if there is no new update.
User Impact: With lots of volumesnapshotschedules running, it is unnecessary load on api-server.
Resolution: Avoiding updates if there is no change to volume snapshot list as part of pruning.

-
Issue: Restore size was taken from VolumeSnapshot size because for some CSI drivers the PVC was not bound; if the VolumeSnapshot size was less than the source volume size.
User Impact: CSI restore was failing with some storage provisioners.
Resolution: Updating the restore volume size only when the VolumeSnapshot size is greater than the source volume size.

-
Issue: MySQL apps can show inconsistent data after being restored.
User Impact: All MySQL backups may fail to run the MySQL application after restore operations due to data inconsistency.
Resolution: Fixed the data inconsistency by holding the table lock for the required duration while backup is in progress.

## 23.5.0​

May 31, 2023

### New Features​

- You can now provide namespace labels in the MigrationSchedule spec. This enables the specification of namespaces to be migrated.

### Improvements​

- Stork now supports the ignoreOwnerReferences parameter in the Migration and MigrationSchedule objects. This parameter enables Stork to skip the owner reference check and migrate all resources, and it removes the ownerReference while applying the resource. This allows migrating all the Kubernetes resources managed and owned by an application Operator’s CR.

note

You need to update the storkctl binary for this change to take effect.

### Fixes​

-
Issue: Restoring from a backup, which was taken from a previously restored PVC, was failing in the CSI system.
User Impact: Unable to restore a backup that had been taken from a previously restored CSI PVC.
Resolution: You can now successfully perform CSI restores using backups taken from already restored PVCs.

-
Issue: You may encounter webhook errors when attempting to modify StatefulSets in order to update Stork as the scheduler.
User Impact: Webhook related errors may give you the impression that the pod scheduler feature does not function properly.
Resolution: Removing webhook for StatefulSets and Deployments as Stork already contains a webhook for pods that manages setting Stork as the scheduler.

-
Issue: Incorrect migration status for service account deletion on source cluster.
User Impact: The expected behavior to delete the service account on the destination cluster, based on migration status, does not occur.
Resolution: Do not display the purged status for resources for which merging is supported on the destination cluster.

-
Issue: Storkctl create clusterpair does not honor the port provided from CLI.
User Impact: You cannot create bi-directional clusterpairs.
Resolution: To create clusterpair, pass the port provided from CLI in the endpoints.

note

You need to update the storkctl binary for this change to take effect.

-
Issue: Stork will delete pods running on the Degraded or Portworx StorageDown nodes.
User Impact: There will be a disruption on application, even though drivers like Portworx support running applications on the StorageDown nodes.
Resolution: Stork will not delete pods running on the StorageDown nodes.

## 23.4.0​

May 05, 2023

### New Features​

- You can now apply exclude label in MigrationSchedule spec to exclude specific resources from migration.

### Improvements​

-
Stork service is updated to not accept old TLS versions 1.0 and 1.1.

-
Stork now creates the default-migration-policy schedule policy, which is set to an interval of 30 minutes instead of 1 minute.

-
Stork now skips migrating the OCP specific (`system:`) ClusterRole and ClusterRoleBinding resources on OpenShift.

-
Stork now uses a default QPS of 1000 and a Burst of 2000 for its Kubernetes client.

-
Updated moby package to fix vulnerability CVE-2023-28840.

### Fixes​

-
Issue: Stork monitoring controller causes a high number of ListPods API calls to be executed repeatedly, resulting in a considerable consumption of memory.
User Impact: When there is a considerable quantity of pods within the cluster, the Stork monitoring system triggers additional ListPods APIs, which leads to a substantial utilization of memory.
Resolution: To reduce the overall memory usage of Stork, utilize a cache for retrieving the pod list within the health monitoring process.

-
Issue: Certain plurals of CRD do not follow pluralizing rules, which causes the APIs to fail to collect plurals during migration or backup.
User Impact: These CRDs neither get migrated or backed up properly, which affects disaster recovery, backup and restore of applications that depend on the CRs.
Resolution: Use API calls with correct CRD plurals, fetched from the cluster.

## 23.3.1​

April 26, 2023

### Improvements​

- Issue: Backing up a significant number of Kubernetes resources has resulted in failures due to limits on gRPC requests, Kubernetes custom resource sizes, or etcd payload sizes.
User Impact: If the number of Kubernetes resources in a backup is large, then the backup process may fail to complete due to errors related to size limits.
Resolution: To prevent errors related to gRPC size limits, etcd payload limits, and custom resource definition size, the resource information was removed from both the ApplicationBackup and ApplicationRestore CRs.

## 23.3.0​

April 06, 2023

### Improvements​

- Stork now supports cluster pairing for Oracle Kubernetes Engine (OKE) clusters.

- Stork now supports bidirectional cluster pairing for Asynchronous DR migration.

- Stork will update StorageClass on PV objects after the PVC migration.

- Fixed CVE-2020-26160 vulnerability by updating the JWT package.

### Fixes​

-
Issue: Failback to primary cluster failed when an app used Portworx CSI volumes, as the volumeHandle pointed to the old volume ID.
User Impact: App did not come up on the primary cluster after failback.
Resolution: Recreate the PVs and specify the correct volume name in the volumeHandle field of the spec. As a result, the app will use properly bound PVCs and will come up without any issue.

-
Issue: Could not find resources for the Watson Knowledge Catalog.
User Impact: Migration failed for the Watson Knowledge Catalog.
Resolution: Use the proper plurals for the CRDs for a successful migration process for the Watson Knowledge Catalog.

-
Issue: Service and service account updates did not reflect on the destination cluster.
User Impact: Migration failed to keep updated resources on the destination cluster.
Resolution: During migration, you need to sync service updates, merge secrets associated with the service account, and update the AutomountServiceAccountToken param for the service account on the destination cluster.

## 23.2.1​

March 29, 2023

### Fixes​

-
Issue: px-backup needs a way to know the custom admin namespace configured in stork deployment.
User Impact: px-backup users were unable to use the custom admin namespace configured in stork deployment.
Resolution: Added a configmap stork-controller-config in kube-system namespace with the details of admin namespace.

-
Issue: rule cmd executor pods were always getting created/started in kube-system namespace.
User Impact: Users had concerns about running the stork rule pods in kube-system namespace.
Resolution: Fixed it to run the rule cmd executor pods in the namespace where stork is deployed.

## 23.2.0​

March 10, 2023

note

- Starting with 23.2.0, the naming scheme for Stork releases has changed. Release numbers are now based on the year and month of the release.

- Customers upgrading to stork 23.2.0 will need to update `storkctl` on their cluster. This is required to correctly set up migration with Auto Suspend.

### Improvements​

- Stork will migrate all the CRDs under the same group for which CR exists if it is for a different kind.

- Stork will update the owner reference for PVC objects on the destination cluster.

- Added support for gke-gcloud-auth-plugin required for authenticating with GKE.

### Fixes​

-
Issue: Users were unable to migrate Confluent Kafka resources during failback.
User Impact: Confluent Kafka application failback was unable to bring up the application.
Resolution: Stork will now remove any finalizers on the CRs when deleting the resource during migration so that a new version of the resource can be recreated.

-
Issue: Migration was suspended after failback if autosuspend was enabled.
User Impact: After failback, the existing migration schedule was not being resumed, which caused the secondary cluster not to sync.
Resolution: With the fix, the primary cluster's migration schedule will correctly detect if migration can be resumed to secondary.

-
Issue: The Confluent Kafka operator was not able to recognize service sub resources during Async-DR migration.
User Impact: Application pods for Confluent Kafka were not able to start.
Resolution: Stork will not migrate Service resources if the owner reference field is set.

-
Issue: Stork was throwing the error `Error migrating volumes: Operation cannot be fulfilled on migrations.stork.libopenstorage.org: the object has been modified; please apply your changes to the latest version and try again`.
User Impact: This error caused unnecessary confusion during migration.
Resolution: Stork no longer raises this event as it retries the failed operation.

-
Issue: Users were not allowed to take backups based on namespace labels.
User Impact: Users had to manually select the static namespaces list for backup schedules. Dynamic selection of the namespace list based on the namespace label was not possible.
Resolution: With namespace label support, users can specify the namespace label such that the list of namespaces with those label will be selected dynamically for backups.

-
Issue: The Rancher project association for the Kubernetes resources in the Rancher environment was not backed up and restored.
User Impact: Since the project configurations are not restored, some applications failed to come up.
Resolution: Project settings are now backed up and applied during the restore. Users can also change to a different project with project mapping during restore.

-
Issue: Users were not able to specify the option to use the default storage class configured on the restore cluster in storage class mapping.
User Impact: Users were not able to use the default storage class for restore.
Resolution: Now users can mention `use-default-storage-class` as the destination storage class in the storage class mapping if they want to use the default configure storage class from the restore cluster.

note

If you are looking for release notes of older releases, refer to GitHub page.

In this topic:
