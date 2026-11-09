# Decommission a Node

Source: https://docs.portworx.com/portworx-enterprise/platform/uninstall/decommission-a-node (Portworx Enterprise latest)

Decommission a Node | Portworx Enterprise Documentation

This guide describes a recommended workflow for decommissioning a Portworx node in your cluster.

note

- The following steps don't apply if you're using an auto-scaling group (ASG) to manage your Portworx nodes. For details about how you can change the size of your auto-scaling group, see the Scaling the Size of Your Auto Scaling Group page of the AWS documentation.

- For cloud platforms, ensure that both the node being decommissioned and the node initiating the decommissioning are in the same zone.

## Migrate application pods using Portworx volumes that are running on this node​

- Openshift

- Kubernetes

If you plan to remove Portworx from a node, you need to migrate applications running on that node that use Portworx. If Portworx is not running, existing application containers end up with read-only volumes and new ones fail to start.

Perform the following steps to migrate select pods.

-
Cordon the node using the following command:

```

oc adm cordon <node>

```

-
Reschedule application pods using Portworx volumes on different nodes:

```

oc delete pod <pod-name> -n <application-namespace>

```

Since application pods are expected to be managed by a controller like `Deployment` or `StatefulSet`, OpenShift creates a new replacement pod on another node.

If you plan to remove Portworx from a node, you need to migrate applications running on that node that use Portworx. If Portworx is not running, existing application containers end up with read-only volumes and new ones fail to start.

Perform the following steps to migrate select pods.

-
Cordon the node using the following command:

```

kubectl cordon <node>

```

-
Reschedule application pods using Portworx volumes on different nodes:

```

kubectl delete pod <pod-name> -n <application-namespace>

```

Since application pods are expected to be managed by a controller like `Deployment` or `StatefulSet`, Kubernetes spins up a new replacement pod on another node.

## Remove Portworx from the cluster​

Follow the section "Removing offline nodes" or "Removing a functional node from a cluster" to decommission the Portworx node from the cluster.

### Removing a functional node from a cluster​

A functional Portworx node may need to be removed from the cluster. This section demonstrates how to remove a node by running commands on the node itself as well as how to remove a node from another node.

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

#### Suspend active cloudsnap operations​

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

#### Prevention of data loss​

If any node hosts a volume with a replication factor of 1, Portworx prevents decommissioning of such nodes to avoid data loss.

One possible workaround to decommission such a node is to increase the replication of single replica volumes by running `volume ha-update`.

-
List all the volumes hosted on the decommissioning node:

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

-
Verify the replication is complete before proceeding. After running `pxctl volume ha-update`, you must confirm that the volume has been successfully replicated to other healthy nodes. Inspect each volume to verify replication status:

```

pxctl volume inspect <volume-id>

```

Check the following in the output:

- HA: Verify the replication factor matches what you set (e.g., `HA : 2`)

- Status: Should show `up`

- Replica sets on nodes: Should show the expected number of replicas distributed across different healthy nodes (not all on the node being decommissioned)

- Replication Status: If this field appears, it should show `Up`. Ensure it does NOT show `Resync`, `Resync Failed`, or `Not in quorum`

You can also check the RuntimeState using JSON output to ensure it shows `clean`:

```

pxctl --json volume inspect <volume-id> | grep -i runtimestate

```

warning

Do not proceed with node decommissioning if any volume shows:

-
Replication Status: `Resync`, `Resync Failed`, or `Not in quorum`

-
RuntimeState: Not `clean` (e.g., `resync` or error states)

-
Missing replicas or incorrect number of replicas

-
All replicas still on the node being decommissioned

Wait for replication to complete. Decommissioning a node while volumes are still replicating can result in permanent data loss.

Once all volumes are completely replicated onto other nodes and verified as healthy, continue with the node decommissioning. At this point, each volume already has replicas on other healthy nodes, so decommissioning the node will reduce the replication factor of the volume and remove the node.

#### Check if the node is running internal KVDB​

If your cluster uses internal KVDB, identify which nodes are KVDB members before placing the node in maintenance mode. Run the following command:

```

pxctl service kvdb members

```

