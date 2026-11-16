# Manage Volume Lifecycle with CSI Driver

Source: https://docs.portworx.com/portworx-enterprise/provision-storage/volume-lifecycle (Portworx Enterprise latest)

Manage Volume Lifecycle with CSI Driver | Portworx Enterprise Documentation

The Container Storage Interface (CSI) is a standard for exposing storage to workloads on Kubernetes. Portworx implements a CSI driver that integrates with the Kubernetes storage framework, enabling dynamic provisioning, snapshotting, cloning, and volume expansion through native Kubernetes APIs.

If the kubernetes version is Kubernetes 1.31.x or higher, CSI is enabled by default for all Portworx PVCs.

This page walks you through the volume lifecycle with the Portworx Enterprise CSI driver:

- Volume Operations: Create PVCs, deploy workloads, create sharedv4 volumes, clone and expand volumes.

- Data Protection and Snapshots: Take local and cloud snapshots, restore volumes from snapshots.

- Secure your volumes: Encrypt volumes using Kubernetes secrets or external key management, and secure volumes with RBAC.

- Ephemeral Volumes: Use ephemeral inline volumes for temporary storage.

- Raw Block Volumes: Provision and use raw block devices.

## Volume Operations​

### Create and use persistent volumes​

Create and use volumes by configuring specification you create for your storage class, PVC, and volumes.

In this example we are using the `px-csi-db` storage class out of the box. For a list of available storage classes offered by Portworx, see Portworx Storage Classes.

-
Create a PersistentVolumeClaim based on the `px-csi-db` StorageClass:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

  name: px-mysql-pvc

spec:

  storageClassName: px-csi-db

  accessModes:

    - ReadWriteOnce

  resources:

    requests:

      storage: 2Gi

```

-
Create a volume by referencing the PVC you created. This example creates a MySQL deployment referencing the `px-mysql-pvc` PVC you created in the previous step:

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

        version: "1"

    spec:

      containers:

      - image: mysql:5.6

        name: mysql

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

          claimName: px-mysql-pvc

```

### Create sharedv4 volumes​

Create sharedv4 volumes by performing the following steps.

-
Create a sharedv4 PVC by creating the following `shared-pvc.yaml` file:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

  name: px-mysql-pvc

spec:

  storageClassName: px-csi-db

  accessModes:

    - ReadWriteMany

  resources:

    requests:

      storage: 2Gi

```

- Kubernetes

- Openshift

-
Apply the `shared-pvc.yaml` file:

```

kubectl apply -f shared-pvc.yaml

```

-
Apply the `shared-pvc.yaml` file:

```

oc apply -f shared-pvc.yaml

```

### Clone volumes​

You can clone Portworx Volumes, duplicating both the volume and content within it.

limitation

Cloning a PVC from a source volume on a non–FADA Active-Active (non-stretched) pod to a target PVC on a FADA Active-Active (stretched) pod is not supported. When you enable this configuration, the clone operation fails and the target PVC remains in the `Pending` state without any error message. The backend logs the failure as: `Failed to create volume(400): Msg1: Cannot copy volume into a stretched pod`.

-
Create a PVC that references the PVC you wish to clone, specifying the `dataSource` with the `kind` and `name` of the target PVC you wish to clone. The following spec creates a clone of the `px-mysql-pvc` PVC in a YAML file named `clonePVC.yaml`:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

    name: clone-of-px-mysql-pvc

spec:

    storageClassName: px-csi-db

    accessModes:

      - ReadWriteOnce

    resources:

      requests:

        storage: 2Gi

    dataSource:

    kind: PersistentVolumeClaim

    name: px-mysql-pvc

```

- Kubernetes

- Openshift

-
Apply the `clonePVC.yaml` spec to create the clone:

```

kubectl apply -f clonePVC.yaml

```

-
Apply the `clonePVC.yaml` spec to create the clone:

```

oc apply -f clonePVC.yaml

```

PVC Migration

You cannot migrate or convert PVCs created using the native Kubernetes driver to the CSI driver. However, both types of PVCs can coexist on the same cluster, so migration is not necessary.

## Data Protection and Snapshots​

To use VolumeSnapshots with the Portworx CSI Driver, Snapshot Controller must be enabled in your StorageCluster. By default, both CSI and `installSnapshotController` are enabled in Portworx. If another component manages the snapshot CRDs, such as the GKE add-on manager or OpenShift CSI controller, set `installSnapshotController` to `false`. Starting with Operator 26.5.0, the Operator then also stops reconciling the snapshot CRDs.

If Snapshot Controller is not enabled, run the following command to edit the `StorageCluster` and update the configuration:

- Kubernetes

- Openshift

```

kubectl edit stc <storageclustername> -n <px-namespace>

```

