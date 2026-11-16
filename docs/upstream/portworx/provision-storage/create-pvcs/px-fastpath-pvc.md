# Create PX-Fast PVCs

Source: https://docs.portworx.com/portworx-enterprise/provision-storage/create-pvcs/px-fastpath-pvc (Portworx Enterprise latest)

Create PX-Fast PVCs | Portworx Enterprise Documentation

PX-Fast reduces I/O latency by providing a more direct path to the underlying storage for volumes with replication factor 1 (`repl=1`). PX-Fast uses the PX-StoreV2 datastore and supports workloads that require low-latency I/O.

PX-Fast supports two attachment types:

- Local attachment: The application and volume replica are on the same node. Portworx accesses the local storage pool directly. This is the default behavior.

- Remote attachment: The application and volume replica are on different nodes, such as in Kube Datastore (KDS) or KubeVirt deployments. Portworx accesses the replica over NVMe over Fabrics using TCP (NVMe-oF/TCP). Remote fastpath must be enabled at the cluster level.

If a volume does not meet the PX-Fast requirements, Portworx uses the standard I/O path.

## Prerequisites​

Before creating PX-Fast PVCs, ensure that your environment meets the requirements for the attachment type.

- Local attachment

- Remote attachment

- Portworx is deployed with the PX-StoreV2 datastore.

- The volume uses replication factor 1 (`repl=1`).

- The application pod or VM runs on the node that hosts the volume replica.

- Portworx Enterprise 3.7.2 or later is running on every node in the cluster.

- Portworx is deployed with the PX-StoreV2 datastore.

- The volume uses replication factor 1 (`repl=1`).

- TCP port `4420` is available exclusively for Portworx on every node, and network connectivity over this port is allowed between application nodes and nodes hosting volume replicas.

- The required NVMe-oF/TCP kernel modules and the `nvme-cli` package are available on every node.

important

When upgrading to Portworx Enterprise 3.7.2 from an earlier version, you can enable remote fastpath during the upgrade. After the upgrade, reboot every node to load the required PX fuse kernel driver. Until a node is rebooted, volumes attached to that node continue to use the standard I/O path.

Remote fastpath requires the following kernel modules, which must be available as loadable modules or built into the kernel. During installation, Portworx attempts to install the required packages and checks for the kernel modules at startup.

ModuleRoleKernel configuration

`nvme-core`NVMe core`CONFIG_NVME_CORE`

`nvme`NVMe PCIe driver`CONFIG_BLK_DEV_NVME`

`nvme-fabrics`NVMe-oF host`CONFIG_NVME_FABRICS`

`nvme-tcp`NVMe-oF/TCP host on the coordinator`CONFIG_NVME_TCP`

`nvmet`NVMe target on the replica node`CONFIG_NVME_TARGET`

`nvmet-tcp`NVMe-oF/TCP target on the replica node`CONFIG_NVME_TARGET_TCP`

`configfs`Configuration filesystem used by `nvmet``CONFIG_CONFIGFS_FS`

In air-gapped environments, install the `nvme-cli` package and ensure that the required kernel modules are available on every node before enabling remote fastpath. To check for loadable modules and required commands on a node, run:

```

for m in nvme-core nvme nvme-fabrics nvme-tcp nvmet nvmet-tcp configfs; do

  modinfo -n "$m" >/dev/null 2>&1 && echo "ok   $m" || echo "MISSING $m"

done

command -v nvme modprobe udevadm ss

```

note

The `modinfo` command checks for loadable modules. A module reported as `MISSING` might be built into the kernel. Verify the kernel configuration before treating it as unavailable.

## Supported platforms and kernels for remote fastpath​

Remote fastpath is supported on the following platforms and kernels:

PlatformSupported versionKernel

Red Hat OpenShift Container Platform (OCP)4.215.14

Ubuntu24.046.8.0-138-generic or later

note

Ubuntu kernels earlier than 6.8.0-138-generic do not include the NVMe/TCP fixes that remote fastpath requires.

## Limitations​

PX-Fast has the following limitations:

- PX-Fast does not support volumes with more than one replica.

- PX-Fast does not support aggregated volumes.

- Remote fastpath is not supported on Amazon Elastic Kubernetes Service (EKS), IBM Cloud Kubernetes Service (IKS), and Oracle Cloud Infrastructure Kubernetes Engine (OKE) clusters.

## Enable remote fastpath on the cluster​

Remote fastpath is disabled by default. You can enable it during Portworx installation or configure it on an existing cluster.

note

This section applies only to remote fastpath. For local fastpath, proceed to Create a StorageClass.

### How remote fastpath works​

Remote fastpath uses two nodes:

- Coordinator: The node where the application runs and the volume is attached.

- Target: The node that hosts the volume replica.

When Portworx activates remote fastpath, the target exports the volume as an NVMe namespace. The coordinator connects to this namespace and makes it available as a local block device.

Each namespace represents one volume. Portworx groups multiple namespaces into an NVMe subsystem for each coordinator-target pair and creates additional subsystems as needed.

On the coordinator, the imported device appears at:

```

/dev/pxfp/pxd<volume-id>-node<node-index>

```

Portworx assigns a stable device identifier, so the device path remains unchanged when the connection is disconnected and reestablished.

Remote fastpath activates when all the following conditions are met:

- The volume uses `repl=1` and has PX-Fast enabled.

- The cluster uses the `nvmeof-tcp` fastpath protocol.

- The volume replica is available on the target node.

- The coordinator and target nodes run the same Portworx Enterprise version.

- No volume operation or other condition prevents fastpath activation.

If any condition is not met, Portworx uses the standard I/O path.

### Enable remote fastpath during installation​

You can enable remote fastpath when generating the Portworx specification in Portworx Central.

- Sign in to Portworx Central and open the Generate Spec page.

- Select the Portworx version, platform, distribution, and namespace for your environment, and then select Customize.

note

Remote fastpath is not supported on Amazon Elastic Kubernetes Service (EKS), IBM Cloud Kubernetes Service (IKS), and Oracle Cloud Infrastructure Kubernetes Engine (OKE) clusters.

- On the Storage tab, select PX-Store V2 as the datastore type.

- On the Deployment tab, select Remote Fastpath (NVMe-oF/TCP).

- Complete the remaining configuration steps and generate the Portworx specification.

Portworx uses the selected fastpath protocol when it starts.

### Configure remote fastpath on an existing cluster​

To enable or change remote fastpath on an existing cluster, update the `-fastpath_protocol` argument in the `portworx.io/misc-args` annotation of the `StorageCluster` resource.

-
Edit the `StorageCluster` resource:

```

kubectl edit stc <storage-cluster-name> -n <portworx-namespace>

```

-
Add or update the `-fastpath_protocol` argument:

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  annotations:

    portworx.io/misc-args: "-fastpath_protocol nvmeof-tcp"

```

If the annotation already contains other arguments, retain them.

Set the argument to one of the following values:

ValueDescription

`nvmeof-tcp`Enables remote fastpath over NVMe-oF/TCP. Locally attached volumes continue to use local fastpath.

`local`Disables remote fastpath. Only local fastpath is available.

-
Save the `StorageCluster` resource.

warning

Changing the `portworx.io/misc-args` annotation restarts Portworx on every node in the cluster. Schedule this change during a maintenance window.

## Create PX-Fast PVCs​

The following procedure applies to both local and remote fastpath. Both attachment types use the same `StorageClass` configuration because remote fastpath is enabled at the cluster level.

### Create a StorageClass​

-
Save the following configuration to a file named `px-fast.yaml`:

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: px-fast

provisioner: pxd.portworx.com

parameters:

  repl: "1"

  fastpath: "true"

allowVolumeExpansion: true

```

The `repl: "1"` parameter provisions volumes with one replica, and `fastpath: "true"` enables PX-Fast for eligible volumes.

-
Create the `StorageClass`:

```

kubectl apply -f px-fast.yaml

```

The output is similar to the following:

```

storageclass.storage.k8s.io/px-fast created

```

-
Verify that the `StorageClass` was created:

```

kubectl describe storageclass px-fast

```

The output is similar to the following:

```

Provisioner:           pxd.portworx.com

Parameters:            fastpath=true,repl=1

AllowVolumeExpansion:  true

MountOptions:          <none>

ReclaimPolicy:         Delete

VolumeBindingMode:     Immediate

Events:                <none>

```

