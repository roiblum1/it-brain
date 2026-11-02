# team-brain → it-brain

> **This branch (`claude/it-brain-multi-team-n7n6kg`) is it-brain**: the same offline brain, grown to serve the
> **OpenShift (ocp)**, **storage** and **network** teams — NetApp ONTAP / Trident, Dell PowerMax / PowerFlex /
> PowerScale, Ceph S3, ODF, SMB/CIFS, OADP, Commvault, Cisco ACI, Palo Alto, VMware, Nutanix — plus our platform
> tools (**server-scan**, **Temporal / Redbull Workflows**) and data/workflow platforms (Prefect, Airflow, Spark,
> ECK / Elastic, Solr, MongoDB, on Kubernetes and VMs). Not merged into team-brain's `main`.
>
> | Start here | |
> |---|---|
> | Architecture | [`docs/it-brain/ARCHITECTURE.md`](docs/it-brain/ARCHITECTURE.md) |
> | Teams: who owns and reviews what | [`docs/it-brain/TEAMS.md`](docs/it-brain/TEAMS.md), [`teams.json`](teams.json) |
> | Cross-team contracts | [`interfaces/`](interfaces/README.md) |
> | Graph (graphify) and Obsidian vault | [`docs/it-brain/GRAPH.md`](docs/it-brain/GRAPH.md) |
> | Offline vendor sources, live tools | [`docs/it-brain/SOURCES-PLAN.md`](docs/it-brain/SOURCES-PLAN.md), [`docs/it-brain/TOOLS-PLAN.md`](docs/it-brain/TOOLS-PLAN.md) |
> | Phases and decisions needed | [`docs/it-brain/ROADMAP.md`](docs/it-brain/ROADMAP.md) |
>
> The rest of this README describes the machinery, which it-brain keeps unchanged.

The shared, versioned memory of the platform team: what we know about our Kubernetes/OpenShift fleet,
how we fix things, what broke and why — plus the tools (skills, hooks and MCP servers) that let Claude Code
**read** that knowledge before it troubleshoots and **write** to it after it learns something.

Contents: [Why](#why-this-exists) · [How it fits together](#how-it-fits-together) · [Layout](#layout) ·
[Offline sources](#offline-knowledge-the-team-knowledge-mcp-server) · [Fleet at a glance](#the-fleet-at-a-glance) ·
[Learning loop](#how-the-learning-loop-works) · [Setup](#setup-once-per-engineer) ·
[Writing rules](#writing-rules-for-humans-and-claude-alike) · [Maintenance](#maintenance-recipes) ·
[Troubleshooting](#troubleshooting) · [Limitations](#what-is-and-isnt-verified-yet) · [Glossary](#glossary)

## Why this exists

We run roughly 100 air-gapped OpenShift clusters (bare metal via Metal3, vSphere, HyperShift hosted control
planes, GPU nodes, AKO load balancing) on a mixed set of versions (now OCP 4.16 / 4.20 / 4.22, and moving).
The knowledge that keeps them healthy used to live in people's heads and chat history, and Claude Code, which
helps with this work, starts every session knowing nothing about our environment and has no internet.

team-brain fixes both:

1. **A repo of curated knowledge** — quirks, runbooks, postmortems — reviewed by humans through merge requests.
2. **An offline search server** (`team-knowledge`) that lets Claude search that knowledge *and* the upstream
   documentation/source we depend on (Red Hat docs and KCS, HyperShift, Cluster API, KServe, vLLM, AKO, …)
   without leaving the air gap.
3. **Skills and hooks** that make Claude look things up before it digs in, and offer to write down what it learned.

## How it fits together

```
 engineer + Claude Code ──► plugin team-brain ──┬─ skills  brain-lookup / brain-learn / brain-curate / incident-report / hypershift-debug  (+ agent hcp-architect)
   (laptop, air-gapped)                          ├─ hooks   SessionStart (load brain), Stop (nudge capture)
                                                 ├─ MCP     team-knowledge  ──► searches the sources below
                                                 └─ MCP     grafana         ──► metrics via our single Grafana

 team-knowledge sources
   brain (this repo) · RHOKP (OCP/ACM/MCE docs, KCS, CVEs) · Argo CD docs mirror
   full git mirrors  : hypershift, ironic, cluster-api, cluster-api-provider-agent   (code + docs at any ref)
   docs-only snapshots: AKO, Envoy, KServe, vLLM, LWS, Kueue, Prometheus, Grafana, Metal3, Gateway API,
                        Portworx, Kubernetes 1.35, … in docs/upstream/
```

Search is keyword (BM25) ranking, built locally from the sources and cached (`server.py --warm`); it needs no
model, no database and no `pip install`.

## Layout

| Path | What lives there | Who writes |
|---|---|---|
| `teams.json` | it-brain registry: teams, areas (owner, consulted, domain), placeholder vocabulary | Humans |
| `knowledge/<area>/` | Curated knowledge: how *our* clusters behave, quirks, decisions, gotchas; `README.md` = the area's charter | Humans + Claude (via MR) |
| `interfaces/` | Cross-team contracts (`type: interface`, approved by every team in `teams:`) | Humans + Claude (via MR) |
| `.gitlab/CODEOWNERS` | Generated from `teams.json` (never edit by hand) | `scripts/brain.py codeowners` |
| `graphify-out/graph.json` | The brain as a graph for graphify / Obsidian (generated, never edit) | `scripts/brain_graph.py graph` |
| `runbooks/<area>/` | Step-by-step procedures | Humans + Claude (via MR) |
| `incidents/YYYY/` | Postmortems, one file per incident | Humans + Claude (via MR) |
| `inbox/` | Raw learnings Claude captured, waiting to be curated | Claude |
| `templates/` | Starting points for knowledge, runbook and incident pages | Humans |
| `docs/upstream/` | Pinned **docs-only** snapshots of upstream projects (generated — never edit) | the sync scripts |
| `docs/FRONTMATTER.md`, `docs/ADMIN.md` | Page header schema; plugin rollout and env setup | Humans |
| `mcp/` | `sources.json` (what team-knowledge searches), docs for every MCP server, client config | Humans |
| `plugins/team-brain/` | The Claude Code plugin: skills, hooks, `.mcp.json`, the team-knowledge server code | Humans |
| `deploy/openshift/` | Shared deployment: RHOKP + team-knowledge over HTTP for the whole team | Humans |
| `scripts/` | `brain.py` (validate/index/stale), `ci_checks.py` (CI gate) and the doc sync scripts | Humans |
| `tests/` | `golden-queries.json`: queries that must keep finding specific pages (CI smoke test) | Humans |
| `.gitlab-ci.yml`, `.github/workflows/` | CI definitions (the GitLab one is the real pipeline) | Humans |
| `INDEX.md` | Generated table of contents (never edit by hand) | `scripts/brain.py index` |

Areas used by `knowledge/` and `runbooks/` are defined in `teams.json` (`python3 scripts/brain.py teams`): the
original OCP areas plus `netapp-ontap`, `trident`, `dell-powermax`, `dell-powerflex`, `dell-powerscale`, `ceph`, `odf`,
`smb-cifs`, `commvault`, `oadp`, `cisco-aci`, `palo-alto`, `vmware`, `nutanix`, `server-scan`, `temporal`, `prefect`,
`airflow`, `spark`, `elastic`, `solr`, `mongodb`.

## Offline knowledge: the team-knowledge MCP server

One zero-dependency MCP server (Python ≥ 3.9 stdlib + `git`) searches every source in a single call and ranks
results across them, so Claude sees *our* notes and Red Hat's KCS side by side. Tools: `search`, `read`,
`list_refs`, `search_code`, `find_definition`, `read_code`, `list_sources`.

There are two kinds of source, and the difference matters when you trust an answer:

| | Full git mirror | Docs-only snapshot |
|---|---|---|
| Products | HyperShift, Ironic, Cluster API, cluster-api-provider-agent (Argo CD optional) | AKO, Envoy (+Gateway), KServe, vLLM, LMCache, Mooncake, LWS, Kueue, Prometheus (+operator), Grafana (+MCP docs), Metal3 (docs, baremetal-operator, CAPM3), Gateway API, GPU operator, NFD, OVN-Kubernetes, Multus, OpenShift alert runbooks, etcd, assisted-service, Portworx, Kubernetes; **inference/HPC/fabrics/kernel:** llm-d, SGLang, TensorRT-LLM, Dynamo, Ray/KubeRay, NCCL, UCX, rdma-core, NVIDIA GPU + Network Operator docs, SR-IOV operator, tuned, Linux kernel docs (selected) |
| Content | code **and** docs, every branch/tag | documentation files only (`.md/.rst/.adoc`) |
| Version | any `ref` (e.g. `release-4.20`) | one pinned snapshot (default branch; Kubernetes = 1.35; Portworx = latest) |
| Lives in | `~/.cache/team-brain/sources/*.git` (fetched by `server.py --sync`) | `docs/upstream/<name>/` (committed in this repo) |
| Refresh | `server.py --sync` | `scripts/sync-*.{sh,py}` on a connected host, then commit |

What each source is good for, and which ref/version to use: `knowledge/meta/fleet-versions.md` (OCP minor →
Kubernetes/HyperShift refs) and `knowledge/meta/doc-sources-catalog.md`. Red Hat's own docs (RHOKP) win over
upstream where they disagree about what we run.

After a hit, the `related` tool follows the **link graph** — pages a document links to, pages that link to it,
and brain pages sharing its tags — so Claude goes from a knowledge page to its runbook and incidents without
searching again (`read` also ends with the linked pages). The graph is built from the text, so it only grows if
pages cite each other by path (`knowledge/<area>/<page>.md` in backticks, or a Markdown link).

The **Grafana MCP** (`mcp-grafana`) is separate and gives Claude metrics. Its binary ships **inside the plugin**
(`plugins/team-brain/mcp-servers/vendor/`, sha256-pinned; linux-x86_64, darwin-arm64, windows-x86_64), so there is
nothing to download in the air gap; it runs read-only with usage statistics off.

The **Kubernetes MCP** (`kubernetes-mcp-server`) ships the same way and lets Claude look at a cluster with your
kubeconfig, with your rights: read, write, exec and Secrets — you approve each call in the permission prompt, so
don't allow-list the write tools. Claude must pass the `context` (cluster) on every call — `mcp/servers/kubernetes.md`. Red Hat's own RHOKP server (`okp-mcp`) is optional and runs from a
container image, not from the plugin: `mcp/servers/okp-mcp.md`. Our layout is one Prometheus per
cluster and **one Grafana with one datasource per cluster named `Moby / <cluster-name>`**, so Claude must
list datasources, pick the cluster's UID and pass it on every query:
`knowledge/observability/grafana-one-datasource-per-cluster-prometheus.md`, `mcp/servers/grafana.md`.

Server details, RHOKP setup and the shared HTTP deployment: [`mcp/README.md`](mcp/README.md).

## The fleet at a glance

Real region, site, MCE and cluster names are classified and never appear in this repo — pages use `<region>`,
`<site>`, `<mce>`, `<cluster>`.

```
hub cluster ── Cluster Navigator · Temporal server · Argo CD (+ a second "upi" Argo)
   └─ MCE clusters (per site) ── ACM · MCE · OADP · NMState · Metal3 · HyperShift · own Argo CD
         └─ hosted clusters (workloads, GPU nodes, AKO, Portworx…)
   └─ UPI clusters (standalone; deployed to by the hub's upi Argo)
```

- **day1** (`platform-config`) provisions clusters and is the *only* place an OCP version is written (`mastertag`).
- **day2** decides what runs where: *a folder is the registration* (`sites/<site>/<env>/mces/<mce>/<cluster>/…`).
- Naming: `ocp4-<env>-<name>-<site>`, env ∈ `prod|prep|test`; folder basename == Argo cluster name.

Start with `knowledge/openshift/fleet-topology-hub-mce-hosted.md`, then the two GitOps pages in
`knowledge/gitops/`.

## How the learning loop works

```
 work session in any repo / cluster
        │
        ├─ SessionStart hook ── pulls the brain, tells Claude where it is + what's in it
        │
        ├─ Claude hits a problem ──► /team-brain:brain-lookup  (brain, RHOKP, upstream docs/code at the right ref)
        │
        ├─ Claude learns something non-obvious ──► /team-brain:brain-learn
        │        worktree on learn/<date>-<slug> ──► validate ──► push ──► GitLab MR
        │
        ├─ an outage worth a postmortem ──► /team-brain:incident-report   (incident/<date>-<slug> branch)
        │
        └─ Stop hook ── after a long session with no capture, asks Claude once:
                         "did this session produce durable knowledge?"

 human reviews MR ──► merge ──► everyone's next session pulls it
 periodically: /team-brain:brain-curate  (you invoke it: promote inbox → knowledge, dedupe, mark stale)
```

Knowledge captured by Claude never lands on `main` without a human approving the merge request. Under the hood
`plugins/team-brain/scripts/brain-git.sh` does the git work (`start` creates a worktree, `submit` runs
`brain.py index` + `validate`, commits, pushes and opens the MR with `glab` if installed, `abort` throws it away),
so the engineer's own checkout is never touched. Repo-structure changes (sources, scripts, tooling docs) can be
committed to `main` directly when the team decides so.

## Setup (once per engineer)

```bash
# 1. Clone the brain to the standard location (the hooks look here)
git clone git@gitlab.internal:platform/team-brain.git ~/team-brain
#    or anywhere else, and export TEAM_BRAIN_DIR=/path/to/team-brain in your shell profile

# 2. Register the repo as a plugin marketplace and install the plugin (user scope = all projects)
claude plugin marketplace add ~/team-brain
claude plugin install team-brain@team-brain

# 3. Point the tools at your internal endpoints (shell profile)
export GIT_MIRROR_BASE=https://gitlab.internal/mirrors            # where the full git mirrors live
export RHOKP_SOLR_URL=http://rhokp.internal:8983  RHOKP_URL=https://rhokp.internal
export ARGOCD_DOCS_URL=https://docs-mirror.internal/argo-cd/stable
export GRAFANA_URL=https://grafana.internal                        # Grafana MCP (optional)
export GRAFANA_SERVICE_ACCOUNT_TOKEN=<read-only service account token>   # never commit this
python3 ~/team-brain/plugins/team-brain/mcp-servers/team-knowledge/server.py --sync --warm --check

# 4. Check
claude plugin list          # team-brain@team-brain  ✔ enabled
# inside claude: /mcp  → plugin:team-brain:team-knowledge connected (and grafana, if configured)
```

Requirements on the workstation: `git`, `jq`, `python3` ≥ 3.9 (stdlib only), and optionally `glab` (without it Claude pushes the branch and prints the MR link).

**Shared alternative:** run one team-knowledge on OpenShift (`oc apply -k deploy/openshift`) so everyone uses a
single RHOKP and one set of mirrors; see `mcp/README.md`. To roll the plugin out to the whole team without
each person running step 2, use managed settings (`docs/ADMIN.md`).

## Writing rules (for humans and Claude alike)

1. **Every page has frontmatter** — `docs/FRONTMATTER.md`. `brain.py validate` enforces it.
2. **No secrets and no real locations, ever.** No tokens, pull secrets, kubeconfigs, BMC passwords, internal
   IPs/hostnames, customer names; region/site/MCE/cluster names become `<region>`, `<site>`, `<mce>`, `<cluster>`.
   `validate` scans for known token patterns only — it can't recognise a hostname or a customer name, so
   reviewers must.
3. **State the scope**: OCP/Kubernetes version, hardware, cluster type (hosted / standalone / SNO). A fix for
   4.16 on one server model is not a fix for everything.
4. **Write version-generic**: ranges ("since 4.18", "up to 4.20") in the text and in `applies_to`; versions live
   in `knowledge/meta/fleet-versions.md` only.
5. **Say how you know**: `verified` (tested on a cluster) · `observed` (seen once, or read from docs/code) ·
   `hypothesis`. Don't upgrade without evidence.
6. **Prefer editing an existing page** over adding one — search first (`grep -ril <term> knowledge runbooks
   incidents inbox`), then bump `last_verified`.
7. **Start from a template** in `templates/`; commit messages are `brain(<area>): <what was learned>`.

Page lifecycle: raw capture → `inbox/` → curated into `knowledge/`/`runbooks/` → re-verified (`last_verified`)
→ flagged by `brain.py stale --days 180` when old (flagged, never auto-deleted).

## Maintenance recipes

| Task | How |
|---|---|
| Fleet moves to a new OCP minor (e.g. 4.24) | Add a row to `knowledge/meta/fleet-versions.md`, add the `ocp-4.24` token where pages apply, create new refs in the full mirrors (`server.py --sync`), refresh pinned snapshots if their docs track the fleet (`K8S_DOCS_REF=release-1.NN scripts/sync-upstream-docs.sh`) |
| Refresh docs-only snapshots | `python3 scripts/sync-ecosystem-docs.py [name…]` (pin one with `REF_<name>=<tag>`, e.g. `REF_vllm=v0.11.0`); Kubernetes: `scripts/sync-upstream-docs.sh`; Portworx: `python3 scripts/sync-portworx-docs.py` (macOS Python: `SSL_CERT_FILE=/etc/ssl/cert.pem`). Connected host only, or set `UPSTREAM_GIT_BASE` to an internal mirror. Commit the result |
| Add a source | Append to `mcp/sources.json` **and** `deploy/openshift/shared-sources.json`; add a row to `knowledge/meta/doc-sources-catalog.md`; full git mirrors also need the repo mirrored into GitLab under `$GIT_MIRROR_BASE` |
| Enable our own repos as sources | Set `GITOPS_DAY1_REMOTE`, `GITOPS_DAY2_REMOTE`, `NAVIGATOR_REMOTE` to the real GitLab URLs and flip `enabled` |
| Add a new area | Create the folder (with a file in it — git ignores empty dirs), add it to `AREAS` in `scripts/brain.py` and to the list in `CLAUDE.md`/this README |
| Bump or add a vendored MCP server | Connected host: `VERSION_grafana=<tag> python3 scripts/fetch-mcp-binaries.py grafana`, update the pin in that script and `mcp/servers/grafana.md`, bump the plugin version |
| Change skills, hooks, `mcp-servers/` or `.mcp.json` | Bump `version` in `plugins/team-brain/.claude-plugin/plugin.json` |
| Curate the inbox | `/team-brain:brain-curate` — one MR with every decision |

Daily commands:

```bash
python3 scripts/brain.py validate           # frontmatter + secret scan + links
python3 scripts/brain.py index              # regenerate INDEX.md  (index --check fails if stale)
python3 scripts/brain.py stale --days 180   # pages whose last_verified is old (--team storage: one team's share)
python3 scripts/brain.py teams              # areas → owner / consulted team / domain
python3 scripts/brain.py codeowners         # regenerate .gitlab/CODEOWNERS from teams.json
python3 scripts/brain_graph.py graph        # regenerate graphify-out/graph.json  (graph --check fails if stale)
python3 scripts/brain_graph.py obsidian --out ~/it-brain-vault   # browse the brain in Obsidian
python3 scripts/ci_checks.py                # everything CI runs (add BASE_REF=origin/main for the version-bump check)
python3 plugins/team-brain/mcp-servers/team-knowledge/server.py --check   # which sources are reachable
python3 plugins/team-brain/mcp-servers/team-knowledge/server.py --call search '{"query":"NodePool stuck Updating","version":"4.20"}'
```

## CI

One script, three places: `python3 scripts/ci_checks.py` locally, `.gitlab-ci.yml` (the real, air-gapped pipeline)
and `.github/workflows/ci.yml` (the GitHub mirror). It fails the merge request if any of these fail:

| Check | What it enforces |
|---|---|
| `validate` / `index` | frontmatter schema, secret patterns, links; **warnings count as errors**; `INDEX.md` is current |
| `graph` | `graphify-out/graph.json` is current |
| `teams` | `teams.json` is consistent (owners, consulted, domains), every area has a charter folder, every folder is an area, CODEOWNERS is current |
| `json`, `syntax` | every JSON file parses; Python/shell scripts compile |
| `sources` | each source has its required keys; enabled sources that read this repo match real files |
| `parity` | `mcp/sources.json` and `deploy/openshift/shared-sources.json` list the same sources with the same `enabled` flags |
| `frontmatter` | `applies_to` tokens are well-formed, `area` is known, `last_verified` isn't in the future |
| `leaks` | private IPs, `.internal` hostnames outside the placeholder allowlist, real-looking `ocp4-<env>-<name>` names, iSCSI IQNs / NVMe NQNs / FC WWNs, and (if configured) your **denylist** |
| `upstream` | each `docs/upstream/<name>` has `.upstream` metadata and documentation files |
| `version` | on merge requests: skills/hooks/`mcp-servers/`/`.mcp.json` changes must come with a `plugin.json` update (needs `BASE_REF`) |
| `mcpbin` | every vendored MCP server archive is present and matches the sha256 in `vendor/manifest.json` |
| `smoke` | the real team-knowledge server answers `tests/golden-queries.json` with the expected page in the top 3 |

Setup in the internal GitLab: set `CI_IMAGE` to a runner image with python3 ≥ 3.9, git and bash from your internal
registry; add a CI/CD variable **`BRAIN_DENYLIST_FILE`** (type *File*, masked/protected) holding one regex per line
with the real region/site/MCE/cluster names — it never enters git, and matches are logged by line and entry number
only. A weekly pipeline schedule runs `brain.py stale` as an informational report.

### Automatic doc refresh

`.github/workflows/docs-refresh.yml` runs on every push to `main`, daily, and on demand. It asks each upstream for
its current commit (`git ls-remote`), re-fetches only the snapshots that moved, rewrites
`docs/upstream/VERSIONS.md` (repo, ref, commit, newest upstream release, file count per snapshot), runs the checks
above on the result and commits `docs(upstream): refresh N snapshots` to `main`.

- It runs **only on GitHub** — the air-gapped GitLab cannot reach upstream and receives the refreshed snapshots
  through the mirror of this repository.
- An upstream that fails or moved its docs keeps its old snapshot and turns the run red; the others still commit.
- Portworx (a site crawl) refreshes on Mondays and on manual runs. Kubernetes stays on its pinned release branch.
- Snapshots follow default branches, so they drift ahead of what is installed; `VERSIONS.md` shows the newest
  release next to each snapshot. Pin one with `REF_<name>=<tag>` if it must match a cluster.
- Vendored MCP binaries are never bumped automatically.

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| A source shows `missing clone … (run: server.py --sync)` | A full git mirror isn't fetched yet or the mirror doesn't exist under `$GIT_MIRROR_BASE` — create it, then `--sync` |
| `rhokp` / `argocd-docs` ❌ in `--check` | The endpoint env var isn't set or the service isn't reachable from this machine |
| Search returns nothing for a docs-only product | Folder under `docs/upstream/<name>` is empty or upstream moved its docs — rerun the sync script and check the file count |
| A source returns docs for the wrong version | Docs-only snapshots are single-version; pass `ref` only works for full mirrors. Check the installed version against the doc |
| Metrics come from the wrong cluster | A query went to the default datasource — resolve the `Moby / <cluster>` UID and pass it explicitly |
| `server.py` can't find the config | Set `TEAM_BRAIN_DIR` (default `~/team-brain`) |

## What is and isn't verified yet

- The `docs-refresh` workflow has been simulated locally step by step but has not yet run on GitHub; if `main` is
  protected, `github-actions[bot]` needs permission to push.
- CI exists (`.gitlab-ci.yml`, `.github/workflows/ci.yml`, both running `scripts/ci_checks.py`) but has only been run
  locally and against fault-injected copies of the repo — not yet on a real GitLab runner. The denylist check needs
  `BRAIN_DENYLIST_FILE` configured in the internal GitLab to do anything. There is no unit-test suite beyond the checks.
- The Kubernetes MCP runs with full access; only its start-up and tool list were checked in that mode (the
  restricted variant was tested against a throwaway local cluster). It has not been used on a cluster of ours; `okp-mcp` and its manifest have not been run at all.
- The Grafana MCP binary was started from the plugin on macOS arm64 and its tools listed; the linux and windows
  archives are checksum-verified only, and nothing has been run against our real Grafana. The shared HTTP
  deployment has not been exercised end to end.
- RHOKP and the Argo CD docs mirror depend on your internal endpoints; they were not reachable from the machine
  this was built on.
- Doc snapshots track upstream default branches at the time of the last sync (dates in each `.upstream` file).
- `session-start.sh` uses GNU `find -printf`/`timeout`, so its area list is empty on stock macOS.

## Glossary

| Term | Meaning |
|---|---|
| hub cluster / prod-hub | top management cluster; Cluster Navigator, Temporal, Argo CD |
| MCE | cluster running MCE/ACM/HyperShift that hosts control planes; runs its own Argo CD |
| hosted cluster | HyperShift cluster whose control plane runs on an MCE; where workloads run |
| UPI cluster | standalone cluster under no MCE |
| day1 / day2 | provisioning values repo (owns `mastertag`) / GitOps repo for what runs where |
| `mastertag` | `<major>.<minor>.<patch>-<arch>`, e.g. `4.16.27-x86_64` — a cluster's OCP version |
| RHOKP | Red Hat Offline Knowledge Portal (product docs, KCS, CVEs) |
| full mirror / docs-only snapshot | see [Offline knowledge](#offline-knowledge-the-team-knowledge-mcp-server) |
| ref | git branch/tag/commit used to read a mirror at a specific version |
