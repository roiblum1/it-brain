# Area `vmware`

The VMware platform itself: vCenter, ESXi, vSAN, NSX (OpenShift-on-vSphere quirks stay in area vsphere).

- **Owner (approves MRs):** Virtualization team (`virtualization`)
- **Consulted:** `ocp`, `storage`, `network`
- **Domain:** hypervisors (`virtualization`)

## Belongs here

vCenter / ESXi / vSAN / NSX behaviour, maintenance and upgrades, DRS / HA effects on VMs, datastore and storage-policy design.

## Not here

OpenShift-on-vSphere installer / machine API / vSphere CSI from the cluster side → `vsphere`.

## Offline sources

`vsphere-csi-driver` docs (kubernetes-sigs/vsphere-csi-driver `docs/` — planned); `powercli-examples` and `powershell-docs` (snapshots) for automation; VMware product docs → vendor-drop. Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<vcenter>`, `<datastore>`, cluster / host names → placeholders. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- vCenter / cluster layout per site, and which VMs are OpenShift nodes (so maintenance does not drain a cluster by surprise); PowerCLI recipes live in `knowledge/powercli/`, migrations to KubeVirt in `knowledge/kubevirt/`

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
