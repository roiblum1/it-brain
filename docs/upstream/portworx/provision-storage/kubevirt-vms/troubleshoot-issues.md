# Troubleshooting, Known Issues, and Limitations for KubeVirt VMs

Source: https://docs.portworx.com/portworx-enterprise/provision-storage/kubevirt-vms/troubleshoot-issues (Portworx Enterprise latest)

Troubleshooting, Known Issues, and Limitations for KubeVirt VMs | Portworx Enterprise Documentation

This page provides troubleshooting steps, known issues, and limitations for KubeVirt VMs managed with Portworx.

## Troubleshooting​

### Reverse migration issues with forklifted VMs​

When you migrate a VM from vSphere to OpenShift by using the Migration Toolkit for Virtualization (MTV) or the Forklift operator, the system creates a conversion pod (`virt-v2v`) in the target namespace. This pod performs disk transformation and remains in a `Completed` state after migration.

By default, the pod is not deleted to allow log inspection. However, it can block reverse migration using Stork. As a result, PVCs and PVs in the namespace may remain stuck in a `Terminating` state, preventing recreation.

#### Workaround​

Before starting a reverse migration, delete the `virt-v2v` conversion pod on the source cluster:

-
Identify the pod:

```

oc get pods -n <target-namespace> -l forklift.app=virt-v2v

```

-
Confirm the pod is in the `Completed` state.

-
Delete the pod:

```

oc delete pod <pod-name> -n <namespace>

```

note

This issue applies to Forklift-based migrations where the `virt-v2v` pod is retained after migration for observability and debugging.

## Known issues​

### KubeVirt VM eviction during abrupt node power-off​

When a node running a KubeVirt VM experiences abrupt power loss, KubeVirt applies the default eviction policy (`LiveMigrate`). KubeVirt attempts to migrate the VM to another node when the source node becomes unavailable.

If the VM uses Portworx volumes with replication (for example, `repl2` or `repl3`), the VM may restart on another node. In some cases, the VM may boot into safe mode due to the interruption. Restart the VM to recover from safe mode.

### Thick-provisioned PVCs after VMware-to-KubeVirt migration​

When you migrate VMs from a VMware environment to a KubeVirt environment with `VolumeMode: Block`, the persistent volume claims (PVCs) may appear fully utilized or thick-provisioned. This behavior can increase pool usage and trigger unnecessary volume expansion.

### Golden image and golden PVC behavior​

A golden image is a preconfigured VM disk that serves as a template for consistent VM provisioning. A golden PVC is a pre-provisioned PVC that contains a golden image. You can clone these PVCs to create new VMs.

- Golden PVCs created via HTTP import can behave like thick-provisioned volumes, consuming more physical storage than the actual image size. Cloned volumes from these PVCs, particularly when using Portworx raw block volumes, may exhibit increased capacity usage and degraded performance compared to sharedv4 volumes. To optimize space efficiency, run defragmentation inside the guest VM.

- VMs and their associated PVCs may be scheduled on the same node as the golden PVC. This can lead to resource bottlenecks. To avoid this, maintain multiple golden PVCs.

- If you create a golden PVC with a replication factor of 3 and a node or Portworx restart occurs during VM creation, the resulting cloned PVC may be created with a replication factor of 2. There is no automatic correction, but replication can be manually restored using `repl add` on the affected PVC.

- When multiple VMs are created at the same time from a single golden PVC, some VMs may display a "Running" status while the guest operating system is unresponsive. To recover the VM, perform a power cycle:

- OpenShift: Use the OpenShift UI or `virtctl` CLI.

- SUSE Virtualization: Use the SUSE Virtualization UI or `virtctl` CLI.

### Storage hot spots when cloning many VMs from a single template PVC​

When you clone many VMs from the same template PVC by using the `cloneStrategy: csi-clone` setting, Portworx initially places every clone's replicas on the same nodes as the template PVC. Portworx relocates these cloned replicas after each VM starts, but only to align them with a non-cloned volume in the same VM. If your VMs have a single disk that is cloned from the template PVC and no non-cloned volume, Portworx has no target to align to, so the replicas remain on the template PVC's nodes. Provisioning a large batch of such VMs concentrates replicas on a few nodes and creates I/O hot spots that degrade performance.

To distribute replicas evenly across the cluster, use one of the following approaches.

tip

Include at least one non-cloned data volume, such as a blank volume or a volume created with the `cloneStrategy: copy` setting, in each VM. Portworx co-locates the cloned disk with this non-cloned volume and spreads replicas across nodes automatically, which avoids the need for the manual approaches that follow.

#### Distribute VMs across multiple template PVCs​

Create multiple template PVCs whose replicas occupy different nodes, and then alternate between the template PVCs as you provision VMs.

On a cluster that has `N` storage nodes and a template PVC with a replication factor of `R`, you can create up to `N/R` template PVCs that occupy mutually exclusive sets of nodes. For example, on a cluster that has 30 storage nodes and a template PVC with a replication factor of 2, create 15 template PVCs, each with replicas on a different pair of nodes.

When you provision VMs, cycle through the template PVCs in round-robin order so that each template PVC serves an equal share of VMs. This spreads the cloned replicas evenly across all nodes.

#### Relocate a single template PVC between batches​

If you prefer to maintain a single template PVC, provision VMs in batches and move the template PVC's replicas to a new set of nodes between batches.

Choose the batch size so that each set of replica nodes serves an equal share of VMs. On a cluster that has `N` storage nodes, a template PVC with a replication factor of `R`, and a total of `M` VMs to create, use a batch size of `M/(N/R)`. For example, to create 900 VMs on a cluster that has 30 storage nodes and a template PVC with a replication factor of 2, use a batch size of 60, which is `900/(30/2)`.

For each batch, do the following:

-
Provision the batch of VMs from the template PVC.

-
Identify the Portworx volume ID of the template PVC:

```

pxctl volume list

```

-
Move each replica of the template PVC to a node that the next batch uses. Because a volume can have at most three replicas, reduce the replication factor to remove a replica from its current node before you increase the replication factor to add a replica on the new node.

For a template PVC with a replication factor of 2, run the following commands. Replace `<template-volume>` with the volume ID, and replace `<old-node>` and `<new-node>` with the applicable node IDs:

```

pxctl volume ha-update --repl 1 <template-volume> --node <old-node>

pxctl volume ha-update --repl 2 <template-volume> --node <new-node>

```

Repeat these two commands for the remaining replica, using its current node and another new node.

-
Provision the next batch of VMs, and then repeat these steps until you create all VMs.

For more information about changing where a volume's replicas are placed, see Evacuating a Portworx node.

### Host LVM autoactivates guest volume groups on KubeVirt VM disks​

On vanilla Kubernetes clusters that run KubeVirt VMs on FlashArray Direct Access volumes, Portworx attaches each VM disk to the node as a multipath device (`/dev/dm-N`), and KubeVirt passes that device to the guest. If the guest uses LVM, the host kernel also sees the guest's volume group. This behavior is standard in Linux distributions and isn't specific to Portworx or KubeVirt. It affects worker nodes that have LVM2 installed, which is the default on Ubuntu and RHEL-family images.

The default LVM udev rules autoactivate any volume group that they find on a block device, including a volume group that belongs to a VM. This autoactivation has the following consequences:

- The host holds an active device-mapper stack on top of the multipath device.

- When the VM stops or is deleted, the Portworx `NodeUnstageVolume` call fails with the error `multipath flush failed because the device is still in use`.

- The `virt-launcher` pod stays in the `Completed` state, the `VolumeAttachment` is never released, and the namespace is stuck in the `Terminating` state.

- The host can read and write the guest's metadata, which is a data-safety risk.

Portworx reports the failure, but the cause is on the host.

Any Linux host that exposes raw block devices to VMs can hit this issue, regardless of the storage backend. OpenShift avoids it through its node image and configuration, so you don't need the udev rule on OpenShift. On vanilla Kubernetes worker nodes that have LVM2 installed, you must apply the rule yourself.

To prevent this issue, do the following:

- Install the udev rule

- Deactivate active guest volume groups

- Verify the rule

#### Install the udev rule​

The rule matches multipath devices by their kernel device-mapper UUID (`DM_UUID`), not by device path, so device aliases can't bypass it. It tells udev to skip the remaining rules for those devices, including LVM autoactivation. The rule works the same way for any multipath-backed raw block VM disk, not only for FlashArray Direct Access volumes. It doesn't affect the Portworx storage pool, which Portworx assembles through `/dev/md127`, or the host's root LVM, which isn't a multipath device.

warning

Validate this rule on hosts that have root disks on SAN volumes and a multipath (`mpath`) setup. Confirm that a node reboot after you apply the rule doesn't prevent the node from coming back online.

On every worker node, before you run VM workloads, do the following:

-
Create the `/etc/udev/rules.d/60-lvm-filter-guard.rules` file with the following content:

```

SUBSYSTEM!="block", GOTO="lvm_filter_guard_end"

KERNEL!="dm-[0-9]*", GOTO="lvm_filter_guard_end"

ENV{DM_UUID}!="mpath-*", GOTO="lvm_filter_guard_end"

ENV{DM_UDEV_DISABLE_OTHER_RULES_FLAG}="1"

LABEL="lvm_filter_guard_end"

```

-
Reload the udev rules:

```

udevadm control --reload-rules

```

You don't need to restart the node or rebuild the initramfs.

important

Install the rule on every worker node, including nodes that you add later. Add the rule to your node provisioning process, and verify it on each new node.

#### Deactivate active guest volume groups​

The udev rule prevents new activations only. It doesn't deactivate guest volume groups that the host activated before you installed the rule.

On each node, do the following:

-
List the volume groups:

```

vgs --noheadings -o vg_name

```

-
Identify the guest volume groups. Ignore the host's own volume groups, such as the root volume group and the `pwx*` volume groups.

-
For each guest volume group whose VM no longer exists, deactivate the volume group:

```

DM_DISABLE_UDEV=1 vgchange -an <guest-vg>

```

Replace `<guest-vg>` with the name of the guest volume group.

note

Always set `DM_DISABLE_UDEV=1`. Without it, `vgchange` can hang when you run it from a container, because the container's IPC namespace can't share the udev synchronization cookie.

-
If a `VolumeAttachment` is still stuck, delete the `VolumeAttachment` object so that Kubernetes runs the unpublish operation. Don't remove the `VolumeAttachment` finalizers.

#### Verify the rule​

On each node, run the following commands:

```

test -f /etc/udev/rules.d/60-lvm-filter-guard.rules && echo present

vgs --noheadings -o vg_name

journalctl -k | grep -c "multipath flush failed"

```

The configuration is correct when:

- The first command prints `present`.

- The `vgs` output lists no guest volume groups.

- The `journalctl` command returns `0` for the period after you applied the rule.

### OpenShift-specific known issues​

-
A known issue in `libvirt` affects the use of 4K block volumes and may cause VMs to pause due to I/O errors. This issue is resolved in OpenShift Container Platform (OCP) version 4.16 or later. For more information, see Red Hat solution.

-
OpenShift Virtualization (OSV) versions 4.18.4 or earlier contain a known issue that incorrectly handles discards when used with Portworx block devices. As a workaround, disable discards on the Portworx volume. If discards are disabled, the StorageClass must include the parameter `nodiscard: true`.
The `nodiscard` setting can also be toggled after PVC creation by using the command `pxctl volume update --nodiscard on <your_pvc_name>`. After updating, restart the pod for the change to take effect.

-
OCP 4.20 versions earlier than 4.20.27 contain a kernel-level discard race condition in RHCOS kernel 5.14.0-570.99.1.el9_6 and earlier that affects Portworx block volumes. Upgrade to OCP 4.20.27 or later (RHCOS kernel 5.14.0-570.124.1.el9_6 or later) to resolve this issue. If you cannot upgrade immediately, add the `nodiscard: true` parameter to the StorageClass as a workaround. For the minimum required patch version for other OCP releases in the 4.18–4.22 range, see Red Hat Solution 7077108.

## Limitations​

### KubeVirt VMs might not automatically fail over to another node​

On OpenShift Container Platform, when a node hosting KubeVirt virtual machines (VMs) becomes unavailable, the VMs might not automatically fail over to another node. This behavior is expected. To address this, you can either deploy a node remediation operator for automated handling or manually trigger a failover:

#### Deploy a node remediation operator​

To automate failover and ensure that VMs are rescheduled on healthy nodes, deploy the Node Health Check (NHC) Operator in OCP.

-
Install the NHC Operator using the OpenShift Web Console or OpenShift CLI.

note

The NHC Operator includes Self-Node Remediation (SNR) functionality by default.

-
Configure a Node Health Check to monitor worker nodes and specify a remediation duration. For detailed configuration steps, see Red Hat documentation.

note

Ensure that you select the worker nodes when creating the Node Health Check.

Once configured, the NHC Operator detects node failures, drains unhealthy nodes after the specified duration, and triggers the rescheduling of pods, including VMs, to healthy nodes.

#### Manually trigger VM failover​

If automated remediation is not feasible, you can manually trigger VM failover by draining and removing the unavailable node.

-
Drain the unavailable node to safely evict workloads from it:

```

oc drain <down-node>

```

-
Delete the node from the OCP cluster:

```

oc delete node <down-node>

```

-
Wait for the pods and VMs to terminate and restart on a healthy node.

After rescheduling, the KubeVirt VMs will return to a `Ready` state.

In this topic:
