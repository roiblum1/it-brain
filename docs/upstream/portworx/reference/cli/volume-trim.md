# Maintain volumes using Filesystem Trim

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/volume-trim (Portworx Enterprise latest)

Maintain volumes using Filesystem Trim | Portworx Enterprise Documentation

A typical Portworx volume is formatted with ext4 and then used by a container application to store its content files and directories. Over time, your application might create and delete files and directories. On the volume, the space which was previously used by a deleted file gets freed in the filesystem metadata and the underlying block device is unaware of this fact. This can lead to the following inefficiencies:

- On thin provisioned volumes, the freed space in the volume does not translate into free space in the pool. This means that other volumes in the pool that require space might not be able to get it from the pool.

- On SSDs, the block device performs better when it has knowledge of all the freed blocks that the user no longer requires. This information is used by the SSD firmware to perform wear-leveling more efficiently to improve the service life of the storage device and also provide better I/O performance. When the information about the blocks freed in the filesystem is not available to the block device, it creates hot spots in the device that cause it to wear more than the rest of the blocks in the device.

To address these inefficiencies, you can instruct the filesystem to inform the block device of all the unused blocks which were previously used by issuing a `FITRIM` `ioctl` command to the mounted filesystem. The filesystem in turn issues a `DISCARD` request for the freed blocks to the block device.

You can use automatic filesystem trim operations, or you can perform filesystem trim operations manually.

note

Filesystem trim discards unused blocks within a volume. When discard passdown is enabled for the storage pool, Portworx passes these discard requests through the pool to the underlying storage. Discard passdown is recommended for SAN-based deployments.

Volume and snapshot deletions behave differently. Without non-blocking device delete (NBDD), deletions release mapped extents only within the pool and do not reclaim the corresponding capacity on the underlying storage. To reclaim this unused capacity on FlashArray or SAN storage, see Reclaim Unused Storage with Pool Trim.

## Automatic filesystem trim operations​

Automatic filesystem trim is disabled by default. You can enable automatic filesystem trimming (auto fstrim) at the volume, node, or cluster level. When all of the following conditions are met, auto fstrim monitors the unused space in all filesystems mounted on Portworx volumes and automatically triggers a trim job to return unused space back to the pool, and you do not have to manually issue trim jobs:

- Auto fstrim is enabled on the volume

- Auto fstrim is enabled at the cluster level or on the node where the volume is attached

note

-
Starting from Portworx Enterprise 3.5.0, auto fstrim supports volumes with both `discard` and `nodiscard` mount options. In earlier versions, auto fstrim only ran on volumes with `nodiscard` enabled.

-
Starting with Portworx Enterprise 3.6.0, Portworx enables discard support when it attaches an encrypted volume. This allows `fstrim` operations, including auto fstrim, to run on encrypted volumes.

-
If you created an encrypted volume in Portworx Enterprise 3.5.x or earlier, detach and reattach the volume one time after you upgrade to 3.6.0 or later. Until you reattach the volume, `fstrim` operations on it fail with the error `the discard operation is not supported`. Kubernetes users can scale down their application pods so that the volume is in a detached state and then scale up to attach the volume.

Auto fstrim takes into account current workloads in the system and dynamically adjusts the rate at which it performs the trim job. This prioritizes user application performance while optimizing trim rate when application load is low. Note that nodiscard and auto fstrim are not supported on volumes formatted with XFS. For more details, see the Force-enable the nodiscard and auto-fstrim options on XFS formatted volumes section.

note

- Enabling auto fstrim or changing IO rates has a small delay before taking effect.

- If a volume is unmounted or detached, Portworx automatically stops auto fstrim on that volume. If the volume is remounted, auto fstrim automatically starts again.

### Enable auto fstrim​

#### Enable on a new volume​

To create a new volume with auto fstrim enabled, specify the following options at volume creation:

```

pxctl volume create <volume_name> --nodiscard

```

```

Volume successfully created: <volume_ID>

```

You can verify that the volume has auto fstrim enabled with the following command:

```

pxctl volume inspect <volume_name>

```

```

...

Mount Options                   :   nodiscard

...

Auto Fstrim                     :   true

...

```

#### Enable on an existing volume​

To enable auto fstrim on an existing volume, run the following command:

```

pxctl volume update --nodiscard on <volume_name>

```

You can verify that the volume has auto fstrim enabled with the following command:

```

pxctl volume inspect <volume_name>

```

```

...

Mount Options                   :   nodiscard

...

Auto Fstrim                     :   true

...

```

#### Enable on a node​

To enable auto fstrim for a node, run the following command:

```

pxctl cluster options update --runtime-options-action update-node-specific --runtime-options-selector node=<node_uuid> --runtime-options NodeAutoFstrimEnabled=1

```

note

This command overwrites any auto fstrim IO rates you have set at the node level to their default values.

#### Enable on a cluster​

To enable auto fstrim for a cluster, run the following command:

```

pxctl cluster options update --auto-fstrim on

```

### Schedule fstrim operations​

Instead of letting auto fstrim trigger jobs automatically, you can schedule fstrim operations by defining a specific time and duration for fstrim to run. This is particularly beneficial when you want to perform operations on a node with low traffic.

When you specify a window, fstrim does a one-time run in the specified window. It collects all locally mounted volumes with auto fstrim enabled in a queue. This queue is then organized based on the amount of space that can be trimmed, and the process sequentially trims these volumes.

If the queue is empty, fstrim does the same job in the next window to trim volumes which are not in use by the filesystem. It stops if it cannot complete the job in the specified window and reinstates the queue to be processed during the next time window.

note

The `auto fstrim` and `fstrim schedule job` cluster options are mutually exclusive. When `autofstrim` is enabled on a node, `fstrim schedule job` will be disabled and vice versa.

To specify a window for fstrim jobs, enter the following `pxctl cluster options update` command, specifying the following:

- the `--fstrim-schedule-start` flag with the UTC time you want to start the `fstrim` operation. The window can either be set to weekly or daily. You can specify this in either the daily format: `daily=hh:mm` or the weekly format: `weekly=day@hh:mm`.

- the `--fstrim-schedule-duration` flag followed by the number of hours you want the window to remain open for.

The following command schedules a fstrim job on a daily basis. To switch to a weekly schedule, modify the format accordingly:

```

pxctl cluster options update --fstrim-schedule-start <daily=hh:mm> --fstrim-schedule-duration <hrs>

```

#### Clear fstrim schedules​

Run the following command to clear all fstrim schedules:

```

pxctl cluster options update --fstrim-schedule-start ""

```

### IO rates​

Auto fstrim allows you to choose specific IO minimum and maximum rates at the cluster or node level.

#### View existing IO rates​
 View rates at the cluster level​
To view your existing IO rates at the cluster level, use the following command:

```

pxctl cluster options list | grep -i fstrim

```

```

Auto Fstrim                : <on or off>

Max Fstrim IO rate         : <rate>

Min Fstrim IO rate         : <rate>

```

 View rates at the node level​
To view your existing IO rates at the node level, use the following command:

```

pxctl cluster options list | grep Runtime

```

If you have manually set both rates, you will see output similar to the following:

```

Runtime options                                         : selector: <node_uuid>, options: NodeFstrimMaxIoRate=<rate>,NodeFstrimMinIoRate=<rate>

```

If the rates are both set to the default, and you have enabled auto fstrim on the node, you will see output similar to the following:

```

Runtime options                                         : selector: node=<node_uuid>, options: NodeAutoFstrimEnabled=1

```

#### Change IO rates​

You can change the IO rates at the cluster level or the node level.
 Change rates at the cluster level​
To change your minimum IO rate at the cluster level, run the following command. Specify `<rate>` in the following format: `K`, `M` or `G` (for example, 10M).

