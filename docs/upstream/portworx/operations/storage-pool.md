# Provision and Manage your Storage Pool

Source: https://docs.portworx.com/portworx-enterprise/operations/storage-pool (Portworx Enterprise latest)

Provision and Manage your Storage Pool | Portworx Enterprise Documentation

Storage pools in Portworx Enterprise are logical groupings of storage devices that provide a unified storage solution for your applications.

Pools can be provisioned either during Portworx installation or after Portworx has been installed.

No additional configuration is required to increase the capacity of PX-StoreV1 storage pools. The pools can automatically expand up to the maximum size supported by the underlying cloud drives, or by adding additional cloud drives to the pool.

By default, PX-StoreV2 storage pools can grow up to 15 TiB in capacity through resize disk expansion. To configure pools with a capacity greater than 15 TiB (up to a maximum of 480 TiB), you must apply additional settings when you provision storage pools.

PX-StoreV2 does not support pool expansion by adding additional disks. This option is available only for PX-StoreV1.

## Pool provisioning during Portworx installation​

-
On-Prem Installation: Provide an explicit list of drives to be used for creating storage pools.

-
Cloud Managed Installation: Specify the number of drives and the capacity of each drive for the selected drive type. The spec generator offers a default configuration with an initial drive size and count optimized for pool scalability through disk resizing.

## Pool provisioning post Portworx installation​

New pools can be created post Portworx installation using `pxctl` CLI `service` mode utilities. The pxctl service command provides the `drive add` option to add storage. The command accepts a list of drives (on-prem) or a drive count (cloud environment) to create pools with multiple drives. For cloud environments, if a drive count is not specified, Portworx would select a default drive count.

This section covers the following key aspects of storage pools:

-
Provision storage pools: Create and configure storage pools, with options for both initial setup and adding pools after installation.

-
Manage your storage pool: Monitor pool capacity, handle alerts, recover full pools, and safely move volumes using Pool Drain.

-
Configure storage pool cache: Enable storage pool caching to improve storage pool performance by building a small caching layer.

-
Recover nodes automatically with Auto Cordon: Automatically bring a storage node back online after a disk failure takes one of its storage pools offline.

-
Reclaim pool space: Reclaim unused capacity from deleted volumes on the underlying FlashArray or SAN storage used by a PX-StoreV2 pool.

In this topic:
