# Scale down nodes

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/scale-down (Portworx Enterprise latest)

Scale down nodes | Portworx Enterprise Documentation

## Removing offline nodes​

This document describes how to remove an offline node from a cluster. If you are specifically interested in decommissioning nodes with no storage that have been offline for an extended period, see Automatic decommission of storageless nodes.

-
Identify the cluster that needs to be managed:

```

pxctl status

```

```

Status: PX is operational

Node ID: xxxxxxxx-xxxx-xxxx-xxxx-3e2b01cd0bc3

    IP: X.X.X.197

    Local Storage Pool: 2 pools

    Pool	IO_Priority	Size	Used	Status	Zone	Region

    0	LOW		200 GiB	1.0 GiB	Online	default	default

    1	LOW		120 GiB	1.0 GiB	Online	default	default

    Local Storage Devices: 2 devices

    Device	Path				Media Type		SizLast-Scan

    0:1	/dev/mapper/volume-27dbb728	STORAGE_MEDIUM_SSD	200 GiB		08 Jan 17 05:39 UTC

    1:1	/dev/mapper/volume-0a31ef46	STORAGE_MEDIUM_SSD	120 GiB		08 Jan 17 05:39 UTC

    total					-			320 GiB

Cluster Summary

    Cluster ID: xxxxxxxx-xxxx-xxxx-xxxx-0242ac110002

    Node IP: X.X.X.197 - Capacity: 2.0 GiB/320 GiB Online (This node)

    Node IP: 10.99.117.129 - Capacity: 1.2 GiB/100 GiB Online

    Node IP: 10.99.119.1 - Capacity: 1.2 GiB/100 GiB Online

Global Storage Pool

    Total Used    	:  4.3 GiB

    Total Capacity	:  520 GiB

```

-
List the nodes in the cluster:

```

pxctl cluster list

```

```

Cluster ID: xxxxxxxx-xxxx-xxxx-xxxx-0242ac110002

Status: OK

Nodes in the cluster:

ID					DATA IP		CPU		MEM TOTAL	MEM FREE	CONTAINERS	VERSION		STATUS

xxxxxxxx-xxxx-xxxx-xxxx-3e2b01cd0bc3	X.X.X.197	1.629073	8.4 GB		7.9 GB		N/A		1.1.2-c27cf42	Online

xxxxxxxx-xxxx-xxxx-xxxx-dd5084dce208	10.99.117.129	0.125156	8.4 GB		8.0 GB		N/A		1.1.3-b33d4fa	Online

xxxxxxxx-xxxx-xxxx-xxxx-d3478c485a61	10.99.119.1	0.25		8.4 GB		8.0 GB		N/A		1.1.3-b33d4fa	Online

```

-
List the volumes in the cluster:

```

pxctl volume list

```

```

ID			NAME	SIZE	HA	SHARED	ENCRYPTED	PRIORITSTATUS

845707146523643463	testvol	1 GiB	1	no	no		LOW	up - attached on X.X.X.197

```

In this case, there is one volume in the cluster and it is attached to node with IP X.X.X.97

-
Identify the node that you want to remove from the cluster.

In the following example, node X.X.X.197 has been marked as offline:

```

pxctl cluster list

```

```

Cluster ID: xxxxxxxx-xxxx-xxxx-xxxx-0242ac110002

Status: OK

Nodes in the cluster:

ID					DATA IP		CPU		MEM TOTAL	MEM FREE	CONTAINERS	VERSION		STATUS

xxxxxxxx-xxxx-xxxx-xxxx-dd5084dce208	10.99.117.129	5.506884	8.4 GB	8.0 GB		N/A		1.1.3-b33d4fa	Online

xxxxxxxx-xxxx-xxxx-xxxx-d3478c485a61	10.99.119.1	0.25		8.4 GB	8.0 GB		N/A		1.1.3-b33d4fa	Online

xxxxxxxx-xxxx-xxxx-xxxx-3e2b01cd0bc3	X.X.X.197	-		-	N/A		1.1.2-c27cf42	Offline

```

