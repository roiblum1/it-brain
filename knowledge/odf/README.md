# Area `odf`

OpenShift Data Foundation (Rook-Ceph, NooBaa / MCG) running on or consumed by our clusters.

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** `ocp`
- **Domain:** storage arrays and services (`storage`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

OpenShift Data Foundation: StorageCluster, Rook-Ceph inside OCP, NooBaa / Multicloud Object Gateway, external-mode ODF against our Ceph, ODF upgrades.

## Not here

the external Ceph cluster itself → `ceph`.

## Offline sources

`rhokp` (ODF product docs — filter by version), `rook-docs` (rook/rook `Documentation` — planned), `ocs-operator` docs (planned). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<cluster>`, `<pool>`, `<bucket>`. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- which clusters run ODF internal vs external mode, and who is paged for each (ownership is provisional)

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