```

Kvdb Cluster Members:

ID						PEER URLs				CLIENT URLs			LEADER	HEALTHY	DBSIZE

xxxxxxxx-xxxx-xxxx-xxxx-abc80d520d77	[http://portworx-2.internal.kvdb:9018]	[http://X.X.X.21:9019]	false	true	6.3 MiB

xxxxxxxx-xxxx-xxxx-xxxx-a9c6e8a38893	[http://portworx-1.internal.kvdb:9018]	[http://X.X.X.20:9019]	true	true	6.3 MiB

xxxxxxxx-xxxx-xxxx-xxxx-0a7c17b51ed4	[http://portworx-3.internal.kvdb:9018]	[http://X.X.X.18:9019]	false	true	6.3 MiB

```

If the node you want to decommission is a KVDB member, the `pxctl cluster delete` command will fail with a message similar to:

```

Cannot remove node ID xxxxxxxx-xxxx-xxxx-xxxx-0a7c17b51ed4: cannot remove this node since it is running kvdb.

```

To resolve this, trigger a KVDB failover before proceeding:

-
Stop Portworx on the node to trigger the KVDB failover:

- Openshift

- Kubernetes

```

oc label node <nodename> px/service=stop --overwrite

```

```

kubectl label node <nodename> px/service=stop --overwrite

```

-
From another worker node, monitor the KVDB members until the node is no longer a member and KVDB has failed over to a different node:

```

pxctl service kvdb members

```

-
Once KVDB has failed over, start Portworx:

- Openshift

- Kubernetes

```

oc label node <nodename> px/service=start --overwrite

```

```

kubectl label node <nodename> px/service=start --overwrite

```

-
Proceed to place the node in maintenance mode.

#### Placing the node in maintenance mode​

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

#### Run the cluster delete command​

You can run this command from the node being decommissioned or from any other node in the cluster. Specify the node ID of the node you want to delete:

```

pxctl cluster delete xxxxxxxx-xxxx-xxxx-xxxx-2eeddcd64d51

```

```

Node xxxxxxxx-xxxx-xxxx-xxxx-2eeddcd64d51 successfully deleted.

```

#### Clean up Portworx metadata on the node​

note

Remove Portworx installation or stop Portworx on the node to allow the clean up of Portworx metadata. See remove Portworx installation/stop Portworx.

To learn how to remove or clean up Portworx metadata on the decommissioned node, see clean up Portworx metadata on the node.

### Removing offline nodes​

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

    Device	Path				Media Type		Size	Last-Scan

    0:1	/dev/mapper/volume-27dbb728	STORAGE_MEDIUM_SSD	200 GiB	08 Jan 17 05:39 UTC

    1:1	/dev/mapper/volume-0a31ef46	STORAGE_MEDIUM_SSD	120 GiB	08 Jan 17 05:39 UTC

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

xxxxxxxx-xxxx-xxxx-xxxx-dd5084dce208	10.XX.117.129	0.125156	8.4 GB		8.0 GB		N/A		1.1.3-b33d4fa	Online

xxxxxxxx-xxxx-xxxx-xxxx-d3478c485a61	10.99.119.1	0.25		8.4 GB		8.0 GB		N/A		1.1.3-b33d4fa	Online

```

-
List the volumes in the cluster:

```

pxctl volume list

```

```

ID			NAME	SIZE	HA	SHARED	ENCRYPTED	IO_PRIORITY	STATUS

845707146523643463	testvol	1 GiB	1	no	no		LOW	up - attached on X.X.X.197

```

In this case, there is one volume in the cluster and it is attached to node with IP X.X.X.197

-
Identify the node that you want to remove from the cluster. Skip to next step if the node you want to remove is already offline.

- Openshift

- Kubernetes

To manually set a node offline, apply the px/enabled=remove label to the node:

```

oc label nodes < node > px/enabled=remove --overwrite

```

To manually set a node offline, apply the px/enabled=remove label to the node:

```

kubectl label nodes < node > px/enabled=remove --overwrite

```

-
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

    0:1	/dev/mapper/volume-9f6be49c	STORAGE_MEDIUM_SSD	100 GiB	08 Jan 17 06:34 UTC

    total					-			100 GiB

Cluster Summary

    Cluster ID: xxxxxxxx-xxxx-xxxx-xxxx-0242ac110002

    Node IP: 10.99.117.129 - Capacity: 1.2 GiB/100 GiB Online (This node)

    Node IP: 10.99.119.1 - Capacity: 1.2 GiB/100 GiB Online

Global Storage Pool

    Total Used    	:  2.3 GiB

    Total Capacity	:  200 GiB

```

