---
title: KubeVirt instance types and preferences, VM templates, cloud-init / Ignition / Sysprep startup scripts, guest agent, and VM rollout strategies (LiveUpdate vs Stage, RestartRequired)
type: knowledge
area: kubevirt
tags: [kubevirt, instancetype, preference, templates, cloud-init, ignition, sysprep, guest-agent, qemu-guest-agent, liveupdate, restartrequired, golden-image, datasource]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/user-guide docs/user_workloads/{instancetypes,startup_scripts,guest_agent_information,vm_rollout_strategies,vm_templates}.md
---

# Instance types, templates, startup scripts and rollout

## Instance types and preferences

- **`VirtualMachineInstancetype`** (namespaced) / **`VirtualMachineClusterInstancetype`**: CPU and memory (required),
  optional GPUs, host devices, IOThreads policy, launch security. **Anything an instance type sets cannot be overridden
  in the VM** — a VM that also sets CPU or memory is rejected.
- **`VirtualMachinePreference`** / **`VirtualMachineClusterPreference`**: *preferred* values (disk/NIC bus, firmware,
  clock…) that the VM may override — typically one per guest OS.
- API `instancetype.kubevirt.io/v1beta1` since KubeVirt v1.0. OpenShift Virtualization ships common cluster instance
  types and preferences (via SSP); DataSources can carry default instance type/preference labels for golden images.

Use them to standardise sizes (`u1.medium`-style) instead of hand-written CPU/memory per VM; resizing becomes a change of
instance type.

## Templates

KubeVirt `VirtualMachineTemplate` (virt-template, parameters `${NAME}`) and OpenShift's common templates (SSP). They can
be exported as OCI artifacts in newer releases. Templates are what the MCP `vm_create_from_template` uses
(`knowledge/kubevirt/kubevirt-kubernetes-mcp-kubevirt-toolset.md`).

## Startup scripts

- **cloud-init** via `cloudInitNoCloud` or `cloudInitConfigDrive` volumes (an ephemeral disk the guest reads at boot):
  users, SSH keys, packages. Prefer `secretRef` for user data that contains credentials — never commit them, never paste
  them into the brain.
- **Ignition** (RHCOS / Fedora CoreOS guests) through `cloudInitConfigDrive` — this is how HyperShift KubeVirt workers
  get their config (`knowledge/kubevirt/kubevirt-hypershift-kubevirt-platform-hosted-clusters-on-vms.md`).
- **Sysprep** for Windows: an `unattend.xml`/`autounattend.xml` in a ConfigMap or Secret attached as a sysprep volume.

## Guest agent

The qemu-guest-agent inside the VM gives the `AgentConnected` condition, OS info, filesystems, logged-in users and
**IPs of all interfaces** in `vmi.status.interfaces` (`infoSource: guest-agent`), plus `guestosinfo`, `userlist`,
`filesystemlist` subresources. It is also what lets online snapshots **freeze** the filesystem
(`knowledge/kubevirt/kubevirt-snapshots-clones-export-and-oadp-backup.md`). Install it in every golden image. Alerts
`GuestFilesystemAlmostOutOfSpace`, `KubeVirtVMGuestMemoryPressure` need it.

## Rollout strategies — when VM edits reach the running guest

| `vmRolloutStrategy` (KubeVirt CR) | Behaviour |
|---|---|
| `Stage` (default) | every change waits for the next reboot; the VM gets condition **`RestartRequired`** |
| `LiveUpdate` | propagate as soon as possible: CPU socket changes hotplug CPUs, memory hotplug, NIC/volume hotplug; only non-live-updatable changes set `RestartRequired` |

Once `RestartRequired` is set, no further changes propagate until a restart, even with `LiveUpdate`; the condition's
message only names the first change. Cluster-wide defaults are never live-updated.

## Scope & caveats

Upstream docs (main, 2026-11); the common instance types and templates shipped by OpenShift differ per CNV version —
`oc get virtualmachineclusterinstancetypes`, `oc get virtualmachineclusterpreferences` on the cluster.

## History

- 2026-11-02: created
