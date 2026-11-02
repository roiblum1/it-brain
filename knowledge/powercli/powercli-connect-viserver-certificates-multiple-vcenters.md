---
title: PowerCLI Connect-VIServer — internal CA certificates, InvalidCertificateAction, DefaultVIServerMode Single vs Multiple, $global:DefaultVIServers, timeouts
type: knowledge
area: powercli
tags: [powercli, connect-viserver, certificate, tls, ca, invalidcertificateaction, defaultviservermode, multiple-vcenters, session, timeout]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: vmware/PowerCLI-Example-Scripts (Set-PowerCLIConfiguration -DefaultVIServerMode Multiple -Scope Session; VISecret Connect-VIServerWithSecret); cmdlet behaviour from general PowerCLI knowledge — check Get-Help Connect-VIServer -Full
---

# Connecting: Connect-VIServer, certificates, many vCenters

Procedure: `runbooks/powercli/connect-powercli-to-vcenter-with-the-internal-ca.md`.

## The connection

```powershell
$vc = Connect-VIServer -Server '<vcenter>' -Credential $viCred -ErrorAction Stop
$vc | Select-Object Name, Version, Build, User, IsConnected
```

`Connect-VIServer` returns a server object and records it in `$global:DefaultVIServer` (the default target) and
`$global:DefaultVIServers` (all connected). Every inventory cmdlet without `-Server` runs against the default
server(s). Credentials: never `-User`/`-Password` literals — `knowledge/powercli/powercli-credentials-secretmanagement-never-plaintext.md`.
Close what you open: `Disconnect-VIServer -Server $vc -Confirm:$false`.

## Certificates — trust the internal CA, don't ignore it

vCenters are signed by our internal CA (or still by the VMCA). PowerCLI's behaviour on an untrusted certificate is
controlled by `Set-PowerCLIConfiguration -InvalidCertificateAction <Fail|Warn|Ignore|Prompt|Unset>`.

- The VMware example scripts use `-InvalidCertificateAction Ignore` in one place — **don't copy that**: it
  accepts any certificate, including a man-in-the-middle's, while you send vCenter credentials.
- Do this instead: make the OS trust the CA, then leave the action at `Fail`.
  - RHEL jump host (pwsh 7 uses the system trust store through .NET/OpenSSL): copy the CA to
    `/etc/pki/ca-trust/source/anchors/` and run `update-ca-trust`.
  - Windows: import the CA into *Trusted Root Certification Authorities* (machine store) via GPO or `Import-Certificate`.
  - If vCenter still uses its own VMCA root, trust *that* root (download it from vCenter's landing page
    "Download trusted root CA certificates") rather than ignoring errors.
- `-Scope Session` changes the setting for this session only; `User` / `AllUsers` persist it. Persisted `Ignore`
  is the dangerous one — check with `Get-PowerCLIConfiguration`.

## One vCenter or many

`Set-PowerCLIConfiguration -DefaultVIServerMode Single|Multiple` decides what "the default server" is:

| Mode | Effect | Risk |
|---|---|---|
| `Single` | only the last connected server is the default | scripts that connect in a loop act on the **last** vCenter only |
| `Multiple` | every connected server is a default; `Get-VM` returns VMs from all of them | a write without `-Server` hits **all** connected vCenters |

The VMware cross-vCenter examples set `-DefaultVIServerMode Multiple -Scope Session` for reports across vCenters.
Our rule: reports may use `Multiple`; **anything that changes state passes `-Server` explicitly** and checks
`$global:DefaultVIServers.Count` first. Each returned object knows its vCenter:
`$vm.Uid` contains the server, and most objects can be piped onward without losing it.

Linked mode: `Connect-VIServer -AllLinked` connects to every vCenter in the SSO link group at once (parameter used
by the VISecret example). Handy for reports, same write rule.

## Timeouts and sessions

- Long operations (large reports, `Get-Stat` over months) can exceed the web operation timeout:
  `Set-PowerCLIConfiguration -WebOperationTimeoutSeconds <n> -Scope Session` (hypothesis — check the parameter on your version).
- vCenter sessions expire when idle; long-running scripts should reconnect on failure instead of assuming the
  session still exists. `$vc.IsConnected` tells you.
- Service accounts for scheduled reports need a vCenter role with only `System.View` / read privileges on the
  objects they report on — see `knowledge/powercli/powercli-tags-privileges-and-preflight-for-openshift-on-vsphere.md`.

## Symptoms

| Symptom | Likely cause | Fix |
|---|---|---|
| `Invalid server certificate. Use Set-PowerCLIConfiguration to set the value for the InvalidCertificateAction option…` | CA not trusted by the OS | trust the CA (above); don't set `Ignore` |
| cmdlets return objects from the wrong vCenter | leftover connection in `$global:DefaultVIServers` (Multiple mode) | `Disconnect-VIServer * -Confirm:$false`, reconnect, pass `-Server` |
| script ran against one vCenter only | Single mode + loop of connects | `Multiple` mode for reports, or loop with explicit `-Server $vc` |
| `The underlying connection was closed` mid-report | session timeout / web operation timeout | raise timeout, reconnect logic |

## History

- 2026-11-02: created
