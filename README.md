# it-brain

The shared, offline memory of four infrastructure teams — **OpenShift (ocp)**, **storage**, **network** and
**virtualization** — and the Claude Code plugin that lets Claude **read** it before troubleshooting and **write**
to it after learning something. Grown from the OpenShift team's *team-brain*; the plugin keeps that name.

| Team | What it covers here |
|---|---|
| **ocp** | ~100 air-gapped OpenShift clusters (hub / MCE / HyperShift hosted / UPI, bare metal via Metal3, vSphere, GPU nodes, AKO), GitOps, OADP, cluster-side storage and networking; our platform tools **server-scan** and **Temporal / Redbull Workflows**; Python / **Pydantic**; data platforms (Prefect, Airflow, Spark, ECK / Elastic, Solr, MongoDB — provisional) |
| **storage** | NetApp ONTAP + **Trident**, Dell **PowerMax / PowerFlex / PowerScale** (Isilon), **Ceph** + S3 (RGW), **ODF**, SMB/CIFS, **Commvault** |
| **network** | Cisco **ACI**, **Palo Alto** firewalls / Panorama, the network side of storage and cluster traffic |
| **virtualization** | **KubeVirt / OpenShift Virtualization** (deep dive), **VMware** with **PowerShell / PowerCLI** (deep dive), **Nutanix**, VM migration (MTV) |

