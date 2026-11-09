# Upgrade Portworx Clusters using the Operator

Source: https://docs.portworx.com/portworx-enterprise/platform/upgrade/upgrade-px-operator (Portworx Enterprise latest)

Upgrade Portworx Clusters using the Operator | Portworx Enterprise Documentation

If you're using the Portworx Operator, you can upgrade or change your Portworx version at any time by modifying the `StorageCluster` spec. In addition to managing a Portworx cluster, the Operator also manages the following other components in the Portworx platform:

- Stork

- Autopilot

For simplicity, the Portworx Operator handles the component upgrades without user intervention. The Operator not only manages the Portworx cluster but also other essential components like Stork and Autopilot.

## Smart upgrade​

The Smart upgrade feature introduces a streamlined, resilient upgrade process for Portworx nodes, allowing them to be upgraded in parallel while maintaining volume quorum and without application disruption.

By default, smart upgrade is disabled and `maxUnavailable` is set to 1. This means one Portworx node is upgraded at a time.

You can enable the smart upgrade by setting the `spec.updateStrategy.rollingUpdate.disruption.allow` parameter to `false` and setting the maximum number of nodes that can be upgraded at a time using the `spec.updateStrategy.rollingUpdate.maxUnavailable` parameter in the StorageCluster.

The following are the key benefits of using smart upgrade:

- Parallel upgrades: Based on volume distribution, the Portworx Operator tries to select multiple nodes for concurrent upgrades, accelerating the upgrade process while eliminating downtime and application disruption.

- Volume quorum maintenance: Ensures volume quorum is maintained throughout the upgrade process.

- Managed node upgrades: You can use the `spec.updateStrategy.rollingUpdate.maxUnavailable` parameter in the StorageCluster CRD to manage the number of nodes upgraded in parallel.

- Automatic reconciliation: The Portworx operator actively monitors and reconciles the storage nodes during upgrades, ensuring smooth progression while preserving quorum integrity.

important

- There will be downtime for applications using volumes with a replication factor of 1.

- Smart upgrade is not supported for:

- Synchronous Disaster Recovery (DR) setup.

- Clusters that run KubeVirt VMs.

## Prerequisites​

-
Ensure that your Portworx cluster meets the System Requirements.

-
Your Portworx cluster must be running the latest available version of Portworx Operator. This method does not work for other Portworx deployments.

-
If you are using Vault to store vSphere credentials, ensure that the correct credentials are configured in Vault before proceeding with the Portworx Enterprise upgrade.

-
For an air-gapped environment, complete the instructions in the Get the updated container images section.

-
If your Portworx cluster is managing the underlying storage devices in an Anthos deployment, add the following annotation to the `StorageCluster` spec to ensure that during an Anthos or a Portworx upgrade, Portworx does not failover the internal KVDB to a storageless node:

```

portworx.io/misc-args: "-rt_opts wait-before-retry-period-in-secs=360"

```

-
If there are any cordoned nodes, ensure that Portworx pods have not been deleted from those nodes. It is safe to proceed with the upgrade if the Portworx pods on cordoned nodes are still running.

-
For smart upgrade, ensure the following prerequisites are met:

- Required Portworx and Operator versions:

- Portworx version 3.1.2 or later

- Operator version 24.2.0 or later

- The cluster must be ready and available for upgrade. You can use the `pxctl status` and `kubectl get storagenodes -n portworx` commands to check the cluster status.

- No nodes or pools should be under maintenance.

- No decommissioned nodes should appear in the output of the `kubectl get storagenodes` command.

- No nodes should have the `px/service=stop` or `px/service=disabled` label. If nodes have these labels, remove them and restart the Portworx service or decommission the node before the upgrade.

## Upgrade Portworx Cluster​

note

-
If using configmap, update the version manifest for Portworx Operator. Otherwise, you might not see the expected image versions.

-
If you override the default PodDisruptionBudget in GKE environments, ensure that the `maxUnavailable` is less than the `storage-pdb-min-available` value for a balanced speed and disruption. Portworx by Everpure recommends using the following configurations for surge upgrades:

- `maxSurge=1`

- `maxUnavailable=0`

-
During an upgrade, Portworx pods are deleted and re-created on each node to apply the spec changes. The `spec.updateStrategy` field in the StorageCluster resource controls how nodes are upgraded. By default, the update strategy is RollingUpdate, and the `maxUnavailable` field specifies the maximum number of nodes that can be unavailable at a time. The default value of `maxUnavailable` is 1.

This is expected behavior, and you might see pod deletion events in the Kubernetes audit logs. You don't need to take any action.

- Kubernetes

- Openshift

-
Identify your StorageCluster:

Retrieve the name of your Portworx StorageCluster within the appropriate namespace:

```

kubectl get storagecluster -n <px-namespace>

```

```

NAME                                            STATUS   VERSION   AGE

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx Online   2.10.3    43d

```

If your cluster is installed in a different namespace, specify it using the `-n` flag.

-
Edit the StorageCluster:

Modify the StorageCluster resource to update Portworx to the desired version:

```

kubectl edit storagecluster -n <px-namespace> <storagecluster-name>

```

In the editor, make the following changes in the StorageCluster:

- Update the `spec.image` field to your desired Portworx version.

- (optional) For smart upgrade, ensure that the `spec.updateStrategy.rollingUpdate.disruption.allow` parameter is set to `false` and set the maximum number of nodes that can be upgraded at a time using the `spec.updateStrategy.rollingUpdate.maxUnavailable` parameter.

important

If you are running KubeVirt VMs, smart upgrade is not supported. You must ensure that the `spec.updateStrategy.rollingUpdate.disruption.allow` parameter is set to `true` and the `spec.updateStrategy.rollingUpdate.maxUnavailable` value is set to `1`.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

   name: portworx

   namespace: <px-namespace>

spec:

   image: portworx/oci-monitor:<desired-version>

   # For smart upgrades, ensure that the below lines are uncommented and `disruption.allow` is set to false. You can use the `maxUnavailable` field to control the maximum number of Portworx nodes that can be upgraded at a time.

   #updateStrategy:

   #   type: RollingUpdate

   #   rollingUpdate:

   #      maxUnavailable: 5

   #      minReadySeconds: 0

   #      disruption:

   #         allow: false

```

note

- If there are any component images configured in the StorageCluster, such as the `spec.stork.image` or `spec.autopilot.image` fields, you need to update the image fields to the latest version.

- To look up recent versions, refer to the following release notes:

- Portworx release notes

- Autopilot release notes

- Stork release notes

-
Verify the upgrade:

Confirm the upgrade by checking the Portworx version on the nodes:

```

kubectl get storagenodes -n <px-namespace> -l name=portworx

```

```

NAME       ID                                     STATUS   VERSION          AGE

node-1-1   xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx   Online   <desired-version>   10d

```

-
Identify your StorageCluster:

Retrieve the name of your Portworx StorageCluster within the appropriate namespace:

```

oc get storagecluster -n <px-namespace>

```

```

NAME                                            STATUS   VERSION   AGE

px-cluster-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx Online   2.10.3    43d

```

If your cluster is installed in a different namespace, specify it using the `-n` flag.

-
Edit the StorageCluster:

Modify the StorageCluster resource to update Portworx to the desired version:

```

oc edit storagecluster -n <px-namespace> <storagecluster-name>

```

In the editor, make the following changes in the StorageCluster:

- Update the `spec.image` field to your desired Portworx version.

- (optional) For smart upgrade, ensure that the `spec.updateStrategy.rollingUpdate.disruption.allow` parameter is set to `false` and set the maximum number of nodes that can be upgraded at a time using the `spec.updateStrategy.rollingUpdate.maxUnavailable` parameter.

important

If you are running KubeVirt VMs, smart upgrade is not supported. You must ensure that the `spec.updateStrategy.rollingUpdate.disruption.allow` parameter is set to `true` and the `spec.updateStrategy.rollingUpdate.maxUnavailable` value is set to `1`.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

   name: portworx

   namespace: <px-namespace>

spec:

   image: portworx/oci-monitor:<desired-version>

   # For smart upgrades, ensure that the below lines are uncommented and `disruption.allow` is set to false. You can use the `maxUnavailable` field to control the maximum number of Portworx nodes that can be upgraded at a time.

   #updateStrategy:

   #   type: RollingUpdate

   #   rollingUpdate:

   #      maxUnavailable: 5

   #      minReadySeconds: 0

   #      disruption:

   #         allow: false

```

note

- If there are any component images configured in the StorageCluster, such as the `spec.stork.image` or `spec.autopilot.image` fields, you need to update the image fields to the latest version.

- To look up recent versions, refer to the following release notes:

- Portworx release notes

- Autopilot release notes

- Stork release notes

-
Verify the upgrade:

Confirm the upgrade by checking the Portworx version on the nodes:

```

oc get storagenodes -n <px-namespace> -l name=portworx

```

```

NAME       ID                                     STATUS   VERSION          AGE

node-1-1   xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx   Online   <desired-version>   10d

```

note

For air-gapped clusters, if you do not see the expected image versions that you have configured in the configmap, you should edit the StorageCluster to include the `autoUpdateComponents: Once` parameter. This will force Portworx Operator to reconcile all the components and retrieve the correct images.

In this topic:
