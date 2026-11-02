---
title: PowerCLI script quality — advanced functions, parameter validation, SupportsShouldProcess / -WhatIf / ConfirmImpact, idempotency, logging, PSScriptAnalyzer and Pester
type: knowledge
area: powercli
tags: [powercli, powershell, shouldprocess, whatif, confirm, cmdletbinding, parameter-validation, idempotency, pester, psscriptanalyzer, logging, transcript]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: MicrosoftDocs/PowerShell-Docs (about_Functions_CmdletBindingAttribute, about_Requires, about_CommonParameters, deep dive everything-about-shouldprocess); vmware/PowerCLI-Example-Scripts (CmdletBinding + ValidateNotNullorEmpty + ParameterSetName in Modules/Set-CBT; Pester/ folder)
---

# How we write PowerCLI scripts

A script that changes vSphere can move hundreds of VMs in a second. These conventions make every such script
dry-runnable, repeatable and reviewable. Language basics: `knowledge/powercli/powershell-essentials-objects-pipeline-errors-for-infra-engineers.md`.

## Skeleton

```powershell
#Requires -Version 7.0
#Requires -Modules VMware.VimAutomation.Core
function Set-OurVmTag {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [ValidateNotNullOrEmpty()]
        [VMware.VimAutomation.ViCore.Types.V1.Inventory.VirtualMachine[]] $VM,

        [Parameter(Mandatory)]
        [ValidateSet('<zone-a>', '<zone-b>')]
        [string] $Zone,

        [Parameter(Mandatory)]
        [VMware.VimAutomation.ViCore.Types.V1.VIServer] $Server
    )
    begin   { $ErrorActionPreference = 'Stop' }
    process {
        foreach ($v in $VM) {
            $have = Get-TagAssignment -Entity $v -Category openshift-zone -Server $Server
            if ($have.Tag.Name -eq $Zone) { Write-Verbose "$($v.Name): already $Zone"; continue }   # idempotent
            if ($PSCmdlet.ShouldProcess($v.Name, "tag zone $Zone")) {
                New-TagAssignment -Entity $v -Tag $Zone -Server $Server | Out-Null
            }
        }
    }
}
```

- `#Requires` (`about_Requires`) fails fast when the module or PowerShell version is missing.
- `[CmdletBinding()]` gives the common parameters (`-Verbose`, `-ErrorAction`, `-WhatIf`, `-Confirm` with
  `SupportsShouldProcess` — `about_CommonParameters`, `about_Functions_CmdletBindingAttribute`).
- Validation attributes (`ValidateNotNullOrEmpty`, `ValidateSet`, `ValidatePattern`, `ValidateRange`) reject bad input
  before anything runs — the `Set-CBT` example uses `ValidateNotNullorEmpty` and parameter sets for mutually exclusive
  switches (`-EnableCBT` / `-DisableCBT`).
- Typed parameters: the type names of PowerCLI objects differ between versions (the `Set-CBT` example uses the older
  `…Impl.V1.Inventory.InventoryItemImpl`); `…Types.V1.…` interfaces are the stable choice (hypothesis — check with
  `$vm.GetType()` / `Get-Member`).

## `-WhatIf` and `-Confirm` (ShouldProcess)

From the deep dive *everything-about-shouldprocess*: commands that support `-WhatIf` show what they would do
without doing it, and support `-Confirm` too. In your own function, wrap **every** state change in
`if ($PSCmdlet.ShouldProcess(<target>, <action>)) { … }`; then `-WhatIf` on your function propagates to
PowerCLI cmdlets inside that honour it.

- `ConfirmImpact = 'High'` makes PowerShell prompt by default (`$ConfirmPreference` is High): use it for deletes,
  power-offs, host maintenance.
- Never put `-Confirm:$false` inside the function on destructive cmdlets "to avoid prompts"; let the caller decide.
- Our rule (`knowledge/powercli/README.md`): the first run of any change script in production is with `-WhatIf`,
  and its output goes in the change ticket.

## Idempotency

Check, then change, then don't care how many times it runs: compare current state first (tag already set, setting
already `TRUE`, host already in maintenance) and `continue`. Re-running after a partial failure must be safe.

## Logging

- `Start-Transcript -Path <log>` captures the session; **transcripts capture everything printed** — never print secrets
  (`knowledge/powercli/powercli-credentials-secretmanagement-never-plaintext.md`).
- Emit result objects (what was changed, before / after) and export them; a CSV of changes is the best audit trail.

## Static analysis and tests

- **PSScriptAnalyzer** (`Invoke-ScriptAnalyzer -Path <script> -Recurse`) catches common mistakes (unapproved verbs,
  `Write-Host`, plaintext password parameters, missing ShouldProcess on state-changing verbs). Run it in CI for the
  scripts repo; both modules must be mirrored offline like PowerCLI
  (`knowledge/powercli/powercli-offline-install-air-gap-save-module-psmodulepath.md`).
- **Pester** (`Invoke-Pester`) for tests; mock PowerCLI cmdlets (`Mock Get-VM { … }`) so tests run without vCenter.
  The VMware examples repo keeps its tests in `Pester/`.

## Modules, not script piles

Group functions into a module (`.psm1` + manifest `.psd1` via `New-ModuleManifest`), version it, ship it the same way as
PowerCLI. Scripts in git, never with credentials or real names in defaults.

## History

- 2026-11-02: created
