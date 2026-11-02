---
title: KubeVirt architecture — virt-operator, virt-api, virt-controller, virt-handler, virt-launcher (virtqemud + QEMU), VM vs VMI vs VMIM, HCO and CDI
type: knowledge
area: kubevirt
tags: [kubevirt, cnv, architecture, virt-launcher, virt-handler, virt-controller, virt-api, hco, hyperconverged, cdi, vmi]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/kubevirt docs/components.md, docs/architecture.md; kubevirt/user-guide docs/architecture/architecture.md; kubevirt/hyperconverged-cluster-operator docs/cluster-configuration.md, docs/component.gv
---

# KubeVirt architecture and components

## The model in one paragraph

KubeVirt adds CRDs (VirtualMachine, VirtualMachineInstance, …) to the Kubernetes API, controllers for cluster-wide
logic and a node daemon. **Every running VM is a pod** (`virt-launcher-<vm>-<hash>`): Kubernetes schedules, networks
and attaches storage to that pod; KubeVirt runs QEMU inside it. So most VM problems are pod problems first
(scheduling, PVC binding, CNI) and only then virtualization problems. The design rule ("the KubeVirt Razor"): if
something is useful for pods, it is not implemented only for VMs — hence Multus/CNI for networking and CSI for disks.

## Components

| Component | Kind | Does |
|---|---|---|
| `virt-operator` | Deployment | installs and updates all other KubeVirt components from the `KubeVirt` CR |
| `virt-api` | Deployment | entry point for virtualization flows: defaulting and validation webhooks for VMI/VM, subresources (console, VNC, migrate, start/stop), and the **pod eviction webhook** (`knowledge/kubevirt/kubevirt-node-drain-eviction-strategy-and-pdbs.md`) |
| `virt-controller` | Deployment | cluster-wide logic: watches VMIs, creates the virt-launcher pod, sets `nodeName` once the pod runs, runs the migration, disruption-budget and evacuation controllers |
| `virt-handler` | DaemonSet (one per node) | node-side: keeps the VMI spec in sync with the libvirt domain, reports domain state, sets up node-side networking/storage; heartbeats the node (`kubevirt.io/schedulable` label, `kubevirt.io/heartbeat` annotation) |
| `virt-launcher` | one pod per VMI | provides the cgroups and namespaces for the VM; its `compute` container runs `virtqemud` (libvirt's QEMU daemon; monolithic `libvirtd` before v0.59) and `virtlogd`, which start and monitor the QEMU process; forwards termination signals to the guest and holds off pod termination until the guest shuts down |

Create flow (`docs/upstream/kubevirt-docs/docs/components.md`): client posts a VMI → virt-api validates → virt-controller
creates the virt-launcher pod → Kubernetes schedules it → virt-controller writes `nodeName` into the VMI →
virt-handler on that node sees the VMI and tells virtqemud in the pod to define and start the domain. Delete is the
reverse: virt-handler sees the deletion and shuts the domain down.

**Heartbeat:** if virt-handler cannot update `kubevirt.io/heartbeat` for **five minutes**, the KubeVirt node
controller sets `kubevirt.io/schedulable=false` on the node and no new VMIs land there (virt-launcher pods carry
`nodeSelector: kubevirt.io/schedulable: "true"`). During those five minutes new VMIs can still be scheduled there
and fail. If the whole node is dead, `oc delete vmi` alone never finishes — the pods on the node must be
force-deleted after you are sure the node is really down (`docs/upstream/kubevirt-user-guide/docs/cluster_admin/unresponsive_nodes.md`).

## The objects

| Object | Short | Is |
|---|---|---|
| `VirtualMachine` | `vm` | the stateful, user-facing object (like a StatefulSet with one replica): start/stop/restart, offline config changes, `runStrategy` |
| `VirtualMachineInstance` | `vmi` | the **running** instance; ephemeral — exists only while the VM runs; carries `status.interfaces`, conditions (`LiveMigratable`, `AgentConnected`…), `migrationState` |
| `VirtualMachineInstanceMigration` | `vmim` | one live migration request and its phase (`knowledge/kubevirt/kubevirt-live-migration-requirements-limits-policies-failures.md`) |
| `VirtualMachineInstanceReplicaSet`, `VirtualMachinePool` | `vmirs`, `vmpool` | groups of VMIs/VMs from a template |
| `DataVolume`, `DataSource`, `DataImportCron`, `StorageProfile` | `dv`… | CDI objects for VM disks (`knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md`) |
| `VirtualMachineSnapshot`, `VirtualMachineRestore`, `VirtualMachineClone`, `VirtualMachineExport` | | `knowledge/kubevirt/kubevirt-snapshots-clones-export-and-oadp-backup.md` |
| `MigrationPolicy` | | per-group migration settings (`migrations.kubevirt.io/v1alpha1`) |
| `VirtualMachine(Cluster)Instancetype`, `VirtualMachine(Cluster)Preference` | | `knowledge/kubevirt/kubevirt-instancetypes-preferences-templates-cloud-init-sysprep.md` |

## HCO — what OpenShift Virtualization actually installs

The HyperConverged Cluster Operator manages KubeVirt and its companions from **one CR**,
`HyperConverged/kubevirt-hyperconverged` in the install namespace. It copies its configuration into the operands'
CRs and **reverts manual edits** of those CRs: it counts reverts in `kubevirt_hco_out_of_band_modifications_total` and
fires `KubeVirtCRModified` (warning) — so configure migrations, eviction, workload updates, CPU ratio, filesystem
overhead etc. in the HyperConverged CR, not in the `KubeVirt` or `CDI` CR. (Our day2 GitOps should own that CR;
an edit made with `oc edit kubevirt` will be undone.)

Operands seen in HCO's component graph (`docs/component.gv`): `KubeVirt` (virt-* components), `CDI`,
`NetworkAddonsConfig` (Cluster Network Addons operator: Multus extras, Linux bridge CNI, kubemacpool), `SSP`
(templates, template validator, common instance types), `aaq-operator` (application-aware quota),
`kubevirt-migration-controller`, `kubevirt-console-plugin`, `kubevirt-apiserver-proxy`,
`virt-platform-autopilot` and others; the exact set depends on the version — `oc get hyperconverged -n openshift-cnv -o yaml`
shows what is enabled.

HCO docs use the newer `hco.kubevirt.io/v1` API (`spec.virtualization.*`, `spec.storage.*`); older CNV releases use
`v1beta1` where the same fields sit directly under `spec` (`spec.liveMigrationConfig`, `spec.filesystemOverhead`…).
Check which one your cluster serves before copying a snippet.

## CDI

The Containerized Data Importer populates PVCs with VM disk images: import (HTTP/S3/registry/VDDK/ImageIO), upload,
clone, blank. It runs short-lived importer/cloner/uploader pods next to the target PVC and needs **scratch space** for
some operations. Details: `knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md`.

## Quick look at a cluster (read-only)

```bash
oc get hyperconverged -A                       # one CR; conditions Available/Progressing/Degraded
oc get kubevirt -A -o jsonpath='{.items[0].status.phase}{"\n"}'
oc get pods -n openshift-cnv -o wide | grep -E 'virt-(api|controller|handler|operator)'
oc get nodes -L kubevirt.io/schedulable
oc get vm,vmi -A
```

## Scope & caveats

General KubeVirt architecture; component names are stable across 1.x. The HCO operand list and API version move —
check the installed CSV. Namespace `openshift-cnv` is the OpenShift default (upstream: `kubevirt`, `kubevirt-hyperconverged`).

## How we know

Read from the upstream docs and HCO configuration guide listed in `source`; not yet checked on our clusters.

## History

- 2026-11-02: created
