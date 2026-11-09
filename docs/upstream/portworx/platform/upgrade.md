# Upgrade Portworx Enterprise

Source: https://docs.portworx.com/portworx-enterprise/platform/upgrade (Portworx Enterprise latest)

Upgrade Portworx Enterprise | Portworx Enterprise Documentation

The topics below provide comprehensive instructions for upgrading Portworx Enterprise on Kubernetes and OpenShift. Choose the appropriate upgrade method based on your installation type, platform, and specific requirements. Before proceeding with any upgrade, review the Portworx Enterprise Release Notes of your target version, and also verify the compatibility of your distros and kernel with the target version (see Supported Kernels).

note

During an upgrade, Portworx pods are deleted and re-created on each node to apply the spec changes. The `spec.updateStrategy` field in the StorageCluster resource controls how nodes are upgraded. By default, the update strategy is RollingUpdate, and the `maxUnavailable` field specifies the maximum number of nodes that can be unavailable at a time. The default value of `maxUnavailable` is 1.

This is expected behavior, and you might see pod deletion events in the Kubernetes audit logs. You don't need to take any action.

## Upgrade with Portworx Operator​

Portworx Operator simplifies the installation, configuration, and management of the Portworx Enterprise within a Kubernetes cluster. To upgrade Portworx clusters using Portworx Operator, perform the following activities:

-
Upgrade Portworx Operator to the latest version. Read the Portworx Operator Release Notes and check the supported Operator OpenShift Upgrade path, before upgrading. For information about upgrading Operator, see Upgrade Portworx Operator.

-
Upgrade Portworx clusters by modify the StorageCluster specification to upgrade and change your Portworx version. For more information, see Upgrade Portworx Clusters using the Operator.

-
If you want to upgrade Portworx clusters that are in an air-gapped environment, you need to fetch the updated container images and pre-stage them within the air-gapped cluster, and then upgrade the clusters. For detailed information, see Upgrade an Air-Gapped Portworx Cluster.

## Upgrade Marketplace Deployment​

If Portworx Enterprise is deployed from the AWS Marketplace or from IBM Cloud, see Upgrade Portworx Marketplace Deployment for instructions on upgrading these Portworx Clusters via Helm.

## Upgrade Using Helm Charts​

If Portworx Enterprise was installed using Helm, check for compatibility and the follow the instructions in Upgrade Portworx using Helm to upgrade.

## Upgrade using the Blue-Green Method​

When you need to manually upgrade with minimal downtime by adding new nodes before decommissioning old ones, you can use the blue-green method to upgrade. For more information, see Upgrade Portworx Cluster using the Blue-Green Method.

## Upgrade the FA/FB driver​

The FA/FB driver is a component of Portworx Enterprise and cannot be upgraded independently. Each Portworx Enterprise release supports a corresponding version of the driver. To upgrade the FA/FB driver, upgrade Portworx Enterprise by using one of the preceding methods. The upgrade installs the version supported by the target Portworx Enterprise release.

important

If your cluster is running a Portworx Enterprise version earlier than 3.7.0, upgrade the cluster to version 3.7.0 or later, verify that the upgrade is complete on all nodes, and then enable the FA/FB driver.

In this topic:
