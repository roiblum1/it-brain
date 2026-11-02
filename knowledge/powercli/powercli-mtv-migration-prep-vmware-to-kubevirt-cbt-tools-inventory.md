---
title: PowerCLI MTV migration prep (VMware → OpenShift Virtualization / KubeVirt) — inventory candidates, enable CBT for warm migration, VMware Tools, snapshots, unsupported disks
type: knowledge
area: powercli
teams: [virtualization, ocp]
tags: [powercli, mtv, forklift, migration, kubevirt, openshift-virtualization, cbt, change-tracking, warm-migration, vmware-tools, rdm, inventory]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: vmware/PowerCLI-Example-Scripts Modules/Set-CBT/Set-CBT.psm1 (ChangeTrackingEnabled via ReconfigVM, snapshot create/remove, skips VMs with snapshots); MTV requirements from general knowledge — check the MTV docs in RHOKP for your version
---

# Preparing VMware VMs for MTV with PowerCLI

MTV (Migration Toolkit for Virtualization, upstream *Forklift*) moves VMs from vSphere into OpenShift
Virtualization (KubeVirt). MTV itself, its providers, mappings and plans belong to `kubevirt`
(`knowledge/kubevirt/README.md`); this page is the **vSphere-side homework** that decides whether a migration goes
smoothly. Requirements change with MTV versions — the MTV docs in RHOKP are the authority.

## 1. Inventory the candidates

```powershell
Get-VM -Location '<folder-or-cluster>' | ForEach-Object {
    $v = $_.ExtensionData
    [pscustomobject]@{
        VM          = $_.Name
        PowerState  = $_.PowerState
        GuestOS     = $v.Config.GuestFullName
        Firmware    = $v.Config.Firmware                     # bios / efi — must match on the target
        NumCpu      = $_.NumCpu
        MemoryGB    = $_.MemoryGB
        Disks       = ($_ | Get-HardDisk).Count
        DiskGB      = [math]::Round(($_ | Get-HardDisk | Measure-Object CapacityGB -Sum).Sum)
        RDM         = [bool]($_ | Get-HardDisk | Where-Object DiskType -like 'Raw*')
        SharedBus   = [bool]($_ | Get-ScsiController | Where-Object BusSharingMode -ne 'NoSharing')
        Snapshots   = ($_ | Get-Snapshot).Count
        CBT         = $v.Config.ChangeTrackingEnabled
        Tools       = $v.Guest.ToolsRunningStatus
        NICs        = ($_ | Get-NetworkAdapter | ForEach-Object { "$($_.NetworkName)" }) -join ';'
    }
} | Export-Csv -NoTypeInformation ./mtv-candidates-<date>.csv
```

What to look for (hypothesis — confirm each against the MTV docs for our version):

| Column | Why it matters |
|---|---|
| `RDM`, `SharedBus` | raw device mappings and shared (multi-writer / clustered) disks are generally not migratable as-is |
| `Firmware` | BIOS vs UEFI (and secure boot) must be reproduced on the KubeVirt VM |
| `Snapshots` | existing snapshots complicate migration and block CBT changes (`Set-CBT` refuses VMs with snapshots) — clean up first |
| `CBT` | **warm migration** copies changed blocks incrementally and needs Changed Block Tracking enabled |
| `Tools` | guest tools help clean shutdown at cutover and report guest IPs; the guest also needs virtio drivers on the target (Windows especially) |
| `NICs` | every source port group needs a network mapping to a NAD / pod network on the target cluster — VLANs agreed with the network team |
| `DiskGB` per datastore | every source datastore needs a storage mapping to a StorageClass; capacity on the target is a storage-team question |

## 2. Enable CBT for warm migration

From `Modules/Set-CBT` (read from the code): it sets `ChangeTrackingEnabled` with a `VirtualMachineConfigSpec` through
`ReconfigVM`, and on a **running** VM creates and immediately removes a snapshot so the change takes effect; it **skips
VMs that already have snapshots**. Equivalent, with a dry run:

```powershell
$vm   = Get-VM '<vm>'
if ($vm.ExtensionData.Snapshot) { Write-Warning "<vm> has snapshots — remove them first"; return }
if (-not $vm.ExtensionData.Config.ChangeTrackingEnabled) {
    if ($PSCmdlet.ShouldProcess($vm.Name, 'enable CBT')) {          # inside a function with SupportsShouldProcess
        $spec = New-Object VMware.Vim.VirtualMachineConfigSpec
        $spec.ChangeTrackingEnabled = $true
        $vm.ExtensionData.ReconfigVM($spec)
        if ($vm.PowerState -eq 'PoweredOn') {
            New-Snapshot -VM $vm -Name 'cbt-enable' | Remove-Snapshot -Confirm:$false
        }
    }
}
```

That snapshot/remove cycle is a short stun on the VM — do it in a window for sensitive workloads. Backup tools also
use CBT; enabling it is normally harmless, but tell the backup owners (`interfaces/ocp-storage-backup.md`).

## 3. Before cutover

- Re-run the inventory: no new snapshots, Tools running, VM still on the planned datastores.
- Record MAC addresses if the guest or the network depends on them (MTV can preserve them — hypothesis, check the plan option).
- After cutover the VMware VM stays powered off as the rollback path until the owner signs off.

## History

- 2026-11-02: created