### Automatic decommission of storageless nodes​

Storageless nodes that have been initialized and added to the cluster might no longer be needed after they complete their tasks, such as those in a scheduler workflow. If these nodes are taken offline or destroyed, the cluster retains the nodes and marks them as offline.

If these offline nodes eventually make up the majority of nodes in the cluster, the cluster loses quorum. To resolve this issue, run cluster delete commands to remove these nodes. This process becomes more time-consuming as the number of nodes or the frequency at which nodes are added and removed increases.

To address this issue, Portworx automatically decommissions storageless nodes that have been offline for longer than the configured auto-decommission timeout. The default timeout is 20 minutes. You don't need to run a CLI command to turn on or trigger this feature.

To change the timeout, run the following command. Replace `<minutes>` with the new timeout value in minutes. The value must be greater than 0:

```

pxctl cluster options update --auto-decommission-timeout <minutes>

```

To view the current value, run `pxctl cluster options list` and check the Auto decommission timeout (minutes) field.

## Remove Portworx installation from the node​

- Openshift

- Kubernetes

Apply the px/enabled=remove label and it will remove the existing Portworx systemd service. It will also apply the px/enabled=false label to stop Portworx from running in the future.

For example, below command will remove existing Portworx installation from minion2 and also ensure that Portworx pod doesn’t run there in the future.

```

oc label nodes < node > px/enabled=remove --overwrite

```

Apply the px/enabled=remove label and it will remove the existing Portworx systemd service. It will also apply the px/enabled=false label to stop Portworx from running in the future.

For example, below command will remove existing Portworx installation from minion2 and also ensure that Portworx pod doesn’t run there in the future.

```

kubectl label nodes < node > px/enabled=remove --overwrite

```

note

Decommission from Kubernetes: If the plan is to decommission this node altogether from the Kubernetes cluster, no further steps are needed.

## Ensure application pods using Portworx don’t run on this node​

If you continue using the node without Portworx, ensure your application pods using Portworx volumes don’t get scheduled here.

You can ensure this by adding the `schedulerName: stork` field to your application specs (Deployment, Statefulset, etc). Stork is a scheduler extension that will schedule pods using Portworx PVCs only on nodes that have Portworx running. Refer to the Using scheduler convergence article for more information.

Another way to achieve this is to use inter-pod affinity

-
You need to define a pod affinity rule in your applications that ensure that application pods get scheduled only on nodes where the Portworx pod is running.

-
Consider the following nginx example:

```

apiVersion: apps/v1

kind: Deployment

 metadata:

  name: nginx-deployment

spec:

  selector:

    matchLabels:

      app: nginx

  replicas: 1

  template:

    metadata:

      labels:

        app: nginx

    spec:

      affinity:

        # Inter-pod affinity rule restricting nginx pods to run only on nodes where Portworx pods are running (Portworx pods have a label

        # name=portworx which is used in the rule)

        podAffinity:

          requiredDuringSchedulingIgnoredDuringExecution:

          - labelSelector:

              matchExpressions:

              - key: name

                operator: In

                values:

                - "portworx"

            topologyKey: kubernetes.io/hostname

            namespaces:

            - "kube-system"

      hostNetwork: true

      containers:

      - name: nginx

        image: nginx

        ports:

        - containerPort: 80

        volumeMounts:

        - name: nginx-persistent-storage

          mountPath: /usr/share/nginx/html

      volumes:

      - name: nginx-persistent-storage

        persistentVolumeClaim:

          claimName: px-nginx-pvc

```

It can also be configured on cluster level by setting `spec.stork.args.webhook-controller` to `true` in StorageCluster to make Stork the default scheduler for workloads using Portworx volumes:

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: portworx

spec:

  stork:

    enabled: true

    args:

      webhook-controller: true

```

## Uncordon the node​

- Openshift

- Kubernetes

You can now uncordon the node using: `oc adm uncordon <node>`

If you want to permanently decommission the node, you can skip the following step.

You can now uncordon the node using: `kubectl uncordon <node>`

If you want to permanently decommission the node, you can skip the following step.

## (Optional) Rejoin node to the cluster​

If you want Portworx to start again on this node and join as a new node, follow the node rejoin steps.

In this topic:
