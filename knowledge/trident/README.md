# Area `trident`

NetApp Trident CSI on OpenShift: backends, StorageClasses, snapshots, Trident Protect.

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** `ocp`
- **Domain:** storage arrays and services (`storage`)

## Belongs here

TridentBackendConfig / TridentOrchestrator behaviour, ontap-nas / ontap-san / ontap-nas-economy drivers, snapshots and clones, volume import, Trident Protect, upgrades.

## Not here

the array side (SVM, export policy, aggregate) → `netapp-ontap`; generic PVC behaviour → `storage`.

## Offline sources

`trident-docs` (NetAppDocs/trident — planned), full mirror `NetApp/trident` (optional, for code). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<svm>`, `<volume>`, backend credentials are Secrets — never copy them. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- Trident ↔ ONTAP ↔ OCP support matrix row in `knowledge/meta/fleet-versions.md`; PVC Pending triage (see `interfaces/ocp-storage-netapp-trident.md`)

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
