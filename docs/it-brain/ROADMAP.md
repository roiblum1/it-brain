---
title: it-brain roadmap — phases, decisions needed from the teams, and what is done on the branch
type: reference
area: meta
tags: [it-brain, roadmap, decisions, phases, migration]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: it-brain-design
---

# it-brain roadmap

Branch: `claude/it-brain-multi-team-n7n6kg` — **not to be merged into team-brain's `main`**. Architecture:
`docs/it-brain/ARCHITECTURE.md`.

## Phase 0 — architecture and skeleton (this branch) ✅

- [x] `teams.json` registry: 3 teams, 35 areas (22 new) in 9 domains, owners / consulted, placeholder vocabulary
- [x] `knowledge/<area>/README.md` charter for every area
- [x] `interfaces/` page type, template, and 7 draft contracts (all `hypothesis`)
- [x] `brain.py`: areas from the registry, `teams:` field, `interface` type, `stale --team`, `teams`, `codeowners`
- [x] `.gitlab/CODEOWNERS` generated from the registry
- [x] CI: `teams` check; leak checks for IQN / NQN / WWN; PAN-OS API key pattern in `validate`
- [x] Team profile in the SessionStart hook (`IT_BRAIN_TEAM`)
- [x] Docs: architecture, teams guide, sources plan (repos/paths/licences checked), tools plan, this roadmap
- [x] Workflow and data areas: temporal, prefect, airflow, spark, elastic (ECK + VMs), solr, mongodb; `domain` per area
- [x] server-scan section (`knowledge/server-scan/`, runbooks, `mcp/servers/server-scan.md`) from the repo's code and docs
- [x] Redbull Workflows (Temporal) pages in `knowledge/temporal/` from the orchestrator's docs site
- [x] Graph: `scripts/brain_graph.py` → `graphify-out/graph.json` (CI-checked) and an Obsidian vault export (`docs/it-brain/GRAPH.md`)

## Phase 1 — make it its own brain

- [ ] Teams answer the **Decisions needed** below
- [ ] Create the GitLab project `it-brain`, push this branch as its `main`, set *require code owner approval*
- [ ] Replace placeholder group handles in `teams.json` (`@it-brain/<team>-team`), regenerate CODEOWNERS
- [ ] Rename in one change: plugin `team-brain` → `it-brain`, `TEAM_BRAIN_DIR` → `IT_BRAIN_DIR` (keep the old name as
      a fallback for one release), cache `~/.cache/team-brain` → `~/.cache/it-brain`, skill prefixes, README / CLAUDE.md
- [ ] Freeze team-brain `main` (README banner pointing to it-brain); existing pages already live here
- [ ] Each team's denylist entries in `BRAIN_DENYLIST_FILE` (internal CI variable)
- [ ] First 3 real pages per team; fill the interface pages' `<…>` cells

## Phase 2 — vendor docs offline

- [ ] Snapshot the public sources in `docs/it-brain/SOURCES-PLAN.md` §A (start: `trident-docs`, `dell-csm-docs`,
      `ceph-docs` selected folders, `velero-docs` for our OADP's Velero, `pan-dev`, `temporal-docs`), with catalog rows and golden queries
- [ ] Measure snapshot sizes; for `ontap-docs` and `ceph-docs` keep only the folders listed
- [ ] Vendor-drop: licence decision per manual, converter (PDF/HTML → Markdown) and the folder on the shared server
- [ ] `applies_to` tokens and `fleet-versions.md` rows for array / fabric / firewall versions

## Phase 3 — read-only live tools

- [ ] `ontap-mcp --read-only` against a lab ONTAP, `mcp/servers/ontap.md`, vendored + pinned
- [ ] APIC read-only, then PAN-OS / Panorama read-only
- [ ] Decide: in-house `it-infra-readonly` server vs one third-party server per system (`docs/it-brain/TOOLS-PLAN.md`)

## Phase 4 — team-specific skills

- [ ] `storage-debug` (PVC → CSI → array → path) and `network-debug` (flow → rule → EPG → endpoint) skills, in the
      style of `hypershift-debug`, written from the interface pages once they are `observed`
- [ ] Per-team golden queries in `tests/golden-queries.json`

## Decisions needed

| # | Decision | Default on this branch | Who decides |
|---|---|---|---|
| 1 | Separate GitLab project `it-brain`, or keep growing team-brain | separate project (Phase 1) | all teams |
| 2 | Owner of **VMware** and **Nutanix** (or a fourth *virtualization* team) | `ocp`, provisional | management |
| 3 | Owner of **ODF** | `storage`, provisional | ocp + storage |
| 4 | Owner of **OADP** and **Commvault**, or a *backup* team | OADP `ocp`, Commvault `storage`, both provisional | ocp + storage |
| 5 | Who owns the Avi / AKO controller and DNS/NTP/DHCP (no area yet) | AKO stays in `networking` (ocp) | ocp + network |
| 6 | Real GitLab groups for CODEOWNERS | placeholders | each team |
| 7 | Which vendor manuals we may store offline (licence) | none until confirmed | each owning team |
| 8 | Does any cluster use the **ACI CNI** instead of OVN-Kubernetes | assumed no | ocp + network |
| 9 | Is FC zoning storage or network | storage (SAN) | storage + network |
| 10 | Who owns Prefect, Airflow, Spark, ECK / Elastic, Solr, MongoDB (a *data platform* team?) | `ocp`, provisional | management |
| 11 | Where the Redbull Workflows docs site's source lives (to make it a `git_repo` source) | read once from the site | ocp |
| 12 | Mirror `team-redbull/server-scan` into GitLab and enable its source | entry present, disabled | ocp |

## History

- 2026-11-02: created with Phase 0 done
