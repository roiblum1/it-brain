# Create Sharedv4 PVCs

Source: https://docs.portworx.com/portworx-enterprise/provision-storage/create-pvcs/create-sharedv4-pvcs (Portworx Enterprise latest)

Create Sharedv4 PVCs | Portworx Enterprise Documentation

This document describes how to use Portworx sharedv4 (ReadWriteMany) volumes in your cluster.

Portworx provides two types of sharedv4 features:

- Sharedv4 volumes

- Sharedv4 service volumes

## Prerequisites​

- Sharedv4 volumes must be enabled on your cluster. Portworx sharedv4 volumes are enabled by default.

- NFS ports must be open

- The `rpcbind.service`, `nfs-server.service`, and `rpcbind.socket` must be enabled and running on each node in the cluster. Portworx Sharedv4 volumes use the NFS protocol, which requires the `rpcbind` service. This service helps NFS clients locate and connect to NFS services that provide Sharedv4 volumes.

## Provision a sharedv4 Volume​

Sharedv4 volumes are useful when you want multiple PODs to access the same PVC (volume) at the same time. They can use the same volume even if they are running on different hosts. They provide a global namespace and the semantics are POSIX compliant.

To increase fault tolerance, Portworx Enterprise creates Sharedv4 service volumes by default. Each Sharedv4 service volume has an associated Kubernetes service, and pods mount the volume through the service IP rather than through a specific node IP address. If the Sharedv4 (NFS) server goes offline and the volume requires a failover, only the application pods running on the two nodes involved in the failover need to be restarted.

important

-
If you do not specify `sharedv4_svc_type` in the `StorageClass`, Portworx uses the default value `ClusterIP` and creates a Sharedv4 service volume.

-
If the Portworx data network uses a private, non-routable network segment, such as a segment without a Layer 3 gateway, set `sharedv4_svc_type: ""` in the `StorageClass`. Otherwise, pods cannot reach the service IP and cannot access the volume through the service.

note

Notes about sharedv4 and sharedv4 service volumes:

- A sharedv4 volume is created if and only if the PVC access mode is `ReadWriteMany` or `ReadOnlyMany`. The "sharedv4" setting in the storageClass does not matter. In other words, if an app expects a sharedv4 volume while using a ReadWriteOnce PVC, some of the pods may fail to start. The PVC will have to be modified to use ReadWriteMany or ReadOnlyMany access mode.

- Sharedv4 service volumes are intended for use within your cluster where the volume resides.

- Sharedv4 service volumes default to using NFS version 4.0. If NFS 4.0 is not available on your hosts, you can allow Portworx to fall back to NFS 4.1 or 4.2. This changes how the volume fails over. For more information, see NFS version fallback.

- Sharedv4 (non-service) volumes default to using NFS version 3.

- Sharedv4 service volumes are not supported on Portworx clusters using Metro DR.

- On failover, applications may receive an error for non idempotent requests. For example, if an `mkdir` call is issued prior to failover, the client can resend it to the new server, which returns an `EEXIST` error if the directory was created by the first call.

### Step 1: Create a StorageClass​

- Kubernetes

- Openshift

-
Create the following `portworx-sharedv4-sc.yaml` StorageClass, specifying your own values for the following fields:

-
`metadata.name`: Specify a name for your StorageClass.

-
`parameters.repl`: Specify the replication factor you'd like to set.

-
`sharedv4`: Set the value to `true`.

-
(Optional) `sharedv4_svc_type`: Set to `"ClusterIP"` to create a Sharedv4 service volume, or to an empty string (`""`) to create a Sharedv4 volume. If you omit this parameter, Portworx uses `"ClusterIP"` by default.

-
(Optional) `stork.libopenstorage.org/preferRemoteNodeOnly`: Set the value to `"true"` if you want to strictly enforce pod anti-hyperconvergence with respect to volume replica.

-
(Optional) `stork.libopenstorage.org/preferRemoteNode`: Set the value to `"false"` if you want hyperconvergence with respect to volume replica. See for Sharedv4 service volume hyperconvergence for more information.

-
(Optional) `sharedv4_failover_strategy`: Set the value to `normal` or `aggressive` (shorter failover grace period)

note

The default value for `sharedv4_failover_strategy` in sharedv4 volumes is `normal`, and the default value for `sharedv4_failover_strategy` in sharedv4 service volumes is `aggressive`.

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: portworx-rwx-rep2

provisioner: pxd.portworx.com

parameters:

  repl: "2"

  sharedv4: "true"

  sharedv4_svc_type: "ClusterIP"

reclaimPolicy: Retain

allowVolumeExpansion: true

```

-
Apply the StorageClass you created by running the following command:

```

kubectl apply -f portworx-sharedv4-sc.yaml

```

-
Verify that the StorageClass is created:

```

kubectl describe storageclass portworx-rwx-rep2

```

```

Name:            portworx-rwx-rep2

IsDefaultClass:  No

Annotations:     kubectl.kubernetes.io/last-applied-configuration={"allowVolumeExpansion":true,"apiVersion":"storage.k8s.io/v1","kind":"StorageClass","metadata":{"annotations":{},"name":"portworx-rwx-rep2"},"parameters":{"disable_io_profile_protection":"1","io_profile":"auto","priority_io":"high","repl":"2","sharedv4":"true","sharedv4_svc_type":"ClusterIP"},"provisioner":"pxd.portworx.com","reclaimPolicy":"Retain"}

Provisioner:           pxd.portworx.com

Parameters:            disable_io_profile_protection=1,io_profile=auto,priority_io=high,repl=2,sharedv4=true,sharedv4_svc_type=ClusterIP

AllowVolumeExpansion:  True

MountOptions:          <none>

ReclaimPolicy:         Retain

VolumeBindingMode:     Immediate

Events:                <none>

```

-
Create the following `portworx-sharedv4-sc.yaml` StorageClass, specifying your own values for the following fields:

-
`metadata.name`: Specify a name for your StorageClass.

-
`parameters.repl`: Specify the replication factor you'd like to set.

-
`sharedv4`: Set the value to `true`.

-
(Optional) `sharedv4_svc_type`: Set to `"ClusterIP"` to create a Sharedv4 service volume, or to an empty string (`""`) to create a Sharedv4 volume. If you omit this parameter, Portworx uses `"ClusterIP"` by default.

-
(Optional) `stork.libopenstorage.org/preferRemoteNodeOnly`: Set the value to `"true"` if you want to strictly enforce pod anti-hyperconvergence with respect to volume replica.

-
(Optional) `stork.libopenstorage.org/preferRemoteNode`: Set the value to `"false"` if you want hyperconvergence with respect to volume replica. See for Sharedv4 service volume hyperconvergence for more information.

-
(Optional) `sharedv4_failover_strategy`: Set the value to `normal` or `aggressive` (shorter failover grace period)

note

The default value for `sharedv4_failover_strategy` in sharedv4 volumes is `normal`, and the default value for `sharedv4_failover_strategy` in sharedv4 service volumes is `aggressive`.

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: portworx-rwx-rep2

provisioner: pxd.portworx.com

parameters:

  repl: "2"

  sharedv4: "true"

  sharedv4_svc_type: "ClusterIP"

reclaimPolicy: Retain

allowVolumeExpansion: true

```

-
Apply the StorageClass you created by running the following command:

```

oc apply -f portworx-sharedv4-sc.yaml

```

-
Verify that the StorageClass is created:

```

oc describe storageclass portworx-rwx-rep2

```

```

Name:            portworx-rwx-rep2

IsDefaultClass:  No

Annotations:     kubectl.kubernetes.io/last-applied-configuration={"allowVolumeExpansion":true,"apiVersion":"storage.k8s.io/v1","kind":"StorageClass","metadata":{"annotations":{},"name":"portworx-rwx-rep2"},"parameters":{"disable_io_profile_protection":"1","io_profile":"auto","priority_io":"high","repl":"2","sharedv4":"true","sharedv4_svc_type":"ClusterIP"},"provisioner":"pxd.portworx.com","reclaimPolicy":"Retain"}

Provisioner:           pxd.portworx.com

Parameters:            disable_io_profile_protection=1,io_profile=auto,priority_io=high,repl=2,sharedv4=true,sharedv4_svc_type=ClusterIP

AllowVolumeExpansion:  True

MountOptions:          <none>

ReclaimPolicy:         Retain

VolumeBindingMode:     Immediate

Events:                <none>

```

