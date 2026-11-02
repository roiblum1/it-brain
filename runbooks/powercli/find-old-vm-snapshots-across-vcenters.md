---
title: Find VM snapshots older than N days across all vCenters with PowerCLI (read-only, CSV for the owners)
type: runbook
area: powercli
tags: [powercli, snapshot, inventory, multiple-vcenters, get-snapshot, export-csv, housekeeping]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: knowledge/powercli/powercli-inventory-reporting-vms-hosts-datastores-snapshots-tools.md
---

# Find old snapshots across vCenters

**When to use:** weekly housekeeping; before vCenter / ESXi upgrades; before enabling CBT or an MTV migration;
when a datastore fills up unexpectedly.
**Impact while running:** read-only; a few minutes of API load per vCenter.
**Prerequisites:** a read-only service account stored in SecretManagement for each vCenter
(`runbooks/powercli/connect-powercli-to-vcenter-with-the-internal-ca.md`); the list of vCenters (kept on the jump host,
not in the brain).

## Pre-checks

```powershell
Get-Module -ListAvailable VMware.VimAutomation.Core | Select-Object Version
$global:DefaultVIServers | Select-Object Name     # should be empty before you start
```

## Procedure

1. Save as `Get-OldSnapshot.ps1` in the scripts repo (no names or credentials in it):
   ```powershell
   [CmdletBinding()]
   param(
       [Parameter(Mandatory)] [string[]] $VCenter,
       [Parameter(Mandatory)] [string]   $SecretPrefix,     # secrets named "<prefix>-<vcenter>"
       [Parameter(Mandatory)] [string]   $Vault,
       [ValidateRange(1, 3650)] [int]    $Days = 7,
       [string] $OutFile = "./old-snapshots-$(Get-Date -Format yyyyMMdd).csv"
   )
   $ErrorActionPreference = 'Stop'
   Set-PowerCLIConfiguration -Scope Session -DefaultVIServerMode Multiple -Confirm:$false | Out-Null
   $cutoff = (Get-Date).AddDays(-$Days)
   $rows = foreach ($name in $VCenter) {
       $viCred = Get-Secret -Name "$SecretPrefix-$name" -Vault $Vault
       $vc = Connect-VIServer -Server $name -Credential $viCred
       try {
           Get-VM -Server $vc | Get-Snapshot -Server $vc | Where-Object Created -lt $cutoff | ForEach-Object {
               [pscustomobject]@{
                   vCenter  = $vc.Name
                   VM       = $_.VM.Name
                   Snapshot = $_.Name
                   Created  = $_.Created
                   AgeDays  = [int]((Get-Date) - $_.Created).TotalDays
                   SizeGB   = [math]::Round($_.SizeGB, 1)
                   Note     = $_.Description
               }
           }
       } finally {
           Disconnect-VIServer -Server $vc -Confirm:$false
       }
   }
   $rows | Sort-Object AgeDays -Descending | Export-Csv -NoTypeInformation -Path $OutFile
   Write-Verbose "wrote $($rows.Count) rows to $OutFile"
   $rows | Group-Object vCenter | Select-Object Name, Count
   ```
2. Run it:
   ```bash
   pwsh -NoLogo -File Get-OldSnapshot.ps1 -VCenter <vcenter-a>,<vcenter-b> -SecretPrefix vc-reports -Vault <vault> -Days 7 -Verbose
   ```
3. Send the CSV to the VM owners (it contains real names — keep it on the share, not in the brain or a ticket title).
4. Deleting snapshots is a **separate change**: `Get-Snapshot … | Remove-Snapshot -WhatIf` first, in a window, a few
   at a time on the same datastore (consolidation load).

## Verification

Row counts per vCenter look plausible; spot-check two snapshots in the vSphere client; no connection left in
`$global:DefaultVIServers`.

## Rollback

Read-only — nothing to roll back.

## History

- 2026-11-02: created