-
Attach and detach the volume in one of the surviving nodes:

```

pxctl host attach 845707146523643463

```

```

Volume successfully attached at: /dev/pxd/pxd845707146523643463

```

```

pxctl host detach 845707146523643463

```

```

Volume successfully detached

```

-
Delete the local volume that belonged to the offline node:

```

pxctl volume delete 845707146523643463

```

```

Volume 845707146523643463 successfully deleted.

```

-
Delete the node that is offline:

```

pxctl cluster delete xxxxxxxx-xxxx-xxxx-xxxx-3e2b01cd0bc3

```

```

Node xxxxxxxx-xxxx-xxxx-xxxx-3e2b01cd0bc3 successfully deleted.

```

-
List the nodes in the cluster to make sure that the node is removed:

```

pxctl cluster list

```

```

Cluster ID: xxxxxxxx-xxxx-xxxx-xxxx-0242ac110002

Status: OK

Nodes in the cluster:

ID					DATA IP		CPU		MEM TOTAL	MEM FREE	CONTAINERS	VERSION		STATUS

xxxxxxxx-xxxx-xxxx-xxxx-dd5084dce208	10.99.117.129	4.511278	8.4 GB	8.0 GB		N/A		1.1.3-b33d4fa	Online

xxxxxxxx-xxxx-xxxx-xxxx-d3478c485a61	10.99.119.1	0.500626	8.4 GB	8.0 GB		N/A		1.1.3-b33d4fa	Online

```

-
Show the cluster status:

```

pxctl status

```

```

Status: PX is operational

Node ID: xxxxxxxx-xxxx-xxxx-xxxx-dd5084dce208

    IP: X.X.X.199

    Local Storage Pool: 1 pool

    Pool	IO_Priority	Size	Used	Status	Zone	Region

    0	LOW		100 GiB	1.2 GiB	Online	default	default

    Local Storage Devices: 1 device

    Device	Path				Media Type		Size	Last-Scan

    0:1	/dev/mapper/volume-9f6be49c	STORAGE_MEDIUM_SSD	100 GiB08 Jan 17 06:34 UTC

    total					-			100 GiB

Cluster Summary

    Cluster ID: xxxxxxxx-xxxx-xxxx-xxxx-0242ac110002

    Node IP: 10.99.117.129 - Capacity: 1.2 GiB/100 GiB Online (This node)

    Node IP: 10.99.119.1 - Capacity: 1.2 GiB/100 GiB Online

Global Storage Pool

    Total Used    	:  2.3 GiB

    Total Capacity	:  200 GiB

```

## Removing a functional node from a cluster​

A functional Portworx node may need to be removed from the cluster. In this section, we'll demonstrate the removal of a node by running commands on the node itself as well as the removal of a node from another node.

The following output shows the state of the cluster and the different node IPs and node IDs:

```

pxctl status

```

