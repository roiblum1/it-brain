---
title: KubeVirt scheduling and performance — CPU model (host-model, host-passthrough, cluster default), vmiCPUAllocationRatio, dedicated CPUs, hugepages, NUMA, memory overhead and overcommit, IOThreads, PCI passthrough / GPUs / vGPU
type: knowledge
area: kubevirt
tags: [kubevirt, scheduling, performance, cpu-model, host-model, host-passthrough, cpuallocationratio, dedicated-cpu, cpu-manager, hugepages, numa, overcommit, memory-overhead, iothreads, host-devices, gpu, vgpu, vfio]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/user-guide docs/compute/{virtual_hardware,dedicated_cpu_resources,resources_requests_and_limits,node_overcommit,numa,hugepages,host-devices}.md, docs/storage/disks_and_volumes.md (IOThreads); kubevirt/hyperconverged-cluster-operator docs/cluster-configuration.md
---

# Scheduling and performance

A VM is scheduled as its virt-launcher pod: its `requests`, nodeSelector/affinity/tolerations and device requests
(`devices.kubevirt.io/kvm`, hugepages, SR-IOV VFs, GPUs) decide where it can run. Nodes without hardware
virtualization advertise no `devices.kubevirt.io/kvm`; if no node has it the alert is
`KubeVirtNoAvailableNodesToRunVMs` (`LowKVMNodesCount` when few do).

## CPU

- **vCPUs** = `sockets × cores × threads` (or `resources.requests.cpu` when `spec.domain.cpu` is empty).
- **CPU request of the pod** = vCPUs × 1/`cpuAllocationRatio`; ratio default **10** (each vCPU requests 0.1 CPU), set in
  HyperConverged as `spec.virtualization.vmiCPUAllocationRatio`. Ratio 1 = one physical thread per vCPU. No CPU limit
  by default; **auto CPU limits** (1 per vCPU) apply when the namespace has a ResourceQuota with CPU limits (or matches
  `autoCPULimitNamespaceLabelSelector`). Ignored for dedicated CPUs.
- **CPU model**: unset → cluster default `cpuModel` if configured, else **`host-model`** (close to the node's CPU).
  `host-passthrough` exposes the exact host CPU (best performance, worst migratability). With `host-model`, migration
  needs a target node with the same host model — a cluster mixing CPU generations should set a common named model as
  the cluster default. Obsolete models can be excluded from node labelling (`obsoleteCPUModels`).

## Dedicated CPUs, NUMA, hugepages

- `spec.domain.cpu.dedicatedCpuPlacement: true` pins vCPUs to pCPUs through the Kubernetes **CPU manager** (static
  policy on those nodes): the pod must be **Guaranteed** (requests = limits, integer CPUs). Don't set both
  `spec.domain.cpu` topology and CPU resources. An isolated emulator thread can be requested in addition.
- **NUMA** `guestMappingPassthrough` (feature gate `NUMA`) needs dedicated CPUs and hugepages; the guest topology
  follows the CPUs kubelet assigned, so it can differ after reschedule and may be asymmetric; the VM may fail to start
  if the NUMA nodes lack hugepages.
- **Hugepages** must be pre-allocated on the nodes (in OpenShift via a MachineConfig / performance profile kernel args)
  and requested with `spec.domain.memory.hugepages.pageSize`.

## Memory

- The guest gets `spec.domain.memory.guest` (or `resources.requests.memory`); the pod requests more: a computed
  **overhead** (video adapter, IOThreads, supplementary software…; the guide gives a default of 32Mi, plus calculated per-device amounts) is added for the scheduler.
- **No classical memory overcommit / ballooning**: memory given to a VM is not returned. Ways to pack more:
  drop the graphics device (`autoattachGraphicsDevice: false`, saves 16 MB and disables VNC),
  `overcommitGuestOverhead: true` (don't request the overhead — risky for long-lived VMs), or tell the guest it has more
  than requested (`memory.guest` > request — real overcommit, OOM risk). KSM can be enabled from HCO.
- Live migration needs **free memory equal to the VM on the target**; plan node maintenance capacity accordingly.

## Disk I/O

`ioThreadsPolicy` (`shared`, `auto`, `supplementalPool`), virtio-blk multi-queue, disk cache modes, and dedicated
IOThreads with pinned CPUs — `docs/upstream/kubevirt-user-guide/docs/storage/disks_and_volumes.md` "High Performance Features".

## PCI passthrough, GPUs, vGPU

Host needs VT-d/AMD-IOMMU in BIOS and `intel_iommu=on`/`amd_iommu=on` (OpenShift: MachineConfig kernel arguments),
devices bound to `vfio-pci`; the device is then listed in HCO's **permitted host devices**
(`spec.virtualization.permittedHostDevices` in the v1 API — `pciHostDevices`, `mediatedDevices`, `usbHostDevices`) and requested by resource name in `spec.domain.devices.hostDevices`/`gpus`. Mediated
devices (vGPU) can be configured automatically by HCO (`spec.virtualization.mediatedDevicesConfiguration`). Passthrough VMs are **not
live-migratable** (`HostDeviceNotLiveMigratable`); vGPU migration has its own limits. Our GPU estate:
`knowledge/gpu/README.md`.

## Placement

Normal Kubernetes tools on the VM template: `nodeSelector`, affinity/anti-affinity (spread a VM pair across nodes),
tolerations; KubeVirt's CPU-feature/model node labels come from its node labeller. `kubevirt.io/schedulable=false`
nodes get nothing (`knowledge/kubevirt/kubevirt-architecture-components-virt-launcher-hco-cdi.md`).

## Scope & caveats

Upstream (main, 2026-11). OpenShift tunes nodes via MachineConfig/PerformanceProfile — check RHOKP for the supported
way per OCP minor.

## History

- 2026-11-02: created
