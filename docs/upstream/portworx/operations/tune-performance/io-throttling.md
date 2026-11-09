# Application I/O Control

Source: https://docs.portworx.com/portworx-enterprise/operations/tune-performance/io-throttling (Portworx Enterprise latest)

Application I/O Control | Portworx Enterprise Documentation

Portworx volumes are created from a common storage pool and share their available IOPS (input/output operations per second) and bandwidth (measured in MBps) between all other provisioned Portworx volumes. If an application's volumes start consuming too many resources, it can become a "noisy neighbor" and reduce the I/O and network bandwidth available to other volumes in the pool.

Portworx Application I/O Control lets you control the IOPS or bandwidth usage of individual volumes in your cluster. You can configure the throttling through a StorageClass, which prevents applications from using excessive bandwidth. To automatically control the IOPS or bandwidth usage of individual volumes in your cluster, you can enable Dynamic App I/O Control with Autopilot.

To control I/O on existing volumes, you can use the `pxctl volume update` command.

In addition to defining parameters in a StorageClass, you can set Application I/O Control values for volumes using the `pxctl` command line interface.

note

By default, this feature is not enabled.

## Prerequisites​

- Application I/O Control is supported for kernel versions 4.6 or later.

- The host must have cgroups mounted and configured.

- Portworx automatically detects the available cgroup version and applies I/O throttling accordingly.

## Supported cgroup versions​

Portworx supports Application I/O Control on hosts using either `cgroup v1` or `cgroup v2`.

- cgroup v1 uses the `blkio` controller (e.g., `/sys/fs/cgroup/blkio/blkio.throttle.read_bps_device`).

- cgroup v2 uses the unified hierarchy and the `io` controller (e.g., `/sys/fs/cgroup/user.slice/io.max`).

Portworx logs errors if no supported cgroup configuration is found.

## Create volumes​

note

- You do not need to restart the Portworx service, as the settings take effect immediately, even if the volume is already attached.

- You can configure a maximum rate for IOPS (measured in input/output operations per second) and bandwidth (measured in MBps) simultaneously.

- Once you set Application I/O Control values, you can check alerts or logs for messages indicating that Application I/O Control is not enabled. For example: `IO throttling supported from kernel v4.6, this node has kernel v3.10` indicates that Application I/O Control is not supported.

- IOPS might be misleading due to batching of small blocksize IOs into a larger one before IO reaches the pxd device, especially when using sharedV4 volumes. Bandwidth throttling is more consistent.

### Apply using a StorageClass​

You can apply Application I/O Control through a StorageClass.

To configure IOPS throttling in a StorageClass, use the following format:

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: portworx-io-profile

provisioner: pxd.portworx.com

parameters:

  repl: "2"

  io_profile: "db_remote"

  io_throttle_rd_iops: "1024"

  io_throttle_wr_iops: "1024"

```

To configure bandwidth throttling in a StorageClass, use the following format:

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: portworx-io-profile

provisioner: pxd.portworx.com

parameters:

  repl: "2"

  io_profile: "db_remote"

  io_throttle_rd_bw: "10"

  io_throttle_wr_bw: "10"

```

You can also configure read IOPS throttling and write bandwidth throttling, or the inverse. For example:

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: portworx-io-profile

provisioner: pxd.portworx.com

parameters:

  repl: "2"

  io_profile: "db_remote"

  io_throttle_rd_iops: "1024"

  io_throttle_wr_bw: "10"

```

note

The minimum value for `rd_bw` and `wr_bw` is `1`, and the minimum value for `rd_iops` and `wr_iops` is `256`.

### Create using pxctl​

When you create volumes using `pxctl`, you can specify the `--max_bandwidth` and `--max_iops` flags to restrict the storage resources that volume uses:

```

pxctl volume create --max_bandwidth <ReadBW>,<WriteBW> <volname/volid>

```

```

pxctl volume create --max_iops <ReadIOPS>,<WriteIOPS> <volname/volid>

```

note

The minimum value for `--max_bandwidth` is `1`, and the minimum value for `--max_iops` is `256`.

## Update volumes using pxctl​

If you want to add Application I/O Control to an existing volume, or change its throttling values, you can do so using the `--max_bandwidth` and `--max_iops` flags with the `pxctl volume update` commands:

```

pxctl volume update --max_bandwidth <ReadBW>,<WriteBW> <volname/volid>

```

```

pxctl volume update --max_iops <ReadIOPS>,<WriteIOPS> <volname/volid>

```

note

If you want to limit only read or write bandwidth/IOPS traffic, set the other value to `off`.

For example: Set read throttling for an existing volume to 1024 IOPS:

```

pxctl volume update --max_iops 1024,off exampleVolume

```

## Remove throttling​

If you want to remove throttling from a volume, set the value of the `--max_bandwidth` and `--max_iops` flags to `off` for any throttling you wish to remove:

```

pxctl volume update --max_bandwidth off,<WriteBW> <volname/volid>

```

```

pxctl volume update --max_iops off,off <volname/volid>

```

## Limitations​

- Application I/O Control is only available on systems with properly mounted and configured `cgroup v1` or `cgroup v2`. This feature manages I/O performance for containers based on cgroup configurations.

- Application I/O Control is not supported for FlashBlade Direct Access (FBDA) and NFS Proxy volumes.

- I/O throttling for sharedv4 volumes does not work on hosts using `cgroup v2` because NFS kernel threads operate outside of cgroup slices.

In this topic:
