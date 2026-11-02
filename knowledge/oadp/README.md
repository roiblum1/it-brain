# Area `oadp`

OADP / Velero backup and restore of OpenShift workloads, its S3 targets and CSI snapshots.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** `storage`
- **Domain:** backup and restore (`backup`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

OADP operator / Velero on our clusters: DataProtectionApplication, BackupStorageLocation, CSI snapshot data movement (Kopia), restores, schedules.

## Not here

the S3 target's own behaviour → `ceph` / `netapp-ontap` / `dell-powerscale`.

## Offline sources

`rhokp` (OADP docs), `oadp-operator` docs (openshift/oadp-operator `docs/` — planned), `velero-docs` (vmware-tanzu/velero `site/content/docs` — planned). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<bucket>`, `<cluster>`; BSL credentials are secrets. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- BSL per cluster convention; restore test procedure as a runbook

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