```

  csi:

    enabled: true

    installSnapshotController: true

```

```

oc edit stc <storageclustername> -n <px-namespace>

```

```

    csi:

      enabled: true

      installSnapshotController: true

```

### Manage local snapshots​

If you already have a PVC, complete the following steps to create, restore, or delete a VolumeSnapshot.

-
Create a VolumeSnapshotClass, specifying the following:

-
The `snapshot.storage.kubernetes.io/is-default-class: "true"` annotation

-
The `csi.storage.k8s.io/snapshotter-secret-name` parameter with your encryption and/or authorization secret

-
The `csi.storage.k8s.io/snapshotter-secret-namespace` parameter with the namespace your secret is in.

note

Specify `snapshotter-secret-name` and `snapshotter-secret-namespace` if px-security is `ENABLED`.

See enable security in Portworx for more information.

```

apiVersion: snapshot.storage.k8s.io/v1

kind: VolumeSnapshotClass

metadata:

  name: px-csi-snapclass

  annotations:

    snapshot.storage.kubernetes.io/is-default-class: "true"

driver: pxd.portworx.com

deletionPolicy: Delete

parameters: ## Specify only if px-security is ENABLED

  csi.storage.k8s.io/snapshotter-secret-name: px-user-token

  csi.storage.k8s.io/snapshotter-secret-namespace: <px-namespace>

  csi.openstorage.org/snapshot-type: local

```

-
Manage Local Snapshots.

You can perform operations such as create, update, or delete a VolumeSnapshot as follows:

-
Create a VolumeSnapshot:

```

apiVersion: snapshot.storage.k8s.io/v1

kind: VolumeSnapshot

metadata:

  name: px-csi-snapshot

spec:

  volumeSnapshotClassName: px-csi-snapclass

  source:

    persistentVolumeClaimName: px-mysql-pvc

```

note

VolumeSnapshot objects are namespace-scoped and should be created in the same namespace as the PVC.

-
Restore from a VolumeSnapshot:

```

apiVersion: v1

kind: PersistentVolumeClaim

metadata:

  name: px-csi-pvc-restored

spec:

  storageClassName: px-csi-db

  dataSource:

    name: px-csi-snapshot

    kind: VolumeSnapshot

    apiGroup: snapshot.storage.k8s.io

  accessModes:

    - ReadWriteOnce

  resources:

    requests:

      storage: 2Gi

```

-
Delete a VolumeSnapshot:

```

kubectl delete VolumeSnapshot <snapshot-name>

```

- Kubernetes

- Openshift

See the Kubernetes CSI Volume Snapshot documentation for more examples and documentation.

See the OpenShift CSI Volume Snapshot documentation for more examples and documentation.

### Manage cloud snapshots​

important

- Before creating or restoring a cloud snapshot, you must configure S3 credentials that Portworx uses to communicate with the S3 endpoint where snapshots are uploaded. For information on how to create the credential using the pxctl command, see Managing Cloud Credentials Using pxctl.

- If your cluster has a single credential configured, you do not need to specify credentials during snapshot or restore operations. Portworx automatically uses the configured credential.

- If your cluster has multiple credentials, create a `Kubernetes secret` containing the `credential ID` and reference it in the `VolumeSnapshotClass` or storage class, depending on your operation. Update the secret whenever credentials change between snapshot creation, deletion, or restore operations to ensure successful authentication.

- When restoring a PVC from a CloudSnapshot, ensure that the target PVC uses the same storage class properties as the source PVC.

If you already have a PVC, complete the following steps to create, restore, or delete a CloudSnapshot.

-
Create a VolumeSnapshotClass:

- Single Credential

- Multiple Credentials

Specify the `csi.openstorage.org/snapshot-type` parameter as `cloud`.

```

apiVersion: snapshot.storage.k8s.io/v1

deletionPolicy: Delete

driver: pxd.portworx.com

kind: VolumeSnapshotClass

metadata:

  name: px-csi-cloud-snapshot-class

parameters:

  csi.openstorage.org/snapshot-type: cloud

```

-
Specify the `csi.openstorage.org/snapshot-type` parameter as `cloud`.

-
Replace the `csi.openstorage.org/snapshot-credential-id` parameter with the UUID of the S3 credential.

```

apiVersion: snapshot.storage.k8s.io/v1

deletionPolicy: Delete

driver: pxd.portworx.com

kind: VolumeSnapshotClass

metadata:

  name: px-csi-cloud-snapshot-class

parameters:

  csi.openstorage.org/snapshot-type: cloud

  csi.openstorage.org/snapshot-credential-id: <credential-UUID>

```

-
Manage Cloud Snapshots.

You can perform operations such as create, update, or delete a Cloud VolumeSnapshot as follows:

-
Create a Cloud VolumeSnapshot:

```

apiVersion: snapshot.storage.k8s.io/v1

kind: VolumeSnapshot

metadata:

  name: cloud-snapshot-1

spec:

  volumeSnapshotClassName: px-csi-cloud-snapshot-class

source:

  persistentVolumeClaimName: task-pv-claim

```

-
Restore from a Cloud VolumeSnapshot:

```

apiVersion: v1

kind: PersistentVolumeClaim

metadata:

  name: pvc-restore

spec:

  storageClassName: px-csi-replicated

  dataSource:

    name: cloud-snapshot-1

    kind: VolumeSnapshot

    apiGroup: snapshot.storage.k8s.io

  accessModes:

    - ReadWriteOnce

  resources:

    requests:

      storage: 3Gi

```

-
Delete a Cloud VolumeSnapshot:

```

kubectl delete VolumeSnapshot <cloudsnapshot-name>

```

- Kubernetes

- Openshift

See the Kubernetes-CSI snapshotting documentation for more examples and documentation.

See the Openshift-CSI snapshotting documentation for more examples and documentation.

## Secure your volumes​

### Encryption​

For information about how to encrypt PVCs using Kubernetes secrets, see Encrypting PVCs with Kubernetes secrets.

### Authorization and Authentication​

You can secure your volumes with token-based authorization. In using token-based authorization, you create secrets containing your token credentials and specify them in your StorageClass in one of two ways:

- Using hardcoded values

- Using template values

You can also mix these two methods to form your own hybrid approach.

#### Using hardcoded values​

This example secures a storage class by specifying hardcoded values for the token and namespace. Users who create PVCs based on this StorageClass will always have their PVCs use the `px-user-token` Secret under the `<px-namespace>` namespace.

-
Find or create your token secret:

For operator deployment with security enabled, a user token is automatically created and refreshed under `px-user-token` in your `StorageCluster` namespace. Refer to secure your storage with the Operator for more information.

- Kubernetes

- Openshift

```

kubectl get secrets px-user-token -n <px-namespace>

```

```

NAME            TYPE     DATA   AGE

px-user-token   Opaque   1      23h

```

```

oc get secrets px-user-token -n <px-namespace>

```

```

NAME            TYPE     DATA   AGE

px-user-token   Opaque   1      23h

```

For all other configurations, create your own token secret:

```

kubectl create secret generic px-user-token \

  -n <px-namespace> --from-literal=auth-token=$USER_TOKEN

```

-
Modify the storageClass:

If you're using Kubernetes secrets, add the following parameters that are shown in the following example:

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: px-csi-db-encrypted-k8s

provisioner: pxd.portworx.com

parameters:

  repl: "3"

  secure: "true"

  io_profile: auto

  io_priority: "high"

  csi.storage.k8s.io/provisioner-secret-name: px-user-token

  csi.storage.k8s.io/provisioner-secret-namespace: <px-namespace>

  csi.storage.k8s.io/node-publish-secret-name: px-user-token

  csi.storage.k8s.io/node-publish-secret-namespace: <px-namespace>

reclaimPolicy: Delete

volumeBindingMode: Immediate

allowVolumeExpansion: true

```

If you're using another secret provider, such as Vault, Google KMS, AWS KMS, or KVDM, define the desired encryption key in the `secret_key` parameter directly as a parameter on the Portworx CSI StorageClass. For example:

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: px-csi-db-encrypted-vault

provisioner: pxd.portworx.com

parameters:

  repl: "3"

  secure: "true"

  io_profile: auto

  io_priority: "high"

  secret_key: px-cluster-key

reclaimPolicy: Delete

volumeBindingMode: Immediate

allowVolumeExpansion: true

```

note

Ensure that the secret called `px-cluster-key` exists and contains the value that you can use to encrypt your volumes.

#### Using template values​

This example secures a StorageClass by hardcoding the token and namespace. If you have created PVCs based on this StorageClass, you can have your PVCs use the StorageClass, which you specify in the annotation of your PVC, and the namespace specified in your PVC.

-
Modify the StorageClass, adding the highlighted `csi.storage.k8s.io` parameters:

```

apiVersion: storage.k8s.io/v1

kind: StorageClass

metadata:

  name: px-csi-db-encrypted-k8s

provisioner: pxd.portworx.com

parameters:

  repl: "3"

  secure: "true"

  io_profile: auto

  io_priority: "high"

  csi.storage.k8s.io/provisioner-secret-name: ${pvc.name}

  csi.storage.k8s.io/provisioner-secret-namespace: ${pvc.namespace}

  csi.storage.k8s.io/node-publish-secret-name: ${pvc.name}

  csi.storage.k8s.io/node-publish-secret-namespace: ${pvc.namespace}

reclaimPolicy: Delete

volumeBindingMode: Immediate

allowVolumeExpansion: true

```

-
Create a secret in your PVC's namespace with the same name as the PVC. For example, a PVC named `px-mysql-pvc` must have an associated secret named `px-mysql-pvc`.

- Kubernetes

- Openshift

- Get the token as mentioned in Using hardcoded values:

```

USER_TOKEN=$(kubectl get secrets px-user-token -n <px-namespace> -o json | jq -r '.data["auth-token"]' | base64 -d)

```

- Create the secret:

```

kubectl create secret generic px-mysql-pvc -n <px-namespace> --from-literal=auth-token=$USER_TOKEN

```

- Get the token as mentioned in Using hardcoded values:

```

USER_TOKEN=$(oc get secrets px-user-token -n <px-namespace> -o json | jq -r '.data["auth-token"]' | base64 -d)

```

- Create the secret:

```

oc create secret generic px-mysql-pvc -n <px-namespace> --from-literal=auth-token=$USER_TOKEN

```

## Create Ephemeral volumes​

Generic ephemeral volumes also work with typical storage operations such as snapshotting, cloning, resizing, and storage capacity tracking.

The following steps will allow you to create a generic ephemeral volume with the Portworx CSI Driver.

In this example we are using the `px-csi-db` storage class out of the box. For a list of available storage classes offered by Portworx, see Portworx Storage Classes.

-
Create a pod spec that uses a Portworx StorageClass, declaring the ephemeral volume as seen below in a YAML file named `ephemeral-volume-pod.yaml`:

```

kind: Pod

apiVersion: v1

metadata:

  name: my-app

spec:

  containers:

    - name: my-frontend

      image: busybox

      volumeMounts:

      - mountPath: "/scratch"

        name: scratch-volume

      command: [ "sleep", "1000000" ]

  volumes:

    - name: scratch-volume

      ephemeral:

        volumeClaimTemplate:

          metadata:

            labels:

              type: my-frontend-volume

          spec:

            accessModes: [ "ReadWriteOnce" ]

            storageClassName: "px-csi-db"

            resources:

              requests:

                storage: 1Gi

```

-
Apply the `ephemeral-volume-pod.yaml` spec to create the pod with a generic ephemeral volume:

- Kubernetes

- Openshift

```

kubectl apply -f ephemeral-volume-pod.yaml

```

```

oc apply -f ephemeral-volume-pod.yaml

```

note

Ephemeral volumes are automatically deleted when the associated application pod is deleted.

## Create and use Raw Block PVCs​

Portworx supports both File and Block volume types in Kubernetes and OpenShift cluster PVCs. If your application has a requirement to consume a raw block device as opposed to a mounted filesystem, follow the instructions to use Portworx PVC with Raw Block devices.

note

Currently, only ReadWriteOnce PVCs can be created with the block volume mode.

In this example we are using the `px-csi-db` storage class out of the box. For a list of available storage classes offered by Portworx, see Portworx Storage Classes.

-
Create a PVC spec that references the portworx-csi-sc as seen below in a YAML file named `raw-block-pvc.yaml`:

```

kind: PersistentVolumeClaim

apiVersion: v1

metadata:

   name: px-csi-raw-block-pvc

spec:

   volumeMode: Block

   storageClassName: px-csi-db

   accessModes:

     - ReadWriteOnce

   resources:

     requests:

       storage: 2Gi

```

-
Apply the `raw-block-pvc.yaml` spec to create the raw block PVC:

- Kubernetes

- Openshift

```

kubectl apply -f raw-block-pvc.yaml

```

```

oc apply -f raw-block-pvc.yaml

```

-
Create a deployment SPEC that references the above raw block PVC in `raw-block-deployment.yaml`:

```

apiVersion: apps/v1

kind: Deployment

metadata:

  name: ioping

spec:

  selector:

    matchLabels:

      app: ioping

  strategy:

    rollingUpdate:

      maxSurge: 1

      maxUnavailable: 1

    type: RollingUpdate

  replicas: 1

  template:

    metadata:

      labels:

        app: ioping

        version: "1"

    spec:

      containers:

      - name: ioping

        image: hpestorage/ioping

        command: [ "ioping" ]

        args: [ "/dev/xvda" ]

        volumeDevices:

        - name: raw-device

          devicePath: /dev/xvda

      volumes:

      - name: raw-device

        persistentVolumeClaim:

          claimName: px-csi-raw-block-pvc

```

-
Apply the `raw-block-deployment.yaml` spec to create the deployment utilizing our raw block PVC:

- Kubernetes

- Openshift

```

kubectl apply -f raw-block-deployment.yaml

```

```

oc apply -f raw-block-deployment.yaml

```

In this topic:
