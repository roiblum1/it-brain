# Migrate Portworx Datastore from PX-StoreV1 to PX-StoreV2

Source: https://docs.portworx.com/portworx-enterprise/how-to-guides/migrate-storev1-to-storev2 (Portworx Enterprise latest)

Migrate Portworx Datastore from PX-StoreV1 to PX-StoreV2 | Portworx Enterprise Documentation

The Portworx Operator can automatically migrate your Portworx datastore from PX-StoreV1 to PX-StoreV2 using an in-place rolling conversion. The Operator manages the migration, including preflight checks, node conversion, data evacuation, and cluster health monitoring.

## How the migration works​

The Operator performs the following steps to migrate your cluster from PX-StoreV1 to PX-StoreV2:

-
Preflight checks: Verify that all nodes meet the PX-StoreV2 requirements. For more information, see System requirements.

-
Enable mixed mode: Allow PX-StoreV1 and PX-StoreV2 nodes to coexist temporarily during the migration by updating the StorageCluster with PX-StoreV2 settings. The Operator injects `allow_mixed_mode=1` into the runtime options, merging it with any existing runtime options you have configured. When the same option is set in multiple places, the Operator applies the following priority order (highest to lowest): node-level `miscArgs` → cluster-level `miscArgs` annotation → node-level `spec.runtimeOptions` → cluster-level `spec.runtimeOptions`.

-
Select nodes for migration: The Operator selects both storageless and storage nodes for migration in parallel:

- Storageless nodes: Multiple storageless nodes (default: 2 nodes at a time) are selected and migrated in parallel batches.

- Cluster health gate for storage nodes: Before selecting the next storage node, the Operator verifies that Portworx is online on every node in the cluster. If any node isn't online, node selection is deferred until the next reconcile. This check doesn't apply to storageless node selection.

- Storage nodes: One storage node is selected at a time based on the highest used space. Selection logic varies based on the number of already migrated StoreV2 nodes:

- First 3 storage nodes: Pool drain is performed without specifying target nodes, data can evacuate to any available node (PX-StoreV1 or PX-StoreV2) with sufficient capacity.

- After migrating 3 nodes: A node is selected only if the PX-StoreV2 nodes collectively have sufficient free space. Pool drain is directed specifically to the PX-StoreV2 target nodes to ensure data migrates to StoreV2 storage.

-
Per-node preflight checks: Before cordoning a selected node, the Operator runs per-node preflight checks to verify the node is ready for migration. These checks run independently of the cluster-wide preflight DaemonSet from step 1. The following checks are performed:

- KVDB quorum healthy: KVDB quorum must be healthy before any node is drained.

- Portworx health on source node: The source PX node must report `STATUS_OK`. If the node is not healthy, the check retries for up to 10 minutes before failing migration. Skipped for storageless nodes. This checks only the source node; the cluster-wide check that every node is online runs earlier, before the node is selected.

- Sufficient free pool space: The source node's pools must have at least 10% free space. If free space is below this threshold, the check retries for up to 10 minutes before failing migration. Skipped for storageless nodes. In practice, a source pool rarely reaches this threshold while still healthy — it typically goes `PoolFull`/`StorageDown` first, which fails the Portworx health on source node check above. Whether the drain itself succeeds depends on target-node capacity, not this source-side threshold.

- Kubernetes node Ready: The Kubernetes node must be Ready so that the node-wiper pod can be scheduled. If the node is not Ready, the check retries for up to 10 minutes before failing migration.

- Cloud drive ConfigMap reachable (cloud storage only): The cloud-drive ConfigMap must be reachable via the Kubernetes API. If unreachable, the check retries for up to 10 minutes before failing migration.

Results are recorded in the NodeDrain CR under `Status.Preflight`.

-
Cordon the nodes: Prevent scheduling by cordoning the selected source nodes.

-
Drain volume attachments: Drain all volume attachments from the source nodes.

-
Reduce replication factor (Three storage node clusters only): The Operator temporarily reduces the HA level from 3 to 2 for volumes that have a replica on the source node, excluding snapshots. This step is required because only 2 nodes remain available while the source node is being converted. This step doesn't apply to clusters with four or more nodes.

-
Evacuate data: Run pool drain to migrate data from storage nodes to other nodes in the cluster. For storageless nodes, a NodeDrain job is created only if there are volume attachments to drain. All snapshots on the cluster are deleted during migration.

- Four or more nodes: Pool drain removes snapshots as part of this step.

- Three storage node clusters only: The Operator removes each snapshot's replica explicitly from the source node.

-
Stop, decommission, wipe, and restart: Stop Portworx on the source node. For internal KVDB clusters, if the node runs a KVDB member, the Operator first confirms all KVDB members are healthy so migration doesn't reduce KVDB quorum. The Operator then decommissions the node from the cluster, wipes it, and restarts it with PX-StoreV2. For cloud storage, new drives are provisioned. For local storage, the same drives are reused.

-
Restore replication factor (Three storage node clusters only): Once Portworx has restarted and the node is back online, the Operator restores the HA level back to 3 for the volumes on the source node that it reduced in step 7.

-
Repeat: Repeat the node-selection and conversion steps until all nodes are converted to PX-StoreV2. Storage and storageless node migrations can run concurrently.

The Operator converts one storage node at a time to maintain cluster availability and resilience. During migration, the cluster operates in mixed mode with both PX-StoreV1 and PX-StoreV2 nodes. The Operator temporarily disables Autopilot to prevent interference with pool drain or rebalance operations and re-enables Autopilot after the migration completes.

## Limitations​

- External KVDB: Migration is not supported for clusters using external KVDB.

- Migration concurrency: Only one storage node migrates at a time. However, multiple storageless nodes (default is 2) can be migrated in parallel.

- No new volumes during migration: Don't create any new volumes while migration is in progress. This can cause the pool drain job for the node being migrated to fail or get stuck.

- Quorum risk with internal KVDB (Three storage node clusters only): Migrating a three storage node cluster with internal KVDB carries a quorum risk, because only 2 KVDB members remain available while a node is being converted. You must explicitly acknowledge this risk before migration starts. For more information, see Migrate your cluster.

- If your cluster has more than three nodes but you have the `px/metadata-node=true` label on nodes that allow only three nodes to run the internal KVDB, you must update the labels to run KVDB on at least four nodes before starting the migration, unless you intend to migrate it as a three storage node cluster. For more information, see Control internal KVDB node placement.

- Local snapshots are deleted during migration: All snapshots on the cluster are deleted as part of the migration. Back up or export any snapshots you need before starting migration.

- Pool drain duration depends on replica resynchronization speed: During migration, pool drain evacuates data from the source node and waits for replicas to resynchronize fully before moving volumes. If resynchronization is slow—for example, because of high application I/O or limited network bandwidth—pool drain can take much longer, which increases the overall migration time.

- Portworx upgrades: Portworx upgrade is not supported during migration. If a Portworx upgrade is triggered while migration is InProgress, the Operator blocks the upgrade and marks the Portworx upgrade condition as Paused in the StorageCluster until migration completes.

- Kubernetes upgrades: Kubernetes upgrade is not supported during migration. Perform upgrades only before starting the migration or after it completes.

- VM restarts: KubeVirt VMs restart during the PX-StoreV1 to PX-StoreV2 migration.

- Mixed mode: Supported only during migration, not for long-term deployment.

- Volumes with StorageClass node constraints: Volumes created from a StorageClass with the `parameters.nodes` parameter set cannot be migrated automatically. Pool drain cannot relocate these volumes because the node constraint prevents placement on any other node.

- Clusters with Volume Placement Strategies (VPS): If any VolumePlacementStrategy (VPS) CRD exists in the cluster, the Operator doesn't specify target nodes when migrating a storage node — even if the VPS doesn't apply to that node. Pool drain's own node-selection logic evaluates VPS rules and picks eligible target nodes instead, so the NodeDrain custom resource for the migration shows no target nodes. Make sure the nodes eligible under your VPS rules have enough combined free capacity, accounting for replication factor, to absorb the evacuated data; if no eligible node has enough capacity, pool drain stalls and migration can't progress until you add capacity or relax the VPS. For more information, see Volume Placement Strategies.

## Supported platform and distributions​

The following platforms and distributions support PX-StoreV1 to PX-StoreV2 migration:

PlatformDistribution

FlashArrayVanilla Kubernetes, OpenShift Container Platform (OCP), Anthos, SUSE Rancher Kubernetes Engine (RKE2)

vSphereVanilla Kubernetes, OCP, Anthos, RKE2

DAS/SANVanilla Kubernetes, OCP, Anthos, RKE2

Google CloudGoogle Kubernetes Engine (GKE)

AWSElastic Kubernetes Service (EKS)

AzureAzure Kubernetes Service (AKS)

note

For more information about supported backends with PX-StoreV2, see Supported Platforms and Distributions.

## Prerequisites​

Before starting the migration, make sure the following requirements are met:

-
Portworx version: 3.7.0 or later.

-
Operator version: 26.4.0 or later.

-
Cluster health: All nodes must be healthy and online.

-
Storage pools: No pools are in a degraded or offline state.

-
KVDB health (for internal KVDB clusters): All KVDB members must be healthy and reachable. The Operator verifies KVDB quorum before starting migration, and again before decommissioning any node that runs a KVDB member, to avoid losing quorum if a different member goes down mid-migration.

-
Cluster size: Migration is supported on clusters with a minimum of 4 nodes using internal KVDB. Three storage node clusters with internal KVDB are also supported, but require an explicit acknowledgment of the quorum risk. For more information, see Limitations.

-
Capacity: Sufficient free space to evacuate the largest node. After the migration, PX-StoreV2 reserves internal space on each pool when the pool is created for metadata and recovery purposes. The overhead varies by pool capacity and can range from approximately 6 GiB for pools smaller than 1 TiB to up to approximately 45 GiB for pools that are 8 TiB or larger. Plan for this reduction in available capacity across all pools before you start the migration.

When planning capacity, also account for the largest individual volumes. Pool drain places one replica on a single target node, regardless of the volume's replication factor. The target node must have free space at least equal to the volume size. If no target node can accommodate a volume, pool drain stops and migration cannot progress until you add capacity.

-
System metadata device: The StorageCluster is configured with a system metadata device (`systemMetadataDevice`) sized appropriately (typically at least 64 GiB). Note that the Operator configures `cloudStorage.systemMetadataDeviceSpec` automatically if you are using cloud storage.

-
Kernel support: All nodes must use kernel modules that PX-StoreV2 supports. For more information, see Supported kernels.

-
Required packages for local storage: For nodes using local drives, install `lvm2`, `dmsetup`, `mdadm`, and `augeas` (provides `augtool`) before starting migration. PX-StoreV2 uses device-mapper thin provisioning (dm-thin), which depends on these packages. For more information, see Software requirements. On OpenShift (Red Hat Enterprise Linux CoreOS) nodes, you can't install `augeas`, and migration can fail the preflight check. For more information, see the known issue.

-
Resources: Each node must meet minimum CPU and memory requirements. For more information, see System requirements.

-
Snapshot schedules: All volume snapshot schedules must be suspended before migration starts. If a snapshot schedule fires while pool drain is in progress, it places a new snapshot replica on the source pool, causing the drain to loop.

List and suspend Stork VolumeSnapshotSchedules:

```

storkctl get volumesnapshotschedules --all-namespaces

storkctl suspend volumesnapshotschedules <schedule-name> -n <namespace>

```

