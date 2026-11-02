# Area `solr`

Apache Solr (SolrCloud) on Kubernetes (Solr operator) and on VMs: ZooKeeper, collections, replicas, backups.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** `storage`
- **Domain:** data platforms on Kubernetes and VMs (`data`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

SolrCloud on Kubernetes (Apache Solr operator) and on VMs: ZooKeeper ensemble, collections / shards / replicas, autoscaling-less operation, backups to S3 or a shared volume, upgrades.

## Not here

the search-engine choice vs Elasticsearch → `elastic`.

## Offline sources

`solr-ref-guide` (apache/solr `solr/solr-ref-guide/modules`, AsciiDoc, Apache-2.0 — planned), `solr-operator-docs` (apache/solr-operator `docs`, Apache-2.0 — planned). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<collection>`, `<namespace>`; basic-auth / security.json content are secrets. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- ZooKeeper placement and how a node loss looks on Kubernetes vs VMs

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
