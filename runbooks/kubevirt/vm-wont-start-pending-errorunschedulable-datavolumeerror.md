---
title: Triage a KubeVirt VM that will not start — ErrorUnschedulable, WaitingForVolumeBinding, DataVolumeError, ErrorPvcNotFound, ImagePullBackOff, CrashLoopBackOff, stuck Starting
type: runbook
area: kubevirt
tags: [kubevirt, vm, start, errorunschedulable, datavolumeerror, waitingforvolumebinding, crashloopbackoff, imagepullbackoff, triage]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/kubevirt types.go (printableStatus); kubevirt/user-guide; openshift/runbooks VirtualMachineStuckOnNode
---

# VM will not start

**When to use:** `oc get vm` shows anything but `Running` after a start, or alert `VirtualMachineStuckOnNode` /
`VirtualMachineStuckInUnhealthyState`.
**Impact while running:** read-only until step 6.
**Prerequisites:** `oc` on the VM's cluster (Kubernetes MCP: pass the `context`); `vm_troubleshoot` from the MCP is a
good first pass (`knowledge/kubevirt/kubevirt-kubernetes-mcp-kubevirt-toolset.md`).

## Pre-checks

```bash
oc get vm <vm> -n <namespace>                                   # STATUS
oc get vm <vm> -n <namespace> -o jsonpath='{.spec.runStrategy}{"\n"}{.status.conditions}{"\n"}'
oc get vmi <vm> -n <namespace> -o wide 2>/dev/null
oc get pods -n <namespace> -l vm.kubevirt.io/name=<vm> -o wide
oc get events -n <namespace> --sort-by=.lastTimestamp | tail -30
```

Meaning of each STATUS: `knowledge/kubevirt/kubevirt-vm-lifecycle-runstrategy-printablestatus.md`.

## Procedure

1. **`Stopped` but should run** — runStrategy is `Halted`/`Manual`, or a guest shutdown with `RerunOnFailure`.
   `virtctl start <vm> -n <namespace>`.
2. **`ErrorUnschedulable`** — read the scheduler's reason:
   ```bash
   oc describe pod -n <namespace> -l vm.kubevirt.io/name=<vm> | sed -n '/Events/,$p'
   ```
   Typical: `Insufficient memory` (VMs need guest memory + overhead — `knowledge/kubevirt/kubevirt-scheduling-performance-cpu-model-dedicated-cpus-hugepages-numa.md`),
   `Insufficient devices.kubevirt.io/kvm` (no virtualization on the nodes), hugepages / SR-IOV / GPU resources missing,
   node selector/affinity/taints, nodes with `kubevirt.io/schedulable=false` (virt-handler down there):
   `oc get nodes -L kubevirt.io/schedulable`.
3. **`WaitingForVolumeBinding` / `Provisioning` / `DataVolumeError` / `ErrorPvcNotFound`** — storage:
   ```bash
   oc get dv,pvc -n <namespace>
   oc describe dv <dv> -n <namespace> | sed -n '/Events/,$p'
   ```
   `WaitForFirstConsumer` is normal until the pod schedules. Anything with `ErrClaimNotValid`, import or clone errors:
   `runbooks/kubevirt/datavolume-import-or-clone-stuck.md`. PVC `Pending` with a CSI error → the backend's area
   (`interfaces/virtualization-storage-kubevirt-vm-disks.md`).
4. **`ErrImagePull` / `ImagePullBackOff`** — a containerDisk image is not in our mirror registry or the pull secret is
   wrong (`knowledge/registry-mirroring/README.md`).
5. **Pod `ContainerCreating` with a network error** — NAD missing in the namespace, bridge/bridge-mapping missing on that
   node: `runbooks/kubevirt/vm-no-network-on-secondary-network.md`. **Pod running but VMI not `Running` / `CrashLoopBackOff`**:
   ```bash
   oc logs -n <namespace> <virt-launcher-pod> -c compute | grep -iE 'error|fail' | tail -30
   oc get vm <vm> -n <namespace> -o jsonpath='{.status.startFailure}{"\n"}'
   ```
   QEMU errors (unsupported CPU model/feature on that node, missing firmware/TPM state PVC → `ErrorVMStateInUse`)
   show here. Also virt-handler on that node: `oc logs -n openshift-cnv -l kubevirt.io=virt-handler --prefix | grep <vm>`.
6. **Fix and retry** — after fixing the cause, `virtctl restart <vm>` (or stop/start). Changes made in GitOps, not by
   hand, if the VM is managed there.

## Verification

```bash
oc get vm <vm> -n <namespace>          # Running
oc get vmi <vm> -n <namespace> -o jsonpath='{.status.conditions[?(@.type=="AgentConnected")].status}{"\n"}'
virtctl console <vm> -n <namespace>    # guest booted
```

## Rollback

Nothing to roll back in steps 1–5 (read-only). A restart in step 6 reboots the guest.

## History

- 2026-11-02: created
