# Area `netapp-ontap`

NetApp ONTAP clusters: SVMs, volumes, LIFs, export policies, SnapMirror, ONTAP S3.

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** —
- **Domain:** storage arrays and services (`storage`)

## Belongs here

SVM / LIF / export-policy behaviour, SnapMirror and SnapMirror active sync, ONTAP S3, QoS, upgrades (ONTAP and firmware), AutoSupport findings, ONTAP REST/CLI quirks.

## Not here

Trident backends and StorageClasses → `trident`; SMB share design → `smb-cifs`; storage VLANs/LIF routing on the fabric → `interfaces/storage-network-data-paths.md`.

## Offline sources

`ontap-docs` (NetAppDocs/ontap, AsciiDoc — planned snapshot), `ontap-mcp` docs (planned); vendor KBs → vendor-drop (not committed). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<array>` for ONTAP cluster names, `<svm>`, `<aggr>`, `<volume>`, `<ip>` for LIFs, `<serial>` for node serials. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- export-policy rules our clusters need; SVM-per-tenant/cluster convention; upgrade order (ONTAP vs Trident support matrix)

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