You can also suspend a schedule by setting `spec.suspend` to `true` on the VolumeSnapshotSchedule object. For more information, see VolumeSnapshotSchedule.

To disable pxctl-based snapshot schedules on individual volumes:

```

pxctl volume snap-interval-update --periodic 0 <volume-id>

```

-
Cluster autoscaler (cloud platforms only): If your cluster runs on a cloud platform with a cluster autoscaler enabled (for example, AKS, EKS, or GKE), disable the autoscaler, or set its minimum node count equal to its maximum, before starting migration. During the node restart step, the newly wiped node briefly appears storageless before PX-StoreV2 initializes and the operator marks its Portworx pod as safe to evict. If the autoscaler remains enabled and considers the cluster underutilized during this window, it can scale down and permanently delete the node being migrated, which blocks migration.

important

The skip label does not exclude nodes from these prerequisites. Preflight checks and the pre-migration validation script evaluate every node and fail if any node, labeled or not, is offline or unhealthy.

## Run pre-migration validation​

Before you start the migration, run the pre-migration validation script to verify that your cluster meets all requirements. This script performs comprehensive checks, including pod health, license validation, cluster capacity, pool health, node resources, disk capacity, and custom labels.

Prerequisites:

- Python 3.8+

- `kubectl` configured with access to your Kubernetes cluster

- Access to the Portworx namespace

-
Download the validation script and make it executable:

```

curl -O https://docs.portworx.com/portworx-enterprise/scripts/migration_validator.py

chmod +x migration_validator.py

```

-
Install the required Python package:

```

pip3 install pyyaml

```

-
Run the validation script:

```

./migration_validator.py -n <portworx>

```

Command-line options:

- `-n, --namespace`: Portworx namespace (required, or the script prompts you interactively)

- `-o, --output`: Save the detailed report to a file (for example, `-o report.txt`)

- `-v, --verbose`: Enable debug logging to troubleshoot issues

Exit codes:

- `0`: All validations passed. Ready for migration.

- `1`: Critical or error issues found. Migration is blocked.

- `2`: Warnings are present. Proceed with caution.

The script generates a detailed validation report that includes information such as Pod health, cluster capacity, cloud storage validation, pool health, and a migration readiness summary at the end.

-
Review the validation report and resolve any blocking issues before you proceed with migration.

For detailed configuration options and example output, see the validation script readme.

## Migrate your cluster​

After running the pre-migration validation script and fixing any blocking issues, perform the following steps to migrate your Portworx cluster from PX-StoreV1 to PX-StoreV2:

-
If you are using local storage, verify that your StorageCluster is configured with a system metadata device. For configuration details, see the StorageCluster CRD reference (`spec.storage.systemMetadataDevice`).

-
(Optional) Exclude specific nodes from migration by labeling each node:

```

kubectl label node <node-name> portworx.io/skip-pxStorev2-migration="true"

```

The Operator respects this label only once migration status is InProgress (from NodeDrain job creation onward) — not during preflight checks or the validation script. Labeled nodes continue running PX-StoreV1, and migration still completes for the remaining nodes. If all nodes have this label, the migration status is Skipped.

Use this label to defer migration on a node, not to exclude an offline or unhealthy one. Bring offline nodes back online instead of relying on the label to work around them.

-
(Optional) Configure the number of storageless nodes to migrate in parallel. By default, the Operator migrates 2 storageless nodes at a time. To change this, add the following annotation to your StorageCluster:

```

metadata:

  annotations:

    portworx.io/max-storageless-nodes-to-migrate: "3"

```

Replace `"3"` with your desired number. This annotation affects only storageless nodes. Storage nodes are always migrated one at a time.

-
Edit the StorageCluster to add the `portworx.io/migrate-v1-to-v2` annotation with a timestamp value:

- Four or more storage node clusters

- Three storage node clusters

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: <px-cluster>

  namespace: <portworx>

  annotations:

    portworx.io/migrate-v1-to-v2: "2 Jan 2026 3:04 PM"