```

Status: PX is operational

Node ID: xxxxxxxx-xxxx-xxxx-xxxx-0027f6bbcbd1

        IP: X.X.X.0

        Local Storage Pool: 1 pool

        POOL    IO_PRIORITY     SIZE    USED    STATUS  ZONE    REGION

        0       LOW             64 GiB  11 GiB  Online  c       us-east-1

        Local Storage Devices: 1 device

        Device  Path            Media Type              Size            Last-Scan

        0:1     /dev/xvdf       STORAGE_MEDIUM_SSD      64 GiB          25 Feb 17 21:13 UTC

        total                   -                       64 GiB

Cluster Summary

        Cluster ID: xxxxxxxx-xxxx-xxxx-xxxx-d4a612b74cc3

        IP              ID                                      Used    Capacity        Status

        172.31.40.38    xxxxxxxx-xxxx-xxxx-xxxx-2bc112f5f131    11 GiB  64 GiB          Online

        172.31.37.211   xxxxxxxx-xxxx-xxxx-xxxx-a85e0514ae8b    11 GiB  64 GiB          Online

        172.31.35.130   xxxxxxxx-xxxx-xxxx-xxxx-893373631483    11 GiB  64 GiB          Online

        172.31.45.106   xxxxxxxx-xxxx-xxxx-xxxx-2eeddcd64d51    11 GiB  64 GiB          Online

        172.31.45.56    xxxxxxxx-xxxx-xxxx-xxxx-ec8e1420e645    11 GiB  64 GiB          Online

        172.31.46.119   xxxxxxxx-xxxx-xxxx-xxxx-0027f6bbcbd1    11 GiB  64 GiB          Online (This node)

        172.31.39.201   xxxxxxxx-xxxx-xxxx-xxxx-936b1b58aa24    11 GiB  64 GiB          Online

        172.31.33.151   xxxxxxxx-xxxx-xxxx-xxxx-41e70a72eafd    11 GiB  64 GiB          Online

        172.31.33.252   xxxxxxxx-xxxx-xxxx-xxxx-428e727eb6b8    11 GiB  64 GiB          Online

Global Storage Pool

        Total Used      :  99 GiB

        Total Capacity  :  576 GiB

```

### Suspend active cloudsnap operations​

-
Identify any active cloudsnap operations being run on the node that you intend to decommission:

```

pxctl cloudsnap status

```

The `STATE` of active operations shows as `Backup-Active`:

```

NAME                                    SOURCEVOLUME        STATE           NODE            TIME-ELAPSED        COMPLETED

xxxxxxxx-xxxx-xxxx-xxxx-278535e49860    885345022234521857  Backup-Done     10.13.90.125    39.746191264s       Tue, 22 Mar 2022 22:53:37 UTC

xxxxxxxx-xxxx-xxxx-xxxx-3c3ccf47f276    186701534582547510  Backup-Done     10.13.90.122    1.677455484s        Tue, 22 Mar 2022 23:59:49 UTC

xxxxxxxx-xxxx-xxxx-xxxx-73176c2d03e2    885345022234521857  Backup-Done     10.13.90.125    27.550329395s       Wed, 23 Mar 2022 00:00:15 UTC

xxxxxxxx-xxxx-xxxx-xxxx-2307865c1b93    649554470078043771  Backup-Active   10.13.90.125    5m12.61653365s

```

From this output, identify the volumes with active backups. For example, if node 10.13.90.125 is being decommissioned, then the volume with active backup is `649554470078043771`.

-
Identify the namespace of the volume the cloudsnap operation is occurring on. The namespace is displayed under the `Labels` section in the output from the following command. Replace `<source_volume>` with the `SOURCEVOLUME` value for the volume that is in a `Backup-Active` state from the previous output:

```

pxctl volume inspect <source_volume>

```

```

Volume               :  649554470078043771

Name                 :  pvc-xxxxxxxx-xxxx-xxxx-xxxx-d4827680f6de

Size                 :  500 GiB

Format               :  ext4

HA                   :  3

IO Priority          :  LOW

Creation time        :  Mar 22 20:37:52 UTC 2022

Shared               :  v4 (service)

Status               :  up

State                :  Attached: xxxxxxxx-xxxx-xxxx-xxxx-10f4e076cac8 (10.13.90.119)

Last Attached        :  Mar 22 20:37:58 UTC 2022

Device Path          :  /dev/pxd/pxd649554470078043771

Labels               :  mount_options=nodiscard=true,namespace=vdbench,nodiscard=true,pvc=vdbench-pvc-sharedv4,repl=3,sharedv4=true,sharedv4_svc_type=ClusterIP

...

```

-
Suspend backup operations for the volume and wait for current backup to complete:

```

storkctl suspend volumesnapshotschedule vdbench-pvc-sharedv4-schedule  -n vdbench

```

-
Verify the suspension. The `SUSPEND` field will show as `true`:

```

storkctl get volumesnapshotschedule -n vdbench

```

```

NAME                            PVC                    POLICYNAME   PRE-EXEC-RULE   POST-EXEC-RULE   RECLAIM-POLICY   SUSPEND   LAST-SUCCESS-TIME

vdbench-pvc-sharedv4-schedule   vdbench-pvc-sharedv4   testpolicy                                    Delete           true      22 Mar 22 17:10 PDT

```

Repeat these steps until all active snaps complete and all backup operations are suspended on the node that you want to decommission.

### Prevention of data loss​

If any node hosts a volume with replication factor of 1, then Portworx disallows decommissioning of such nodes because there is data loss.

One possible workaround to decommission such a node is to increase the replication of single replica volumes by running `volume ha-update`.

-
List all the volumes hosts on the decommissioning node:

```

pxctl volume  list --node xxxxxxxx-xxxx-xxxx-xxxx-2eeddcd64d51

```

```

ID                      NAME                                            SIZE    HA      SHARED  ENCRYPTED  PROXY-VOLUME     IO_PRIORITY     STATUS                          SNAP-ENABLED

633738568577538909      pvc-xxxxxxxx-xxxx-xxxx-xxxx-d4827680f6de        2 GiB   3       no      no         no               LOW             up - attached on 172.31.45.106    no

161898313715947409      pvc-xxxxxxxx-xxxx-xxxx-xxxx-68f0d970e10c        2 GiB   1       no      no         no               LOW             up - attached on 172.31.45.106    no

```

-
Increase the replication factor:

```

pxctl volume ha-update --repl 2 161898313715947409

```

Once the volume is completely replicated onto another node, continue with the node decommissioning. This time, the volume already has another replica on another node, so decommissioning the node will reduce the replication factor of the volume and remove the node.

### Placing the node in maintenance mode​

After identifying the node to be removed (see "Identify the node that you want to remove from the cluster" above), place the node in maintenance mode.

Log in to the node to be decommissioned:

```

pxctl service maintenance --enter

```

```

This is a disruptive operation, PX will restart in maintenance mode.

Are you sure you want to proceed ? (Y/N): y

Entered maintenance mode.

```

### Run the cluster delete command​

Example 1: Running the cluster delete command from a different node

`ssh` to `172.31.46.119` and run the following command:

```

pxctl cluster delete xxxxxxxx-xxxx-xxxx-xxxx-2eeddcd64d51

```

```

Node xxxxxxxx-xxxx-xxxx-xxxx-2eeddcd64d51 successfully deleted.

```

Example 2: Running the cluster delete command from the same node

`ssh` to `172.31.33.252` and type:

```

pxctl cluster delete xxxxxxxx-xxxx-xxxx-xxxx-428e727eb6b8

```

```

Node xxxxxxxx-xxxx-xxxx-xxxx-428e727eb6b8 successfully deleted.

```

### Clean up Portworx metadata on the node​

To learn how to remove or clean up Portworx metadata on the decommissioned node, see clean up Portworx metadata on the node.

## Automatic decommission of storageless nodes​

Storageless nodes that have been initialized and added to the cluster might no longer be needed after they complete their tasks, such as those in a scheduler workflow. If these nodes are taken offline or destroyed, the cluster retains the nodes and marks them as offline.

If these offline nodes eventually make up the majority of nodes in the cluster, the cluster loses quorum. To resolve this issue, run cluster delete commands to remove these nodes. This process becomes more time-consuming as the number of nodes or the frequency at which nodes are added and removed increases.

To address this issue, Portworx automatically decommissions storageless nodes that have been offline for longer than the configured auto-decommission timeout. The default timeout is 20 minutes. You don't need to run a CLI command to turn on or trigger this feature.

To change the timeout, run the following command. Replace `<minutes>` with the new timeout value in minutes. The value must be greater than 0:

```

pxctl cluster options update --auto-decommission-timeout <minutes>

```

To view the current value, run `pxctl cluster options list` and check the Auto decommission timeout (minutes) field.

In this topic:
