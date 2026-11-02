---
title: Pre-flight check vSphere for an OpenShift install with PowerCLI — objects, paths, privileges, tags for zones, datastore mounts, disk.EnableUUID
type: runbook
area: powercli
teams: [virtualization, ocp]
tags: [powercli, openshift, vsphere-ipi, vsphere-upi, preflight, privileges, tags, failure-domain, disk-enableuuid]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: knowledge/powercli/powercli-tags-privileges-and-preflight-for-openshift-on-vsphere.md; required privileges and tag names to be checked against RHOKP for the OCP version
---

# Pre-flight check vSphere for an OpenShift install

**When to use:** before the `ocp` team runs `openshift-install` against a vCenter (new cluster, new zone, new datastore).
**Impact while running:** read-only.
**Prerequisites:** the planned `install-config.yaml` values (datacenter, cluster, datastore, network, folder, failure
domains) from the `ocp` team; the installer service account name; RHOKP's privilege list for the OCP version.
Background: `knowledge/powercli/powercli-tags-privileges-and-preflight-for-openshift-on-vsphere.md`.

## Pre-checks

Connected read-only to the target vCenter (`runbooks/powercli/connect-powercli-to-vcenter-with-the-internal-ca.md`).

## Procedure

Run each block; every `FAIL` line is a blocker to fix before the install.

```powershell
$plan = @{ Datacenter = '<datacenter>'; Cluster = '<cluster>'; Datastore = '<datastore>'; Network = '<portgroup>';
           Folder = '<folder>'; Principal = '<sso-domain>\<svc-account>'; Zones = @('<zone-a>', '<zone-b>') }

# 1. objects exist
foreach ($k in 'Datacenter', 'Cluster', 'Datastore', 'Folder') {
    $o = switch ($k) { 'Datacenter' { Get-Datacenter -Name $plan.Datacenter -ErrorAction SilentlyContinue }
                       'Cluster'    { Get-Cluster    -Name $plan.Cluster    -ErrorAction SilentlyContinue }
                       'Datastore'  { Get-Datastore  -Name $plan.Datastore  -ErrorAction SilentlyContinue }
                       'Folder'     { Get-Folder -Type VM -Name $plan.Folder -ErrorAction SilentlyContinue } }
    '{0,-10} {1}' -f $k, $(if ($o) { 'ok' } else { 'FAIL: not found' })
}
$pg = Get-VDPortgroup -Name $plan.Network -ErrorAction SilentlyContinue
'Network    {0}' -f $(if ($pg) { "ok (VLAN: $($pg.VlanConfiguration))" } else { 'FAIL: port group not found' })

# 2. datastore mounted on every host of the cluster
$hosts = Get-Cluster $plan.Cluster | Get-VMHost
$mounted = Get-Datastore $plan.Datastore | Get-VMHost
$missing = $hosts | Where-Object { $mounted.Name -notcontains $_.Name }
'Mounts     {0}' -f $(if ($missing) { "FAIL: not on $($missing.Name -join ',')" } else { "ok ($($hosts.Count) hosts)" })
'FreeGB     {0}' -f [math]::Round((Get-Datastore $plan.Datastore).FreeSpaceGB)

# 3. permissions of the installer account (compare with RHOKP's list for the OCP version)
Get-VIPermission -Principal $plan.Principal | Select-Object Entity, Role, Propagate
Get-VIPermission -Principal $plan.Principal | ForEach-Object { Get-VIRole $_.Role } |
    Select-Object -ExpandProperty PrivilegeList | Sort-Object -Unique | Out-File ./installer-privileges.txt

# 4. zones / regions (multi-zone installs only)
Get-TagCategory -Name openshift-zone, openshift-region -ErrorAction SilentlyContinue | Select-Object Name, Cardinality, EntityType
Get-Cluster | Get-TagAssignment -Category openshift-zone -ErrorAction SilentlyContinue | Select-Object Entity, Tag
Get-Datacenter | Get-TagAssignment -Category openshift-region -ErrorAction SilentlyContinue | Select-Object Entity, Tag

# 5. UPI only: template has disk.EnableUUID
Get-Template '<rhcos-template>' -ErrorAction SilentlyContinue | Get-AdvancedSetting -Name disk.EnableUUID
```

Hand `installer-privileges.txt` to the `ocp` team to diff against RHOKP's list. The VLAN in step 1 must exist on the
fabric with the planned subnet — confirm with the network team (`interfaces/ocp-network-aci-fabric.md`).

## Verification

Every check prints `ok`; the privilege diff is empty; zone tags present on the planned clusters (multi-zone).

## Rollback

Read-only — nothing to roll back.

## History

- 2026-11-02: created
