# Area `ceph`

Ceph clusters: RADOS, RBD, CephFS, and the RGW S3 object gateway.

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** —
- **Domain:** storage arrays and services (`storage`)

## Belongs here

Ceph clusters we run outside OpenShift: health states, PG / OSD behaviour, RBD and CephFS, **RGW (S3)** users, buckets, quotas, multisite, cephadm upgrades.

## Not here

Ceph *inside* OpenShift (Rook / ODF) → `odf`; S3 consumers (OADP, registry, Loki) → `interfaces/ocp-storage-object-s3.md`.

## Offline sources

`ceph-docs` (ceph/ceph `doc/`, reStructuredText — planned; large, consider `doc/radosgw`, `doc/rados`, `doc/rbd`, `doc/cephfs`, `doc/cephadm` only). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<array>` for cluster fsid/name, `<pool>`, `<bucket>`, S3 access/secret keys are secrets. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- RGW endpoint, TLS and bucket-policy conventions for cluster consumers

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
