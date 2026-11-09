# Update Portworx file system dependencies

Source: https://docs.portworx.com/portworx-enterprise/how-to-guides/pxlibupdate (Portworx Enterprise latest)

Update Portworx file system dependencies | Portworx Enterprise Documentation

The Portworx Enterprise container ships with an archive containing precompiled modules for the kernels which were available at the time the container was released. If a kernel is released after a Portworx release, a pre-compiled version of the modules will not exist in the container. If Portworx is deployed in a setup which does not have access to `mirrors.portworx.com` to download the latest modules (for example, an air-gapped deployment), then Portworx will fail to come up.

Alternatively, in such deployments, you can publish the updated containers to internal container repositories where Portworx can download the new kernel modules.

Regardless of whether your cluster accesses the updated container through `mirrors.portworx.com` or an internal container registry, you can use that container to update your nodes' Portworx installation to include the latest batch of precompiled modules. Perform the update by running a DaemonSet in the cluster where Portworx has been installed.

## Update filesystem dependencies​

- Airgapped

- Non-airgapped

- IBM

In air-gapped environments, you can update filesystem dependencies using one of the following methods:

- Operator-managed update (recommended): Configure the Portworx Operator to automatically deploy and manage the `pxfslibs` update DaemonSet through the StorageCluster specification.

- Manual update: Manually deploy the `pxfslibs` update DaemonSet in your cluster.

### Operator-managed update

You can use the `spec.pxfslibsUpdate` section in the StorageCluster specification to configure the Portworx Operator to automatically deploy and manage the `pxfslibs` update DaemonSet. The Operator handles DaemonSet creation, execution monitoring, status updates, and cleanup.

-
Run the following command to get the latest pxfslib image version for your Portworx Enterprise version.

```

curl -fsL "https://install.portworx.com/<px-version>/?comp=pxlibupdate" | grep image: | sed 's/image://'

```

```

portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

```

-
Pull the above image from the external registry, tag it, and push it to your internal registry:

```

docker pull portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

docker tag portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update <internal-registry>/portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

docker push <internal-registry>/portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

```

-
Edit the `StorageCluster` specification to add the `pxfslibsUpdate` configuration:

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: px-cluster

  namespace: <portworx>

spec:

  pxfslibsUpdate:

    enabled: true

    image: <internal-registry>/portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

    autoDelete: true

    onDemandTrigger: "27 Oct 2025 9:35 PM"

    schedule: "0 3 * * 0"

```

Parameters:

- `enabled`: Set to `true` to enable the `pxfslibs` update DaemonSet deployment.

- `image`: Specify the `pxfslib-updater` image from your internal registry.

- `autoDelete`: Set to `true` to automatically delete the DaemonSet after successful execution. Set to `false` to keep it for debugging.

- `onDemandTrigger`: Specify a timestamp to trigger an immediate update. Each time you update this field with a new timestamp, the Operator triggers a new update. Use this when you manually push updated `pxfslib-updater` images to your internal registry.

- `schedule`: Specify a Cron expression to schedule recurring updates (for example, `"0 3 * * 0"` runs every Sunday at 3:00 AM). Use this if you have automation in place to update the `pxfslib-updater` image in your internal registry, allowing you to automatically update the filesystem dependencies on a schedule.

note

If neither `onDemandTrigger` nor `schedule` is configured, the DaemonSet is deployed only during Portworx Enterprise installation or Portworx Enterprise upgrade. To update filesystem dependencies before an OCP upgrade without upgrading Portworx Enterprise, set `onDemandTrigger` to a current timestamp, or configure a `schedule`.

-
Apply the updated StorageCluster specification:

```

kubectl apply -f <storagecluster-spec>.yaml

```

-
Check the StorageCluster status to verify update completion:

```

kubectl get storagecluster px-cluster -n <portworx> -o yaml

```

The status section shows the `pxfslibs` update history:

```

...

status:

  pxfslibsUpdate:

    triggers:

    - lastTransitionTime: "2025-11-24T19:55:19Z"

      message: px-libs-update completed

      phase: Completed

      triggerTime: "2025-11-23T19:45:00Z"

      type: Install

    - lastTransitionTime: "2025-11-24T11:28:49Z"

      message: px-libs-update completed

      phase: Completed

      triggerTime: "2025-11-23T18:30:00Z"

      type: OnDemand

```

-
If `autoDelete` is set to `false`, manually delete the DaemonSet after verifying the changes:

```

kubectl delete daemonset px-libs-update -n <portworx>

```

#### Configure placement rules for px-libs-update

By default, the `px-libs-update` DaemonSet inherits placement rules (NodeAffinity and Tolerations) from `StorageCluster.Spec.Placement`, so it runs on the same nodes as Portworx storage pods.

You can override this default with a `ComponentK8sConfig` CR using the `PxLibsUpdate` component and `px-libs-update` workload. Placement configured this way takes precedence over `StorageCluster.Spec.Placement`.

note

Component names in `ComponentK8sConfig` are case-sensitive. Use `PxLibsUpdate` exactly as shown.

The following example configures `px-libs-update` to run only on nodes with the `node-role.kubernetes.io/infra` label, and adds a matching toleration:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: pxlibsupdate-placement

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - PxLibsUpdate

      workloadConfigs:

        - workloadNames:

            - px-libs-update

          placement:

            nodeAffinity:

              requiredDuringSchedulingIgnoredDuringExecution:

                nodeSelectorTerms:

                  - matchExpressions:

                      - key: node-role.kubernetes.io/infra

                        operator: Exists

            tolerations:

              - key: node-role.kubernetes.io/infra

                operator: Exists

                effect: NoSchedule

```

Apply the CR:

```

kubectl apply -f pxlibsupdate-placement.yaml

```

