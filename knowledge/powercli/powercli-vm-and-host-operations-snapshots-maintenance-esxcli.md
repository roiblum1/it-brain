---
title: PowerCLI VM and host operations — power, snapshots, hardware and advanced settings (disk.EnableUUID), maintenance mode with DRS / vSAN, Get-EsxCli -V2
type: knowledge
area: powercli
tags: [powercli, vm, snapshot, advanced-setting, disk-enableuuid, maintenance-mode, drs, vsan, esxcli, get-esxcli]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: vmware/PowerCLI-Example-Scripts (Get-EsxCli -V2 … .Invoke() / .CreateArgs() in Modules/Validate-ESXiPackages and Konfig-ESXi; New-AdvancedSetting -Entity $vm … -Confirm:$false -Force; Set-CBT ReconfigVM); cmdlet parameters from general PowerCLI knowledge — check Get-Help on your version
---

# VM and host operations

Everything on this page **changes state**. Rules for every one of them: `-WhatIf` first, explicit `-Server`, a
window if it touches production, and the change written down. Script structure:
`knowledge/powercli/powercli-script-quality-shouldprocess-whatif-pester-scriptanalyzer.md`.

## Power

| Cmdlet | Does | Needs |
|---|---|---|
| `Stop-VMGuest -VM <vm>` | clean guest OS shutdown | VMware Tools running |
| `Stop-VM -VM <vm>` | hard power-off (like pulling the plug) | nothing — last resort |
| `Restart-VMGuest` / `Restart-VM` | guest reboot / hard reset | Tools / nothing |
| `Start-VM` | power on | — |

`Stop-VM` prompts by default; scripts that pass `-Confirm:$false` must have checked the target list first.

## Snapshots

```powershell
New-Snapshot -VM <vm> -Name 'pre-change-<ticket>' -Description '<who/why>' -Memory:$false -Quiesce:$false -WhatIf
Get-Snapshot -VM <vm> | Select-Object Name, Created, SizeGB
Get-Snapshot -VM <vm> -Name 'pre-change-<ticket>' | Remove-Snapshot -WhatIf
```

- A snapshot is **not a backup**; delete it after the change. Consolidation after a large delete loads the datastore.
- `-Memory` captures RAM (big, stuns the VM longer); `-Quiesce` needs Tools and asks the guest to flush.
- The `Set-CBT` example creates and removes a snapshot on a running VM to make a CBT change take effect — a
  snapshot is also how some config changes reach a running VM.

## Hardware and advanced settings

```powershell
Set-VM -VM <vm> -NumCpu 4 -MemoryGB 16 -WhatIf          # hot-add only if enabled for the VM; otherwise power off first
Get-AdvancedSetting -Entity <vm> -Name 'disk.EnableUUID'
New-AdvancedSetting -Entity <vm> -Name 'disk.EnableUUID' -Value 'TRUE' -WhatIf     # examples add -Confirm:$false -Force once reviewed
```

`disk.EnableUUID = TRUE` makes the guest see stable disk UUIDs — **required for OpenShift on vSphere** (vSphere
CSI relies on it). IPI installs set it on the VMs they create; UPI templates must have it
(`knowledge/powercli/powercli-tags-privileges-and-preflight-for-openshift-on-vsphere.md`). Advanced settings on a VM
take effect at the next power-on (hypothesis — check per setting).

For anything the cmdlets don't expose, the API: build a `VMware.Vim.VirtualMachineConfigSpec` and call
`$vm.ExtensionData.ReconfigVM($spec)` — as `Modules/Set-CBT` does for `ChangeTrackingEnabled`.

## Hosts: maintenance mode

```powershell
Get-Cluster -VMHost <esxi> | Select-Object Name, DrsEnabled, DrsAutomationLevel, HAEnabled
Set-VMHost -VMHost <esxi> -State Maintenance -Evacuate -WhatIf
# vSAN cluster: choose what happens to data (EnsureAccessibility is the usual choice for short work)
Set-VMHost -VMHost <esxi> -State Maintenance -VsanDataMigrationMode EnsureAccessibility -WhatIf
Set-VMHost -VMHost <esxi> -State Connected -WhatIf       # leave maintenance
```

- With DRS **fully automated**, entering maintenance vMotions running VMs away; `-Evacuate` also moves powered-off
  / suspended VMs. With DRS partially automated or off, the task waits for VMs that someone must move — a
  maintenance task "hanging at 2%" is usually this.
- VMs pinned to the host (passthrough devices, local disks, affinity rules, vGPU) block evacuation.
- **OpenShift nodes are VMs too**: draining a host moves control-plane and worker VMs; one host's VMs moving is
  fine, several hosts at once can break etcd quorum if anti-affinity is missing. Coordinate with `ocp` for clusters
  on vSphere (`knowledge/vsphere/README.md`).
- Full procedure with checks: `runbooks/powercli/put-an-esxi-host-into-maintenance-mode-safely.md`.

## esxcli through PowerCLI: `Get-EsxCli -V2`

```powershell
$esxcli = Get-EsxCli -VMHost <esxi> -V2
$esxcli.system.version.get.Invoke()
$esxcli.network.nic.list.Invoke() | Select-Object Name, LinkStatus, Speed, Duplex, MTU
$esxcli.software.vib.list.Invoke() | Where-Object Name -like '*nvme*'
# with arguments: build them, then invoke
$cliArgs = $esxcli.storage.core.device.list.CreateArgs()
$cliArgs.device = '<naa-id>'
$esxcli.storage.core.device.list.Invoke($cliArgs)
```

`-V2` is the form the examples use: methods take one argument object from `CreateArgs()` (named fields) instead of
positional arguments. Read-only namespaces (`list`, `get`) are safe; `software.vib.install`, `system.maintenanceMode.set`
and friends are changes.

## Patch / compliance basics

ESXi versions and builds come from `Get-VMHost | Select Name, Version, Build`; installed VIBs from `esxcli software vib list`
(the `Validate-ESXiPackages` example compares a host's VIBs to a reference host). Image / baseline remediation is
done through vCenter's lifecycle manager; PowerCLI support for it depends on the module version (hypothesis).

## History

- 2026-11-02: created