```

pxctl cluster options update --fstrim-min-io-rate <rate>

```

```

Successfully updated cluster-wide options

```

To change your maximum IO rate at the cluster level, run the following command:

```

pxctl cluster options update --fstrim-max-io-rate <rate>

```

```

Successfully updated cluster-wide options

```

 Change rates at the node level​
To change your minimum and maximum IO rates at the node level, run the following command:

```

pxctl cluster options update --runtime-options-action update-node-specific --runtime-options-selector node=<node_uuid> --runtime-options NodeFstrimMaxIoRate=<rate>,NodeFstrimMinIoRate=<rate>

```

```

Successfully updated cluster-wide options

```

note

If you issue the previous command with only `NodeFstrimMaxIoRate` or `NodeFstrimMinIoRate` defined, not both, the unspecified value will be set to the default value, and any previous change will be overwritten.

 Disable node-level rates​
To disable node-specific IO rate options but keep auto fstrim enabled, use the following command:

```

pxctl cluster options update --runtime-options-action update-node-specific --runtime-options-selector node=<node_uuid> --runtime-options NodeAutoFstrimEnabled=1

```

```

Successfully updated cluster-wide options

```

### View auto fstrim usage​

To view usage information about locally attached volumes that are auto fstrim eligible, run the following command:

```

pxctl volume autofstrim usage

```

For information about running auto fstrim processes, use the following command:

```

pxctl volume autofstrim status

```

This can have a variety of outputs if the process is not running, such as:

```

AutoFsTrimStatus: No auto fstrim volumes found

```

```

AutoFsTrimStatus: Filesystem Trim busy, please retry

```

```

Auto fs trim is not running for any volume.

```

When auto fstrim is running, this command displays output with the following columns of information:

```

Volume ID    Status    Volume Size    Trimmable Space    Trimmed Space    Average Rate    Current Rate    Percentage Complete

```

note

Auto fstrim needs to run for a short time before the average rate displays.

### View auto fstrim status for a volume​

You can also specify a volume name to view its auto fstrim status:

For information about running auto fstrim processes, use the following command:

```

pxctl volume autofstrim status <volume_name>

```

Additionally, you can specify a flag to have these results returned in JSON format:

```

pxctl volume autofstrim status <volume_name> -j

```

### Disable auto fstrim​

#### Disable on a volume​

To turn off auto fstrim for a volume, run the following command:

```

pxctl volume update <volume_name> --nodiscard off

```

### Edit the auto fstrim job queue​

Auto fstrim keeps volume IDs that are eligible for trimming in a first in first out queue. It picks one volume ID at a time from the queue and processes it, then picks the next volume ID, and so on. To modify the auto fstrim job queue, use one of the following commands.

-
To add a volume ID to the front of the existing queue so that auto fstrim will pick this volume next, use the following command:

```

pxctl volume autofstrim push <volume_id>

```

-
To remove a volume ID from the job queue or stop the trimming of a volume which is in the process of trimming space, use the following command:

```

pxctl volume autofstrim pop <volume_id>

```

#### Disable on a node​

To turn off auto fstrim for a node, run the following command:

```

pxctl cluster options update --runtime-options-action update-node-specific --runtime-options-selector node=<node uuid> --runtime-options NodeAutoFstrimEnabled=0

```

#### Disable on a cluster​

To turn off auto fstrim for a cluster, run the following command:

```

pxctl cluster options update --auto-fstrim off

```

### Force-enable the nodiscard and auto_fstrim options on XFS-formatted volumes (not recommended)​

Although the `nodiscard` and `auto_fstrim` options are not recommended on XFS volumes, you can force-enable them using volume labels. Depending on the specific options you want to enable, proceed to one of the following sections:

-
When creating a new XFS volume with the options `nodiscard` and/or `auto_fstrim`, the volume is created successfully, but both of these options are set to false. You also receive alerts notifying you of this change.

