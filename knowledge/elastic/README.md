# Area `elastic`

Elastic stack on Kubernetes via ECK (Elasticsearch, Kibana, Fleet) and on VMs: shards, ILM, snapshots, upgrades.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** `storage`
- **Domain:** data platforms on Kubernetes and VMs (`data`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

Elasticsearch / Kibana / Fleet on OpenShift via ECK and on VMs: shard allocation, disk watermarks, ILM, snapshot repositories (S3), rolling upgrades, ECK operator behaviour and licensing.

## Not here

OpenShift's own logging stack (Loki / LokiStack) → `observability`.

## Offline sources

`eck-docs` (elastic/docs-content `deploy-manage/deploy/cloud-on-k8s` + `self-managed`, CC BY-NC-ND 4.0 — internal use only; elastic/cloud-on-k8s `docs/reference`, `docs/release-notes`, Elastic License 2.0 — planned). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<es-cluster>`, `<bucket>`, index names that reveal customers → placeholders; elastic user password / API keys are secrets. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- VM vs ECK: which clusters run where, and the snapshot repository convention

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