Contents: [Why](#why) · [Problems that cross teams](#problems-that-cross-teams) · [How it fits together](#how-it-fits-together) ·
[Layout](#layout) · [Offline sources](#offline-sources) · [Live tools (MCP)](#live-tools-mcp-servers) ·
[Graph and Obsidian](#graph-and-obsidian) · [The fleet](#the-fleet-at-a-glance) · [Learning loop](#the-learning-loop) ·
[Setup](#setup-once-per-engineer) · [Writing rules](#writing-rules) · [Maintenance](#maintenance) · [CI](#ci) ·
[Troubleshooting](#troubleshooting) · [Verified or not](#what-is-and-isnt-verified) · [Glossary](#glossary)

Design and plans: [`docs/it-brain/ARCHITECTURE.md`](docs/it-brain/ARCHITECTURE.md) ·
[`TEAMS.md`](docs/it-brain/TEAMS.md) · [`SOURCES-PLAN.md`](docs/it-brain/SOURCES-PLAN.md) ·
[`TOOLS-PLAN.md`](docs/it-brain/TOOLS-PLAN.md) · [`GRAPH.md`](docs/it-brain/GRAPH.md) · [`ROADMAP.md`](docs/it-brain/ROADMAP.md)

## Why

Claude Code starts every session knowing nothing about our environment, and the environment is air-gapped. The
knowledge that keeps it running lives in people's heads, chat history and vendor manuals — split across teams,
while the hard outages cross team lines. it-brain gives every team:

1. **Curated knowledge in git** — quirks, runbooks, postmortems, cross-team contracts — reviewed through merge requests
   and approved by the team that owns the area.
2. **One offline search** (`team-knowledge` MCP server) over that knowledge *and* the vendor / upstream docs and code
   we depend on, ranked together, with no internet.
3. **Skills, hooks and MCP servers** that make Claude route a problem to the right teams, look things up first, check
   live systems read-only, and offer to write down what it learned.

## Problems that cross teams

More knowledge must not make Claude worse for any one team. So:

- **Each session stays small.** The SessionStart hook loads counts, your team profile and recent changes — never page
  bodies. Pages are read on demand.
- **Your team profile only orders the search.** `export IT_BRAIN_TEAM=ocp|storage|network|virtualization` tells Claude
  where to look first; every team's pages stay searchable.
- **`route` finds every side of a problem.** The `route` tool (and `python3 scripts/brain.py route "<problem>"`) maps
  the problem to areas using each area's `keywords` in `teams.json`, names the owner teams and the **interface page**
  between them. Example:

  ```
  $ python3 scripts/brain.py route "PVC stuck Pending on OpenShift with PowerFlex"
  areas: dell-powerflex (storage) · storage, openshift (ocp)
  read first: interfaces/ocp-storage-dell-csm.md
  ```
- **Interface pages** (`interfaces/`) write each seam once: who provides what, how each side checks its own half,
  and which symptoms on one side are caused on the other. Every team in `teams:` approves changes.
- **The `it-triage` skill** answers with evidence per side, the side most likely at fault, and the team to involve.
- **CI keeps it working:** `tests/routing.json` holds cross-team questions that must reach the right areas, teams
  and interface page.

## How it fits together

```
 engineer + Claude Code ──► plugin team-brain
   (laptop, air-gapped)       ├─ skills  brain-lookup (routes first) · it-triage · brain-learn · brain-curate ·
                              │          incident-report · hypershift-debug   (+ agent hcp-architect)
                              ├─ hooks   SessionStart (load brain + team profile) · Stop (nudge capture)
                              └─ MCP     team-knowledge  route / search / read / related / code tools over every source
                                         kubernetes      your kubeconfig, every call approved; core + KubeVirt tools
                                         grafana         metrics from our single Grafana (read-only)
                                         temporal        Redbull Workflows runs and task queues (read-only, optional)

 team-knowledge sources
   brain (this repo) · RHOKP (OCP/ACM/MCE/ODF/OADP/CNV docs, KCS, CVEs) · Argo CD docs mirror
   full git mirrors    : hypershift, ironic, cluster-api, cluster-api-provider-agent (+ server-scan, when mirrored)
   docs-only snapshots : ~60 projects in docs/upstream/ — Kubernetes, Metal3, AKO, KServe, vLLM, Prometheus, Grafana,
                         KubeVirt, CDI, HCO, MTV, Trident, Dell CSM, PowerShell, PowerCLI, Temporal, Pydantic, …
```

Search is keyword (BM25) ranking built locally and cached (`server.py --warm`): no model, no database, no `pip install`.

## Layout

| Path | What lives there | Who writes |
|---|---|---|
| `teams.json` | **the registry**: teams, areas (owner, consulted teams, domain, routing keywords), placeholder vocabulary | Humans |
| `knowledge/<area>/` | how *our* systems behave: quirks, decisions, root causes. `README.md` = the area's charter (scope, what goes elsewhere, sources, redaction) | Humans + Claude (via MR) |
| `runbooks/<area>/` | step-by-step procedures | Humans + Claude (via MR) |
| `interfaces/` | cross-team contracts (`type: interface`, approved by every team in `teams:`) | Humans + Claude (via MR) |
| `incidents/YYYY/` | postmortems, one file per incident | Humans + Claude (via MR) |
| `inbox/` | raw captures waiting to be curated | Claude |
| `templates/` | starting points for knowledge, runbook, interface and incident pages | Humans |
| `docs/upstream/` | pinned **docs-only** snapshots of upstream projects (generated — never edit) | the sync scripts |
| `docs/it-brain/` | architecture, teams guide, sources / tools plans, graph guide, roadmap | Humans |
| `docs/FRONTMATTER.md`, `docs/ADMIN.md` | page header schema; plugin rollout and env setup | Humans |
| `mcp/` | `sources.json` (what team-knowledge searches), one page per MCP server in `mcp/servers/` | Humans |
| `plugins/team-brain/` | the Claude Code plugin: skills, hooks, `.mcp.json`, team-knowledge server, vendored MCP binaries | Humans |
| `deploy/openshift/` | shared deployment: RHOKP + team-knowledge over HTTP for everyone | Humans |
| `scripts/` | `brain.py` (validate, index, stale, teams, codeowners, route), `brain_graph.py`, `ci_checks.py`, sync scripts | Humans |
| `tests/` | `golden-queries.json` (pages that must stay findable), `routing.json` (cross-team routing cases) | Humans |
| `INDEX.md`, `.gitlab/CODEOWNERS`, `graphify-out/graph.json` | generated: table of contents, review routing, knowledge graph | `brain.py index` / `codeowners`, `brain_graph.py graph` |

Areas (38) are defined only in `teams.json` — `python3 scripts/brain.py teams` lists them with their owner team:

| Owner | Areas |
|---|---|
| ocp | openshift, kubernetes, hypershift, baremetal, vsphere, networking, storage, gpu, observability, registry-mirroring, gitops, security, oadp, server-scan, temporal, python, prefect, airflow, spark, elastic, solr, mongodb |
| storage | netapp-ontap, trident, dell-powermax, dell-powerflex, dell-powerscale, ceph, odf, smb-cifs, commvault |
| network | cisco-aci, palo-alto |
| virtualization | kubevirt, vmware, nutanix, powercli |
| all | meta |

`networking` and `storage` are the **cluster side** (OVN-K, ingress, AKO; StorageClasses, PVCs); the fabric, the
firewalls and the arrays have their own areas. Owners marked provisional in `teams.json` still need confirming.

## Offline sources

| | Full git mirror | Docs-only snapshot |
|---|---|---|
| Products | HyperShift, Ironic, Cluster API, cluster-api-provider-agent (Argo CD optional; server-scan once mirrored) | everything in `docs/upstream/` — platform (Kubernetes 1.35, Metal3, OVN-K, Multus, etcd, assisted-service, OpenShift alert runbooks), networking (AKO, Envoy, Gateway API), observability (Prometheus, Grafana), AI/GPU (KServe, vLLM, llm-d, NCCL, GPU / Network operators, …), storage (Portworx, **Trident**, **Dell CSM**), virtualization (**KubeVirt user guide + repo docs, CDI, HCO, MTV / Forklift, PowerShell, PowerCLI examples**), tools (**Temporal, temporal-mcp, Pydantic, pydantic-settings**), the MCP servers' own docs |
| Content | code **and** docs, every branch / tag | documentation files only (`.md` / `.rst` / `.adoc`) |
| Version | any `ref` (e.g. `release-4.20`) | one snapshot (default branch unless pinned; Kubernetes = 1.35) |
| Lives in | `~/.cache/team-brain/sources/*.git` (`server.py --sync`) | `docs/upstream/<name>/` (committed here) |
| Refresh | `server.py --sync` | `scripts/sync-*.{sh,py}` on a connected host — automatic on GitHub, see [CI](#ci) |

Which source answers what, and which ref or version to use: `knowledge/meta/doc-sources-catalog.md` and
`knowledge/meta/fleet-versions.md`. **Red Hat's docs (RHOKP) win** over upstream where they disagree about what we run
(OpenShift Virtualization, ODF and OADP ship Red Hat builds). Planned sources (ONTAP, Ceph, Rook, Velero, ACI, pan.dev,
Elastic, Solr, MongoDB, …) and licensed vendor manuals that must stay out of git (*vendor-drop*):
`docs/it-brain/SOURCES-PLAN.md`.

After a hit, `related` follows the **link graph** — pages a document links to, pages that link to it, pages sharing its
tags — so Claude goes from a knowledge page to its runbook and incidents without searching again. The graph only grows
if pages cite each other by repo path (`knowledge/<area>/<page>.md` in backticks).

## Live tools (MCP servers)

Third-party servers ship as **sha256-pinned release archives inside the plugin** (`plugins/team-brain/mcp-servers/vendor/`,
started by `launch.py`): nothing to download in the air gap.

| Server | Access | Notes |
|---|---|---|
| `team-knowledge` | read | our own, stdlib Python: `route`, `search`, `read`, `related`, `search_code`, `find_definition`, `read_code`, `list_refs`, `list_sources` |
| `kubernetes` (`kubernetes-mcp-server`) | **full**, with your kubeconfig — approve every call | pass `context` on every call; includes the **KubeVirt toolset** (`vm_troubleshoot`, `vm_guest_info`, `vm_lifecycle`, `vm_create`, `vm_clone` …) — `mcp/servers/kubernetes.md` |
| `grafana` (`mcp-grafana`) | read-only | one Grafana, one datasource per cluster named `Moby / <cluster-name>`: resolve the UID first — `mcp/servers/grafana.md` |
| `temporal` (`temporal-mcp`, pre-release) | read-only | optional: runs when `TEMPORAL_MCP_CONFIG` points at a config, otherwise a stub that explains setup — `mcp/servers/temporal.md` |
| server-scan | read-only | its own MCP at `https://<server-scan-host>/mcp`, added per engineer — `mcp/servers/server-scan.md` |
| `okp-mcp` | read | optional Red Hat RHOKP server, container image — `mcp/servers/okp-mcp.md` |

Evaluated, not deployed: NetApp `ontap-mcp` (`--read-only`, container) and the Nutanix MCP (Python package) —
`mcp/servers/ontap-mcp.md`, `mcp/servers/nutanix-mcp.md`, and the plan for the rest in `docs/it-brain/TOOLS-PLAN.md`.
Rule for every live system: read-only first, one read-only account per system, credentials never in git.

## Graph and Obsidian

`scripts/brain_graph.py` turns `teams.json`, frontmatter and the path references between pages into a graph —
teams → domains → areas → pages → links — with no LLM pass:

```bash
python3 scripts/brain_graph.py graph                             # graphify-out/graph.json (committed, CI-checked)
graphify query "S3 bucket for OADP backups" --graph graphify-out/graph.json   # if graphify is installed
python3 scripts/brain_graph.py obsidian --out ~/it-brain-vault   # Obsidian vault: wikilinks, team/area hubs, colours
python3 scripts/brain_graph.py stats                             # most-linked pages, pages with no links
```

`docs/upstream` is left out of both, which keeps them fast. Details: `docs/it-brain/GRAPH.md`.

## The fleet at a glance

Real region, site, MCE and cluster names are classified and never appear here: pages use `<region>`, `<site>`, `<mce>`,
`<cluster>`. The same goes for array, SVM, firewall, EPG, vCenter and iDRAC names (`teams.json` → `placeholders`).

```
hub cluster ── Cluster Navigator · Temporal (Redbull Workflows) · Argo CD (+ a second "upi" Argo)
   └─ MCE clusters (per site) ── ACM · MCE · OADP · NMState · Metal3 · HyperShift · own Argo CD
         └─ hosted clusters (workloads, GPU nodes, AKO, VMs on OpenShift Virtualization…)
   └─ UPI clusters (standalone; deployed to by the hub's upi Argo)
server-scan ── inventory of every bare-metal server (iDRAC / OME / Redfish), feeds the install-server workflow
```

- **day1** provisions clusters and is the *only* place an OCP version is written (`mastertag`).
- **day2** decides what runs where: *a folder is the registration* (`sites/<site>/<env>/mces/<mce>/<cluster>/…`).
- Naming: `ocp4-<env>-<name>-<site>`, env ∈ `prod|prep|test`.

Start with `knowledge/openshift/fleet-topology-hub-mce-hosted.md`, `knowledge/temporal/README.md` and
`knowledge/server-scan/README.md`.

## The learning loop

```
 work session in any repo / cluster
        ├─ SessionStart hook ── pulls the brain, loads your team profile
        ├─ a problem ──► route ──► brain-lookup / it-triage  (brain, RHOKP, snapshots, code at the right ref)
        ├─ learned something non-obvious ──► /team-brain:brain-learn
        │        worktree on learn/<date>-<slug> ──► index + validate ──► push ──► merge request
        ├─ an outage worth a postmortem ──► /team-brain:incident-report
        └─ Stop hook ── after a long session with no capture, asks once: "durable knowledge?"

 owning team reviews the MR (CODEOWNERS) ──► merge ──► everyone's next session pulls it
 periodically: /team-brain:brain-curate (inbox → knowledge, dedupe, flag stale)
```

`plugins/team-brain/scripts/brain-git.sh` does the git work (`start` / `submit` / `abort`) in a separate worktree, so
the engineer's own checkout is never touched; `submit` also regenerates the index, CODEOWNERS and the graph.

## Setup (once per engineer)

```bash
# 1. Clone the brain to the standard location (the hooks look here; or set TEAM_BRAIN_DIR)
git clone https://github.com/roiblum1/it-brain ~/team-brain      # inside the air gap: from your internal mirror

# 2. Register it as a plugin marketplace and install the plugin (user scope = all projects)
claude plugin marketplace add ~/team-brain
claude plugin install team-brain@team-brain

# 3. Shell profile: your team, then your internal endpoints
export IT_BRAIN_TEAM=storage                                       # ocp | storage | network | virtualization
export GIT_MIRROR_BASE=https://gitlab.internal/mirrors              # where the full git mirrors live
export RHOKP_SOLR_URL=http://rhokp.internal:8983  RHOKP_URL=https://rhokp.internal
export ARGOCD_DOCS_URL=https://docs-mirror.internal/argo-cd/stable
export GRAFANA_URL=https://grafana.internal                         # optional: Grafana MCP
export GRAFANA_SERVICE_ACCOUNT_TOKEN=<read-only token>              # never commit this
export TEMPORAL_MCP_CONFIG=~/.config/it-brain/temporal-mcp.yaml     # optional: from mcp-servers/temporal-mcp.example.yaml
python3 ~/team-brain/plugins/team-brain/mcp-servers/team-knowledge/server.py --sync --warm --check

# 4. Check
claude plugin list          # team-brain@team-brain  ✔ enabled
# inside claude: /mcp  → team-knowledge, kubernetes, grafana, temporal connected
```

Requirements: `git`, `jq`, `python3` ≥ 3.9 (stdlib only); optionally `glab` (without it Claude pushes the branch and
prints the MR link). The vendored MCP binaries cover linux-x86_64 and darwin-arm64 (Grafana and Kubernetes also Windows).

**Shared alternative** — recommended for teams without a local Python / git setup: one team-knowledge on OpenShift
(`oc apply -k deploy/openshift`) serving everyone over HTTP (`mcp/README.md`). To roll the plugin out without each
person running step 2, use managed settings (`docs/ADMIN.md`).

## Writing rules

1. **Every page has frontmatter** (`docs/FRONTMATTER.md`); `brain.py validate` enforces it.
2. **No secrets and no real names, ever**: tokens, passwords, kubeconfigs, BMC / iDRAC credentials, IPs, hostnames,
   customer names, serials, WWNs / IQNs → placeholders. The checks catch known token and identifier shapes only;
   reviewers must catch the rest.
3. **State the scope** — product version, hardware, cluster type — and **write version-generic** ("since 4.18");
   versions live in `knowledge/meta/fleet-versions.md` only.
4. **Say how you know**: `verified` (tested on our systems) · `observed` (seen once, or read from docs/code) · `hypothesis`.
5. **Search before you write**, edit the existing page and bump `last_verified`; for a seam between teams, update the
   `interfaces/` page instead of copying facts into two areas.
6. **Start from a template** in `templates/`; commit messages are `brain(<area>): <what was learned>`.

Lifecycle: capture → `inbox/` → curated into `knowledge/` / `runbooks/` → re-verified → flagged by
`brain.py stale --days 180` when old (never auto-deleted).

## Maintenance

| Task | How |
|---|---|
| Add an area | an entry in `teams.json` (owner, consulted, domain, description, keywords) + `knowledge/<area>/README.md` charter, then `python3 scripts/brain.py codeowners` |
| A cross-team question routes badly | add the missing words to the area's `keywords` in `teams.json` and a case to `tests/routing.json` |
| Fleet moves to a new OCP minor | a row in `knowledge/meta/fleet-versions.md`, the `ocp-4.NN` token where pages apply, new refs in the full mirrors (`server.py --sync`) |
| Add or refresh a docs snapshot | add `(repo, [paths])` to `SOURCES` in `scripts/sync-ecosystem-docs.py`, run it on a connected host (`REF_<name>=<tag>` to pin), add the source to `mcp/sources.json` **and** `deploy/openshift/shared-sources.json`, a row in `knowledge/meta/doc-sources-catalog.md` |
| Enable our own repos as sources | set the real remotes (`GITOPS_DAY1_REMOTE`, `GITOPS_DAY2_REMOTE`, `NAVIGATOR_REMOTE`, server-scan's mirror) and flip `enabled` |
| Bump or add a vendored MCP server | connected host: `VERSION_<name>=<tag> python3 scripts/fetch-mcp-binaries.py <name>`, update its `mcp/servers/` page, bump the plugin version |
| Change skills, hooks, `mcp-servers/` or `.mcp.json` | bump `version` in `plugins/team-brain/.claude-plugin/plugin.json` |
| Curate | `/team-brain:brain-curate`, or per team: `python3 scripts/brain.py stale --team <team>` |

Daily commands:

```bash
python3 scripts/brain.py validate                  # frontmatter + secret scan + links
python3 scripts/brain.py index                     # regenerate INDEX.md
python3 scripts/brain.py teams                     # areas → owner / consulted / domain
python3 scripts/brain.py route "<problem>"         # which areas, teams and interface pages a problem touches
python3 scripts/brain.py stale --days 180 --team network
python3 scripts/brain.py codeowners                # regenerate .gitlab/CODEOWNERS
python3 scripts/brain_graph.py graph               # regenerate graphify-out/graph.json
python3 scripts/ci_checks.py                       # everything CI runs (BASE_REF=origin/main adds the version check)
python3 plugins/team-brain/mcp-servers/team-knowledge/server.py --check     # which sources are reachable
python3 plugins/team-brain/mcp-servers/launch.py --check                    # which MCP binary runs on this machine
```

## CI

One script, three places: `python3 scripts/ci_checks.py` locally, `.github/workflows/ci.yml` on GitHub and
`.gitlab-ci.yml` for an internal GitLab mirror. It fails the change if any check fails:

| Check | What it enforces |
|---|---|
| `validate` / `index` | frontmatter schema, secret patterns, links (**warnings count as errors**); `INDEX.md` is current |
| `graph` | `graphify-out/graph.json` is current |
| `teams` | `teams.json` is consistent, every area has a charter, every folder is an area, CODEOWNERS is current |
| `route` | every case in `tests/routing.json` reaches its areas, teams and interface page |
| `json`, `syntax` | every JSON file parses; Python / shell scripts compile |
| `sources`, `parity` | sources are well-formed and match real files; `mcp/sources.json` and `deploy/openshift/shared-sources.json` agree |
| `frontmatter` | `applies_to` tokens are well-formed, `area` is known, `last_verified` isn't in the future |
| `leaks` | private IPs, non-placeholder `.internal` hosts, real-looking cluster names, iSCSI IQNs / NVMe NQNs / FC WWNs, and the internal **denylist** (`BRAIN_DENYLIST_FILE`, never in git) |
| `upstream` | each `docs/upstream/<name>` has `.upstream` metadata and documentation files |
| `mcpbin` | every vendored MCP archive is present and matches its sha256 in `vendor/manifest.json` |
| `version` | plugin changes come with a `plugin.json` version bump (needs `BASE_REF`) |
| `smoke` | the real team-knowledge server finds each page in `tests/golden-queries.json` in its top 3 |

**Automatic doc refresh:** `.github/workflows/docs-refresh.yml` runs on every push to `main`, daily and on demand. It
re-fetches only the snapshots whose upstream moved, rewrites `docs/upstream/VERSIONS.md`, runs the checks and commits
`docs(upstream): refresh N snapshots` to `main` — **pull before you push**. An air-gapped mirror receives the refreshed
snapshots through the mirror. Vendored MCP binaries are never bumped automatically.

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `missing clone … (run: server.py --sync)` | a full mirror isn't fetched or doesn't exist under `$GIT_MIRROR_BASE` — create it, then `--sync` |
| `rhokp` / `argocd-docs` ❌ in `--check` | the endpoint env var isn't set or the service isn't reachable from this machine |
| Search finds nothing for a docs-only product | its `docs/upstream/<name>` is empty or upstream moved its docs — rerun the sync script |
| Docs for the wrong version | snapshots are single-version; `ref` works only for full mirrors — check the installed version |
| Claude stays inside one team's pages | ask it to `route` the problem; if an area is missed, add keywords in `teams.json` + a routing case |
| `temporal` MCP shows only `how_to_configure` | `TEMPORAL_MCP_CONFIG` isn't set or the file is missing — `mcp/servers/temporal.md` |
| Metrics from the wrong cluster | a query used the default datasource — resolve `Moby / <cluster>` and pass its UID |
| `server.py` can't find the config | set `TEAM_BRAIN_DIR` (default `~/team-brain`) |

## What is and isn't verified

- **Checked here:** CI passes locally (15 checks). The vendored binaries start through `launch.py` on linux-x86_64 and
  list their tools: Kubernetes MCP with the KubeVirt toolset (25 tools), temporal-mcp (8 read-only tools). The
  Temporal "not configured" stub answers. graphify 0.9.100 reads `graph.json`. Routing passes its 14 cases.
- **Not yet run against our environment:** any MCP against our clusters, Grafana, Temporal or server-scan; RHOKP and the
  Argo CD mirror (internal endpoints); the shared HTTP deployment; the GitHub workflows (first run happens on GitHub).
- **Interface pages are drafts** (`confidence: hypothesis`) until both teams fill the `<…>` cells.
- **Written from docs and code, not tested on our systems:** the server-scan, Temporal, KubeVirt, PowerCLI and Pydantic
  sections are `observed`, with uncertain claims marked `hypothesis` inline.
- Snapshots track upstream default branches at their last sync (`docs/upstream/VERSIONS.md`).
- `session-start.sh` uses GNU `find -printf` / `timeout`, so its area list is empty on stock macOS.

## Glossary

| Term | Meaning |
|---|---|
| hub cluster | top management cluster: Cluster Navigator, Temporal, Argo CD |
| MCE | cluster running MCE / ACM / HyperShift that hosts control planes; runs its own Argo CD |
| hosted cluster | HyperShift cluster whose control plane runs on an MCE |
| UPI cluster | standalone cluster under no MCE |
| day1 / day2 | provisioning values repo (owns `mastertag`) / GitOps repo for what runs where |
| `mastertag` | `<major>.<minor>.<patch>-<arch>` — a cluster's OCP version |
| area / charter | a knowledge topic owned by one team (`teams.json`) / its `knowledge/<area>/README.md` |
| interface page | the contract between two or more teams, in `interfaces/` |
| route | mapping a problem to every area, team and interface page it touches |
| RHOKP | Red Hat Offline Knowledge Portal (product docs, KCS, CVEs) |
| CNV | OpenShift Virtualization (KubeVirt as shipped by Red Hat) |
| MTV | Migration Toolkit for Virtualization (Forklift): VMware → KubeVirt migrations |
| full mirror / snapshot | see [Offline sources](#offline-sources) |
| vendor-drop | licensed vendor manuals converted for offline search, kept outside git |
