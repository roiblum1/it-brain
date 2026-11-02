# Area `mongodb`

MongoDB on Kubernetes (operator) and on VMs: replica sets, sharding, backups, upgrades.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** `storage`
- **Domain:** data platforms on Kubernetes and VMs (`data`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

MongoDB replica sets and sharded clusters on Kubernetes (MongoDB Controllers for Kubernetes / community resources) and on VMs: elections, oplog window, backups, version upgrades (feature compatibility version).

## Not here

Ops Manager / Atlas specifics if not used here.

## Offline sources

`mongodb-kubernetes-docs` (mongodb/mongodb-kubernetes `docs`, plus `mongodb/docs` `content/kubernetes`, `content/manual` selected — licence to confirm). Note: `mongodb/mongodb-kubernetes-operator` (community operator) is **deprecated** in favour of `mongodb/mongodb-kubernetes` per its README (checked 2026-11-02). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<replset>`, `<namespace>`; connection strings carry credentials — never paste them. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- which operator each Kubernetes deployment uses, and the migration plan off the deprecated community operator if any still run it

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
