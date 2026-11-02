---
title: KubeVirt VM lifecycle — runStrategy (Always, RerunOnFailure, Manual, Halted, Once) and every printableStatus (ErrorUnschedulable, DataVolumeError, WaitingForVolumeBinding, CrashLoopBackOff…)
type: knowledge
area: kubevirt
tags: [kubevirt, vm, vmi, runstrategy, printablestatus, errorunschedulable, datavolumeerror, waitingforvolumebinding, crashloopbackoff, virtctl]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/kubevirt staging/src/kubevirt.io/api/core/v1/types.go (VirtualMachinePrintableStatus, VirtualMachineRunStrategy); kubevirt/user-guide docs/compute/run_strategies.md
---

# VM lifecycle: runStrategy and printableStatus

## runStrategy

`spec.runStrategy` on the VirtualMachine decides whether a guest should run and what happens when it stops.
`spec.running` is **deprecated since KubeVirt v1.4.0** (`running: true` = `Always`, `false` = `Halted`); the API server
warns `spec.running is deprecated, please use spec.runStrategy instead.` and **rejects** a VM that sets both.

| runStrategy | Behaviour |
|---|---|
| `Always` | keep it running: a new VMI is created whenever the old one ends, controlled (guest shutdown) or not (crash) |
| `RerunOnFailure` | restart only after an uncontrolled, infrastructure-caused end (node crash, QEMU OOM-killed); a shutdown from inside the guest stays off. Guest-side crashes (BSOD) are **not** covered — use a watchdog or liveness probe |
| `Manual` | KubeVirt never starts/stops it by itself; only `start`/`stop`/`restart` subresources (virtctl, console, MCP `vm_lifecycle`) |
| `Halted` | ensure nothing runs: any VMI is stopped |
| `Once` | run once, never restart, whatever the outcome |
| `WaitAsReceiver` | internal: VM waiting to receive a (decentralized) migration |

`virtctl start|stop|restart <vm>` call the subresources and may change runStrategy (e.g. `stop` on an `Always` VM sets
`Halted`). An `Always` VM that you stop from inside the guest comes straight back — use `RerunOnFailure` if guest
owners must be able to power off.

## printableStatus — what `oc get vm` STATUS means

Values from `VirtualMachinePrintableStatus` in the KubeVirt API (`types.go`), with what to look at next:

| STATUS | Meaning (from the API comments) | First look |
|---|---|---|
| `Stopped` | stopped and not expected to start | runStrategy |
| `Provisioning` | resources such as DataVolumes are being provisioned | `oc get dv -n <namespace>` — `knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md` |
| `Starting` | being prepared to run | virt-launcher pod events |
| `Running` | running | — |
| `Paused` | paused (virtctl pause, or a migration paused it to converge) | `virtctl unpause vmi <vm>`; migration settings |
| `Stopping` | being stopped | stuck? guest ignores ACPI shutdown → `terminationGracePeriodSeconds` |
| `Terminating` | being deleted with its VMI and DataVolumes | finalizers, node health |
| `CrashLoopBackOff` | VMI keeps failing to start; waiting to retry | `oc get vm <vm> -o yaml` → `status.startFailure`; virt-launcher logs |
| `Migrating` | live migration in progress | `oc get vmim -n <namespace>` |
| `Unknown` | state could not be obtained, typically cannot talk to the host | virt-handler on the node, node health |
| `ErrorUnschedulable` | scheduling failed: unsatisfiable requests or constraints | `oc describe pod virt-launcher-<vm>-…` → `FailedScheduling` message |
| `ErrImagePull` / `ImagePullBackOff` | pulling a **containerDisk** image failed | image mirrored? (air gap) pull secret |
| `ErrorPvcNotFound` | references a PVC that does not exist | volume names in the VM spec |
| `DataVolumeError` | a referenced DataVolume reports an error | `oc describe dv` events |
| `WaitingForVolumeBinding` | some PVCs backing the VM are not bound yet | `oc get pvc`; WaitForFirstConsumer StorageClass is normal until the pod schedules |
| `WaitingForReceiver` | receiver VM of a migration, migration should start next | decentralized migration |
| `ErrorVMStateInUse` | its VirtualMachineState PVC (vTPM/EFI state) is used by another running VM | who mounts that PVC |

The alert `VirtualMachineStuckOnNode` fires when a VM with a VMI stays `Starting`, `Stopping`, `Terminating` or in an
error state for more than 5 minutes on one node (runbook in `docs/upstream/openshift-runbooks/alerts/openshift-virtualization-operator/`).

## Useful commands (read-only)

```bash
oc get vm -n <namespace>                                # STATUS = printableStatus
oc get vm <vm> -n <namespace> -o jsonpath='{.status.conditions}' | jq
oc get vmi <vm> -n <namespace> -o wide                  # node, IP, LIVE-MIGRATABLE
oc get pods -n <namespace> -l kubevirt.io=virt-launcher -o wide
oc get events -n <namespace> --sort-by=.lastTimestamp | tail -30
```

Procedure for a VM that will not start: `runbooks/kubevirt/vm-wont-start-pending-errorunschedulable-datavolumeerror.md`.

## Scope & caveats

Status names from the KubeVirt API on `main` (2026-11); a few (`WaitingForReceiver`, `ErrorVMStateInUse`) are recent —
older CNV releases do not show them.

## History

- 2026-11-02: created
