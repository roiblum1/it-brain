---
title: it-brain teams guide — what the OCP, storage and network teams each get, own and review
type: reference
area: meta
tags: [it-brain, teams, onboarding, ownership, review, codeowners, storage, network, ocp]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp]
source: it-brain-design
---

# it-brain teams guide

Registry: `teams.json` (`python3 scripts/brain.py teams` prints it). Architecture: `docs/it-brain/ARCHITECTURE.md`.

## Every team

**Cross-team problems** (a PowerFlex volume on OpenShift, a VM disk on Trident, cluster egress through the
firewall): Claude calls `route` first, reads the interface page it names and uses the `it-triage` skill, so the
answer uses every team's pages and says which side the evidence points to (`docs/it-brain/ARCHITECTURE.md` §1.1).

- **Search before you write**, across everything — the answer to a storage question is often on an OCP page.
- **Write in your areas**; for anything that spans teams, write or update the `interfaces/` page instead of
  copying the same facts into two areas.
- **Review MRs in your areas** (CODEOWNERS sends them to you). When a page lists your team in `teams:` or touches an
  area where you are *consulted*, the author @-mentions your group in the MR description; reply there.
- **Interface pages need an approval from every team in `teams:`** (a review rule, not enforced by CODEOWNERS).
- **Curate your share** monthly: `python3 scripts/brain.py stale --team <team> --days 180` and the `inbox/` items in your areas.
- Same rules for everyone: frontmatter, `confidence`, `applies_to`, no secrets, no real names (`CLAUDE.md`).

Set `export IT_BRAIN_TEAM=<ocp|storage|network|virtualization>` in your shell profile so Claude starts with your team's areas.
To browse instead of search: `python3 scripts/brain_graph.py obsidian --out ~/it-brain-vault` and open it in
Obsidian (`docs/it-brain/GRAPH.md`) — your team's hub note lists your areas and interfaces.

## ocp — OpenShift Container Platform

| | |
|---|---|
| Owns | openshift, kubernetes, hypershift, baremetal, vsphere, networking (cluster side), storage (cluster side), gpu, observability, registry-mirroring, gitops, security, oadp†; our platform tools **server-scan** and **temporal** (Redbull Workflows); prefect†, airflow†, spark†, elastic†, solr†, mongodb† (on Kubernetes and VMs); python (Pydantic) |
| Consulted on | trident, dell-*, odf, smb-cifs, commvault, cisco-aci, palo-alto |
| Sources | everything team-brain has today, plus RHOKP for ODF / OADP |
| Live tools | Kubernetes MCP, Grafana MCP (exist) |
| Interfaces | all seven in `interfaces/` |

Also maintains the brain's tooling (scripts, plugin, CI, shared deployment) until another team co-owns it.

## storage

| | |
|---|---|
| Owns | netapp-ontap, trident, dell-powermax, dell-powerflex, dell-powerscale, ceph, odf†, smb-cifs, commvault† |
| Consulted on | storage (cluster side), oadp, security, vmware, nutanix |
| Sources (planned) | ONTAP and Trident docs, Dell CSM docs, Ceph docs, Rook / ODF, SMB CSI; vendor-drop for licensed manuals (`docs/it-brain/SOURCES-PLAN.md`) |
| Live tools (planned) | `ontap-mcp --read-only` first; Dell / Ceph / Commvault read-only later (`docs/it-brain/TOOLS-PLAN.md`) |
| Interfaces | `ocp-storage-netapp-trident`, `ocp-storage-dell-csm`, `ocp-storage-object-s3`, `ocp-storage-backup`, `storage-network-data-paths`, `ocp-network-palo-alto-flows` (storage flows) |

First pages that would pay off: SVM / export-policy convention for clusters, the array ↔ CSI driver ↔ OCP support
rows in `knowledge/meta/fleet-versions.md`, S3 endpoint and CA conventions.

## virtualization

| | |
|---|---|
| Owns | **kubevirt** (OpenShift Virtualization — deep dive), vmware, nutanix, **powercli** (PowerShell / PowerCLI deep dive) |
| Consulted on | vsphere (OpenShift on vSphere) |
| Sources | `kubevirt-user-guide`, `kubevirt-docs`, `cdi-docs`, `hco-docs`, `forklift-docs` (MTV), `powershell-docs`, `powercli-examples` (snapshots, in the repo); RHOKP for OpenShift Virtualization |
| Live tools | the Kubernetes MCP's `kubevirt` toolset (`vm_troubleshoot`, `vm_guest_info`, `vm_lifecycle` …); Nutanix MCP evaluated |
| Interfaces | `virtualization-storage-kubevirt-vm-disks`, `virtualization-network-kubevirt-vm-networks`, `ocp-virtualization-kubevirt-platform` |

## network

| | |
|---|---|
| Owns | cisco-aci, palo-alto |
| Consulted on | networking (cluster side), security, vmware, nutanix |
| Sources (planned) | Palo Alto pan.dev (API / automation), ACI CNI repo if used; vendor-drop for PAN-OS and APIC guides |
| Live tools (planned) | APIC read-only, PAN-OS / Panorama read-only |
| Interfaces | `ocp-network-aci-fabric`, `ocp-network-palo-alto-flows`, `storage-network-data-paths` |

First pages that would pay off: the EPG / BD layout for an OpenShift cluster, the per-cluster flow table filled
in, endpoint-learning settings for bridge domains that carry VIPs.

† provisional owner — see `docs/it-brain/ROADMAP.md`.

## Onboarding a new engineer (any team)

1. Clone and install the plugin (`README.md` → Setup) **or** use the shared server (`mcp/README.md`), which is the
   easier path for teams without a local Python/git setup.
2. `export IT_BRAIN_TEAM=<team>`.
3. Ask Claude to look something up in your area; check that `brain` and your planned sources answer.
4. Write your first page from `templates/` through `/team-brain:brain-learn` — it opens the MR for you.

## History

- 2026-11-02: created
