---
title: PowerCLI inventory and reports — VMs, hosts, datastores, snapshots older than N days, VMware Tools status, export to CSV / JSON
type: knowledge
area: powercli
tags: [powercli, inventory, report, snapshot, vmware-tools, datastore, export-csv, convertto-json, capacity]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: vmware/PowerCLI-Example-Scripts (Get-Snapshot, Get-Datastore, Get-Cluster usage across Scripts/ and Modules/; Modules/VMToolsManagement Get-VMToolsInfo); property names to confirm with Get-Member on the installed version
---

# Inventory and reporting patterns

All read-only. Connect first (`knowledge/powercli/powercli-connect-viserver-certificates-multiple-vcenters.md`);
for many vCenters use `Multiple` mode and keep the vCenter in every row. On big vCenters, prefer the
`Get-View` versions (`knowledge/powercli/powercli-object-model-get-view-extensiondata-performance-at-scale.md`).
Property names below are the usual ones — confirm with `| Get-Member` on your PowerCLI version.

## VMs

```powershell
Get-VM | Select-Object Name, PowerState, NumCpu, MemoryGB, ProvisionedSpaceGB, UsedSpaceGB,
    @{ N = 'Host';    E = { $_.VMHost.Name } },
    @{ N = 'Cluster'; E = { ($_.VMHost | Get-Cluster).Name } },
    @{ N = 'vCenter'; E = { ([uri]$_.Client.ConnectivityService.ServerAddress).Host } } |   # hypothesis: or parse $_.Uid
    Export-Csv -NoTypeInformation -Path ./vms-<date>.csv
```

Add guest data from the API view: `$_.ExtensionData.Guest.GuestFullName`, `.Guest.IpAddress`, `.Guest.ToolsRunningStatus`.
`ConvertTo-Json -Depth 4` for machine-readable output (the default depth truncates nested objects silently).

## Hosts and clusters

```powershell
Get-VMHost | Select-Object Name, ConnectionState, PowerState, Version, Build, NumCpu, MemoryTotalGB, MemoryUsageGB,
    @{ N = 'Cluster'; E = { $_.Parent.Name } }
Get-Cluster | Select-Object Name, HAEnabled, DrsEnabled, DrsAutomationLevel
```

`ConnectionState` `Maintenance` / `NotResponding` / `Disconnected` is the first column to look at after an incident.

## Datastores

```powershell
Get-Datastore | Select-Object Name, Type, CapacityGB, FreeSpaceGB,
    @{ N = 'FreePct'; E = { [math]::Round(100 * $_.FreeSpaceGB / $_.CapacityGB, 1) } },
    @{ N = 'Provisioned'; E = { [math]::Round(($_.ExtensionData.Summary.Capacity - $_.ExtensionData.Summary.FreeSpace +
                                               $_.ExtensionData.Summary.Uncommitted) / 1GB) } } |
    Sort-Object FreePct
```

Provisioned > capacity means thin over-commit — a storage-team conversation (`interfaces/storage-network-data-paths.md`
for the data path, the array areas for capacity).

## Snapshots older than N days

Old snapshots grow, slow the VM and block things (CBT changes, some migrations, `Set-CBT` skips VMs with snapshots).

```powershell
$cutoff = (Get-Date).AddDays(-7)
Get-VM | Get-Snapshot | Where-Object Created -lt $cutoff |
    Select-Object @{ N = 'VM'; E = { $_.VM.Name } }, Name, Created, @{ N = 'SizeGB'; E = { [math]::Round($_.SizeGB, 1) } },
                  Description |
    Sort-Object Created
```

Full procedure across vCenters, with output for the owners: `runbooks/powercli/find-old-vm-snapshots-across-vcenters.md`.
Deleting snapshots is a change (consolidation load on the datastore) — report first, delete in a window.

## VMware Tools

The example module `Modules/VMToolsManagement` has `Get-VMToolsInfo` (version + build), `Get-VMByToolsInfo`
(filter by Tools state) and `Get-VMToolsUpgradePolicy`. Without the module:

```powershell
Get-View -ViewType VirtualMachine -Property Name, Guest.ToolsRunningStatus, Guest.ToolsVersionStatus2 |
    Where-Object { $_.Guest.ToolsVersionStatus2 -ne 'guestToolsCurrent' } |
    Select-Object Name, @{ N = 'Running'; E = { $_.Guest.ToolsRunningStatus } }, @{ N = 'Version'; E = { $_.Guest.ToolsVersionStatus2 } }
```

Tools matter for clean shutdowns, guest IPs in inventory and for MTV migrations
(`knowledge/powercli/powercli-mtv-migration-prep-vmware-to-kubevirt-cbt-tools-inventory.md`).

## Report hygiene

- One row per object, the vCenter in every row, the date in the filename, no credentials anywhere.
- Real VM / host / datastore names are classified in the brain: reports stay on the jump host / file share, and only
  aggregated, placeholder-ised findings go into pages.

## History

- 2026-11-02: created
