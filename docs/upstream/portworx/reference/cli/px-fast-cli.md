# PX-Fast volumes using pxctl

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/px-fast-cli (Portworx Enterprise latest)

PX-Fast volumes using pxctl | Portworx Enterprise Documentation

This section provides instructions for performing operations on PX-Fast volumes using `pxctl`.

## Create a PX-Fast volume​

To create a PX-fast volume, run the following command on any of the worker nodes of your cluster:

```

pxctl volume create --fastpath <px-volume>

```

```

Volume successfully created: 913654286436616938

```

## Attach a volume​

Attach your PX-Fast volume to the host:

```

pxctl host attach <px-volume>

```

By default, a volume uses PX-Fast only when you attach it on the node that holds its replica. If you enable remote fastpath on the cluster, the volume can also use PX-Fast when you attach it on another node. For more information, see Enable remote fastpath on the cluster.

## List volumes in your cluster​

Run the following command to get the list of volumes within a cluster:

```

pxctl volume list

```

```

ID			NAME						SIZE	HA	SHARED	ENCRYPTED	PROXY-VOLUME	IO_PRIORITY	STATUS		SNAP-ENABLED

1150247763189801500	pvc-xxxxxxxx-xxxx-xxxx-xxxx-84d9193d55a5	2 GiB	no	no		no		LOW		up - detached		no

79554029234843357	v1						1 GiB	no	no		no		LOW		up - detached		no

909303106655754070	v2						1 GiB	no	no		no		LOW		up - attached on 10.13.160.65	no

```

Note the ID or name of one of the volume; you can use it to view details using the `pxctl` command.

## Get volume details​

Run the following command to view the details of a volume:

```

pxctl volume inspect <px-volume>

```

```

Volume          	 :  909303106655754070

	Name            	 :  v2

	Size            	 :  1.0 GiB

	Format          	 :  ext4

	HA              	 :  1

	IO Priority     	 :  LOW

	Creation time   	 :  Oct 11 01:43:36 UTC 2022

	Shared          	 :  no

	Status          	 :  up

	State           	 :  Attached: xxxxxxxx-xxxx-xxxx-xxxx-502e658bc307 (10.13.160.65) (fastpath active)

	Last Attached   	 :  Oct 11 01:43:42 UTC 2022

	Device Path     	 :  /dev/pxd/pxd909303106655754070

	Mount Options          	 :  discard

	Reads           	 :  40

	Reads MS        	 :  20

	Bytes Read      	 :  1060864

	Writes          	 :  0

	Writes MS       	 :  0

	Bytes Written   	 :  0

	IOs in progress 	 :  0

	Bytes used      	 :  33 MiB

	Replica sets on nodes:

		Set 0

		  Node 		 : 10.13.160.65 (Pool xxxxxxxx-xxxx-xxxx-xxxx-f9131bf7ef9d )

	Replication Status	 :  Up

```

The `State` field shows `fastpath active` when the volume uses PX-Fast. If it does not, the volume uses the standard I/O path.

## Get pool details servicing your volume​

Run the following command to view the details of the pool servicing your volume:

```

pxctl service pool show

```

```

PX drive configuration:

Pool ID: 0

	Type:  PX-StoreV2

	UUID:  xxxxxxxx-xxxx-xxxx-xxxx-db8abe01d4f0

	IO Priority:  HIGH

	Labels:  medium=STORAGE_MEDIUM_SSD,beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,iopriority=HIGH,kubernetes.io/arch=amd64,kubernetes.io/hostname=username-vms-silver-sight-3,kubernetes.io/os=linux

	Size: 25 GiB

	Status: Online

	Has metadata:  No

	Balanced:  Yes

	Drives:

	0: /dev/sda, Total size 32 GiB, Online

	Cache Drives:

	No Cache drives found in this pool

Metadata  Device:

	1: /dev/sdd, STORAGE_MEDIUM_SSD

```

## Update a volume to enable PX-Fast​

You can update an existing volume to use the PX-Fast functionality by running the following command:

```

pxctl volume update --fastpath <px-volume>

```

```

Volume          	 :  289859383805313381

Name            	 :  v5

Size            	 :  1.0 GiB

Format          	 :  ext4

HA              	 :  1

IO Priority     	 :  LOW

Creation time   	 :  Oct 14 02:35:02 UTC 2022

Shared          	 :  no

Status          	 :  up

State           	 :  detached

Mount Options          	 :  discard

Reads           	 :  0

Reads MS        	 :  0

Bytes Read      	 :  0

Writes          	 :  0

Writes MS       	 :  0

Bytes Written   	 :  0

IOs in progress 	 :  0

Bytes used      	 :  1.0 MiB

Replica sets on nodes:

		Set 0

		  Node 		 : 10.13.161.121 (Pool xxxxxxxx-xxxx-xxxx-xxxx-434152789beb )

Replication Status	 :  Detached

```

The volume is now eligible for PX-Fast. Portworx uses PX-Fast when you attach the volume and it has one replica. The volume must be attached on the node that holds its replica, unless you enable remote fastpath on the cluster.

In this topic:
