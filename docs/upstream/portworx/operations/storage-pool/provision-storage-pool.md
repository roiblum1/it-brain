# Provision Storage Pool

Source: https://docs.portworx.com/portworx-enterprise/operations/storage-pool/provision-storage-pool (Portworx Enterprise latest)

Provision Storage Pool | Portworx Enterprise Documentation

Portworx creates one or more storage pools by grouping together homogeneous drives that are of the same size, medium type and drive type (for cloud drives).

note

- This topic describes the configuration parameters for creating custom storage pools, including how to provision higher-capacity PX-StoreV2 pools. Use these parameters only when you need a custom storage pool configuration. For a standard installation, use the default settings provided when generating the Portworx installation specification.

- To add a storage pool, the node must be in pool maintenance mode. Node maintenance mode alone is not sufficient. Otherwise, the command fails with the `Requires pool maintenance mode` error. For more information, see Storage pool maintenance.

## What are Portworx storage pool configurable parameters?​

The following configurable parameters allow Portworx pool provisioning with custom configuration. All configurable parameters are available as cluster runtime options that could be specified:

- Using `StorageCluster` spec during Portworx installation

- Using `pxctl` cluster runtime options post Portworx installation

- Using `pxctl` for new storage pool post Portworx installation

note

The total number of drives that can be attached to a node is limited and varies by cloud provider. Refer to your cloud provider's drive limits per node and the relevant cluster option in the Expand Your Storage Pool Size with Disks Managed by Portworx document.

The following terms describe the capacity of a storage pool:

-
Max pool size: The maximum capacity a pool can reach in the future through expansion using resize disks (cloud drives).

-
Initial pool size: The capacity of a pool at the time of creation, calculated as `number of drives × sum of size of pool drive sizes`.

### max_pool_size_tb​

This parameter specifies the maximum capacity that the PX-StoreV2 pool can grow later after creation(in TiB units). This parameter is only applicable for PX-StoreV2. If the value is not specified, Portworx selects a default value of 15 TiB. If you want a customized value of max pool size (non-default), it has to be explicitly specified for PX-StoreV2 pools.

note

The `max_pool_size_tb` parameter can only be specified during pool creation and cannot be changed after the pool is created.

PX-StoreV2 storage pools use chunk sizes that are powers of 2 and multiples of 64 KiB. To meet this requirement, Portworx rounds certain `max_pool_size_tb` values (`--max-pool-size-tb` in `pxctl`) up when creating a pool.

The following table shows how the configured maximum pool size (N) affects the chunk size and actual maximum pool size:

max_pool_size_tb (N)Chunk sizeActual maximum pool size

`N <= 15`64 KiB15 TiB

`15 < N <= 30`128 KiB30 TiB

`30 < N <= 60`256 KiB60 TiB

`60 < N <= 120`512 KiB120 TiB

`120 < N <= 240`1024 KiB240 TiB

`240 < N <= 480`2048 KiB480 TiB

For example, if you set `max_pool_size_tb` to `45`, Portworx creates the pool with a maximum size of 60 TiB instead of 45 TiB.

### limit_drives_per_pool​

The `limit_drives_per_pool` parameter specifies the maximum number of drives per pool and is applicable to both PX-StoreV1 and PX-StoreV2. The supported range is 1 to 32.

-
Default behavior: If this parameter is not set, Portworx uses its internal mechanism to split drives into one or more pools.

-
During installation: When creating pools during Portworx installation, if the number of drives of the same type exceeds the specified limit, the drives are split into multiple pools.

- Example: If limit_drives_per_pool is set to 6 and 8 drives of the same type are specified, Portworx creates one pool with 6 drives and another pool with 2 drives.

-
Restoring defaults: To revert to the Portworx default behavior, set `limit_drives_per_pool` to 0.

-
Post-installation pool creation (CLI): When creating pools after installation using the CLI, this parameter is not applied. The drive count can be explicitly set during newpool creation, overriding the `limit_drives_per_pool` limit.

### limit_pools_count​

This parameter specifies the maximum number of pools per node and is applicable for both PX-StoreV1 and PX-StoreV2. The supported range is 1 to 32 and the default is 8.

## How to update Portworx storage pool configurable parameters​

Portworx provides multiple methods at different levels of installation to update the storage pool parameters.

### Method 1: Using StorageCluster spec during Portworx installation​

Pass the following annotations to the StorageCluster spec manually and set the value based on the requirement of parameters. There are two options to add the annotations:

- Option 1: `portworx.io/misc-args: --rt_opts "limit_pools_count=12,limit_drives_per_pool=4,max_pool_size_tb=60"`

- Option 2:

```

   runtimeOptions:

     limit_pools_count: "12"

     limit_drives_per_pool: "4"

```

After updating the StorageCluster spec, apply it to the cluster to configure Portworx storage pool. In the above examples, the value for `limit_pools_count` is set as 12. Restart the Portworx service after changes are made through STC to allow the new settings to take effect.

### Method 2: Using pxctl cluster runtime options post Portworx installation​

Pool configuration options are runtime-configurable via cluster settings. Here are examples of how to apply updates using runtime-options.

```

pxctl cluster options update --runtime-options "limit_drives_per_pool=4"

pxctl cluster options update --runtime-options "limit_pools_count=10"

pxctl cluster options update --runtime-options "limit_drives_per_pool=4,limit_pools_count=10"

```

Retain the values previously defined in `--runtime-options` along with the above parameters. For more information, see Set runtime options.

### Method 3: Using pxctl for new storage pool post Portworx installation​

warning

Adding a new storage pool is disruptive because it restarts the Portworx on the node and might interrupt running applications.

Before adding a pool:

- Cordon the node by running `kubectl cordon <node-name>`, and move any workloads that might be affected by the restart to another node.

- Suspend any CloudSnap or Async DR schedules and wait for active operations to complete.

- Enter pool maintenance mode by running `pxctl service pool maintenance --enter`.

After adding the pool, verify it by running `pxctl service pool show`. Then, exit pool maintenance mode by running `pxctl service pool maintenance --exit` and uncordon the node by running `kubectl uncordon <node-name>`.

The pxctl service command provides the `drive add` with `--newpool` parameter to setup new pools. These options are the same for PX-StoreV1 and PX-StoreV2. CLI cluster runtime options do not need Portworx service restart to take effect.

note

After pool creation, reset the cluster runtime option settings to their defaults: `limit_drives_per_pool` to 6 and `max_pool_size_tb` to 0. Otherwise, the set values continue to be used across the cluster.

## How to calculate initial number of drives in pool for cloud drives​

If you need a pool with a maximum total capacity of X TiB and the maximum drive size is Y TiB, calculate the required number of drives (N) as follows:

`Number of drives(N) = ceil(Desired pool capacity / Maximum drive size)`

`ceil` function rounds a number up to the nearest integer.

Example: You need a pool with 10 TiB of total capacity and maximum drive size is 1.92 TiB.

```

Number of drives = ceil(10 / 1.92)

  = ceil(5.2083)

  = 6

```

If you do not know the maximum pool capacity while creating the pool, you can let Portworx select the default number of drives for the pool.

## PX-StoreV2 capacity provisioning​

For provisioning higher capacity pools, you need to specify the `max_pool_size_tb` during pool creation. This value is set so that pool can be expanded only up to a specified size in future. You also need to select an appropriate number of drives in the pool so that they can reach the specified max size.

For example, if you want the Portworx pool to be 240 TiB in capacity and if each cloud drive can resize up to maximum of 45 TiB, you need at least 6 disks in the pool.

PX-StoreV2 pools can scale roughly up to 480 TiB in capacity through resize disk expansion. By default, Portworx provisions pools to grow up to 15 TiB in capacity.

## Default selection of number of drives in pool for cloud drives​

Drive count selection is based on the backend cloud provider. The default selection applies during any new pool creation.

- For new pool creation during installation, the spec generator uses the following values as defaults unless you make a selection.

- For new pool creation after Portworx installation, if drive count is not specified in the CLI creation of a new pool (`pxctl service drive add --newpool`), the following values are used as defaults:

Sr noCloud providerDefault number of drives

1Vsphere4

2AWS4

3Azure4

4Pure1

5GKE4

6All others4

## Use cases for creating pools on cloud drive environment​

### Pool creation during new Portworx installation​

-
You do not have specific requirements for pool capacity:

Solution: The spec generator provides default selections that allow the pool to reach a suitable size. This approach is recommended for standard pool capacity requirements.

-
You require a single storage pool with 150 TiB capacity.:

Solution: Based on cloud drive type, find out the maximum size it can expand up to. Find out the number of drives required in the pool by calculating as discussed in section above. Select the number of drives in the spec generator. If the calculated number of drives in the pool exceeds 6, specify limit_drives_per_pool value as the number of drives through `runc` runtime options while installing Portworx. Additionally specify `max_pool_size_tb` value as 150 through `runc` runtime options for PX-StoreV2 pools only. Do not specify `max_pool_size_tb` for PX-StoreV1 pools.

Reset the cluster runtime options after pool creation to respective defaults.

-
You require multiple pools, each of capacity of 200 TiB with homogeneous drives:

Solution: Based on cloud drive type, find out the maximum size it can expand up to. Find out the number of drives required in the pool by calculating as discussed in section above. Select twice the number of drives (as there are two pools). Specify `limit_drives_per_pool` value as the number of drives in a single pool through runc runtime options while installing PX. Additionally specify `max_pool_size_tb` value as 200 through runc runtime options for PX-StoreV2 pools. Do not specify `max_pool_size_tb` for PX-StoreV1 pools.

Reset the cluster runtime options after pool creation to respective defaults.

-
You require multiple pools of different capacity of 100 TiB and 200 TiB with homogeneous drives:

Solution: In this case, it is advisable to create one pool during installation using solution provided in use case 2 and another pool after installation using method mentioned in post installation use case 2.

-
You require two pools, one of capacity 100 TiB and the other of 200 TiB with heterogenous drives:

Solution: If both the pools have different capacity drives, calculate the number of drives for both pools and if one or both of them goes beyond 6, set the `limit_drives_per_pool` value to the higher value and install PX. Additionally specify `max_pool_size_tb` value as 200 through runc runtime options for PX-StoreV2 pools. Do not specify `max_pool_size_tb` for PX-StoreV1 pools.

Reset the cluster runtime options after pool creation to respective defaults.

### Pool creation post Portworx install​

warning

Adding a new storage pool is disruptive because it restarts the Portworx on the node and might interrupt running applications.

Before adding a pool:

- Cordon the node by running `kubectl cordon <node-name>`, and move any workloads that might be affected by the restart to another node.

- Suspend any CloudSnap or Async DR schedules and wait for active operations to complete.

- Enter pool maintenance mode by running `pxctl service pool maintenance --enter`.

After adding the pool, verify it by running `pxctl service pool show`. Then, exit pool maintenance mode by running `pxctl service pool maintenance --exit` and uncordon the node by running `kubectl uncordon <node-name>`.

-
You do not have any specific requirements for pool capacity:

Solution: Create newpool using the pxctl service command as shown below:

`pxctl service drive add --newpool -s <type=y,size=x>`

Additional optional argument `--drives-count` is available to select the number of drives in the pool. If no selection is made, PX would pick the default number of drives as indicated in section above.

-
You require a single pool of 180 TiB capacity:

Solution: Create newpool using the following command:

`pxctl service drive add --newpool -s <type=y,size=x> --max-pool-size-tb 180 --drives-count n`

The `max-pool-size-tb` needs to be specified only for PX-StoreV2 pools. Additional optional argument `--drives-count` is available to select the number of drives in the pool. If no selection is made, PX would pick the default drive count based on the table in the above section. The drives count needs to be calculated as follows and at least that many drives need to be specified.

`Number of drives(n) = ceil(Desired pool capacity / Maximum drive size).`

If a lesser number of drives are specified, the pool creation would fail with an appropriate error message suggesting you to select correct configurable values.

Note: The `--max-pool-size-tb` is an optional CLI argument to specify max pool size only for this new pool creation. Alternatively, this can also be set via the cluster runtime option settings as well discussed in the previous sections, but you need to reset the cluster runtime option values back to respective defaults after pool creation completes, otherwise the new setting would apply for all future new pool creations on the cluster. Do not specify `max_pool_size_tb` for PX-StoreV1 pools.

## Troubleshooting​

Following are common misconfigurations during new pool creation:

-
The number of drives specified by you are insufficient to reach the specified value of max pool size (PX-StoreV2 only). Based on pre or post installation, choose one of the following:

- For pool creation during new Portworx installations: Configure the `limit_drives_per_pool` and `max_pool_size_tb` values correctly as detailed in this document and create the pool again.

- For pool creation post Portworx installation: Configure the `drives-count` and `max-pool-size-tb` CLI parameters `(pxctl service drive add --newpool)` correctly as detailed in this document and create the pool again

-
The number of drives specified exceeds the maximum number of cloud drives that could be attached on the node. In that case, as a fix, create a new pool on a different node.

-
The pool gets created with misconfigured values. To fix this, check if there is no data on the pool, then delete the pool and re-create it again. Reach out to technical support in case of further assistance.

-
If the creation of a new pool is interrupted during Portworx installation or after installation due to a Portworx service restart or a node reboot, stale Portworx signatures might remain on the drives used for the new pool. In such scenarios, the affected drives must be wiped before attempting to create the new pool again. Follow the steps below to resolve this issue:

-
Determine the drives that were used for the new pool creation which failed. These drives will require wiping. Use the following command to wipe Portworx signatures from the affected drives:

```

pxctl service node-wipe --help

```

-
After wiping the affected drives, attempt to create the new pool again.

note

-
If the node already contains other pools that are in active use, ensure that only the drives associated with the failed new pool creation are wiped. Wiping drives belonging to existing pools in use will result in data loss and should be avoided.

-
If the node wipe procedure fails or if there is any uncertainty about which drives to wipe, contact Portworx Customer Support for further assistance.

In this topic:
