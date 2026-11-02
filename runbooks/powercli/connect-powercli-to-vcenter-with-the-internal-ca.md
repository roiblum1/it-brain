---
title: Connect PowerCLI to vCenter with the internal CA trusted (no InvalidCertificateAction Ignore), credentials from SecretManagement
type: runbook
area: powercli
tags: [powercli, connect-viserver, certificate, ca, tls, secretmanagement, update-ca-trust]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: knowledge/powercli/powercli-connect-viserver-certificates-multiple-vcenters.md; vmware/PowerCLI-Example-Scripts Modules/VISecret
---

# Connect PowerCLI to vCenter with the internal CA

**When to use:** first connection from a new jump host, after a vCenter certificate change, or when you see
`Invalid server certificate`.
**Impact while running:** none (read-only connection).
**Prerequisites:** PowerCLI installed (`runbooks/powercli/install-powercli-offline-in-the-air-gap.md`); the internal
CA certificate (PEM) from the PKI owners or vCenter's "Download trusted root CA certificates" link; a vCenter account.
Background: `knowledge/powercli/powercli-connect-viserver-certificates-multiple-vcenters.md`,
`knowledge/powercli/powercli-credentials-secretmanagement-never-plaintext.md`.

## Pre-checks

```bash
openssl s_client -connect <vcenter>:443 -servername <vcenter> </dev/null 2>/dev/null | openssl x509 -noout -issuer -subject -enddate
pwsh -NoLogo -Command 'Get-PowerCLIConfiguration | Select Scope, InvalidCertificateAction, DefaultVIServerMode'
```

Note the issuer — that CA (or its root) is what must be trusted.

## Procedure

1. **Trust the CA on the OS** (RHEL jump host):
   ```bash
   sudo cp <internal-root-ca>.pem /etc/pki/ca-trust/source/anchors/
   sudo update-ca-trust
   openssl s_client -connect <vcenter>:443 -servername <vcenter> </dev/null 2>/dev/null | grep 'Verify return code'   # expect 0 (ok)
   ```
   Windows: import into *Trusted Root Certification Authorities* (Local Machine).
2. **Keep certificate checking strict** — undo any persisted `Ignore`:
   ```powershell
   Set-PowerCLIConfiguration -Scope User -InvalidCertificateAction Fail -Confirm:$false
   ```
3. **Store the credential once** (service account, unattended use) — interactive users skip this and use `Get-Credential`:
   ```powershell
   Import-Module Microsoft.PowerShell.SecretManagement
   Set-Secret -Name 'vc-<site>-reports' -Secret (Get-Credential -Message '<svc-account>') -Vault '<vault>'
   ```
4. **Connect:**
   ```powershell
   $viCred = Get-Secret -Name 'vc-<site>-reports' -Vault '<vault>'
   $vc = Connect-VIServer -Server '<vcenter>' -Credential $viCred -ErrorAction Stop
   ```

## Verification

```powershell
$vc | Select-Object Name, Version, Build, User, IsConnected
(Get-Datacenter -Server $vc).Name
Disconnect-VIServer -Server $vc -Confirm:$false
```

## Rollback

Nothing to roll back on vCenter. To remove the CA: delete it from `/etc/pki/ca-trust/source/anchors/` and run
`update-ca-trust`; `Remove-Secret -Name 'vc-<site>-reports' -Vault '<vault>'` removes the stored credential.

## History

- 2026-11-02: created
