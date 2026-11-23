# Portworx Enterprise StorageClass

Source: https://docs.portworx.com/portworx-enterprise/reference/storageclass (Portworx Enterprise latest)

Portworx Enterprise StorageClass | Portworx Enterprise Documentation

Portworx Enterprise uses standard Kubernetes StorageClass resources with a set of PX-specific parameters for FlashArray and FlashBlade backend storage.

## Example of StorageClass​

The following is an example of a StorageClass configuration in Portworx Enterprise.

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

    name: elasticsearch-sc

provisioner: pxd.portworx.com

parameters:

  io_priority: high

  repl: "2"

  group: "amq_vg"

allowVolumeExpansion: true

```

## StorageClass Fields​

Using Storage Classes objects, an admin can define the different classes of Portworx Volumes that are offered in a cluster. The following table lists the fields in a StorageClass.

FieldDescriptionType

`apiVersion`The Kubernetes API version for the `StorageClass` object.string

`kind`The kind of Kubernetes object. This value is always `StorageClass`.string

`metadata.name`The name of the `StorageClass`.string

`provisioner`Specifies the CSI driver used for dynamic provisioning. For Portworx Enterprise, use `pxd.portworx.com`.string

`reclaimPolicy`Defines what happens to a volume when it's released from its claim. Options are `Delete` or `Retain`. See the Kubernetes documentation.string

`volumeBindingMode`Controls when volume binding and dynamic provisioning occur. Options are `Immediate` or `WaitForFirstConsumer`. See the Kubernetes documentation.string

`allowVolumeExpansion`Specifies whether the volume can be dynamically resized.boolean

`mountOptions`A list of mount options supported by the backend. Common examples: `nfsvers=3`, `tcp`, `nfsvers=4.1`.array

`parameters`Portworx Enterprise-specific configuration parameters. See below for details.object

## `parameters` fields​

NameDescriptionExample

fsSpecifies a filesystem to be laid out: xfs|ext4.

Note: The only preferred and default filesystem across all backends is ext4. The default backend can also support xfs.fs: "ext4"

replSpecifies the replication factor for the volume: 1|2|3repl: "3"

sharedv4Creates a globally shared namespace volume which can be used by multiple pods over NFS with POSIX compliant semanticssharedv4: "true"

sharedv4_svc_typeSpecifies whether Portworx creates a Sharedv4 service volume or a Sharedv4 volume.

Set to `"ClusterIP"` to create a Sharedv4 service volume. With this setting, pods access the volume through a Kubernetes service IP rather than through a specific node IP address. This is the default behavior.

Set to an empty string (`""`) to create a Sharedv4 volume. Use this value if the Portworx data network uses a private, non-routable network segment. For more information, see Create Sharedv4 PVCs.`sharedv4_svc_type: "ClusterIP"`

sharedv4_failover_strategySpecifies how aggressively to fail over to a new server for a Sharedv4 or Sharedv4 Service volume (Valid Values: aggressive, normal).

The default failover strategy for sharedv4 service volumes is aggressive, because these volumes are able to fail over without restarting all the application pods. For more information, see Sharedv4 failover and failover strategy.sharedv4_failover_strategy: "normal"

priority_ioSpecifies the I/O priority tier for placing volumes in storage pools: `low`, `medium`, or `high`. The default is `low`.
Portworx places volumes on storage pools that match the requested priority tier. This is a best-effort placement, not a guarantee of runtime bandwidth.priority_io: "high"

io_profileOverrides I/O algorithm that Portworx uses for a volume. For more information about IO profiles, see the IO profiles section of the documentation.io_profile: "db_remote"

kube_datastore_affinityPins the volumes created from this StorageClass to a single Kube Datastore (KDS), and therefore to a single FlashArray. Specify the name of one KDS. Portworx adds an internal replica affinity rule that places all volume replicas on the pools of that KDS, and combines this rule with any other placement rules that apply to the volume. Supported only for Portworx volumes on FlashArray Cloud Drive (FACD) storage pools. Not supported for FlashArray Direct Access (FADA) volumes. For more information, see Provision volumes with KDS-aware StorageClasses.kube_datastore_affinity: "fa-x90-1a"

groupSpecifies the group a volume should belong to. Portworx restricts replication sets of volumes of the same group on different nodes. If the force group option 'fg' is set to true, the volume group rule is strictly enforced. By default, it's not strictly enforced.group: "volgroup1"

fgEnforces volume group policy. If a volume belonging to a group cannot find nodes for its replication sets which don't have other volumes of the same group, the volume creation will fail.fg: "true"

labelArbitrary key: value labels that can be applied on a volumelabel: "name: mypxvol"

nodesSpecifies comma-separated Portworx Node IDs to use for replication sets of the volumenodes: "minion1,minion2"

ephemeralCreates the ephemeral volumesephemeral: false

sizeSpecifies a volume size in GB (default 1)size: "1073741824"

block_sizeSpecifies a block size in Bytes (default 4096)block_size: "4096"

queue_depthSpecifies a block device queue depth. (Valid Range: [1 256]) (default 128)queue_depth: 128

snap_intervalSpecifies an interval in minutes at which periodic snapshots will be triggered. Set to 0 to disable snapshots

snap_scheduleSpecifies the name of the snapshot schedule policy created using the `pxctl sched-policy` commandRefer to this page for examples

zonesSpecify comma-separated zone names in which the volume replicas should be distributed

racksSpecify comma-separated rack names in which the volume replicas should be distributed

async_ioEnables asynchronous IO processing on the backend drives and could be useful in situations where the workload profile is bursty in nature.

Please reach out to Portworx Support before enabling.async_io: false

csi_mount_optionsSpecifies the mounting options for a volume through CSI

sharedv4_mount_optionsSpecifies a comma-separated list of Sharedv4 NFS client mount options provided as key=value pairs

proxy_endpointSpecifies the endpoint address of the external NFS share Portworx is proxyingproxy_endpoint: "nfs://`<nfs-share-endpoint>`"

proxy_nfs_subpathSpecifies the sub-path from the NFS share to which this proxy volume has access

proxy_nfs_exportpathExports path for NFS proxy volumeproxy_nfs_exportpath: "/`<mount-path>`"

export_optionsDefines the export options. Currently, only NFS export options are supported for Sharedv4 volumes

mount_optionsSpecifies the mounting options for a volume when it is attached and mounted

best_effort_location_provisioningRequested nodes, zones, racks are optional

direct_ioEnables Direct IO on a volumedirect_io: "true"

scan_policy_triggerSpecifies the trigger point on which filesystem check is triggered. Valid Values: none, on_mount, on_next_mount

scan_policy_actionSpecifies a filesystem scan action to be taken when triggered. Valid Values: none, scan_only, scan_repair

force_unsupported_fs_typeForces a filesystem type that is not supported. The driver may still refuse to use the typeforce_unsupported_fs_type: false

match_src_vol_provisionProvisions the restore volume on the same pools as the source volume (src volume must exist)

nodiscardMounts the volume with nodiscard option. This is useful when the volume undergoes a large amount of block discards and later the application rewrites to these discarded block making the discard work done by Portworx useless. This option must be used along with `auto_fstrim`. Refer to this page for limitations on xfs formatted volumes.nodiscard: false

auto_fstrimEnables `auto_fstrim` on a volume and requires the `nodiscard` option to be set. Refer to this page for more details.auto_fstrim: true

storagepolicyCreates a volume on the Portworx cluster that follows the specified set of specs/rules. Refer to this page for more details.

backendSpecifies which storage backend Portworx is going to provide direct access to. (Valid Values: pure_block, pure_file)backend: "pure_block"

pure_export_rulesSpecifies the export rules for exporting a Pure Flashblade volumepure_export_rules: "*(rw)"

io_throttle_rd_iopsSpecifies maximum Read IOPs a volume will be throttled to. Refer to this page for more details.io_throttle_rd_iops: "1024"

io_throttle_wr_iopsSpecifies maximum Write IOPs a volume will be throttled to. Refer to this page for more details.io_throttle_wr_iops: "1024"

io_throttle_rd_bwSpecifies maximum Read bandwidth a volume will be throttled to. Refer to this page for more details.io_throttle_rd_bw: "10"

io_throttle_wr_bwSpecifies maximum Write bandwidth a volume will be throttled to. Refer to this page for more details.io_throttle_wr_bw: "10"

aggregation_levelSpecifies the number of replication sets the volume can be aggregated fromaggregation_level: "2"

stickyCreates sticky volumes that cannot be deleted until the flag is disabledsticky: "true"

journalIndicates if you want to use journal device for the volume's data. This will use the journal device that you used when installing Portworx. This is useful to absorb frequent syncs from short bursty workloads. Default: falsejournal: "true"

secureCreates an encrypted volume. For details about how you can create encrypted volumes, see the Create encrypted PVCs page.secure: "true"

placement_strategyFlag to refer the name of the `VolumePlacementStrategy`. For example:

`apiVersion: storage.k8s.io/v1`
`kind: StorageClass`
`metadata:`
` name: postgres-storage-class`
`provisioner: pxd.portworx.com`
`parameters:`
` placement_strategy: "postgres-volume-affinity"`

 For details about how to create and use `VolumePlacementStrategy`, see this page.placement_strategy: "postgres-volume-affinity"

snapshotschedule.stork.libopenstorage.orgCreates scheduled snapshots with Stork. For example:
`snapshotschedule.stork.libopenstorage.org/default-schedule:`
` schedulePolicyName: daily`
` annotations:`
` portworx/snapshot-type: local`
`snapshotschedule.stork.libopenstorage.org weekly-schedule:`
` schedulePolicyName: weekly`
` annotations:`
` portworx/snapshot-type: cloud`
` portworx/cloud-cred-id: <credential-uuid>`
NOTE: This example references two schedules:

- The `default-schedule` backs up volumes to the local Portworx cluster daily.

- The `weekly-schedule` backs up volumes to cloud storage every week.

For details about how you can create scheduled snapshots with Stork, see the Scheduled snapshots page.

## CSI Enabled Storage Classes​

Portworx provides a set of preconfigured CSI-enabled `StorageClass` objects to support common deployment scenarios, such as high availability, performance tuning, and replication. These StorageClasses simplify dynamic provisioning of volumes using the CSI driver.

To use the CSI driver with a custom or existing `StorageClass`, set the `provisioner` field to `pxd.portworx.com`.

The following is an example of a CSI enabled StorageClass configuration in Portworx Enterprise.

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: fio-fa-da-sc

provisioner: pxd.portworx.com

parameters:

  backend: "pure_block"

  max_iops: "1000"

  max_bandwidth: "1G"

  fs: "ext4"

volumeBindingMode: WaitForFirstConsumer

allowVolumeExpansion: true

```

For more information on the fields in the StorageClass, see StorageClass Fields. For more information on supported StorageClass parameters, see Parameters Fields.

### Defaults created by Portworx Enterprise​

Portworx automatically deploys the following default CSI enabled StorageClass objects during installation:

StorageClassPurpose

`px-csi-db`Default database‑optimized StorageClass. Creates low‑latency, HA Portworx volumes (replicated across nodes) using a DB‑friendly IO profile.

`px-csi-db-encrypted`Encrypted database‑optimized volumes. Same as `px-csi-db`, but with Portworx volume encryption turned on for workloads that require at‑rest encryption without tying in snapshot policies.

`px-csi-db-cloud-snapshot`Database‑optimized volumes with cloud‑snapshot capability. Same as `px-csi-db`, but preconfigured to be used with Portworx cloud snapshots.

`px-csi-db-cloud-snapshot-encrypted`Encrypted, cloud‑snapshot‑ready DB volumes. Same behavior as `px-csi-db-cloud-snapshot`, but with Portworx encryption at rest enabled on the volumes.

`px-csi-db-local-snapshot`Database‑optimized volumes with local‑snapshot capability. Same as `px-csi-db`, but intended for use with Portworx local snapshots on the cluster.

`px-csi-db-local-snapshot-encrypted`Encrypted DB volumes with local‑snapshot capability. Combines `px-csi-db-local-snapshot` behavior with Portworx encryption at rest for secure, locally protected database workloads.

`px-csi-replicated`General‑purpose replicated StorageClass. Creates HA Portworx volumes replicated across nodes, suitable as the cluster‑wide default for most workloads (including VMs/KubeVirt where used).

`px-csi-replicated-encrypted`Encrypted, general‑purpose replicated volumes. Same as `px-csi-replicated` but with Portworx encryption at rest enabled, for non‑DB workloads that still need HA and encryption.

To view available StorageClass objects, run the following command:

```

kubectl get sc

```

In this topic:
