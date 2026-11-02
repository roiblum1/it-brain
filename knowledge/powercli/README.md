# Area `powercli`

PowerShell and VMware PowerCLI: connecting to vCenter, the object model (cmdlets vs `Get-View`), inventory and
reports, VM / host / datastore / vDS operations, credentials, offline install in the air gap, and scripts for
OpenShift on vSphere and for VMware → KubeVirt migrations.

- **Owner (approves MRs):** Virtualization team (`virtualization`)
- **Consulted:** `ocp`
- **Domain:** hypervisors (`virtualization`)

## Page map

| Page | What it answers |
|---|---|
| `knowledge/powercli/powershell-essentials-objects-pipeline-errors-for-infra-engineers.md` | PowerShell for people who know bash: objects, pipeline, hashtables, splatting, errors that `try/catch` does *not* catch, PS 7 on Linux vs 5.1 |
| `knowledge/powercli/powercli-offline-install-air-gap-save-module-psmodulepath.md` | getting PowerCLI (and pwsh) onto an air-gapped jump host; module names; version pinning |
| `knowledge/powercli/powercli-connect-viserver-certificates-multiple-vcenters.md` | `Connect-VIServer`, the internal CA, `InvalidCertificateAction`, Single vs Multiple server mode, timeouts |
| `knowledge/powercli/powercli-credentials-secretmanagement-never-plaintext.md` | where vCenter credentials may live (SecretManagement / SecretStore), what never to do |
| `knowledge/powercli/powercli-object-model-get-view-extensiondata-performance-at-scale.md` | why scripts are slow on big vCenters and how `Get-View -Property -Filter` fixes it |
| `knowledge/powercli/powercli-inventory-reporting-vms-hosts-datastores-snapshots-tools.md` | report patterns: VMs, hosts, datastores, old snapshots, VMware Tools, CSV / JSON output |
| `knowledge/powercli/powercli-vm-and-host-operations-snapshots-maintenance-esxcli.md` | power, snapshots, hardware and advanced settings, maintenance mode, `Get-EsxCli -V2` |
| `knowledge/powercli/powercli-storage-and-networking-datastores-spbm-vds-portgroups-vlans.md` | datastores, storage policies (SPBM), vDS / port groups / VLANs — and the team seams |
| `knowledge/powercli/powercli-tags-privileges-and-preflight-for-openshift-on-vsphere.md` | tag categories for OpenShift zones / regions, roles and privileges, `disk.EnableUUID`, pre-install checks |
| `knowledge/powercli/powercli-mtv-migration-prep-vmware-to-kubevirt-cbt-tools-inventory.md` | preparing VMs for MTV (VMware → OpenShift Virtualization): inventory, CBT for warm migration, Tools, snapshots |
| `knowledge/powercli/powercli-script-quality-shouldprocess-whatif-pester-scriptanalyzer.md` | how our scripts are written: parameters, `-WhatIf`, idempotency, logging, PSScriptAnalyzer, Pester |

Runbooks: `runbooks/powercli/install-powercli-offline-in-the-air-gap.md`,
`runbooks/powercli/connect-powercli-to-vcenter-with-the-internal-ca.md`,
`runbooks/powercli/find-old-vm-snapshots-across-vcenters.md`,
`runbooks/powercli/put-an-esxi-host-into-maintenance-mode-safely.md`,
`runbooks/powercli/preflight-check-vsphere-for-an-openshift-install.md`.

## Belongs here

How to *drive* vSphere from PowerShell: cmdlet behaviour and quirks, performance of PowerCLI scripts, the
object model, module installation and versions, credential handling, script conventions, and the scripts we
run (inventory, maintenance, OpenShift pre-flight, migration prep).

## Not here

- How vSphere itself behaves (DRS, HA, vSAN, NSX, vMotion rules) → `vmware` (`knowledge/vmware/README.md`).
- OpenShift running on vSphere — installer, machine API, vSphere CSI from the cluster side → `vsphere` (`knowledge/vsphere/README.md`).
- KubeVirt / OpenShift Virtualization and MTV itself → `kubevirt` (`knowledge/kubevirt/README.md`).
- Who provides which VLAN / datastore → the interface pages (`interfaces/storage-network-data-paths.md`, `interfaces/ocp-network-aci-fabric.md`).

## Offline sources

Planned snapshots (none fetched yet; status in `docs/it-brain/SOURCES-PLAN.md`):

| Name | Repo / paths | Licence | Notes |
|---|---|---|---|
| `powershell-docs` | `MicrosoftDocs/PowerShell-Docs` — `reference/docs-conceptual` and `reference/<LTS>/Microsoft.PowerShell.Core/About` | docs CC BY 4.0 (`LICENSE.md`), code samples MIT (`LICENSE-CODE.md`) | `about_*` topics, deep dives (exceptions, ShouldProcess, PSCustomObject, hashtables), Linux install, 5.1 vs 7 differences |
| `powercli-examples` | `vmware/PowerCLI-Example-Scripts` — `Modules`, `Scripts`, `Pester`, `README.md` | BSD-2-Clause (`LICENSE.txt`) | real usage patterns (`Get-View -Property -Filter`, `Get-EsxCli -V2`, VISecret, Set-CBT, VMToolsManagement) |

The **PowerCLI cmdlet reference** is not in any public git repository (checked 2026-11-02): it lives on
Broadcom's developer portal → **vendor-drop** (`docs/it-brain/SOURCES-PLAN.md` §C). Until then, `Get-Help <cmdlet> -Full`
on the jump host is the reference for the version actually installed.

## Redact

Use `<vcenter>`, `<esxi>`, `<datastore>`, `<vds>`, `<vm>`, `<cluster>` (vSphere cluster too), `<site>`, `<ip>`;
SSO domains and service accounts → `<sso-domain>`, `<svc-account>`. **Never** a password, a credential file, a
SecretStore export or a session ticket — not even "temporarily" in a script committed anywhere. General rules: `CLAUDE.md`,
placeholders: `teams.json`.

## First pages we want

- Our jump hosts: which pwsh and PowerCLI versions are installed and where the module share lives (a row in `knowledge/meta/fleet-versions.md`).
- The service account and role our read-only reports use, and which vCenters they cover.

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
