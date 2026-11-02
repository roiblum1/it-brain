---
title: Frontmatter schema
type: reference
area: meta
tags: [meta, schema]
applies_to: []
confidence: verified
last_verified: 2026-11-02
owners: [platform-team]
---

# Frontmatter schema

Every Markdown file under `knowledge/`, `runbooks/`, `interfaces/`, `incidents/`, `inbox/`, `mcp/servers/`
starts with a YAML block (`README.md` files are area/folder charters and are exempt). `scripts/brain.py validate` enforces it.

```yaml
---
title: HyperShift NodePool stuck in "Updating" after CAPI pre-drain hook timeout
type: knowledge            # knowledge | runbook | interface | incident | inbox | mcp | reference
area: hypershift           # a key of teams.json → areas (python3 scripts/brain.py teams)
teams: [ocp, storage]      # optional; REQUIRED (>= 2) on interface pages; keys of teams.json → teams
tags: [nodepool, capi, drain]
applies_to: [ocp-4.16, ocp-4.17, mce-2.7]   # versions / hardware / cluster types; [] = general
confidence: observed       # verified | observed | hypothesis
last_verified: 2026-10-03  # date someone last confirmed this is still true
owners: [roi]              # who to ask
source: claude-session     # optional: incident id, MR, ticket, "claude-session", upstream URL
---
```

Incidents additionally require:

```yaml
severity: sev2             # sev1 | sev2 | sev3 | sev4
status: resolved           # open | mitigated | resolved
clusters: [site2-gpu-03]   # cluster names (no IPs)
started: 2026-10-01T09:12+03:00
resolved: 2026-10-01T11:40+03:00
```

Rules

- `title` is a sentence that would match what someone greps for during an outage.
- `applies_to` uses short tokens: `ocp-4.16`, `k8s-1.29`, `mce-2.7`, `hgx-h200`, `xe9680`,
  `vsphere-8`, `sno`, `hosted-cp`; for the storage/network/virtualization estates the same shape, e.g.
  `ontap-9.16`, `trident-25.06`, `powermax-10.2`, `onefs-9.7`, `ceph-19`, `odf-4.18`, `aci-6.0`, `panos-11.1`,
  `esxi-8`, `aos-6.10`.
- `teams` names every team a page concerns beyond the area's owner (the owner comes from `teams.json`).
  Interface pages list both (or all) sides; incidents list every team that took part.
- The folder decides `type`: `knowledge/`→knowledge, `runbooks/`→runbook, `interfaces/`→interface,
  `incidents/`→incident, `inbox/`→inbox, `mcp/servers/`→mcp.
- `confidence` is honest. A single observation is `observed`, not `verified`.
