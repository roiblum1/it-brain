# Area `prefect`

Prefect: flows, deployments, work pools and workers, Prefect server on Kubernetes.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** —
- **Domain:** workflow orchestration (`workflow`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

Prefect server / Prefect on Kubernetes (prefect-helm), work pools and workers, deployments, flow-run states, retries and caching, blocks and how they hold credentials.

## Not here

Temporal-based orchestration (Redbull Workflows) → `temporal`; Airflow DAGs → `airflow`.

## Offline sources

`prefect-docs` (PrefectHQ/prefect `docs/v3`, Apache-2.0 — planned), `prefect-helm` (PrefectHQ/prefect-helm `charts` READMEs — planned). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<namespace>`, work-pool and deployment names that reveal projects → placeholders; block / API keys are secrets. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- when we use Prefect vs Temporal vs Airflow (one table), and how a Prefect worker gets cluster credentials

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
