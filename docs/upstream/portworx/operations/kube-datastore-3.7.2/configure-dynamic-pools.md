# Set Up KDS Dynamic Pools on a Portworx Cluster

Source: https://docs.portworx.com/portworx-enterprise/operations/kube-datastore-3.7.2/configure-dynamic-pools (Portworx Enterprise latest)

Set Up KDS Dynamic Pools on a Portworx Cluster | Portworx Enterprise Documentation

You can enable Kube Datastore (KDS) dynamic pools during a new Portworx Enterprise installation or when upgrading an existing cluster. If your cluster already uses dynamic pools, you can upgrade Portworx Enterprise while retaining the existing dynamic pool configuration.

You can also migrate existing virtual machines (VMs) from VMware to OpenShift Virtualization on Kube Datastore.

note

You can enable dynamic pools without configuring KDS affinity for workloads. KDS affinity is required only when you want to place volumes on a specific Kube Datastore.

Choose the procedure that matches your environment:

ScenarioDescriptionProcedure

Fresh installationInstall a new Portworx Enterprise cluster with dynamic pools enabled.Install Portworx Enterprise with dynamic pools enabled

Existing cluster without dynamic poolsUpgrade Portworx Enterprise and enable dynamic pools for the first time. This workflow requires preparing existing volumes by using the migration tool. Contact Portworx Support for the migration tool.Upgrade a cluster that does not have dynamic pools enabled

Existing cluster with dynamic poolsUpgrade Portworx Enterprise while retaining the existing dynamic pool configuration.Upgrade a cluster that already uses dynamic pools

VMware migrationMigrate existing VMware VMs to OpenShift Virtualization on Kube Datastore.Migrate VMs from VMware to Kube Datastore

## Prerequisites​

Before enabling dynamic pools, ensure that your environment meets the following requirements:

- Portworx Enterprise 3.7.2 or later is installed.

- Portworx Operator 26.5.0 or later is installed.

- Stork 26.5.0 or later is installed.

- The cluster uses FlashArray Cloud Drives (FACD) as the storage backend.

- The cluster uses PX-StoreV2.

- The cluster runs on a supported platform.

- TCP port `17024` is open between Portworx nodes. Fast node-down detection uses this port for the host-level liveness service. Ensure that network policies, host firewalls, security groups, and other network controls allow communication over this port.

- If you plan to use PX-Fast volumes on dynamic pools, ensure that all nodes in the cluster run PX fuse kernel driver version 3.7.2 or later. For remote fastpath, also review the remote fastpath prerequisites.

- Pools that use dynamic pool failover do not contain SharedV4 volumes, volumes with journal profiles, or volumes with a replication factor greater than 1.

note

For an existing cluster that does not yet use dynamic pools, the migration tool helps prepare eligible volumes. Review the cluster eligibility requirements before enabling dynamic pools.

### Additional requirements for upgrades​

Before upgrading an existing cluster:

- Verify that the KubeVirt live migration settings, including `bandwidthPerMigration` and `completionTimeoutPerGiB`, are configured for your VM workloads. Incorrect settings can delay or prevent VM live migrations and potentially block the Portworx Enterprise or OpenShift Container Platform (OCP) upgrade. For more information, see the Red Hat documentation on VM live migration settings.

- Allow sufficient time for the upgrade based on the cluster configuration and the number of pools to relocate. When dynamic pools are enabled, the Portworx Operator relocates dynamic pools from each node before restarting Portworx on that node. Portworx relocates pools sequentially, which can increase the overall upgrade duration.

## Install Portworx Enterprise with dynamic pools enabled​

To install a new Portworx Enterprise cluster with dynamic pools enabled, follow the FlashArray installation procedure and enable dynamic pools when generating the Portworx specification.

-
Prepare your environment for installing Portworx with FlashArray.

-
Sign in to Portworx Central and generate the Portworx specification:

-
In the Generate Portworx Specification section, select OpenShift 4+ as the distribution and click Customize.

-
On the Storage tab:

- Select PX-Store V2 as the datastore type.

- Select Enable Dynamic Pools.

For more information, see Generate Portworx Specification.

The generated specification includes the following fields:

```

spec:

  kubeDatastore:

    enableDynamicPools: true

  cloudStorage:

    provider: pure

```