### Create a PVC​

-
Save the following configuration to a file named `px-fast-pvc.yaml`:

```

apiVersion: v1

kind: PersistentVolumeClaim

metadata:

  name: px-fast-pvc

spec:

  storageClassName: px-fast

  accessModes:

    - ReadWriteOnce

  resources:

    requests:

      storage: 1Gi

```

-
Create the PVC:

```

kubectl apply -f px-fast-pvc.yaml

```

-
Verify that the PVC was created:

```

kubectl get pvc

```

## Deploy an application that uses a PX-Fast PVC​

Application scheduling depends on whether the volume uses local or remote fastpath.

- Local attachment

- Remote attachment

For local fastpath, the application pod must run on the node that hosts the volume replica.

The following Deployment uses the `stork.libopenstorage.org/preferLocalNodeOnly: "true"` annotation to require Stork to schedule the pod on the replica node:

```

apiVersion: apps/v1

kind: Deployment

metadata:

  name: mysql

spec:

  selector:

    matchLabels:

      app: mysql

  strategy:

    rollingUpdate:

      maxSurge: 1

      maxUnavailable: 1

    type: RollingUpdate

  replicas: 1

  template:

    metadata:

      annotations:

        stork.libopenstorage.org/preferLocalNodeOnly: "true"

      labels:

        app: mysql

    spec:

      containers:

        - name: mysql

          image: mysql:5.6

          env:

            - name: MYSQL_ROOT_PASSWORD

              value: password

          ports:

            - containerPort: 3306

          volumeMounts:

            - name: mysql-persistent-storage

              mountPath: /var/lib/mysql

      volumes:

        - name: mysql-persistent-storage

          persistentVolumeClaim:

            claimName: px-fast-pvc

```

If you omit the annotation, Stork makes a best-effort attempt to schedule the pod on the replica node.

If the pod runs on another node, the volume cannot use local fastpath.

warning

Do not use the `stork.libopenstorage.org/preferLocalNodeOnly: "true"` annotation with remote fastpath. This annotation requires the pod to run on the replica node, preventing remote attachment.

When remote fastpath is enabled, Stork can schedule the application pod on any eligible node.

If the pod runs on a node other than the replica node, Portworx can use NVMe-oF/TCP to provide remote fastpath.

The following Deployment does not use the local-node scheduling annotation:

```

apiVersion: apps/v1

kind: Deployment

metadata:

  name: mysql

spec:

  selector:

    matchLabels:

      app: mysql

  strategy:

    rollingUpdate:

      maxSurge: 1

      maxUnavailable: 1

    type: RollingUpdate

  replicas: 1

  template:

    metadata:

      labels:

        app: mysql

    spec:

      containers:

        - name: mysql

          image: mysql:5.6

          env:

            - name: MYSQL_ROOT_PASSWORD

              value: password

          ports:

            - containerPort: 3306

          volumeMounts:

            - name: mysql-persistent-storage

              mountPath: /var/lib/mysql

      volumes:

        - name: mysql-persistent-storage

          persistentVolumeClaim:

            claimName: px-fast-pvc

```

## Verify that a volume uses PX-Fast​

To check whether a volume uses PX-Fast, run:

```

pxctl volume inspect <volume-id>

```

If PX-Fast is active, the `State` field includes `fastpath active`:

```

State                : Attached: xxxxxxxx-xxxx-xxxx-xxxx-cb3180bf27d1 (10.13.178.41) (fastpath active)

```

If the `State` field does not show `fastpath active`, the volume uses the standard I/O path.

To check for related alerts, run:

```

pxctl alerts show

```

The output includes a `VolumeFastpathStatusActive` alert for each volume on which fastpath is active:

```

VOLUME	VolumeFastpathStatusActive	113199871200195289	NOTIFY	115	Nov 3 16:14:36 UTC 2026	Oct 30 22:18:17 UTC 2026	Volume (Name: pvc-xxxx-xxxx-xxx-xxxxxx-xxxxx Id: 113199871200195289) fastpath status is active.

VOLUME	VolumeFastpathStatusActive	618950033963944167	NOTIFY	70	Nov 3 16:14:36 UTC 2026	Oct 31 19:23:40 UTC 2026	Volume (Name: pvc-xxxx-xxxx-xxx-xxxxxx-xxxxx Id: 618950033963944167) fastpath status is active.

```

