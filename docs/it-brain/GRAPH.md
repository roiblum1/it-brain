---
title: it-brain knowledge graph — graphify graph.json and Obsidian vault (teams, domains, areas, pages, links)
type: reference
area: meta
tags: [it-brain, graph, graphify, obsidian, links, navigation]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: it-brain-design
---

# it-brain knowledge graph (graphify + Obsidian)

The brain is already a graph: `teams.json` says which team owns each area, and pages cite each other by repo path
(`knowledge/<area>/<page>.md`). `scripts/brain_graph.py` turns that into files two tools can open directly, so
navigation is a click (Obsidian) or one command (graphify) instead of a search.

```
teams.json ──┐                                   ┌─► graphify-out/graph.json  (committed, CI-checked)
frontmatter ─┼─► scripts/brain_graph.py ─────────┤      graphify query / path / explain / export html|obsidian
path refs  ──┘    (deterministic, stdlib, no LLM) └─► ~/it-brain-vault/          (generated, not committed)
                                                         Obsidian: HOME → team → area → page, coloured by domain
```

## What is in the graph

| Nodes | From |
|---|---|
| `team:<t>`, `domain:<d>`, `area:<a>` | `teams.json` |
| one node per page (id = repo path) | `knowledge/`, `runbooks/`, `interfaces/`, `incidents/`, `inbox/`, `mcp/servers/`, `docs/` (not `docs/upstream`) and every area charter |
| `tag:<tag>` | tags used by two or more pages |

| Edge | Meaning |
|---|---|
| `in_area`, `in_domain` | page → area → domain |
| `owned_by`, `consulted` | area → team |
| `concerns` | page → team (frontmatter `teams:`; every interface page has two or more) |
| `links_to` | page → page, from repo paths in backticks or Markdown links — the same references team-knowledge's `related` tool follows |
| `tagged` | page → shared tag |

Every edge is `confidence: EXTRACTED` (read from the files); nothing is inferred.

## graphify

`graphify-out/graph.json` is networkx node-link JSON with the fields graphify uses, so no `/graphify` extraction
run is needed (that run sends docs through an LLM — not available in the air gap). Tested with graphify 0.9.100
(PyPI `graphifyy`) on 2026-11-02: `explain`, `query`, `path`, `export obsidian` and `export html` work on it.

```bash
python3 scripts/brain_graph.py graph                       # regenerate (brain-git.sh submit does it for you)
graphify explain "trident" --graph graphify-out/graph.json  # an area: owner, consulted teams, pages
graphify query "S3 bucket for OADP backups" --graph graphify-out/graph.json
graphify path "palo-alto" "trident" --undirected --graph graphify-out/graph.json
graphify export html --graph graphify-out/graph.json        # graphify-out/graph.html, open in a browser
```

graphify is optional and installed by each engineer (Python ≥ 3.10; in the air gap from the internal PyPI mirror).
If someone does run `/graphify .` on the whole repo, `.graphifyignore` keeps `docs/upstream`, vendored binaries and
generated files out.

## Obsidian

```bash
python3 scripts/brain_graph.py obsidian --out ~/it-brain-vault   # rebuild any time; keeps your .obsidian settings
```

Open the folder in Obsidian (*Open folder as vault*) and start at `HOME.md`. The vault:

- holds every brain page with repo-path references rewritten to Obsidian wikilinks — the graph view shows real page links;
- has hub notes `_hubs/teams/<team>`, `_hubs/areas/<area>`, `_hubs/domains/<domain>`, and every page ends with a link to its area hub;
- tags each page `area/<a>`, `domain/<d>`, `team/<owner>`, and colours the graph by domain (`.obsidian/graph.json`);
- leaves out `docs/upstream` (thousands of vendor pages), which is what keeps it fast.

It is **read-only by convention**: it is rebuilt from git, so edits made there are lost. Write pages in the repo
(through `/team-brain:brain-learn` or a branch) and rebuild. Opening the repository itself as a vault also works;
`.obsidian/app.json` excludes `docs/upstream`, vendored binaries and `graphify-out/` there, and new notes go to `inbox/`.

## Keeping the graph useful

- `python3 scripts/brain_graph.py stats` lists the most linked-to pages and pages with no links in or out — cite
  related pages by path to connect them.
- CI's `graph` check fails when `graph.json` is stale, like `INDEX.md`.

## History

- 2026-11-02: created; tested with graphify 0.9.100 and an exported vault