For a full list of configurable fields, see ComponentK8sConfig CRD reference.

### Manual update

-
On your air-gapped cluster, run the following command to download the correct version of the manifest that installs a DaemonSet in your cluster. Substitute `<px-version>` with the specific Portworx version you require:

```

REL="/<px-version>" && curl -fsL -o pxlibupdate-spec.yaml "https://install.portworx.com${REL}/?comp=pxlibupdate"

```

```

portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

```

info

If you are using an internal registry, you can prepend your internal registry name to the image name. When you run the following command, the image will be fetched from the specified internal registry rather than an external source:

```

REL=/3.1.0 && curl -fsL  "https://install.portworx.com${REL}/?comp=pxlibupdate&reg=internal-registry" | grep  image: | sed 's/image://'

```

```

internal-registry/portworx/px-lib:pxfslibs-3.1.0-mver12-update

```

-
Ensure that your internal image registry contains the above image. If using an internal registry, pull the image from the external registry, tag it, and push it to your internal registry:

```

docker pull portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

docker tag portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update <internal-registry>/portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

docker push <internal-registry>/portworx/px-lib:pxfslibs-<px-version>-mver<xx>-update

```

-
Apply the spec:

```

kubectl apply -f pxlibupdate-spec.yaml

```

Inspect the pod log to determine success or failure of the update.

-
Restart Portworx on each node, one node at a time. Restarting all nodes at the same time can cause the cluster to lose quorum and result in an outage. For each node, do the following:

-
Restart Portworx on the node. Replace `<node-name>` with the name of the node:

```

kubectl label nodes <node-name> px/service=restart --overwrite

```

-
Check the Portworx pod on the node. Before you restart the next node, wait until the `STATUS` column shows `Running` and the `READY` column shows that all containers in the pod are ready, for example `1/1`:

```

kubectl get pods -n <portworx> -l name=portworx --field-selector spec.nodeName=<node-name>

```

Portworx is deployed with the latest kernel version.

-
Run the following command to download the correct version of the manifest that installs a DaemonSet in your cluster. Substitute `<px-version>` with the specific Portworx version you require:

```

REL="/<px-version>" && curl -fsL -o pxlibupdate-spec.yaml "https://install.portworx.com${REL}/?comp=pxlibupdate"

```

-
Apply the spec:

```

kubectl apply -f pxlibupdate-spec.yaml

```

Inspect the pod log to determine success or failure of the update.

-
Restart Portworx on each node, one node at a time. Restarting all nodes at the same time can cause the cluster to lose quorum and result in an outage. For each node, do the following:

-
Restart Portworx on the node. Replace `<node-name>` with the name of the node:

```

kubectl label nodes <node-name> px/service=restart --overwrite

```

-
Check the Portworx pod on the node. Before you go to the next node, wait until the `STATUS` column shows `Running` and the `READY` column shows that all containers in the pod are ready, for example `1/1`:

```

kubectl get pods -n <portworx> -l name=portworx --field-selector spec.nodeName=<node-name>

```

Portworx is deployed with the latest kernel version.

Check if the cluster has access to the mirror server URL `https://px-mirror.storage.cloud.ibm.com`. Based on the access, follow one of the following methods:

### Method 1: Mirror Server URL is accessible

If the cluster has access to the mirror server URL, then add the following in `spec.env` of StorageCluster.

```

  - name: MIRRORS_SERVER

    value: https://px-mirror.storage.cloud.ibm.com

```

### Method 2: Mirror Server URL is not accessible

If the cluster does not have access to the mirror server URL, to update Portworx filesystem dependencies on an IBM Cloud environment, perform the following steps:

-
Download the `pxlibupdate-spec.yaml` file:

```

curl -fsL -o pxlibupdate-spec.yaml "https://install.portworx.com/<px-version>/?comp=pxlibupdate"

```

-
Edit the downloaded YAML file:

```

sed -i -e "s#image: portworx/px-lib:pxfslibs-#image: icr.io/ext/portworx/px-lib:pxfslibs-#g" pxlibupdate-spec.yaml

sed -i -e '/- key: node-role.kubernetes.io/master/d' pxlibupdate-spec.yaml

sed -i -e '/operator: DoesNotExist/d' pxlibupdate-spec.yaml

```

-
Apply the edited YAML file:

```

kubectl apply -f pxlibupdate-spec.yaml

```

Inspect the pod log to determine success or failure of the update.

-
Verify that all `pxlibupdate` pods are running:

```

kubectl get pods -n <portworx> -l name=px-libs-update

```

```

NAME                   READY   STATUS    RESTARTS   AGE

px-libs-update-m8jvs   1/1     Running   0          42s

px-libs-update-mgmcp   1/1     Running   0          42s

px-libs-update-qt44w   1/1     Running   0          42s

```

-
Restart Portworx on each node, one node at a time. Restarting all nodes at the same time can cause the cluster to lose quorum and result in an outage. For each node, do the following:

-
Restart Portworx on the node. Replace `<node-name>` with the name of the node:

```

kubectl label nodes <node-name> px/service=restart --overwrite

```

-
Check the Portworx pod on the node. Before you go to the next node, wait until the `STATUS` column shows `Running` and the `READY` column shows that all containers in the pod are ready, for example `1/1`:

```

kubectl get pods -n <portworx> -l name=portworx --field-selector spec.nodeName=<node-name>

```

Portworx Enterprise is deployed with the latest kernel version.

The DaemonSet above will update the pre-compiled module archives within the Portworx install location on the node (for example, `/opt/pwx`).

Note that this process assumes that Portworx is already installed since it only updates an existing installation. The system checks the existing installation's version for compatibility with the update container and does not proceed if it detects incompatibility.

In this topic:
