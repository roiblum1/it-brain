# Area `dell-powermax`

Dell PowerMax arrays, Unisphere, and the PowerMax CSI driver (Dell CSM).

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** `ocp`
- **Domain:** storage arrays and services (`storage`)

## Belongs here

PowerMax arrays, Unisphere for PowerMax, storage groups, masking views, SRDF, the PowerMax CSI driver and its reverse proxy, FC / iSCSI / NVMe-TCP host connectivity.

## Not here

fabric zoning and VLANs → `interfaces/storage-network-data-paths.md`; node multipath config from the cluster side → `storage`.

## Offline sources

`dell-csm-docs` (dell/csm-docs — planned), driver repo `dell/csi-powermax` docs (planned); Unisphere / Solutions Enabler guides → vendor-drop. Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<array>` / `<serial>` (array SID), `<wwn>`, `<iqn>`, `<nqn>`, `<pool>` (SRP). General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- how a new cluster gets host groups / masking; CSI driver version ↔ OCP matrix

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
