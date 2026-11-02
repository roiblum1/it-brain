---
title: it-brain architecture — one shared, offline brain for the OpenShift, storage and network teams
type: reference
area: meta
tags: [it-brain, architecture, teams, storage, network, ocp, design]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp]
source: it-brain-design
---

# it-brain architecture

**Status:** design, on branch `claude/it-brain-multi-team-n7n6kg` (not merged). Phase 0 of `docs/it-brain/ROADMAP.md`.
`confidence: hypothesis` because nothing here has run for the storage or network teams yet.

it-brain grows team-brain — the OpenShift team's offline memory — into one brain for three teams:

| Team | Estate (examples) |
|---|---|
| **ocp** — OpenShift Container Platform | hub / MCE / hosted / UPI clusters, GitOps, GPU nodes, OADP, cluster-side storage and networking |
| **storage** | NetApp ONTAP + Trident, Dell PowerMax / PowerFlex / PowerScale (Isilon), Ceph + S3 (RGW), ODF, SMB/CIFS, Commvault |
| **network** | Cisco ACI, Palo Alto firewalls / Panorama, the network side of storage and cluster connectivity |
| *ocp — our platform tools* | **server-scan** (our bare-metal inventory and management platform, `team-redbull/server-scan`), **Temporal** and the Redbull Workflows orchestrator built on it |
| *owner to confirm* | VMware (vCenter, ESXi, vSAN, NSX), Nutanix (AOS, AHV, Prism); Prefect, Airflow, Spark, ECK / Elastic, Solr, MongoDB — on Kubernetes and on VMs |

## 1. Why one brain and not three

Most hard outages in this estate cross a team boundary: a PVC stuck `Pending` is a Trident question for OCP, an
export-policy question for storage and sometimes a VLAN question for network. Three separate brains would each
hold one third of the answer. One brain gives:

- **one search** across every team's notes and every vendor's docs, ranked together;
- **interface pages** (`interfaces/`) — the contract at each seam, written once, approved by both sides;
- **one set of rules** for redaction, confidence and review, so a page from any team can be trusted the same way.

What stays separate per team: who **approves** pages in an area (`teams.json` → `.gitlab/CODEOWNERS`), what each
team's sessions are **told first** (team profile, §6), and which **live tools** a team may connect (§3.4).

## 2. Design principles (inherited from team-brain, extended)

1. **Air-gapped and offline-first.** Everything — search, docs, MCP servers — works without internet.
2. **Human-reviewed knowledge.** Every page arrives through a merge request; the owning team approves it.
3. **A wrong page is worse than a missing one.** Scope (`applies_to`), `confidence` and `last_verified` are mandatory.
4. **No secrets, no real locations.** Extended for storage and network identifiers (§5).
5. **Read-only by default for live systems.** Arrays and firewalls have a larger blast radius than one cluster:
   tools against them start read-only; writes are a later, explicit decision per system (§3.4).
6. **One source of truth per fact.** Areas and owners: `teams.json`. Versions: `knowledge/meta/fleet-versions.md`.
   Source list: `mcp/sources.json` (+ the shared copy, kept in parity by CI).
7. **Stdlib only.** Scripts and the search server need Python ≥ 3.9 and git, nothing to `pip install`.

## 3. The layers

```
 ┌──────────────────────────── people + Claude Code (ocp / storage / network engineers) ─────────────────────────┐
 │  plugin (today: team-brain, later: it-brain) ── skills · hooks · team profile (IT_BRAIN_TEAM)                  │
 └───────────────┬───────────────────────────────┬─────────────────────────────────────┬──────────────────────────┘
                 │ search / read / related       │ live, read-only first               │ capture / curate
 ┌───────────────▼──────────────┐  ┌─────────────▼──────────────────────┐  ┌───────────▼───────────────────────────┐
 │ RETRIEVAL: team-knowledge MCP│  │ TOOLS: MCP servers per system      │  │ WORKFLOW: brain-git.sh → MR           │
 │  brain (this repo)           │  │  kubernetes, grafana (exist)       │  │  learn/ curate/ incident/ branches    │
 │  RHOKP (OCP, ODF, OADP…)     │  │  ontap-mcp --read-only (candidate) │  │  CI: ci_checks.py (validate, teams,   │
 │  docs/upstream snapshots     │  │  Dell / ACI / PAN-OS / vCenter /   │  │      leaks, smoke…)                   │
 │  full git mirrors            │  │  Prism / Commvault: read-only REST │  │  CODEOWNERS → owning team approves    │
 │  vendor-drop (licensed docs) │  │  wrappers, to be evaluated         │  │                                       │
 └───────────────┬──────────────┘  └────────────────────────────────────┘  └───────────┬───────────────────────────┘
                 │                                                                     │
 ┌───────────────▼─────────────────────────────────────────────────────────────────────▼───────────────────────────┐
 │ CONTENT (git): knowledge/<area>/ · runbooks/<area>/ · interfaces/ · incidents/ · inbox/ · teams.json · templates │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Content

| Path | What | New in it-brain |
|---|---|---|
| `teams.json` | teams, areas (owner + consulted), placeholder vocabulary | **new** — the registry |
| `knowledge/<area>/README.md` | the area's charter: owner, scope, what goes elsewhere, sources, redaction | **new**, one per area |
| `knowledge/<area>/`, `runbooks/<area>/` | quirks, root causes, procedures | 22 new areas |
| `graphify-out/graph.json` | the brain as a graph (teams, domains, areas, pages, links) | **new**, generated, CI-checked (`docs/it-brain/GRAPH.md`) |
| `interfaces/` | cross-team contracts, `type: interface`, `teams: [a, b]` | **new** |
| `incidents/`, `inbox/` | unchanged; incidents may list several teams in `teams:` | — |
| `.gitlab/CODEOWNERS` | generated from `teams.json` (`brain.py codeowners`) | **new** |

**Areas stay flat** (`knowledge/<area>/page.md`, folder = area) because the frontmatter parser, the index, the
search source globs and the existing pages all assume it. Grouping by team is a property of the area in
`teams.json`, not a folder level. That keeps every existing path valid and lets an area change owner without a
move. Vendor-level areas (`trident`, `dell-powermax`, `palo-alto` …) instead of three big `storage`/`network`
folders, because ownership, sources and redaction rules differ per product, and engineers search by product
during an outage.

Areas and owners (run `python3 scripts/brain.py teams` for the live table):

| Owner | Areas |
|---|---|
| ocp | openshift, kubernetes, hypershift, baremetal, vsphere, networking\*, storage\*, gpu, observability, registry-mirroring, gitops, security\*, oadp\*†, vmware†, nutanix†, **server-scan**\*, **temporal**, prefect†, airflow†, spark\*†, elastic\*†, solr\*†, mongodb\*† |
| storage | netapp-ontap, trident\*, dell-powermax\*, dell-powerflex\*, dell-powerscale\*, ceph, odf\*†, smb-cifs\*, commvault\*† |
| network | cisco-aci\*, palo-alto\* |
| all | meta |

\* another team is *consulted* (named in `teams.json`, @-mentioned on MRs, not a required approver). † provisional owner.

Every area also has a **domain** (`teams.json` → `domains`: platform, platform-tools, workflow, data, storage,
backup, network, virtualization, meta) — used for grouping in the graph and the Obsidian colours, never for paths.
The data-platform areas (`elastic`, `solr`, `mongodb`, `spark`, `airflow`) cover the product both **on
Kubernetes** (operator / Helm) and **on VMs**; a page says which in `applies_to` (`k8s`, `vm`) and in its scope.

Existing OCP areas keep their meaning: `networking` and `storage` are the **cluster side** (OVN-K, ingress, AKO;
StorageClasses, PVCs, Portworx); the fabric, firewalls and arrays have their own areas.

### 3.2 Interface pages

An interface page describes one seam: parties, what crosses the boundary, a *who provides what* table (item,
provider, how to request, lead time), read-only checks each side can run on its **own** systems, a table of
symptoms seen on one side and usually caused on the other, escalation, and open questions. Template:
`templates/interface.md`. Validation requires `teams:` with at least two teams; CODEOWNERS lets any team approve
`interfaces/`, and the MR rule (`docs/it-brain/TEAMS.md`) is that every team in `teams:` approves.

Drafts on this branch (all `hypothesis`, to be filled in by the teams):

- `interfaces/ocp-storage-netapp-trident.md` — ONTAP volumes for OpenShift through Trident
- `interfaces/ocp-storage-dell-csm.md` — PowerMax / PowerFlex / PowerScale through Dell CSM
- `interfaces/ocp-storage-object-s3.md` — S3 for cluster consumers (any provider)
- `interfaces/ocp-storage-backup.md` — who backs up what (OADP, Commvault, array snapshots)
- `interfaces/ocp-network-aci-fabric.md` — what a cluster needs from ACI
- `interfaces/ocp-network-palo-alto-flows.md` — firewall flows a cluster needs
- `interfaces/storage-network-data-paths.md` — node → fabric → array data paths

Our own platform tools get the same treatment as vendors: `knowledge/server-scan/` (the bare-metal platform) and
`knowledge/temporal/` (Temporal and the Redbull Workflows orchestrator, whose `provision-dell-server` workflow lists
servers in server-scan) are written from their code and docs, and link to each other.

### 3.3 Retrieval (offline sources)

The `team-knowledge` MCP server already supports four source kinds (`markdown_dir`, `git_repo`, `mkdocs_site`,
`rhokp_solr`) and ranks all sources together. it-brain adds sources, not a new engine:

| Kind | For | Examples (status in `docs/it-brain/SOURCES-PLAN.md`) |
|---|---|---|
| docs-only snapshot in `docs/upstream/<name>` | vendors that publish docs in public git | NetApp ONTAP + Trident docs, Dell CSM docs, Ceph `doc/`, Rook, Velero, OADP operator, SMB CSI, vSphere CSI, Nutanix CSI, Palo Alto pan.dev |
| RHOKP (exists) | Red Hat products | ODF, OADP, OCP on vSphere / Nutanix |
| full git mirror (exists) | code-level questions | optional: `NetApp/trident` |
| **vendor-drop** (new convention, same `markdown_dir` kind) | licensed vendor docs that may not be committed | Commvault, PAN-OS admin guides, APIC guides, PowerMax / Unisphere, Nutanix portal, VMware docs |

**Vendor-drop:** licensed manuals are converted to Markdown on a connected or internal host and stored **outside
git** at `${IT_BRAIN_VENDOR_DOCS:-~/.cache/it-brain/vendor-docs}/<name>/` (or on the shared server's volume). Each
gets a `markdown_dir` source entry, `enabled: false` until the folder exists. This keeps the repo redistributable
inside the organisation while still making the manuals searchable. A converter is Phase 2 work.

Candidate sources are listed in `docs/it-brain/SOURCES-PLAN.md` with the exact upstream repo and paths; each was
checked to exist on 2026-11-02. They are **not yet added** to `mcp/sources.json` — a source entry is only added
together with its snapshot, so CI's `sources` and `upstream` checks stay meaningful.

### 3.4 Live tools (MCP servers)

Existing: `kubernetes` (full access, every call approved) and `grafana` (read-only). server-scan ships its own
read-only MCP server (`mcp/servers/server-scan.md`) — the first in-house candidate to connect. For the new teams the order is:

1. **Docs and brain only** (Phase 1) — no live access. Already valuable.
2. **Read-only live access** (Phase 3), one system at a time, with a dedicated read-only service account per
   system, vendored and sha256-pinned like the existing servers. First candidate: NetApp's own
   [`ontap-mcp`](https://github.com/NetApp/ontap-mcp) (Apache-2.0, Go), whose docs describe a `--read-only` flag
   that registers only tools annotated `readOnlyHint`. Others (PowerMax Unisphere, PowerFlex, OneFS, APIC, PAN-OS /
   Panorama, vCenter, Prism, Commvault) need an evaluation of what exists; where nothing suitable exists, one
   small in-house stdlib MCP that only issues HTTP `GET`s against an allow-list of endpoints.
3. **Writes** — out of scope until a team asks, per system, with a written blast-radius review. A firewall commit
   or a volume delete affects many clusters at once.

Details and safety rules: `docs/it-brain/TOOLS-PLAN.md`.

### 3.5 Graph and Obsidian

`scripts/brain_graph.py` builds a deterministic graph of the brain — teams → domains → areas → pages, page → page
links from repo-path references, shared tags — and writes it as `graphify-out/graph.json` (graphify's format; no
LLM pass) and, on demand, as an Obsidian vault with wikilinks, team/area/domain hub notes and domain colours.
Both leave `docs/upstream` out, which keeps them fast. Details: `docs/it-brain/GRAPH.md`.

### 3.6 Workflow and governance

Unchanged mechanics — `brain-git.sh start|submit|abort`, one MR per capture, CI on every MR — with three additions:

- **Ownership:** `.gitlab/CODEOWNERS` is generated from `teams.json`; CI (`teams` check) fails if it is stale, if an
  area has no folder, or if a folder is not a registered area. With GitLab's *require code owner approval* on `main`,
  the owning team must approve pages in its areas.
- **Team-scoped maintenance:** `brain.py stale --team storage` lists only pages that concern that team (owner,
  consulted, or listed in `teams:`), so each team curates its own share.
- **Commit messages** keep `brain(<area>): …`; the area already identifies the team.

## 4. Data model

Frontmatter stays a flat YAML subset (`docs/FRONTMATTER.md`). Changes:

| Field | Change |
|---|---|
| `type` | adds `interface` (folder `interfaces/`) |
| `area` | any key of `teams.json` → `areas` (validate warns, CI fails on an unknown area) |
| `teams` | **new, optional** list of team keys; **required (≥ 2)** on interface pages; use it on any page or incident that concerns more than the area's owner |
| `owners` | unchanged (people or team keys) |
| `applies_to` | same rules; new token families for the new estates, e.g. `ontap-9.16`, `trident-25.06`, `powermax-10.2`, `aci-6.0`, `panos-11.1`, `esxi-8`, `aos-6.10`, `odf-4.18`, `ceph-19` — versions still belong in `knowledge/meta/fleet-versions.md` |

## 5. Classification and leak prevention

Everything in `CLAUDE.md` still applies. New identifiers that point at one real system are classified too; the
placeholder vocabulary lives in `teams.json` → `placeholders` (`<array>`, `<serial>`, `<svm>`, `<wwn>`, `<iqn>`,
`<nqn>`, `<tenant>`, `<epg>`, `<bd>`, `<vrf>`, `<fw>`, `<device-group>`, `<zone>`, `<vcenter>`, `<prism>` …).

Machine checks added on this branch:

| Check | Catches |
|---|---|
| `brain.py validate` | PAN-OS API keys (`LUFRPT…`), plus the existing token patterns |
| `ci_checks.py leaks` | iSCSI IQNs, NVMe NQNs (with a host part), Fibre Channel WWNs — in addition to private IPs, `.internal` hosts, real cluster names and the internal denylist |

Not machine-checkable, so reviewers must catch them: array and switch names, firewall rule and address-object
names that reveal customers, tenant/EPG names, serial numbers in prose, public IPs. Teams add their real names to
the internal `BRAIN_DENYLIST_FILE` (never committed).

## 6. Team profiles (how sessions differ per team)

One plugin, one brain clone. The SessionStart hook reads `IT_BRAIN_TEAM` (`ocp` | `storage` | `network`; unset =
no profile) and adds the team's areas, the areas it is consulted on, its interface pages and its channel to the
context — so a storage engineer's Claude starts by looking at `trident` and `netapp-ontap`, not HyperShift.
Search is never restricted by team: the profile only says where to look first.

## 7. Deployment

- **Per engineer:** clone + plugin, as today (`README.md` → Setup), plus `export IT_BRAIN_TEAM=<team>`.
- **Shared:** the existing OpenShift deployment (`deploy/openshift/`) serves every team over HTTP; vendor-drop
  folders are mounted there once instead of on every laptop. This is the recommended way for the storage and
  network teams, who may not keep a local Python/git toolchain.
- **Repository:** this branch is the seed. When the teams agree, it moves to its own GitLab project (`it-brain`)
  and team-brain's `main` stops taking new pages (`docs/it-brain/ROADMAP.md`, Phase 1). Until then nothing here
  changes how the OCP team uses team-brain on `main`.

## 8. What is deliberately not changed yet

- The plugin is still named `team-brain`, env var `TEAM_BRAIN_DIR`, cache `~/.cache/team-brain` — the rename is one
  mechanical change in Phase 1, done when the repository moves, so installed clients only break once.
- No vendor snapshot is committed yet (size and licence review first — `docs/it-brain/SOURCES-PLAN.md`).
- No new live MCP server is vendored yet.

## 9. Open decisions

Listed with owners in `docs/it-brain/ROADMAP.md` → *Decisions needed*: owner of VMware / Nutanix / ODF / OADP /
Commvault, real GitLab groups for CODEOWNERS, separate repo vs keep in team-brain, whether a fourth
(virtualization / backup) team is needed, and which vendor docs we are licensed to store offline.

## History

- 2026-11-02: created (Phase 0: registry, areas, interfaces, checks, docs)
