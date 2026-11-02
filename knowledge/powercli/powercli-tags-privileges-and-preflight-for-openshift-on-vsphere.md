---
title: PowerCLI for OpenShift on vSphere — openshift-region / openshift-zone tag categories, vCenter roles and privileges, folders, disk.EnableUUID, pre-install checks
type: knowledge
area: powercli
teams: [virtualization, ocp]
tags: [powercli, openshift, vsphere-ipi, tags, tag-category, openshift-zone, openshift-region, failure-domain, privileges, role, disk-enableuuid, preflight]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: vmware/PowerCLI-Example-Scripts (New-TagAssignment, Get-TagAssignment, Get-VIRole usage); OpenShift-on-vSphere requirements from general knowledge — check RHOKP "Installing on vSphere" for the OCP version you install
---

# PowerCLI for OpenShift on vSphere

The OpenShift installer talks to vCenter with an account; when it fails, it is usually missing privileges, a
missing tag, or a wrong path in `install-config.yaml`. These checks find that **before** an install. Cluster-side
behaviour stays in `vsphere` (`knowledge/vsphere/README.md`); requirements change per OCP version — **RHOKP is the
authority** (search `rhokp` with `version: "4.NN"`).

## Tags and categories (zones and regions)

Multi-zone OpenShift on vSphere maps *failure domains* to vSphere objects through tags: a **region** tag category on
datacenters and a **zone** tag category on clusters, conventionally named `openshift-region` and `openshift-zone`,
referenced from the failure domains in `install-config.yaml` (hypothesis on exact names — check RHOKP for your version).

```powershell
Get-TagCategory | Select-Object Name, Cardinality, EntityType
Get-Datacenter | Get-TagAssignment -Category openshift-region | Select-Object Entity, Tag
Get-Cluster    | Get-TagAssignment -Category openshift-zone   | Select-Object Entity, Tag
# creating them is a change:
New-TagCategory -Name openshift-zone -Cardinality Single -EntityType ClusterComputeResource -WhatIf
New-Tag -Name '<zone>' -Category openshift-zone -WhatIf
Get-Cluster '<cluster>' | New-TagAssignment -Tag '<zone>' -WhatIf
```

Tags live in vCenter's CIS (REST) service, not the classic API: if tag cmdlets fail while `Get-VM` works, the CIS
endpoint or the account's tagging privileges are the problem (the community module `VMware.Community.CISTag` in the
examples works against that REST API).

## Roles and privileges

The installer account needs a defined set of privileges on vCenter, the datacenter, the cluster / resource pool,
datastores, port groups and the VM folder (RHOKP lists them per object; they differ between IPI and UPI and grow
with features like zones). Check what an account really has:

```powershell
Get-VIRole -Name '<role>' | Select-Object -ExpandProperty PrivilegeList
Get-VIPermission -Principal '<sso-domain>\<svc-account>' | Select-Object Entity, Role, Propagate
```

- Missing **propagation** on a parent object is the classic cause of "permission denied on folder X" mid-install.
- Keep one role per purpose (OpenShift installer, CSI driver if separate, read-only reports) — never reuse an
  administrator account.

## disk.EnableUUID and templates

vSphere CSI needs `disk.EnableUUID = TRUE` on node VMs. IPI sets it; for UPI (RHCOS templates we import), check the template:

```powershell
Get-Template '<template>' | Get-AdvancedSetting -Name disk.EnableUUID          # hypothesis: templates expose advanced settings like VMs
Get-VM -Location (Get-Folder '<cluster-folder>') | Get-AdvancedSetting -Name disk.EnableUUID | Where-Object Value -ne 'TRUE'
```

## Paths in install-config

The installer wants inventory **paths** (`/<datacenter>/host/<cluster>`, `/<datacenter>/datastore/<datastore>`,
`/<datacenter>/vm/<folder>`). Resolve them from PowerCLI rather than typing them:

```powershell
Get-Datastore '<datastore>' | Select-Object Name, @{ N = 'Path'; E = { $_.DatastoreBrowserPath } }   # hypothesis — property may differ
Get-Folder -Type VM '<folder>' | Select-Object Name, Parent
```

## Pre-flight checklist

Scripted in `runbooks/powercli/preflight-check-vsphere-for-an-openshift-install.md`:

1. Account connects; vCenter version is in the support matrix for the OCP version (RHOKP).
2. Role has the required privileges on each object, propagated where needed.
3. Datacenter / cluster / datastore / port group / folder exist and resolve to the paths in install-config.
4. Tag categories and tags for regions / zones exist and are assigned (multi-zone only).
5. Datastore mounted on every host of the cluster; enough free space for the nodes.
6. Port group's VLAN exists on the fabric (network team) and has DHCP / IPs as planned.
7. `disk.EnableUUID` on templates (UPI).

## History

- 2026-11-02: created
