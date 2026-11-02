---
title: Put an ESXi host into maintenance mode safely with PowerCLI — DRS level, pinned VMs, OpenShift node VMs, vSAN data mode, -WhatIf first
type: runbook
area: powercli
teams: [virtualization, ocp]
tags: [powercli, esxi, maintenance-mode, drs, vmotion, vsan, openshift, set-vmhost]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: knowledge/powercli/powercli-vm-and-host-operations-snapshots-maintenance-esxcli.md
---

# Put an ESXi host into maintenance mode safely

**When to use:** patching, hardware work, firmware, a failing component on `<esxi>`.
**Impact while running:** every VM on the host vMotions away (short stun per VM); cluster capacity drops by one host
until it returns. OpenShift node VMs on the host move too.
**Prerequisites:** change window; an account allowed to change host state; DRS fully automated on the cluster (or a
plan to move VMs by hand); enough spare capacity on the remaining hosts. Tell `ocp` if OpenShift node VMs run there.

## Pre-checks

```powershell
$h = Get-VMHost '<esxi>' -Server $vc
$c = Get-Cluster -VMHost $h
$c | Select-Object Name, DrsEnabled, DrsAutomationLevel, HAEnabled
$h | Get-VM | Select-Object Name, PowerState, NumCpu, MemoryGB
# VMs that will not move by themselves: passthrough / vGPU / local disks / CD-ROM to a host file
$h | Get-VM | Where-Object { ($_ | Get-PassthroughDevice) -or ($_ | Get-CDDrive | Where-Object IsoPath -like '*[[]*local*') } |
    Select-Object Name
# capacity: can the rest of the cluster hold it?
$c | Get-VMHost | Where-Object Name -ne $h.Name | Measure-Object MemoryTotalGB, MemoryUsageGB -Sum
```

- `DrsAutomationLevel` not `FullyAutomated` → the task will wait for you to move VMs.
- OpenShift: list node VMs on the host and on the other hosts; if **two control-plane VMs of the same cluster** would
  end up on one host, stop and fix anti-affinity first (losing that host would break etcd quorum).
- vSAN cluster: decide the data mode — `EnsureAccessibility` (normal short maintenance) vs `Full` (long / decommission).

## Procedure

1. Dry run:
   ```powershell
   Set-VMHost -VMHost $h -State Maintenance -Evacuate -WhatIf
   ```
2. Enter maintenance (async, so you can watch):
   ```powershell
   $t = Set-VMHost -VMHost $h -State Maintenance -Evacuate -RunAsync
   # vSAN: add -VsanDataMigrationMode EnsureAccessibility
   while ($t.State -eq 'Running') { Start-Sleep 15; $t = Get-Task -Id $t.Id; "$($t.PercentComplete)%" }
   $t | Select-Object State, Result
   ```
3. If it stalls: `$h | Get-VM | Where PowerState -eq PoweredOn` shows what is left; move it with
   `Move-VM -VM <vm> -Destination <other-esxi> -WhatIf` then without `-WhatIf`, or ask the VM owner.
4. Do the work. Then exit:
   ```powershell
   Set-VMHost -VMHost $h -State Connected -WhatIf
   Set-VMHost -VMHost $h -State Connected
   ```

## Verification

```powershell
(Get-VMHost '<esxi>').ConnectionState            # Maintenance during work, Connected after
Get-Datastore -RelatedObject (Get-VMHost '<esxi>') | Select-Object Name, State   # all datastores back after exit
```

After exit, DRS rebalances VMs back over time. For OpenShift clusters on the cluster: `oc get nodes` all `Ready`
(the `ocp` team checks).

## Rollback

Exit maintenance mode (`-State Connected`) at any time; VMs already moved stay where they are until DRS rebalances.

## History

- 2026-11-02: created
