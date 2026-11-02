---
title: PowerShell essentials for infra engineers — objects not text, pipeline, hashtables, splatting, and errors try/catch does not catch without -ErrorAction Stop
type: knowledge
area: powercli
tags: [powershell, pwsh, pipeline, pscustomobject, splatting, hashtable, error-handling, erroractionpreference, try-catch]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: MicrosoftDocs/PowerShell-Docs reference/7.4/Microsoft.PowerShell.Core/About (about_Pipelines, about_Try_Catch_Finally, about_Preference_Variables, about_Splatting, about_PSCustomObject, about_PSModulePath) and docs-conceptual/learn/deep-dives
---

# PowerShell essentials for infra engineers

Written for people who know bash and `oc`. Every PowerCLI page in this area assumes these basics; most
"PowerCLI bugs" we see are PowerShell misunderstandings. Read from Microsoft's PowerShell docs
(`about_*` topics and the *deep dives*); planned offline snapshot `powershell-docs` (`knowledge/powercli/README.md`).

## 1. Objects, not text

Commands emit **.NET objects**, and the pipeline passes objects, not lines (`about_Pipelines`). Never parse
the formatted table that `Get-VM` prints — select the property:

```powershell
Get-VM | Where-Object PowerState -eq 'PoweredOn' | Select-Object Name, NumCpu, MemoryGB
Get-VM | Get-Member                         # what properties / methods the objects really have
```

- `Format-Table` / `Format-List` are for **screens only** — after a `Format-*` you no longer have the objects.
  Put them last, or not at all in scripts. For files use `Export-Csv -NoTypeInformation` or `ConvertTo-Json -Depth N`.
- `Select-Object` with a calculated property: `@{Name='DiskGB'; Expression={ $_.ProvisionedSpaceGB }}`.
- `ForEach-Object` (pipeline, streams one at a time) vs `foreach ($x in $list)` (statement, loads the list first,
  usually faster). `ForEach-Object -Parallel` exists only in PowerShell 7 — and PowerCLI connection objects are not
  automatically shared into parallel runspaces (hypothesis: test before you rely on it; pass `-Server` explicitly).

## 2. Build your own objects

`[pscustomobject]` is the way to emit report rows (`about_PSCustomObject`, deep dive *everything-about-pscustomobject*):

```powershell
[pscustomobject]@{
    VM        = $vm.Name
    Host      = $vm.VMHost.Name
    ToolsOk   = $vm.ExtensionData.Guest.ToolsRunningStatus -eq 'guestToolsRunning'
}
```

Property order is kept, it pipes into `Export-Csv`, `ConvertTo-Json` and `Sort-Object` like any object.

## 3. Hashtables and splatting

A hashtable `@{ Key = 'value' }` is also how you pass many parameters at once — **splatting** with `@`
instead of `$` (`about_Splatting`):

```powershell
$params = @{
    Server      = '<vcenter>'
    Credential  = $viCred
    ErrorAction = 'Stop'
}
Connect-VIServer @params
```

Splatting keeps long cmdlet calls readable and lets you add parameters conditionally
(`if ($Port) { $params.Port = $Port }`) — the pattern the VMware example modules use (`Connect-VIServerWithSecret`
in `vmware/PowerCLI-Example-Scripts/Modules/VISecret`).

## 4. Errors: the trap that bites every new script

PowerShell has **non-terminating** errors (the cmdlet writes an error and *keeps going*) and **terminating**
errors. `try/catch` only catches terminating ones (`about_Try_Catch_Finally`). Most cmdlet failures — a VM not
found, one host unreachable — are non-terminating, so this does **not** do what it looks like:

```powershell
try { Get-VM -Name '<vm>' } catch { Write-Warning 'never reached for a missing VM' }
```

Make the error terminating with `-ErrorAction Stop` (per call) or `$ErrorActionPreference = 'Stop'` (whole
script, `about_Preference_Variables`; the deep dive *everything-about-exceptions* names `-ErrorAction Stop`
escalation as one of the ways a terminating error is produced):

```powershell
$ErrorActionPreference = 'Stop'          # at the top of every script that changes anything
try {
    $vm = Get-VM -Name '<vm>'
} catch {
    Write-Error "VM <vm> not found: $($_.Exception.Message)"
    return
}
```

- Inside `catch`, `$_` is the `ErrorRecord`; `$_.Exception.Message` is the text, `$_.CategoryInfo` the category.
- `-ErrorAction SilentlyContinue` hides errors — fine for "does it exist?" probes, never for writes.
- `$?` and `$LASTEXITCODE` are for native commands (`esxcli` over SSH, `oc`), not for cmdlets.

## 5. Output streams and verbosity

`Write-Output` is the data stream (what the pipeline and `$x = …` capture). Use `Write-Verbose` (shown with
`-Verbose`), `Write-Warning`, `Write-Error` and `Write-Information` for messages — **not** `Write-Host` in
functions whose output is captured, and never `Write-Output` for log lines (they become part of the result).

## 6. PowerShell 7 on Linux vs Windows PowerShell 5.1

From *Differences between Windows PowerShell 5.1 and PowerShell 7.x* (`docs-conceptual/whats-new`):

- 5.1 runs on .NET Framework (Windows only); 7.x on .NET (Core) and runs on Windows, macOS and Linux. The language
  barely differs; cmdlet availability and behaviour do (Windows-only modules, `-Parallel`, encoding defaults).
- On Linux, user modules live in `$HOME/.local/share/powershell/Modules` and machine-wide modules in
  `/usr/local/share/powershell/Modules` (`about_PSModulePath`) — this matters for the offline install
  (`knowledge/powercli/powercli-offline-install-air-gap-save-module-psmodulepath.md`).
- PowerShell 7 has LTS and stable releases; pick the LTS for jump hosts (*PowerShell Support Lifecycle*), and
  record the version we run in `knowledge/meta/fleet-versions.md`, not in pages.
- On RHEL, pwsh installs from Microsoft's `.rpm` (the docs give direct download URLs per release) — in the air
  gap, mirror the RPM rather than the repo config.

## 7. Small things that cost time

| Symptom | Cause |
|---|---|
| `if ($list -eq $null)` behaves oddly | put `$null` on the left: `$null -eq $list` (comparison against arrays filters) — deep dive *everything-about-null* |
| a function "returns" extra values | every uncaptured expression is output; assign or `[void]` it, or pipe to `Out-Null` |
| `-eq` is case-insensitive | yes, by default; use `-ceq` for case-sensitive |
| a variable assigned in a `ForEach-Object -Parallel` block is empty outside | runspaces don't share variables; return objects instead |
| a script works interactively, fails in a scheduled task | different profile, module path, execution policy (`about_Execution_Policies`) or no connected server — connect inside the script |

## Related

`knowledge/powercli/powercli-script-quality-shouldprocess-whatif-pester-scriptanalyzer.md` (how we structure scripts),
`knowledge/powercli/powercli-object-model-get-view-extensiondata-performance-at-scale.md` (objects at scale).

## History

- 2026-11-02: created
