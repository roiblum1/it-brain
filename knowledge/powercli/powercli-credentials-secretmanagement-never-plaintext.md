---
title: PowerCLI credentials — Get-Credential and SecretManagement / SecretStore, never plaintext passwords in scripts, CSV, git or the VICredentialStore file
type: knowledge
area: powercli
tags: [powercli, credentials, secretmanagement, secretstore, pscredential, securestring, vicredentialstore, visecret, security]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: vmware/PowerCLI-Example-Scripts Modules/VISecret (README.md, VMware.VISecret.psm1); MicrosoftDocs/PowerShell-Docs docs-conceptual/learn/deep-dives/add-credentials-to-powershell-functions.md
---

# PowerCLI credentials

Same rule as everywhere in the brain (`CLAUDE.md`): no password, token or credential file goes into a page, a
script in git, a CSV, a scheduled-task argument or a chat. This page is how to do it right instead.

## Interactive: `Get-Credential`

```powershell
$viCred = Get-Credential -Message 'vCenter account for <vcenter>'
Connect-VIServer -Server '<vcenter>' -Credential $viCred
```

A `PSCredential` holds the password as a `SecureString`. Functions you write should take a
`[pscredential]` parameter, not a string password (deep dive *add-credentials-to-powershell-functions*, which also
warns that `ConvertTo-SecureString -AsPlainText` puts the plain text into logs and history).

## Stored: SecretManagement + SecretStore

Microsoft's `Microsoft.PowerShell.SecretManagement` (the API) with a vault extension — locally
`Microsoft.PowerShell.SecretStore` — is the supported way to keep credentials for unattended scripts. VMware's
example module `VMware.VISecret` (`vmware/PowerCLI-Example-Scripts/Modules/VISecret`, PS 5.1 and 7) wraps it for
PowerCLI:

- `Initialize-VISecret` registers a vault (default name `VMwareSecretStore`) as the default vault;
- `New-VISecret -Server <vcenter> -User <svc-account>` saves a credential under the secret name `VISecret|<server>|<user>`;
- `Connect-VIServerWithSecret -Server <vcenter> -User <svc-account>` reads it with `Get-Secret` and splats it into `Connect-VIServer`.

**Caveat read from the code:** `Initialize-VISecret` runs
`Set-SecretStoreConfiguration -Scope CurrentUser -Authentication None -Interaction None` — the store is then
protected only by the OS user's file permissions, with no store password. That is a reasonable trade-off for a
dedicated service user on a locked-down jump host, and a bad one on a shared account. Decide per host; prefer an
enterprise vault extension (if we have one) over a local store for production automation.

Usage pattern (no password ever typed into the script):

```powershell
Import-Module Microsoft.PowerShell.SecretManagement
$viCred = Get-Secret -Name 'vc-<site>-reports' -Vault '<vault>' -ErrorAction Stop    # returns a PSCredential if stored as one
Connect-VIServer -Server '<vcenter>' -Credential $viCred -ErrorAction Stop
```

## Things not to do

| Don't | Why | Instead |
|---|---|---|
| `-User x -Password y` in a script or scheduled task | plaintext in git, process list, history, task XML | `-Credential` from SecretManagement |
| `ConvertTo-SecureString -AsPlainText` with a literal | the literal is still in the file and in logs | `Get-Credential` once → vault |
| `Export-Clixml` credentials and copy the file to other hosts | DPAPI-protected on Windows only, tied to user + machine; on Linux the content is **not** encrypted (hypothesis — verify on your pwsh) | vault per host |
| `New-VICredentialStoreItem` / `-SaveCredentials` (PowerCLI's own credential store file) | an old mechanism; how well the file is protected depends on the platform (hypothesis) — and it hides which credential a script uses | SecretManagement, which also works the same on PS 5.1 and 7 |
| put credentials in `$PROFILE` | every session, every child process | vault lookup in the script that needs it |
| print `$viCred.GetNetworkCredential().Password` "to debug" | it is now in your terminal scrollback and maybe a transcript | test the connection instead |

## Least privilege

Report scripts use a read-only vCenter role; scripts that change state use a separate account whose role covers
only the objects they touch. Roles and privileges: `knowledge/powercli/powercli-tags-privileges-and-preflight-for-openshift-on-vsphere.md`.

## History

- 2026-11-02: created
