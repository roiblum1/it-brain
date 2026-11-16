# Readahead

Source: https://docs.portworx.com/portworx-enterprise/operations/tune-performance/readahead (Portworx Enterprise latest)

Readahead | Portworx Enterprise Documentation

EARLY ACCESS

This feature is available as Early Access (EA) and should not be used in production.

Readahead is the process of prefetching data from a disk during sequential reads before the application issues read requests. When enabled, Portworx Enterprise detects sequential read I/O patterns and prefetches data from a disk into memory before an application requests it. Serving prefetched data from memory reduces disk and network costs in the read IO path, improves read throughput and IOPS, and lowers read latency.

ReadAhead is a configurable option for Portworx volumes and is disabled by default. When enabled, readahead activates based on the I/O access pattern when applications mount a PVC. Workloads with sequential I/O patterns benefit the most.

By default, Portworx Enterprise limits readahead memory usage to 64 MiB per node and 8 MiB per volume. Therefore, Portworx by Everpure recommends enabling readahead on no more than 32 volumes per node to avoid exceeding node-level memory limits. If additional memory is available, you can increase the node-level RA limit up to 2 GiB, which allows more volumes to use readahead. You can modify these limits using the runtime options listed in Readahead runtime options.

Enable readahead for workloads that perform sequential reads, for example, reading a large file sequentially, reading multiple files sequentially, or reading multiple files sequentially in parallel. Without readahead, each read request waits for disk access. Readahead reduces this wait time by loading data into memory in advance. This improves overall read performance and application responsiveness. Do not enable readahead for workloads that perform mostly random reads. In these cases, readahead can reduce performance. Read throughput and IOPS can drop anywhere between 15-40%.

To determine whether readahead improves your read operations:

- Run the application with readahead enabled and disabled over the same time window.

- Compare read performance metrics in Grafana, including throughput, IOPS, and latency.

- Review readahead statistics for the volume.

## Prerequisites​

Ensure that your cluster meets the following prerequisites before you enable readahead:

- Have Portworx Enterprise version 3.6.0 or later installed.

## Limitations​

Consider the following limitations before you enable readahead in your volumes:

- Readahead is not supported for aggregated volumes.

- Readahead does not improve performance of all read workloads. It benefits sequential read workloads only.

- Readahead does not activate for sequential read workloads with a queue depth of 1, where the application has only one outstanding read request at a time. For example, a `fio` workload configured with `iodepth=1` does not activate readahead because Portworx cannot detect the sequential access pattern from a single outstanding read request. Readahead can activate when the workload has multiple outstanding read requests.

## Enable Readahead​

Readahead is a per-volume setting and is disabled by default. You must enable it manually on each volume.

To enable readahead when you create a volume:

```

pxctl volume create vol1 --readahead

```

To enable readahead on an existing volume:

```

pxctl volume update vol1 --readahead on

```

## Disable readahead​

To disable readahead on a specific volume:

```

pxctl volume update vol1 --readahead off

```

To disable readahead at the cluster level:

```

pxctl cluster options update --readahead off

```

This prevents enabling readahead on new volumes and stops new readahead operations.

## Readahead runtime options​

The following table provides the readahead runtime options that can be used to configure readahead behavior at runtime.

warning

Do not modify the runtime options unless necessary. Contact Portworx Support before changing the runtime options.

ParameterNameDescriptionDefault ValueRange

`readahead_total_limit_kib`Readahead total limitDefines the readahead cache size per volume.8192 KiB2048 KiB to 32768 KiB

`readahead_node_total_limit_kib`Readahead node total limitDefines the total readahead cache size per node.65536 KiB8192 KiB to 2097152 KiB

`readahead_len_kib `Readahead lengthDefines the amount of data prefetched per request.1024 KiB128 KiB to 1024 KiB

`readahead_next_threshold_percent `Readahead next threshold percentageDefines the percentage of the current readahead buffer that must be accessed before starting the next readahead.50%10% to 90%

`readahead_timeout_ms `Readahead timeoutDefines how long data remains in the readahead cache.10 ms1 ms to 1000 ms

note

-
Increase `readahead_total_limit_kib` if the application runs multiple parallel sequential I/O streams on the same volume. Each sequential stream requires approximately 2 MiB of readahead cache. The default value of 8 MiB supports up to four parallel streams. If the application runs more than four parallel sequential streams and sufficient memory is available on the node, increase this limit. If the application runs only one sequential stream, reduce the value to 2 MiB. Reducing the limit allows more volumes on the same node to enable readahead while using the same amount of shared memory.

-
Increase `readahead_node_total_limit_kib` in the following situations:

- The node has additional available memory.

- Many attached volumes have readahead enabled.

- Runtime statistics show that volumes hit node-level limits (num_readaheads_node_rejects increases), which prevents new readahead operations from starting.

-
The default value (1 MiB) of `readahead_len_kib` is the maximum supported size. Reduce this value only if the application performs very small sequential I/O operations at varying offsets. After modifying this setting, monitor performance metrics to ensure the change improves behavior.

-
Reduce `readahead_next_threshold_percent` for slower disks to start the next readahead operation earlier. Lowering this value can increase unnecessary disk reads if the sequential read pattern does not continue. Monitor performance after making changes.

-
Increase `readahead_timeout_ms` to retain prefetched data in the readahead cache for a longer period. This adjustment is useful for workloads that access data sequentially with slower or staggered read patterns within the sequential stream.

## How to update readahead configurable parameters​

Portworx Enterprise provides multiple methods to update the readahead runtime parameters.

### Method 1: Using StorageCluster spec during Portworx installation​

Pass the following annotations to the StorageCluster spec manually and set the value based on the requirement of parameters. There are two options to add the annotations:

- Option 1: `portworx.io/misc-args: --rt_opts 'readahead_total_limit_kib=32768,readahead_next_threshold_percent=10'`

- Option 2:

```

 runtimeOptions:

  readahead_total_limit_kib: "32768"

  readahead_next_threshold_percent: "10"

```

After updating the `StorageCluster` spec, apply them to the cluster to configure readahead parameters. In the above example, the value for readahead total limit is set as 32768 KiB and the threshold percentage is set to 10%. Restart the Portworx service after changes are made through STC to allow the new settings to take effect.

### Method 2: Using pxctl cluster runtime options post Portworx installation​

Readahead configuration options are runtime-configurable using cluster settings:

```

pxctl cluster options update --runtime-options <param>=<value>

```

Replace:

- `<param>` with a parameter name from the table above.

- `<value>` with a supported value from the range specified in the table above.

The following is an example:

```

  pxctl cluster options update --runtime-options readahead_next_threshold_percent=10,readahead_total_limit_kib=32768

```

Retain the values previously defined in `--runtime-options` along with the above parameters. For more information, see Set runtime options.

In this topic:
