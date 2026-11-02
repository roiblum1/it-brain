# Area `dell-powerscale`

Dell PowerScale (Isilon) OneFS: access zones, NFS/SMB/S3, and the PowerScale CSI driver.

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** `ocp`
- **Domain:** storage arrays and services (`storage`)

## Belongs here

OneFS access zones, NFS exports, SMB shares, S3 on OneFS, SmartQuotas, SyncIQ, the PowerScale CSI driver.

## Not here

SMB share conventions shared with ONTAP → `smb-cifs`.

## Offline sources

`dell-csm-docs` (planned), `dell/csi-powerscale` docs (planned); OneFS guides → vendor-drop. Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<array>`, `<access-zone>`, `<share>`, `<ip>` (SmartConnect zones are hostnames: `<array>-sc`). General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- access-zone ↔ cluster mapping; quota behaviour seen from a PVC

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
