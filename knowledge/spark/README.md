# Area `spark`

Apache Spark on Kubernetes (spark-submit, Spark operator) and on VMs/YARN: executors, shuffle, S3/HDFS access.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** `storage`
- **Domain:** data platforms on Kubernetes and VMs (`data`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

Spark on Kubernetes (spark-submit to the API server, the Kubeflow Spark operator), on VMs / YARN; executor sizing, shuffle and spill, dynamic allocation, S3A / object-store access, history server.

## Not here

the S3 provider's behaviour → `ceph` / `netapp-ontap` / `dell-powerscale` (`interfaces/ocp-storage-object-s3.md`).

## Offline sources

`spark-docs` (apache/spark `docs`, Apache-2.0 — pin to the Spark version we run), `spark-operator-docs` (kubeflow/spark-operator `docs`, `README.md`, `examples` — planned). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<bucket>`, `<namespace>`; S3 keys in spark-defaults or env are secrets. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- S3A settings that work against our S3 endpoints (path style, CA, committers)

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
