---
title: Install PowerShell 7 and PowerCLI offline on an air-gapped jump host (Save-Module, copy, PSModulePath, CEIP off)
type: runbook
area: powercli
tags: [powercli, pwsh, install, offline, air-gap, save-module, psmodulepath]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: MicrosoftDocs/PowerShell-Docs (install-rhel.md, about_PSModulePath); background in knowledge/powercli/powercli-offline-install-air-gap-save-module-psmodulepath.md
---

# Install PowerShell 7 and PowerCLI offline

**When to use:** a new jump host, or moving all jump hosts to a new PowerCLI version.
**Impact while running:** none on vSphere; users of the jump host should not run scripts during the swap.
**Prerequisites:** a connected staging host with pwsh 7 and internet access; the agreed versions (from
`knowledge/meta/fleet-versions.md`); a way to move files into the air gap; root / admin on the jump host.
Background: `knowledge/powercli/powercli-offline-install-air-gap-save-module-psmodulepath.md`.

## Pre-checks

```bash
pwsh -NoLogo -Command '$PSVersionTable.PSVersion; Get-Module -ListAvailable VMware.*,VCF.* | Select Name, Version, Path'
```

Decide the meta-module name for the target version (`VMware.PowerCLI` or `VCF.PowerCLI`) — don't install both.

## Procedure

1. **Connected host — fetch PowerShell** (RHEL jump hosts): download the RHEL `.rpm` for the chosen LTS release
   from PowerShell's GitHub releases (URL pattern in `install-rhel.md`) and record its sha256.
2. **Connected host — fetch PowerCLI and helpers:**
   ```powershell
   $v = '<powercli-version>'
   New-Item -ItemType Directory ./powercli-$v | Out-Null
   Save-Module -Name VMware.PowerCLI -RequiredVersion $v -Path ./powercli-$v
   Save-Module -Name Microsoft.PowerShell.SecretManagement, Microsoft.PowerShell.SecretStore -Path ./powercli-$v
   Save-Module -Name PSScriptAnalyzer, Pester -Path ./powercli-$v          # for the scripts repo CI
   Get-ChildItem ./powercli-$v | Select-Object Name                        # one folder per module
   ```
   Archive the folder (`tar czf powercli-$v.tgz powercli-$v`) and record its sha256.
3. **Transfer** both artifacts through the approved path; verify the sha256 on arrival.
4. **Jump host — install pwsh:** `sudo dnf install ./powershell-<version>.rh.x86_64.rpm`.
5. **Jump host — install modules for all users:**
   ```bash
   sudo tar xzf powercli-<version>.tgz -C /tmp
   sudo cp -r /tmp/powercli-<version>/* /usr/local/share/powershell/Modules/
   ```
   Remove an older PowerCLI from the same path first if you are upgrading (keep the archive to roll back).
6. **Trust the internal CA** if not done yet: `runbooks/powercli/connect-powercli-to-vcenter-with-the-internal-ca.md` step 1.
7. **Disable CEIP for everyone** (no telemetry endpoint exists in the air gap):
   ```bash
   sudo pwsh -NoLogo -Command 'Import-Module VMware.VimAutomation.Core; Set-PowerCLIConfiguration -Scope AllUsers -ParticipateInCEIP $false -Confirm:$false'
   ```

## Verification

```bash
pwsh -NoLogo -Command 'Get-Module -ListAvailable VMware.VimAutomation.Core | Select Name, Version, Path; Get-PowerCLIConfiguration'
```

Exactly one version, loaded from `/usr/local/share/powershell/Modules`; `InvalidCertificateAction` not `Ignore`.
Then connect read-only to one vCenter (`runbooks/powercli/connect-powercli-to-vcenter-with-the-internal-ca.md`).
Record the installed versions in `knowledge/meta/fleet-versions.md`.

## Rollback

Remove the new module folders from `/usr/local/share/powershell/Modules/` and copy back the previous archive;
`sudo dnf downgrade` / reinstall the previous pwsh RPM.

## History

- 2026-11-02: created