The `enableDynamicPools` field enables dynamic pools, and `cloudStorage.provider` specifies Pure Storage as the cloud storage provider.

note

Reserve enough pool slots on each node to accommodate pools relocated during failover. Set `limit_pools_count` to four more than the number of pools you plan to create per node. The maximum value is `16`, and the default is `8`. For more information, see Plan pool capacity for failover.

-
(Optional) If your environment has multiple FlashArrays, choose which FlashArray backs each storage pool. For more information, see Provision storage pools from a specific FlashArray.

-
(Optional) If you use Secure Multi-Tenancy (SMT), you can place Portworx system volumes in specific FlashArray pods. For more information, see Customize Portworx system volumes for secure multi-tenancy.

-
Complete the installation by applying the specification. For more information, see Apply Portworx Specification.

-
Verify that `px-rwx-block-kubevirt-repl1` is the default KubeVirt StorageClass.

note

When dynamic pools are enabled, Portworx Operator replaces `px-rwx-block-kubevirt` with `px-rwx-block-kubevirt-repl1` as the default KubeVirt `StorageClass` by adding the `storageclass.kubevirt.io/is-default-virt-class: "true"` annotation to `px-rwx-block-kubevirt-repl1` during installation. For more information, see Create a StorageClass.

-
Verify that dynamic pools are enabled:

-
Check the `StorageCluster` configuration:

```

kubectl get stc -n portworx <storage-cluster-name> -o jsonpath='{.spec.kubeDatastore}'

```

Replace `<storage-cluster-name>` with the name of your `StorageCluster`.

Verify that the output includes:

```

{"enableDynamicPools":true}

```

-
Check the `StorageCluster` status:

```

kubectl get stc <storage-cluster-name> -n portworx

```

Wait until the `STATUS` field displays `Running`. The status might display `Updating` while Portworx applies the configuration.

note

When you enable dynamic pools, Portworx adds a metadata drive to all non-storageless nodes. This drive supports dynamic pool operations and remains attached to its node during pool relocation.

## Upgrade a cluster that does not have dynamic pools enabled​

Use this procedure when upgrading an existing Portworx Enterprise cluster that does not have dynamic pools enabled.

This procedure involves the following steps:

- Upgrade Portworx Enterprise and enable dynamic pools.

- Use the migration tool to identify and resolve conditions that prevent pool failover and prepare existing volumes. Contact Portworx Support for the migration tool.

- Use the pool descheduler to assign pools to affinity groups. Rebalance then moves pools based on these assignments.

### Verify cluster eligibility​

Before upgrading, verify that the cluster meets the following requirements:

RequirementWhy it mattersAction

The cluster uses PX-StoreV2.Dynamic pools require PX-StoreV2.If the cluster uses PX-StoreV1, migrate to PX-StoreV2. See Migrate from PX-StoreV1 to PX-StoreV2.

The cluster uses FlashArray Cloud Drives.Dynamic pools require FACD storage.Dynamic pools cannot be enabled on other storage backends.

Each pool contains one drive.A dynamic pool requires one FACD per pool.Existing multi-drive pools cannot be converted to dynamic pools.

All pools and volumes are healthy.Unhealthy or full pools can prevent migration.Resolve health and capacity issues before continuing.

Pools intended to become dynamic do not contain SharedV4 volumes, volumes with `repl=2` or higher, or volumes with journal profiles.These volume types prevent pools from becoming dynamic.Use replica affinity rules to place these volumes in designated pools that remain static, so that the remaining pools meet the requirements for enabling dynamic pools.

All disks belonging to a VM use the same replication factor.Mixed replication factors prevent the required VM volume placement during conversion.Configure the same replication factor for all disks belonging to the VM.

Volumes intended for dynamic pools use `repl=1`.Dynamic pools require volumes with replication factor 1 (`repl=1`).Use replica affinity rules to place volumes with `repl=2` or higher in designated pools that remain static.

Resolve any conditions that prevent dynamic pool failover before continuing.

### Upgrade Portworx Enterprise and enable dynamic pools​

-
Upgrade Portworx Operator.

For more information, see Upgrade Portworx Operator.

-
Upgrade Portworx Enterprise. For more information, see Upgrade Portworx Clusters using the Operator.

-
Enable dynamic pools in the `StorageCluster` resource by adding the following fields:

```

spec:

  kubeDatastore:

    enableDynamicPools: true

  cloudStorage:

    provider: pure

```

important

- You can enable dynamic pools as part of a Portworx Enterprise upgrade only if the cluster is already running version 3.5.0 or later. Follow the appropriate sequence for steps 2 and 3 based on your current version:

-
If your cluster runs Portworx Enterprise 3.5.0 or later, apply the configuration in step 3 along with the version update in step 2 to enable dynamic pools during the upgrade.

-
If your cluster runs a version earlier than 3.5.0, complete the upgrade in step 2 before applying the configuration in step 3.

- Reserve enough pool slots on each node to accommodate pools relocated during failover. Set `limit_pools_count` to four more than the number of pools you plan to create per node. The maximum value is `16`, and the default is `8`. For more information, see Plan pool capacity for failover.

Verify that dynamic pools are enabled by following the verification steps in Install Portworx Enterprise with dynamic pools enabled.

-
Prepare existing volumes by using the migration tool.
The migration tool identifies conditions that prevent pool failover and prepares eligible volumes by handling replica reduction and volume colocation. Do not perform these operations manually because they can cause placement issues.

To obtain and run the supported migration tool, contact Portworx Support.

-
Verify that `px-rwx-block-kubevirt-repl1` is the default KubeVirt StorageClass.

If not, remove the `storageclass.kubevirt.io/is-default-virt-class: "true"` annotation from the current default StorageClass and add it to `px-rwx-block-kubevirt-repl1`. For more information, see Create a StorageClass.

-
(Optional) Generate a pool affinity group placement plan to help optimize pool distribution after converting volumes from `repl=2` to `repl=1`:

```

pxctl service pool affinity-group plan

```

-
Review the plan and apply it:

```

pxctl service pool affinity-group plan --apply

```

For more information, see Dynamic pool descheduler.

-
Wait for rebalance to complete.

Rebalance moves eligible pools according to their affinity group assignments. For more information, see Dynamic pool rebalance.

## Upgrade a cluster that already uses dynamic pools​

Use this procedure when upgrading an existing Portworx Enterprise cluster that already has dynamic pools enabled. Volumes that use dynamic pool failover already use `repl=1`, and existing KubeVirt volumes use pool-level topology.

After upgrading, use the pool descheduler to establish affinity group assignments for existing pools and rebalance their placement.

### Upgrade Portworx Enterprise​

-
Upgrade the Portworx Operator.

For more information, see Upgrade Portworx Operator.

-
Upgrade Portworx Enterprise.

For more information, see Upgrade Portworx Clusters using the Operator.

warning

With Portworx Operator 26.5.0, upgrading Portworx Enterprise from 3.7.0 to 3.7.2 does not relocate dynamic pools before restarting Portworx on each node. As a result, VMs using `repl=1` volumes can experience I/O interruptions while Portworx restarts on the nodes hosting their storage. Schedule the upgrade during a maintenance window.

To skip pool relocation during the upgrade, see Disable pool relocation during upgrades.

-
Run pool descheduler to generate a pool affinity group placement plan:

```

pxctl service pool affinity-group plan

```

For more information, see Dynamic pool descheduler.

note

You can also create affinity groups and assign pools to them manually instead of using a placement plan. For more information, see Pool affinity groups.

-
Review the plan and apply it:

```

pxctl service pool affinity-group plan --apply

```

-
Wait for rebalance to complete.

Rebalance moves eligible pools according to the updated affinity group assignments.

-
Verify pool placement and VM hyperconvergence:

```

pxctl service pool affinity-group --group-by node

```

Verify that `SPLIT` is `no` for affinity groups that should remain together.

## Migrate VMs from VMware to Kube Datastore​

You can migrate existing VMs from VMware to OpenShift Virtualization on Kube Datastore by using Rapid VM Migration. Rapid VM Migration uses the Migration Toolkit for Virtualization with `XCOPY` to offload data copying to FlashArray. For the complete procedure, see Rapid Migration of VMs from VMware to OpenShift Virtualization using XCOPY.

Rapid VM Migration supports initial hyperconvergence. For more information, see Use a WaitForFirstConsumer StorageClass for hyperconvergence.

In this topic:
