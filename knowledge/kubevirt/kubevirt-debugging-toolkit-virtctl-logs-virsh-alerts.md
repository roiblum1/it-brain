---
title: KubeVirt debugging toolkit — virtctl (console, vnc, ssh, guestfs, migrate), virt-launcher / virt-handler logs, guest-console-log, virsh and QMP inside the launcher, CDI pod retention, OpenShift Virtualization alerts, error → cause table
type: knowledge
area: kubevirt
tags: [kubevirt, debugging, troubleshooting, virtctl, console, guestfs, virt-launcher, virt-handler, virsh, qmp, libvirt-log-filters, must-gather, alerts, runbooks]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/user-guide docs/debug_virt_stack/{logging,virsh-commands}.md, docs/storage/guestfs.md, docs/user_workloads/virtctl_client_tool.md; kubevirt/containerized-data-importer doc/debug.md; openshift/hypershift docs/content/how-to/kubevirt/troubleshooting-kubevirt-cluster.md; openshift/runbooks alerts/openshift-virtualization-operator/
---

# Debugging toolkit

## Order of investigation

1. **VM** — `oc get vm <vm> -n <namespace>` STATUS (`knowledge/kubevirt/kubevirt-vm-lifecycle-runstrategy-printablestatus.md`), conditions.
2. **VMI** — `oc get vmi <vm> -o yaml`: phase, node, conditions (`LiveMigratable`, `AgentConnected`, `Paused`), `migrationState`, interfaces.
3. **virt-launcher pod** — `oc describe pod -n <namespace> -l vm.kubevirt.io/name=<vm>` (label deprecated in favour of `vmi.kubevirt.io/id` but still set) for scheduling, PVC attach, CNI errors.
4. **Logs** — launcher `compute` container (QEMU/libvirt), then virt-handler on that node, then virt-controller.
5. **Storage / network objects** — DV, PVC, StorageProfile; NAD, NNCP.
6. **Inside the guest** — console, guest agent.

## virtctl

The client for what `oc` cannot do: `console` (serial), `vnc`, `ssh`/`scp` (through the API), `start|stop|restart`,
`pause|unpause`, `migrate`/`migrate-cancel`, `vnc screenshot`, `image-upload` (into a DV/PVC), `guestfs <pvc>` (a libguestfs pod with the
PVC mounted — `virt-cat`, `virt-customize`… on a **stopped** VM's disk; it refuses a PVC in use but does not stop a VM
starting meanwhile), `memory-dump get <vm> --claim-name=<pvc>`. Get the binary matching the cluster version — in the
air gap from the cluster itself (the OpenShift console's command-line downloads — *hypothesis: confirm in RHOKP*), not
GitHub. Also usable as `oc virt …` via krew where installed.

## Logs

```bash
oc logs -n <namespace> <virt-launcher-pod> -c compute               # virt-launcher + virtqemud + QEMU (JSON lines)
oc logs -n <namespace> <virt-launcher-pod> -c guest-console-log     # guest serial console (since KubeVirt v1.1)
oc logs -n openshift-cnv -l kubevirt.io=virt-handler --tail=200 --prefix | grep <vm>   # on the VM's node
oc logs -n openshift-cnv deploy/virt-controller --tail=200 | grep <vm>
```

More detail for one VM: annotation `kubevirt.io/libvirt-log-filters: "2:qemu.qemu_monitor 3:*"` on the VMI (template)
— takes effect at next start. Component verbosity is set cluster-wide (through HCO).

## virsh / QMP in the launcher (read-only use)

`virsh` is in the `compute` container: `virsh list` (domain name `<namespace>_<vm>`), `virsh dumpxml <domain>` (the
real domain XML), `virsh qemu-monitor-command <domain> query-status --pretty`, `query-kvm`,
`virsh qemu-monitor-event --pretty --loop` to watch events. **Don't change domains with virsh** — virt-handler owns
them and will fight you; use it to look.

```bash
oc exec -n <namespace> <virt-launcher-pod> -c compute -- virsh list
oc exec -n <namespace> <virt-launcher-pod> -c compute -- virsh dumpxml <namespace>_<vm>
```

## CDI

DV annotation `cdi.kubevirt.io/storage.pod.retainAfterCompletion: "true"` keeps importer/cloner/uploader pods for their
logs; CDI `spec.config.logVerbosity`. `runbooks/kubevirt/datavolume-import-or-clone-stuck.md`.

## must-gather

`oc adm must-gather --image=<cnv-must-gather-image>` collects CNV namespaces, CRs, logs — image name for the installed
CNV version is in RHOKP. Never attach it to the brain (it contains Secrets' metadata, IPs, names).

## Alerts → runbooks (offline)

OpenShift Virtualization alerts have runbooks in `docs/upstream/openshift-runbooks/alerts/openshift-virtualization-operator/`
— check there first when one fires. The ones we expect to meet:

| Alert | Points at |
|---|---|
| `VMCannotBeEvicted` | `LiveMigrate` VM that is not migratable → drains/upgrades block |
| `OutdatedVirtualMachineInstanceWorkloads` | VMs still on the old virt-launcher 24 h after a CNV update |
| `VirtualMachineStuckOnNode`, `VirtualMachineStuckInUnhealthyState` | VM stuck > 5 min starting/stopping/terminating/error |
| `KubeVirtVMIExcessiveMigrations` | > 12 migrations of one VMI in 24 h |
| `VirtLauncherPodsStuckFailed` | ≥ 200 failed launcher pods for 10 min — migration loops, image/network/storage issues |
| `CDIStorageProfilesIncomplete`, `CDINoDefaultStorageClass`, `CDIMultipleDefaultVirtStorageClasses`, `CDIDataImportCronOutdated` | storage profile / default class / golden images |
| `VMStorageClassWarning` | Windows VMs on RBD without `krbd:rxbounce` |
| `KubemacpoolMACCollisionDetected`, `KubemacpoolDown` | MAC conflicts / pool down |
| `KubeVirtCRModified` | someone edited an operand CR that HCO owns |
| `KubeVirtNoAvailableNodesToRunVMs`, `LowKVMNodesCount` | nodes without hardware virtualization |
| `VirtHandlerDown`, `NoReadyVirtController`, `VirtAPIDown`, `LowReadyVirtHandlerCount` | control-plane health |

## Error → cause

| Exact text (where) | Cause | Page |
|---|---|---|
| `cannot migrate VMI which does not use masquerade to connect to the pod network` (VMI condition `InterfaceNotLiveMigratable`) | bridge binding on the pod network | `knowledge/kubevirt/kubevirt-networking-masquerade-bridge-multus-localnet-sriov.md` |
| `DisksNotLiveMigratable` (VMI condition / migration rejected) | a disk is not RWX | `knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md` |
| `DataVolume.storage spec is missing accessMode and cannot get access mode from StorageProfile <sc>` (DV event `ErrClaimNotValid`) | empty StorageProfile (e.g. Trident class without `backendType`) | same |
| `The volume modes of source and target are incompatible` (PVC `cdi.kubevirt.io/cloneFallbackReason`) | clone fell back to host-assisted copy | same |
| `Migration target pod for VMI [<ns>/<vm>] is currently unschedulable.` → `unschedulable pod … timeout period exceeded` | no node can take the target pod (memory, CPU model, affinity) | `knowledge/kubevirt/kubevirt-live-migration-requirements-limits-policies-failures.md` |
| `cannot get nodes to migrate VMI with host-model CPU` | no node with a matching host CPU model | `knowledge/kubevirt/kubevirt-scheduling-performance-cpu-model-dedicated-cpus-hugepages-numa.md` |
| `Failed to calculate the number of expected pods: virtualmachineinstances.kubevirt.io does not implement the scale subresource` (PDB event) | own PDB uses `maxUnavailable` / percentage | `knowledge/kubevirt/kubevirt-node-drain-eviction-strategy-and-pdbs.md` |
| `spec.running is deprecated, please use spec.runStrategy instead.` (API warning) | old manifest | `knowledge/kubevirt/kubevirt-vm-lifecycle-runstrategy-printablestatus.md` |
| `Warm import retry limit reached` (MTV) | too many CBT snapshots on the source VM | `knowledge/kubevirt/kubevirt-mtv-forklift-migrating-vms-from-vmware.md` |

## MCP

With the `kubevirt` toolset, the Kubernetes MCP's `vm_troubleshoot` collects VM, VMI, volumes, DV/PVC, cloud-init,
pod, logs and events with heuristics — a good first call (`knowledge/kubevirt/kubevirt-kubernetes-mcp-kubevirt-toolset.md`).

## History

- 2026-11-02: created
