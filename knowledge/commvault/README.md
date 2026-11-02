# Area `commvault`

Commvault backup: storage policies, media agents, Kubernetes/OpenShift protection.

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** `ocp`
- **Domain:** backup and restore (`backup`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

Commvault CommServe, media agents, storage policies / plans, Kubernetes / OpenShift protection, restores, retention.

## Not here

OADP-based backups → `oadp`; where backups land on S3 / arrays → the array area.

## Offline sources

no public docs repo — Commvault documentation → vendor-drop (offline export, not committed). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<media-agent>`, `<storage-policy>`, CommServe hostname → placeholder. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- what Commvault protects on OpenShift vs what OADP protects (one table, no overlap)

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