...

```

You must also add the `portworx.io/migrate-storev1-to-v2-force-ack=true` annotation, in addition to `portworx.io/migrate-v1-to-v2`, to acknowledge the quorum risk of running with only 2 KVDB members while a node is being converted. Migration will not start without this annotation.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: <px-cluster>

  namespace: <portworx>

  annotations:

    portworx.io/migrate-v1-to-v2: "2 Jan 2026 3:04 PM"

    portworx.io/migrate-storev1-to-v2-force-ack: "true" # Three storage node clusters only

...

```

The following timestamp formats are also supported:

- `"2 January 2026 3:04 PM"` (full month name)

- `"Mon Feb 2 23:48:51 IST 2026"` (terminal format)

- `"02-01-2026 15:04:05"` (dd-MM-yyyy HH:mm:ss)

- `"2026-01-02 15:04:05"` (yyyy-MM-dd HH:mm:ss)

The timestamp value determines when the migration starts:

- If the timestamp is in the future, the migration waits until that time.

- If the timestamp is in the past or current, the migration starts immediately.

note

During migration, the Operator updates the StorageCluster fields. This triggers a rolling update of Portworx pods.

-
Monitor the migration status:

```

kubectl get storagecluster <px-cluster> -n <portworx> -o yaml

```

```

status:

conditions:

- type: PXStoreMigration

  status: InProgress

  message: "PX store migration is in progress"

```

Check the migration condition in the status section. The migration can be in one of the following states:

- Pending: Preflight checks are running.

- Ready: Preflight passed, and the migration is ready to start.

- InProgress: Migration is actively converting nodes. Storageless nodes migrate in parallel batches, and storage nodes migrate one at a time. Both types can be migrated concurrently.

- Failed: Migration failed due to an error or was canceled. Check the `message` field for details.

- Completed: All nodes successfully converted to PX-StoreV2, or migration completed with some nodes skipped due to skip labels.

- Skipped: All nodes are already running PX-StoreV2, or all nodes have the skip migration label.

-
Monitor node conversion progress:

```

kubectl get pods -n <portworx> -l name=portworx

```

You can also check NodeDrain custom resources (CRs) to see which nodes are being migrated:

```

kubectl get nodedrain -n <portworx>

```

The output shows the migration job status for each node, including whether it's a storageless or storage node.

For more details, describe a NodeDrain CR:

```

kubectl describe nodedrain <node-drain-name> -n <portworx>

```

Each NodeDrain CR reports a condition for every step described in How the migration works, showing whether that step is complete, in progress, or failed, along with a message explaining why. For the full list of condition types, their meanings, and the `status.phase` values, see the NodeDrain CRD reference.

If per-node preflight checks are failing, check the `Status.Preflight` field on the NodeDrain CR for the individual check results (Three storage node clusters only: available in Operator 26.4.0 and later):

```

kubectl get nodedrain <node-drain-name> -n <portworx> -o jsonpath='{.status.preflight}'

```

-
Check for migration events:

```

kubectl get events -n <portworx> --sort-by='.lastTimestamp'

```

Common events include:

- Preflight check results

- Node selection and migration start

- Warnings about insufficient capacity or missing nodes

- Migration progress updates

## Post-migration verification​

After the migration completes:

-
Verify all nodes are running PX-StoreV2:

```

pxctl status

```

Check for `PX-StoreV2` in the output.

-
Check cluster health:

```

pxctl cluster provision-status

```

-
Verify all volumes are healthy:

```

pxctl volume list

```

-
Check whether any nodes were skipped:

```

kubectl get nodes -l portworx.io/skip-pxStorev2-migration=true

```

If nodes were skipped, they are still running PX-StoreV1. To migrate them, remove the skip label and re-annotate the StorageCluster to restart migration:

```

kubectl label node <node-name> portworx.io/skip-pxStorev2-migration-

kubectl annotate storagecluster <px-cluster> -n <portworx> \

  portworx.io/migrate-v1-to-v2="$(date -u +%Y-%m-%dT%H:%M:%SZ)" --overwrite

```

-
Remove the migration annotation (optional):

```

kubectl annotate storagecluster <px-cluster> -n <portworx> \

  portworx.io/migrate-v1-to-v2-

```

-
The Operator automatically removes the following from your StorageCluster after all nodes complete migration:

- The `allow_mixed_mode=1` runtime option

- Node labels `portworx.io/pxStorev2-migrated-node`

The `-T PX-StoreV2` flag is retained in the StorageCluster CRD.

note

If some nodes were skipped due to skip labels, the mixed mode configuration remains in place until you complete migration for those nodes or manually remove the configuration.

-
Resume any snapshot schedules you suspended before migration:

```

storkctl resume volumesnapshotschedules <schedule-name> -n <namespace>

```

If you disabled pxctl-based snapshot schedules, re-enable them on each volume using the original schedule settings you noted before migration.

-
If you disabled the cluster autoscaler or changed its minimum node count before migration, restore its original configuration.

## Troubleshooting​

If you have any issues during migration, describe the relevant NodeDrain CR and review its per-step conditions to identify where the migration is stalled or has failed.

-
Pool drain stops because no target node has enough free space to accommodate a large volume. The source node is cordoned and volume attachments are disabled, but migration doesn't progress.

Symptom: Pool drain logs contain `free size must be >= X`.

Recovery:

-
Get the pool drain job ID from the NodeDrain CR:

```

kubectl get nodedrain -n <portworx> -o wide

```

-
Cancel the pool drain job. After cancellation, the migration marks itself as Failed, the Operator uncordons the source node, and volume attachments are re-enabled. Wait a few minutes for any affected pods to return to the `Running` state.

```

pxctl service pool drain cancel --job-id <job-id>

```

-
Add capacity so that at least one target node can accommodate the volume:

-
Cloud drives: Expand the pool on a target node:

```

pxctl service pool expand -o <mode> -s <size> -u <pool-uid>

```

-
Preprovisioned drives: Either add a new node with sufficient capacity to the cluster, or decommission an existing node (either an already-migrated PX-StoreV2 node or a PX-StoreV1 node), add drives to it by updating the StorageCluster node spec, and then recommission it. Move volume replicas off the node before decommissioning. A recommissioned PX-StoreV1 node restarts as PX-StoreV2.

-
Restart the migration:

```

kubectl annotate storagecluster <px-cluster> -n <portworx> \

  portworx.io/migrate-v1-to-v2="$(date -u +%Y-%m-%dT%H:%M:%SZ)" --overwrite

```

-
If the migration fails, follow these steps to troubleshoot:

-
Check the StorageCluster status for error details:

```

kubectl get storagecluster <px-cluster> -n <portworx> -o jsonpath='{.status.conditions[?(@.type=="PXStoreMigration")]}'

```

-
Review the Operator logs:

```

kubectl logs -n <portworx> -l name=portworx-operator

```

-
Check the status of NodeDrain CRs:

```

kubectl get nodedrain -n <portworx> -o yaml

kubectl describe nodedrain <node-drain> -n <portworx>

```

The NodeDrain status determines the recovery path:

-
Canceled: The migration automatically marks itself as Failed and sets `LastMigrationState` to enable restart. The Operator automatically uncordons the affected nodes. When you restart the migration, canceled `NodeDrain` custom resources (CRs) are reset to `NotStarted`.

-
Failed: Review the `NodeDrain` CR details to determine the recovery steps before restarting:

-
Node started in a storageless state: Review the Portworx logs on the affected node and the NodeDrain CR for error details. If you cannot resolve the issue, contact support. When you restart the migration, the Operator replays the failed NodeDrain CR from its first non-succeeded step. If the node cannot be recovered through the replay, delete the NodeDrain CR and remove the `portworx.io/pxStorev2-migrated-node` label from the node, then restart the migration to force a clean retry:

```

kubectl delete nodedrain <node-drain-name> -n <portworx>

kubectl label node <node-name> portworx.io/pxStorev2-migrated-node-

```

-
Node started as `PX-StoreV1` (`btrfs`) again: The node was not successfully converted. Delete the failed `NodeDrain` custom resource (CR) and remove the `portworx.io/pxStorev2-migrated-node` label from the affected node before you restart the migration:

```

kubectl delete nodedrain <node-drain-name> -n <portworx>

kubectl label node <node-name> portworx.io/pxStorev2-migrated-node-

```

-
Restart the migration by updating the annotation timestamp:

```

kubectl annotate storagecluster <px-cluster> -n <portworx> \

  portworx.io/migrate-v1-to-v2="$(date -u +%Y-%m-%dT%H:%M:%SZ)" --overwrite

```

When you restart a failed migration, the Operator resumes from the migration phase recorded at the time of failure: either `Pending` to re-run preflight checks, or `InProgress` to continue node migration. Nodes already running PX-StoreV2 are not re-migrated. Cancelled NodeDrain CRs are reset to `NotStarted` and retried. Failed NodeDrain CRs are replayed from their first non-succeeded step — the Operator increments `Spec.Restart.Attempt` on the NodeDrain CR, which causes the controller to re-run steps from the point of failure rather than skipping the node.

## Known issues​

-
On OpenShift Container Platform (OCP) environments, NFS kernel threads can get stuck in an uninterruptible sleep state. These stuck threads prevent unmounting of encrypted SharedV4 volumes even when there is no active I/O on the device. As a result, the node drain-attachments job times out and migration stalls on the affected node.

Symptoms:

- The drain-attachments job shows `FAILED` with the message `job timed out and node still has volume attachments`.

- `umount` on the affected volume returns `target is busy` even though the `inflight` I/O count is zero.

- NFS kernel threads (`mount.nfs`) appear in the `D` (uninterruptible sleep) state in `ps` output.

Workaround: Reboot the affected node. This releases the stuck kernel NFS threads, allowing migration to proceed.

-
Three storage node clusters only: The Operator identifies repl3 volumes on the source node once, early in that node's migration, and reduces only those to replication factor 2. A repl3 volume created on the source node afterward is never reduced, and on a three-node cluster there's no other node available to hold its third replica. Pool drain then has no valid way to evacuate it, and the node's migration stalls indefinitely with no clear error. This can happen without any direct action from you — for example, KubeVirt/CDI `DataImportCron` jobs periodically create temporary repl3 scratch volumes during scheduled OS image imports.

Symptoms:

- Migration makes no progress on the affected node, and the NodeDrain CR doesn't report a clear failure reason.

- A volume with `ha_level: 3` and a replica on the source node exists, but isn't tracked in the NodeDrain CR's `Status.Repl3VolumeIDs`.

Workaround: Avoid creating new volumes during migration. If migration on a three-storage-node cluster appears stalled, check for repl=3 volumes on the source node created after migration started, and manually reduce their replication factor to 2. If your cluster runs KubeVirt with `DataImportCron` scheduled imports, pause them for the duration of the migration.

-
OpenShift clusters using local drives: Migration fails during preflight checks with the error `package augtool not found`. Red Hat Enterprise Linux CoreOS (RHCOS) is immutable, doesn't include `augtool`, and doesn't support installing additional packages. Portworx doesn't require `augtool` on these nodes, so the preflight failure doesn't reflect a problem with the node. Clusters that use cloud drives and fresh PX-StoreV2 installations aren't affected.

Symptoms:

- The `PXStoreMigration` condition on the StorageCluster shows `Failed` with the message `PX store migration failed due to preflight checks failure`.

- The preflight result on each node reports `package augtool not found`.

Workaround: Contact the Everpure support for assistance.

In this topic:
