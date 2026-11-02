# Area `dell-powerflex`

Dell PowerFlex (SDS, SDC on nodes), its gateway, and the PowerFlex CSI driver.

- **Owner (approves MRs):** Storage team (`storage`)
- **Consulted:** `ocp`
- **Domain:** storage arrays and services (`storage`)

## Belongs here

PowerFlex protection domains, storage pools, SDS/SDC/MDM behaviour, the gateway, the PowerFlex CSI driver (SDC on OpenShift nodes), NVMe-TCP mode.

## Not here

SDC kernel module / MachineConfig rollout on nodes is shared with `ocp` — write it here and link from `storage`.

## Offline sources

`dell-csm-docs` (planned), `dell/csi-powerflex` docs (planned); PowerFlex admin guides → vendor-drop. Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<array>` (system id), `<pool>` (protection domain / storage pool), `<ip>` for MDM addresses. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- SDC on RHCOS: how it is delivered and what breaks on OCP upgrade

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
