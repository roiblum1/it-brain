---
title: PowerCLI slow on a big vCenter — cmdlets vs Get-View, -Property and -Filter (regex), ExtensionData, UpdateViewData, and calling Get-Stat once for many entities
type: knowledge
area: powercli
tags: [powercli, get-view, extensiondata, performance, filter, property, updateviewdata, get-stat, vsphere-api, managed-object]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: vmware/PowerCLI-Example-Scripts (Get-View -ViewType … -Property … -Filter in Modules/VCHA, Modules/ProactiveHA, Modules/VMToolsManagement; UpdateViewData; Get-Stat -Entity arrays in Modules/Recommend-Sizing and Get-VMmaxIOPS)
---

# The PowerCLI object model and performance

## Two layers

| Layer | You get | Cost |
|---|---|---|
| **Cmdlets** (`Get-VM`, `Get-VMHost`, `Get-Datastore`) | friendly "Impl" objects (`VirtualMachineImpl`) with a curated set of properties | each object is built from many API properties; convenient, slow at thousands of objects |
| **vSphere API views** (`Get-View`, `.ExtensionData`) | the raw managed-object view (`VirtualMachine`, `HostSystem`, `Datastore`, `ClusterComputeResource`) — every property the API has | fast when you ask only for the properties you need |

Every cmdlet object has **`.ExtensionData`** — its full API view — so you can mix: `$vm.ExtensionData.Config.ChangeTrackingEnabled`
(used by `Modules/Set-CBT`), `$vm.ExtensionData.Guest.ToolsRunningStatus`, `$vm.ExtensionData.Snapshot`.
Methods of the API are on the view too: `$vm.ExtensionData.ReconfigVM($spec)` (with a `VMware.Vim.VirtualMachineConfigSpec`).

## The fast pattern: `Get-View -ViewType … -Property … -Filter …`

From the example modules:

```powershell
Get-View -ViewType ClusterComputeResource -Property Name, Host, ConfigurationEx -Filter @{ 'Name' = $Cluster }
Get-View -ViewType HostSystem -Property Name -Filter @{ 'name' = $EsxiHost }
Get-View $vmMoRef -Property Config.Tools.ToolsUpgradePolicy
```

- `-ViewType` names the managed-object type; `-Property` limits what is retrieved (nested paths like
  `Runtime.PowerState`, `Summary.Storage.Committed` work); `-Filter` is applied **server-side**.
- `-Filter` values are **regular expressions** matched against the property: `@{ Name = 'app' }` also matches
  `myapp01`. Anchor for an exact name: `@{ Name = '^app01$' }` (and escape regex characters in names). This is the
  most common reason a filtered `Get-View` returns "too much".
- Properties you didn't ask for are `$null` on the returned view — not "missing in vSphere". If you need more
  later: `$view.UpdateViewData('Summary.Runtime')` (the examples call `UpdateViewData()` to refresh, and
  `UpdateViewData('Info')` for one property path).
- Turn a view back into a cmdlet object when you need a cmdlet: `Get-VIObjectByVIView $view` (or pass the
  MoRef: `Get-VM -Id $view.MoRef`). Turn a MoRef into a name cheaply: `(Get-View -Id $moRef -Property Name).Name` —
  pattern used in the examples.

Example — every powered-on VM with its host and Tools state, fast:

```powershell
$vms = Get-View -ViewType VirtualMachine -Property Name, Runtime.Host, Runtime.PowerState, Guest.ToolsRunningStatus `
                -Filter @{ 'Runtime.PowerState' = 'poweredOn' }
$hostNames = @{}
Get-View -ViewType HostSystem -Property Name | ForEach-Object { $hostNames[$_.MoRef.Value] = $_.Name }
$vms | ForEach-Object {
    [pscustomobject]@{ VM = $_.Name; Host = $hostNames[$_.Runtime.Host.Value]; Tools = $_.Guest.ToolsRunningStatus }
}
```

Two API calls instead of one per VM: resolve MoRefs through a lookup table, not with a `Get-View` per row.

## Things that are slow (and what to do)

| Slow | Why | Faster |
|---|---|---|
| `Get-VM \| ForEach-Object { Get-VMHost -VM $_ }` | one round-trip per VM | `$vm.VMHost` (already loaded) or a MoRef lookup table |
| `Get-VM \| Get-Stat …` with a per-VM loop | one performance query per VM | **one** `Get-Stat -Entity $vms -Stat <metrics> -Start … -Finish …` call — exactly how the sizing examples query (`Get-Stat -Realtime -Stat $VMMetrics -Entity $VMs`), then `Group-Object Entity` |
| `Get-VM -Name x` repeated in a loop | full lookup each time | load once into a hashtable keyed by name |
| `Get-VM` on a large vCenter, then `Where-Object` | builds every object client-side | `Get-View -Filter` server-side, or `Get-VM -Location <cluster>` to narrow first |
| reading `.ExtensionData` of thousands of cmdlet objects | already fetched, cheap — but `Get-VM` itself was the cost | start from `Get-View` when you don't need cmdlet objects |

## `Get-Stat` notes

- `-Realtime` reads the 20-second samples a host keeps for a short window; longer ranges come from vCenter's
  rolled-up intervals and are coarser (`-IntervalSecs`/`-IntervalMins`). Which intervals exist depends on the
  vCenter statistics level (hypothesis — check *Statistics* settings on the vCenter).
- Metric names are `group.counter.rollup`, e.g. `cpu.usage.average`, `mem.usage.average`, `disk.maxTotalLatency.latest`.
  `Get-StatType -Entity $vm` lists what is available.

## Related

`knowledge/powercli/powercli-inventory-reporting-vms-hosts-datastores-snapshots-tools.md` (report recipes built on this),
`knowledge/powercli/powershell-essentials-objects-pipeline-errors-for-infra-engineers.md`.

## History

- 2026-11-02: created