-
On an existing XFS volume, if you update options `nodiscard=on` and/or `auto_fstrim=on`, the update fails.

Although the `nodiscard` and `auto_fstrim` options are not supported on the XFS volumes, you can still enable them using labels. Depending on the specific options you want to enable, proceed to one of the following sections:

#### Enable only the nodiscard option​

This section shows how you can enable the nodiscard option for XFS volumes and disabling `--auto_fstrim=off`:

-
Create volume with the `nodiscard` option and XFS filesystem:

```

pxctl volume create <volume-name> --fs xfs --nodiscard -l allowNodiscardOnXFS=true

```

-
Update volume options to enable nodiscard on XFS formatted volume:

```

pxctl volume update <volume_name> --nodiscard=on --auto_fstrim=off -l allowNodiscardOnXFS=true

```

#### Enable both nodiscard and auto-fstrim options​

-
Create volume with the `nodiscard`, `auto_fstrim` options, and XFS filesystem:

```

pxctl volume create <volume-name> --fs xfs --nodiscard --auto_fstrim -l allowNodiscardOnXFS=true,allowAutoFstrimOnXFS=true

```

-
Update volume options with enabling `nodiscard` and `auto_fstrim` on XFS formatted volume:

```

pxctl volume update <volume_name> --nodiscard=on --auto_fstrim=on -l allowNodiscardOnXFS=true,allowAutoFstrimOnXFS=true

```

## Manual filesystem trim operations​

You can also perform filesystem trim operations manually using `pxctl`.

note

- To manually run filesystem trim operations, you need to disable auto fstrim on the node

- Filesystem trim operations can sometimes take a very long time to complete, so the service runs as a background operation

- You can only perform filesystem trim operations on a mounted volume

- If you unmount a volume while filesystem trim operations are running on it, those filesystem trim operations will stop

- You can only run 1 instance of filesystem trim at-a-time on a volume

- You can only run 1 instance of filesystem trim on a system. This limitation reduces the impact on IO performance for user workloads running on that node

- You must start filesystem trim operations from the node on which the volume's storage is mounted. For sharedv4 volumes, run the filesystem trim operation on the nfs server node where the pxd volume is attached, mounted, and exported

### Perform a filesystem trim operation​

-
Open a shell session with the Portworx node on which the volume you intend to run the filesystem trim operation on is mounted.

-
Enter the `pxctl volume trim start` command and volume name to start the filesystem trim operation on a volume:

```

pxctl volume trim start <volume_name>

```

-
Monitor the filesystem trim operation running on a volume by entering the `pxctl volume trim status` command and volume name:

```

pxctl volume trim status <volume_name>

```

### Stop a filesystem trim operation​

Stop a running filesystem trim operation by entering the `pxctl volume trim stop` command and volume name:

```

pxctl volume trim stop <volume_name>

```

### pxctl volume trim reference​

#### pxctl volume trim start​

```

pxctl volume trim start <volume_name>

```

DescriptionArguments

Start a filesystem trim operation on the block device and volume you specify`<volume_name>` - The name of the volume on which you want to perform a filesystem trim operation.

 Example​
Start a filesystem trim operation on an example volume:

```

pxctl volume trim start exampleVolume

```

#### pxctl volume trim status  ​

```

pxctl volume trim status <volume_name>

```

DescriptionArguments

Display the status of a currently running filesystem trim operation on the block device and volume you specify`<volume_name>` - The name of the volume you want to see the currently running filesystem trim operation status for.

 Example​
Show the status for a running filesystem trim operation on an example volume:

```

pxctl volume trim status exampleVolume

```

#### pxctl volume trim stop​

```

pxctl volume trim stop <volume_name>

```

DescriptionArguments

Stop a currently running filesystem trim operation on the block device and volume you specify`<volume_name>` - The name of the volume for which you want to stop a filesystem trim operation

 Example​
Stop the running filesystem trim operation on an example volume:

```

pxctl volume trim stop exampleVolume

```

In this topic:
