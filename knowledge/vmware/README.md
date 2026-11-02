# Area `vmware`

The VMware platform itself: vCenter, ESXi, vSAN, NSX (OpenShift-on-vSphere quirks stay in area vsphere).

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** `storage`, `network`
- **Domain:** hypervisors (`virtualization`)

> **Ownership is provisional** — not yet confirmed by the teams (`docs/it-brain/ROADMAP.md`).

## Belongs here

vCenter / ESXi / vSAN / NSX behaviour, maintenance and upgrades, DRS / HA effects on VMs, datastore and storage-policy design.

## Not here

OpenShift-on-vSphere installer / machine API / vSphere CSI from the cluster side → `vsphere`.

## Offline sources

`vsphere-csi-driver` docs (kubernetes-sigs/vsphere-csi-driver `docs/` — planned); VMware product docs → vendor-drop. Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<vcenter>`, `<datastore>`, cluster / host names → placeholders. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- who owns vCenter (ownership is provisional — confirm a team)

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
