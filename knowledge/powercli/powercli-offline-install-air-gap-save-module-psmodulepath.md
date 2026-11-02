---
title: PowerCLI offline install in the air gap — Save-Module on a connected host, copy to PSModulePath, pin versions, VMware.PowerCLI vs VCF.PowerCLI module names
type: knowledge
area: powercli
tags: [powercli, offline, air-gap, save-module, psmodulepath, install, powershellget, ceip, module-version]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: MicrosoftDocs/PowerShell-Docs about_PSModulePath and install-rhel; vmware/PowerCLI-Example-Scripts (#Requires lines); PowerCLI module naming from general knowledge — verify
---

# PowerCLI offline install (air gap)

The jump hosts cannot reach the PowerShell Gallery, so PowerCLI travels as files. Procedure:
`runbooks/powercli/install-powercli-offline-in-the-air-gap.md`. This page explains the parts.

## What "PowerCLI" is on disk

PowerCLI is a **set of modules** with one meta-module that depends on the rest. Scripts usually need only the core
one: the example scripts declare `#Requires -Modules VMware.VimAutomation.Core` (e.g.
`vmware/PowerCLI-Example-Scripts/Modules/Set-CBT/Set-CBT.psm1`). Other modules you meet: `VMware.VimAutomation.Vds`
(distributed switches), `VMware.VimAutomation.Storage` (SPBM / storage policies), `VMware.VimAutomation.Cis.Core`
(tags via the CIS/REST endpoint), `VMware.VimAutomation.Sdk` (shared).

**Module name changed (hypothesis — check before you fetch):** the classic meta-module is `VMware.PowerCLI`
(13.x line). Newer releases under Broadcom are published as **`VCF.PowerCLI`**. Decide which line the jump hosts
run, write it into `knowledge/meta/fleet-versions.md`, and use the same name everywhere (`Save-Module`,
`#Requires`, docs). Mixing both on one host gives duplicate cmdlets from two module sets.

## Moving modules across the air gap

On a connected host with the same OS family (PowerShellGet's `Save-Module`):

```powershell
Save-Module -Name VMware.PowerCLI -RequiredVersion <version> -Path ./powercli-<version>   # downloads it + all dependencies
```

`Save-Module` writes one folder per module and version (`<Module>/<version>/…`), which is exactly the layout
PowerShell loads from. Archive the folder, bring it across, and unpack it into a folder on `PSModulePath`:

| Scope | Linux (pwsh 7) | Windows PowerShell 5.1 / pwsh on Windows |
|---|---|---|
| one user | `$HOME/.local/share/powershell/Modules` | `$HOME\Documents\PowerShell\Modules` (7) / `…\WindowsPowerShell\Modules` (5.1) |
| all users | `/usr/local/share/powershell/Modules` | `$env:ProgramFiles\PowerShell\Modules` (7) / `…\WindowsPowerShell\Modules` (5.1) |

Linux paths from `about_PSModulePath`. Check what the current session searches: `$env:PSModulePath -split [IO.Path]::PathSeparator`.

Alternative: a shared **internal PSRepository** (a file share or an internal NuGet feed) registered with
`Register-PSRepository`; then `Install-Module -Repository <internal>` works inside the air gap. Better for many
jump hosts; same files.

## After copying

```powershell
Get-Module -ListAvailable VMware.VimAutomation.Core | Select-Object Name, Version, Path   # is it found, which version, from where
Import-Module VMware.VimAutomation.Core
Set-PowerCLIConfiguration -Scope AllUsers -ParticipateInCEIP $false -Confirm:$false        # no telemetry prompt (and nowhere to send it)
```

- Pin versions: keep exactly one PowerCLI version under the all-users path; a newer copy in a user's
  path silently wins for that user (first match on `PSModulePath`).
- On Windows, files copied from another machine may be blocked: `Get-ChildItem -Recurse <path> | Unblock-File`.
  Execution policy (`about_Execution_Policies`) can also refuse unsigned scripts; PowerCLI modules are signed.
- PowerShell 7 itself on RHEL: mirror the `.rpm` from PowerShell's GitHub releases (the RHEL install doc lists direct
  URLs) and install it with `dnf`.

## Why not `Install-Module` with a proxy

There is no proxy out of the air gap. Don't try to make one for this — the module set is small and changes a few
times a year.

## Related

`knowledge/powercli/powershell-essentials-objects-pipeline-errors-for-infra-engineers.md`,
`knowledge/powercli/powercli-connect-viserver-certificates-multiple-vcenters.md` (first thing to do after install).

## History

- 2026-11-02: created
