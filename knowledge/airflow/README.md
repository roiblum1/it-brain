# Area `airflow`

Apache Airflow on Kubernetes and on VMs: scheduler, executors (Kubernetes / Celery), DAG deployment, metadata DB.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** —
- **Domain:** data platforms on Kubernetes and VMs (`data`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

Airflow on Kubernetes (official Helm chart, KubernetesExecutor / CeleryExecutor, KEDA) and on VMs; DAG deployment (git-sync, image), metadata DB, connections and variables, upgrades between majors.

## Not here

Spark job behaviour → `spark`; the workflow-engine choice → `prefect` / `temporal`.

## Offline sources

`airflow-docs` (apache/airflow `airflow-core/docs` + `chart/docs`, reStructuredText, Apache-2.0 — planned). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<dag>`, `<namespace>`, connection URIs contain credentials — never paste them. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- executor and DAG-delivery convention per environment (Kubernetes vs VM)

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