### Step 2: Create a persistent volume claim​

- Kubernetes

- Openshift

-
Create a ReadWriteMany persistent volume claim. Save the following content into a file:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

  name: px-sharedv4-pvc

  annotations:

    volume.beta.kubernetes.io/storage-class: portworx-rwx-rep2

spec:

  accessModes:

    - ReadWriteMany

  resources:

    requests:

      storage: 10Gi

```

-
Apply the spec:

```

kubectl create -f px-sharedv4-pvc.yaml

```

Note that `accessModes` for this PVC is set to `ReadWriteMany` (RWX) so Kubernetes allows mounting this PVC on multiple pods.

-
Verify that the persistent volume claim is created:

```

kubectl get pvc

```

```

NAME              STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS     AGE

px-sharedv4-pvc   Bound    pvc-xxxxxxxx-xxxx-xxxx-xxxx-78dbc2ef7aeb   10Gi       RWX            portworx-rwx-rep2   46s

```

-
Create a ReadWriteMany persistent volume claim. Save the following content into a file:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

  name: px-sharedv4-pvc

  annotations:

    volume.beta.kubernetes.io/storage-class: portworx-rwx-rep2

spec:

  accessModes:

    - ReadWriteMany

  resources:

    requests:

      storage: 10Gi

```

-
Apply the spec:

```

oc create -f px-sharedv4-pvc.yaml

```

Note that `accessModes` for this PVC is set to `ReadWriteMany` (RWX) so Kubernetes on OCP allows mounting this PVC on multiple pods.

-
Verify that the persistent volume claim is created:

```

oc get pvc

```

```

NAME              STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS     AGE

px-sharedv4-pvc   Bound    pvc-xxxxxxxx-xxxx-xxxx-xxxx-78dbc2ef7aeb   10Gi       RWX            portworx-rwx-rep2   46s

```

### Step 3: Create pods which use the persistent volume claim​

- Kubernetes

- Openshift

We will start two pods which use the same shared volume.

-
Save the next two blocks into files pod1.yaml and pod2.yaml; use `kubectl apply -f pod1.yaml` and `kubectl apply -f pod2.yaml`

```

apiVersion: v1

kind: Pod

metadata:

  name: pod1

spec:

  containers:

  - name: test-container

    image: gcr.io/google_containers/test-webserver

    volumeMounts:

    - name: test-volume

      mountPath: /test-portworx-volume

  volumes:

  - name: test-volume

    persistentVolumeClaim:

      claimName: px-sharedv4-pvc

```

```

apiVersion: v1

kind: Pod

metadata:

  name: pod2

spec:

  containers:

  - name: test-container

    image: gcr.io/google_containers/test-webserver

    volumeMounts:

    - name: test-volume

      mountPath: /test-portworx-volume

  volumes:

  - name: test-volume

    persistentVolumeClaim:

      claimName: px-sharedv4-pvc

```

-
Verify that the pods are running:

```

kubectl get pods

```

```

NAME      READY     STATUS    RESTARTS   AGE

pod1      1/1       Running   0          2m

pod2      1/1       Running   0          1m

```

We will start two pods which use the same shared volume.

-
Save the next two blocks into files pod1.yaml and pod2.yaml; use `oc apply -f pod1.yaml` and `oc apply -f pod2.yaml`

```

apiVersion: v1

kind: Pod

metadata:

  name: pod1

spec:

  containers:

  - name: test-container

    image: gcr.io/google_containers/test-webserver

    volumeMounts:

    - name: test-volume

      mountPath: /test-portworx-volume

  volumes:

  - name: test-volume

    persistentVolumeClaim:

      claimName: px-sharedv4-pvc

```

```

apiVersion: v1

kind: Pod

metadata:

  name: pod2

spec:

  containers:

  - name: test-container

    image: gcr.io/google_containers/test-webserver

    volumeMounts:

    - name: test-volume

      mountPath: /test-portworx-volume

  volumes:

  - name: test-volume

    persistentVolumeClaim:

      claimName: px-sharedv4-pvc

```

-
Verify that the pods are running:

```

oc get pods

```

```

NAME      READY     STATUS    RESTARTS   AGE

pod1      1/1       Running   0          2m

pod2      1/1       Running   0          1m

```

## Convert a sharedv4 volume to a sharedv4 service volume​

Perform the following steps to convert a sharedv4 volume to use the new sharedv4 service feature:

- Detach the volume by scaling the application pods down to 0.

- Run the following `pxctl` command:

```

pxctl volume update --sharedv4_service_type=ClusterIP <volume>

```

- Scale the deployment back up to start the application.

## Convert a sharedv4 service volume to a sharedv4 volume​

Perform the following steps to convert a sharedv4 service volume to a sharedv4 volume:

- Detach the volume by scaling the application pods down to 0.

- Run the following pxctl command:

```

pxctl volume update --sharedv4_service_type="" <volume>

```

- Scale the deployment back up to start the application.

## Convert an existing sharedv4 service volume to prefer remote nodes only​

-
Scale down the application pods.

-
Run the following command to convert the volume to use `preferRemoteNodeOnly`:

```

pxctl volume update --label stork.libopenstorage.org/preferRemoteNodeOnly="true" <volume>

```

-
Scale the pods back up to start the application.

## Convert an existing sharedv4 service volume to prefer local nodes​

-
Scale down the application pods.

-
Run the following pxctl command to convert the volume to use `preferRemoteNode`:

```

pxctl volume update --label stork.libopenstorage.org/preferRemoteNode="false" <volume>

```

-
Scale the pods back up to start the application.

## Update a legacy shared volume to a sharedv4 volume​

You can convert an existing shared volume (deprecated) to a sharedv4 volume. Run the following command to update the volume setting:

```

pxctl volume update --sharedv4=on <volume>

```

note

To access PV/PVCs with a non-root user, refer here.

## NFS version fallback​

Some newer Linux distributions ship with NFS 4.0 disabled and support only NFS 4.1 and 4.2. Because a PVC with the `ReadWriteMany` access mode creates a sharedv4 service volume by default, and that volume defaults to NFS 4.0, the mount fails with a protocol-not-supported error on such a host.

If your distribution allows it, re-enabling NFS 4.0 on the host is the preferred fix, because it preserves seamless failover.

If NFS 4.0 cannot be enabled, you can allow Portworx to fall back to a later protocol version by setting the following environment variable in the `StorageCluster` specification:

```

env:

  - name: PX_ENABLE_SHAREDV4_NFS_NEGOTIATION

    value: "true"

```

With this variable set, a newly created volume advertises compatibility with NFS 4.0, 4.1, and 4.2, and the mount is attempted in that order: 4.0 first, then 4.1, then 4.2. The fallback applies to all sharedv4 volumes.

Instead of updating the `StorageCluster` specification, you can also enable the fallback at runtime with the `pxctl cluster options update` command. This does not require a Portworx restart:

```

pxctl cluster options update --enable-sharedv4-nfs-negotiation true

```

To verify the current setting, run the following command and look for the Enable sharedv4 NFS version negotiation (4.0->4.1->4.2) field:

```

pxctl cluster options list

```

To disable the fallback again, run the following command:

```

pxctl cluster options update --enable-sharedv4-nfs-negotiation false

```

As with the environment variable, this setting applies only to volumes created after it is changed; volumes that already exist are not affected.

When a volume mounts over NFS 4.1 or 4.2, Portworx uses the data IP of the node exporting it rather than the ClusterIP. The volume is still a sharedv4 service volume, but it fails over like a sharedv4 (non-service) volume:

BehaviorNFS 4.0NFS 4.1 and 4.2

Mount targetClusterIP of the volume's Kubernetes serviceData IP of the node exporting the volume

Pods restarted on failoverOnly the pods on the two nodes involved in the failoverAll application pods using the volume

I/O disruptionNone for pods on uninvolved nodesAll pods using the volume see a disruption

note

`PX_ALLOW_SHAREDV4_NFS_VERSION_FALLBACK` is disabled by default because it changes failover behavior. Enable it only if NFS 4.0 cannot be enabled on your hosts and you accept the loss of seamless failover for volumes created afterward.

In this topic:
