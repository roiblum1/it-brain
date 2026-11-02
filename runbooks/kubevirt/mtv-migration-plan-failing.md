---
title: Troubleshoot a failing MTV (Forklift) migration plan from VMware — provider not Ready, VDDK pull errors, warm import retry limit, disk resize errors, firewall ports 443/902
type: runbook
area: kubevirt
teams: [network, storage]
tags: [kubevirt, mtv, forklift, vmware, migration-plan, vddk, cbt, warm-migration, ports, troubleshooting]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubev2v/forklift-documentation documentation/modules (ref_error-messages, proc_troubleshooting-*, ref_ports, ref_vmware-prerequisites)
---

# MTV migration plan failing

**When to use:** an MTV plan or one of its VMs fails or does not progress.
**Impact while running:** read-only on the cluster; steps on vCenter (snapshots) need the VMware owners.
**Prerequisites:** access to the MTV namespace and UI; VMware contact (`knowledge/vmware/README.md`).
Background: `knowledge/kubevirt/kubevirt-mtv-forklift-migrating-vms-from-vmware.md`.

## Pre-checks

```bash
oc get providers.forklift.konveyor.io -A          # Ready?
oc get plans.forklift.konveyor.io -n <namespace>
oc get migrations.forklift.konveyor.io -n <namespace>
oc describe plan.forklift.konveyor.io <plan> -n <namespace> | sed -n '/Status/,$p'
oc get pods -n <namespace> | grep -iE 'importer|virt-v2v|populat'
```

## Procedure

1. **Provider not `Ready`** — credentials, vCenter reachable from the nodes on **443/TCP**; ESXi hosts on **443** and
   **902/TCP** for disk transfer (`interfaces/ocp-network-palo-alto-flows.md`); egress NetworkPolicies in the target
   namespace block it.
2. **`Error pulling VDDK image`** — the provider's namespace cannot pull our VDDK image: image in our registry, pull
   secret, path in the provider's `VDDK init image`. **`Migration failed: VDDK image required for vSAN storage`** — vSAN
   VMs need VDDK.
3. **`Warm import retry limit reached`** — the source VM reached the CBT snapshot limit during precopy: delete old
   snapshots in vCenter (VMware owners), restart the plan. Windows warm migration
   `An error occurred while taking a snapshot: Failed to restart the virtual machine` — VSS service disabled in the guest.
4. **`Unable to resize disk image to required size`** — target StorageClass is EXT4 on block; adjust filesystem overhead
   for that class or use a Block-mode target (`knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md`).
5. **`VM name validation failed: Invalid DNS name`** — rename the VM for the plan (DNS-compatible).
6. **Slow** — no VDDK; too many VMs from one ESXi host (> 10 needs more NFC memory); network path; consider copy offload
   with the storage team.
7. **Copy offload errors** (`Cannot derive SVM to use; please specify SVM in config file`, SSH errors to ESXi) — storage
   team (`interfaces/virtualization-storage-kubevirt-vm-disks.md`).
8. Collect logs: MTV UI per VM, or `oc adm must-gather --image=<mtv-must-gather-image>` (image for our MTV version: RHOKP).
   Don't paste logs with hostnames into the brain.

## Verification

The VM appears as a `VirtualMachine` in the target namespace, starts, and has its NICs on the mapped networks with the
same MACs.

## Rollback

Cold migration leaves the source VM powered off — power it back on in vCenter if the target is not accepted. Warm
migration keeps the source running until cutover.

## History

- 2026-11-02: created
