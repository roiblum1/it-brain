# Portworx OpenShift Dynamic Plugin Release Notes

Source: https://docs.portworx.com/portworx-enterprise/ocp-plugin-release-notes (Portworx Enterprise latest)

Portworx OpenShift Dynamic Plugin Release Notes | Portworx Enterprise Documentation

## 2.4.0​

October 29, 2026

### New Features​

View Kube Datastore in OpenShift clusters
 The OpenShift Dynamic Plugin now lets you view Kube Datastore (KDS) details in OpenShift clusters. The new Kube Datastore tab on the Portworx dashboard lists each Datastore with its storage backend, capacity, storage pools, and virtual machines. You can now view per-KDS details page (Overview, Virtual Machines, Pools, and Volumes tabs, with capacity and write-performance charts) and the Top Datastore by usage on cluster overview. For more information, see Monitor Portworx Clusters on Openshift.

### Improvements​

Improvement NumberImprovement Description

PWX-59449Improved the visibility of Pool status on the OpenShift console dashboard. For more information, see Monitor Portworx Clusters on Openshift.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-57366The OpenShift Dynamic Plugin's Kube Datastores Volumes view could show an incorrect replica count for migration child volumes by using the `repl` label instead of the current physical replica count.

User Impact: Users could see an inaccurate replica count for a migrated volume, for example, 3 instead of 1, when inspecting the volume in the UI.

Resolution: The replica count shown in the UI now uses `ha_level`, the authoritative current replica count, rather than the potentially stale `repl` label.

Components: IX-OCP-UI, IX-OCP-Backend
Affected Versions: 2.3.0Minor

## 2.3.0​

August 03, 2026

This release includes a fix for an issue identified in the previous version.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-51909The OpenShift Dynamic Plugin did not support Portworx clusters with Portworx Security enabled.

User Impact: Users could not view or manage Portworx resources through the OpenShift Dynamic Plugin when Portworx Security was enabled.

Resolution: The OpenShift Dynamic Plugin now includes the Portworx security token with Portworx API requests, enabling full support for Portworx Security-enabled clusters.

Components: IX-OCP-UI
Affected Versions: 2.2.0Minor

## 2.2.0​

March 24, 2026

### New Features​

Enhanced Portworx Dashboard
 The Portworx tab in the OpenShift Dynamic Plugin now includes significant enhancements. The updated dashboard delivers improved cluster health visibility, performance metrics, alert integration, capacity insights, and storage observability for nodes, pools, and volumes. This enhancement enables administrators to manage, monitor, and observe Portworx storage without completely relying on CLI tools such as `pxctl`. These improvements streamline storage observability and accelerate troubleshooting within OpenShift environments.
For more information, see Monitor Portworx Clusters on Openshift.

### Known issues (Errata)​

Issue NumberIssue DescriptionSeverity

PWX-51909
The OpenShift Dynamic Plugin does not support Portworx clusters with Portworx Security enabled.

User Impact: When Portworx Security is enabled on the cluster, the Dynamic Plugin UI fails to function correctly. Users may encounter permission-related errors, and certain Portworx information and operations are not accessible through the OpenShift console.

Workaround: Use `pxctl` or REST APIs to perform management and monitoring operations on security-enabled clusters.

Components: IX-OCP-UI
 Affected Versions: 2.2.0
Minor

## 2.1.2​

February 18, 2026

This release includes a fix for an issue identified in the previous version.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-50684A change introduced in OCP Dynamic Plugin SDK from OCP version 4.20 and later caused an issue in Portworx Openshift Dynamic Plugin where Kubernetes API calls were not scoped to the active namespace. This led to the failure of Kubernetes API calls for resources such as VMs, VMIs, and PVCs.

User Impact: An infinite loading screen appears in the Portworx VM tab if your cluster is running OCP version 4.20 and later.

Resolution: Portworx Openshift Dynamic Plugin now supports the updated OCP Dynamic Plugin SDK. Kubernetes API calls are correctly scoped to the selected namespace, and the Portworx VM tab loads as expected.

Components: IX-OCP-UI
Affected Versions: AllMinor

## 2.1.1​

January 27, 2026

This release includes a fix for an issue identified in the previous version.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-49661On the OpenShift Container Platform (OCP) Portworx page, the storage donut chart in the Portworx dynamic plugin displayed incorrect information. In dark mode, chart labels were not visible, and free space values were sometimes shown as negative.

User Impact: Users viewing the Cluster page could see misleading storage information or unreadable chart text in dark mode, which could cause confusion when assessing cluster storage usage.

Resolution: Portworx now correctly reports accurate free space values and updated the chart styling to render text correctly in dark mode. The Cluster page storage donut chart now displays accurate data and remains readable across UI themes.

Components: IX-OCP-UI
Affected Versions: 2.1.0Minor

## 2.1.0​

December 8, 2025

Portworx OpenShift Dynamic Plugin provides integrated storage observability and management directly in the OpenShift console, simplifying Day-2 operations, monitoring, and troubleshooting for Portworx storage clusters, Kubernetes applications and OpenShift integrations such as KubeVirt.
For information on how to enable the plugin, see Enable Portworx OpenShift Dynamic Plugin.

### New Features​

- Support for managing PVCs or Disks for KubeVirt VMs
Portworx OpenShift Dynamic Plugin now supports observing and managing Portworx-backed Persistent Volume Claims (PVCs) or Disks for KubeVirt virtual machines (VMs) from the Portworx tab in the OpenShift web console.
For more information, see Monitor Portworx Clusters on Openshift.

### Known issues (Errata)​

Issue NumberIssue DescriptionSeverity

PWX-47959
When users navigate from the VirtualMachines page to the PersistentVolumeClaims or StorageClasses page in OpenShift Container Platform (OCP), the Portworx tab displays an error instead of loading correctly. The issue occurs due to a KubeVirt dynamic plugin conflict within OCP.

User Impact: The Portworx tab fails to load on the PersistentVolumeClaims or StorageClasses pages when accessed through the VirtualMachines page.

Workaround: Refresh the PersistentVolumeClaims or StorageClasses pages to restore the Portworx tab.

Components: IX-OCP-UI
 Affected Versions: 2.1.0
Minor

In this topic:
