---
title: Migrating VMs from VMware to OpenShift Virtualization with MTV (Forklift) — providers, plans, cold vs warm (CBT snapshots, cutover), VDDK image, network and storage maps, ports 443/902, storage copy offload, common errors
type: knowledge
area: kubevirt
teams: [network, storage]
tags: [kubevirt, mtv, forklift, vmware, vsphere, migration, warm-migration, cold-migration, cbt, vddk, network-map, storage-map, copy-offload, xcopy, virt-v2v, vsan]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubev2v/forklift-documentation documentation/modules (con_about-cold-warm-migration, con_warm-migration-stages-*, ref_vmware-prerequisites, ref_network-prerequisites, ref_ports, proc_creating-vddk-image, con_about-storage-copy-offload, ref_error-messages, proc_troubleshooting-*)
---

# MTV / Forklift: VMware → OpenShift Virtualization

Migration Toolkit for Virtualization (upstream **Forklift**) moves VMs from vSphere (also RHV, OpenStack, OVA, Hyper-V,
other OpenShift Virtualization clusters) into KubeVirt VMs, converting the guest with `virt-v2v`.

## Objects

- **Provider** — source (a vCenter, with credentials Secret, optional **VDDK init image**) and destination (the local
  cluster or a remote one). Status must be `Ready`.
- **NetworkMap** / **StorageMap** — source network → pod network or a NAD; source datastore → StorageClass. Plan-owned
  or ownerless (reusable). Each extra destination network needs a NAD.
- **Plan** — VMs, maps, target namespace, cold or warm, hooks; **Migration** — one run of a plan (cutover time for warm).

## Cold vs warm

- **Cold**: source VM shut down, disks copied, converted, started on the target.
- **Warm** (vSphere and RHV only): disks copied **while the VM runs** using **CBT** (changed block tracking) snapshots —
  one every hour by default — then at **cutover** (manual or scheduled in the Migration CR) the VM is shut down and the
  last delta copied. RAM is not migrated. Requirements: CBT enabled on the VM and its disks, VMware Tools installed;
  Windows needs **VSS** and the VMware Snapshot Provider service enabled (otherwise
  `An error occurred while taking a snapshot: Failed to restart the virtual machine`).
- Snapshot limit: `Warm import retry limit reached` when the VM hits the CBT snapshot maximum during precopy (the docs
  say **28** in one place and **32** in another) — delete old snapshots in vCenter and restart the plan.

## VMware-side prerequisites (from the docs)

Compatible vSphere version; a user with at least MTV's minimal VMware privileges; **VDDK image required for VMs on
vSAN** (`Migration failed: VDDK image required for vSAN storage`); hibernation disabled; the target namespace must reach
the vSphere environment (egress NetworkPolicies break it); guest OS certified for `virt-v2v`; more than 10 VMs from one
ESXi host in a plan → raise that host's NFC service memory; vSphere 6/7 VMs cannot go to a FIPS-enabled cluster; VM
names must be DNS-compatible (`VM name validation failed: Invalid DNS name`). Don't change IPs, VLANs or networking
during a migration — **MAC addresses are preserved**.

## VDDK

Strongly recommended for speed (without it: much slower). You build a small image from VMware's VDDK tarball (a
filesystem that keeps symlinks) and push it to **our** registry — publishing it publicly may break VMware's licence.
Reference it in the vSphere provider (`VDDK init image`). A provider in another namespace that cannot pull it gives
`Error pulling VDDK image`.

## Ports (firewall)

| From | To | Port | Why |
|---|---|---|---|
| OCP nodes | vCenter | 443/TCP | inventory, disk-transfer auth |
| OCP nodes | ESXi hosts | 443/TCP | disk-transfer auth |
| OCP nodes | ESXi hosts | 902/TCP | disk data copy (NFC) |

These belong in the per-cluster flow table: `interfaces/ocp-network-palo-alto-flows.md`.

## Storage copy offload

With VMs on a SAN, MTV can have the **array** copy the disks (vSphere VAAI `XCOPY` via `vmkfstools`) instead of
streaming them: the storage map points at the array (Volume Populators) rather than the network path. Don't mix VDDK
and copy-offload mappings in one plan; delete pre-existing VM snapshots first (delta chains force a slower software
clone). NetApp-specific error: `Cannot derive SVM to use; please specify SVM in config file`; SSH-to-ESXi errors
(`Manual SSH key configuration required`, `Failed to connect via SSH`). Needs storage-team work —
`interfaces/virtualization-storage-kubevirt-vm-disks.md`.

## Other errors

`Unable to resize disk image to required size` — target PVC is EXT4 on block and CDI's filesystem-overhead estimate
misses the reserved space (`knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md`,
filesystem overhead). Logs: MTV UI per VM, or `oc adm must-gather --image=<mtv-must-gather-image>` (image name for
the installed MTV version: RHOKP).

Procedure: `runbooks/kubevirt/mtv-migration-plan-failing.md`. VMware side and PowerCLI helpers (enable CBT, list
snapshots): `knowledge/vmware/README.md`, `knowledge/powercli/README.md`.

## Scope & caveats

Upstream Forklift docs (latest tag v2.11 at snapshot time). Red Hat's MTV docs in RHOKP win for the version we run.
Whether we use MTV at all is an open question in `knowledge/kubevirt/README.md`.

## History

- 2026-11-02: created
