# Area `smb-cifs`

SMB/CIFS shares (ONTAP, PowerScale, Windows) and the SMB CSI driver.

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** `ocp`
- **Domain:** storage arrays and services (`storage`)

## Belongs here

SMB/CIFS shares on ONTAP, PowerScale or Windows used by workloads; the SMB CSI driver; AD / Kerberos joins; share permissions.

## Not here

array-specific config → `netapp-ontap` / `dell-powerscale`.

## Offline sources

`csi-driver-smb` (kubernetes-csi/csi-driver-smb `docs/` — planned). Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<share>`, AD domain → `<ad-domain>`, service-account credentials are secrets. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- how a namespace gets an SMB share and its credentials (Secret owner, rotation)

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