## When Portworx uses the standard I/O path​

Portworx switches a volume from fastpath to the standard I/O path under the following conditions:

ConditionBehavior

Volume operationPortworx switches the volume to the standard I/O path before a resize, snapshot, clone, restore, or CloudSnap operation. After the operation completes and the taint timeout expires, it attempts to reactivate fastpath. Reactivation is not immediate.

Pool operationPortworx switches the volumes on the pool to the standard I/O path before a pool move, pool resize, or pool maintenance mode operation.

NVMe-oF/TCP I/O errorIf the connection is lost or times out, Portworx switches to the standard I/O path and retries fastpath activation.

Repeated failoverIf a volume fails over five times within 10 minutes, Portworx keeps it on the standard I/O path to prevent further disruption. Detach and reattach the volume to make it eligible for fastpath again.

Target node restart or failureThe coordinator switches affected volumes to the standard I/O path and disconnects from the stale NVMe subsystem.

Coordinator node restart or failureVolumes attached to the coordinator switch to the standard I/O path. The target releases its exports without waiting for the coordinator.

Rolling upgradeA coordinator cannot establish remote fastpath with a target running a different Portworx version. Eligible volumes return to fastpath after both nodes complete the upgrade.

Volume detachPortworx removes the remote fastpath session when the volume is detached.

Switching a volume between fastpath and the standard I/O path briefly suspends I/O. I/O resumes after the switch completes.

After a Portworx restart, node restart, or volume operation, fastpath activation is blocked for three minutes. A background monitor then checks eligible volumes for fastpath activation.

Because the monitor runs every three minutes, a volume can take several minutes to return to fastpath. You do not need to restart the application or reattach the volume.

## Monitor PX-Fast alerts​

Portworx raises the following alerts for PX-Fast operations, failures, and status changes.

To view these alerts, run:

```

pxctl alerts show

```

AlertResource typeDescription

`FastpathPortInUse`NodeAnother process is using TCP port `4420`, preventing the node from serving as a remote fastpath target.

`VolumeFastpathSetupFailed`VolumePortworx could not activate fastpath for the volume. The alert identifies the affected node and reason.

`VolumeFastpathStatusActive`VolumeThe volume switched to fastpath.

`VolumeFastpathStatusInactive`VolumeThe volume switched to the standard I/O path.

## Troubleshoot PX-Fast issues​

The following table describes common PX-Fast issues, their possible causes, and how to resolve them:

SymptomPossible causeResolution

Volumes continue to use the standard I/O path after remote fastpath is enabled.Portworx is not running on every node, or some nodes have not been rebooted after upgrading to Portworx Enterprise 3.7.2.Verify that Portworx is running on every node. Reboot any node that has not been rebooted since the upgrade.

A volume does not show `fastpath active` even though remote fastpath is enabled.The volume has more than one replica, PX-Fast is not enabled for the volume, or a volume operation is in progress.Run `pxctl volume inspect <volume-id>` and verify that `HA` is `1`. Wait for any ongoing volume operation to complete.

A volume repeatedly returns to the standard I/O path.The volume failed over five times within 10 minutes, so Portworx keeps it on the standard I/O path.Check the network path between the coordinator and target nodes, and then detach and reattach the volume.

Portworx raises a `FastpathPortInUse` alert.Another process is using TCP port `4420` on the affected node. Volumes using that node as a target can also raise `VolumeFastpathSetupFailed`.Run `ss -lptn 'sport = :4420'` to identify the process. Stop the process or configure it to use another port, and then restart Portworx on the affected node.

Pods are not scheduled on nodes other than the replica node.The application specification contains the `stork.libopenstorage.org/preferLocalNodeOnly: "true"` annotation.Remove the annotation. For more information, see Deploy an application that uses a PX-Fast PVC.

## Related topics​

- PX-Fast volumes using pxctl

- Portworx Datastores

- Kube Datastore for Portworx Enterprise 3.7.2

In this topic:
