# Area `cisco-aci`

Cisco ACI fabric: tenants, VRFs, bridge domains, EPGs, contracts, L3Outs, APIC.

- **Owner (approves MRs):** Network team (`network`)
- **Consulted:** `ocp`
- **Domain:** fabric and firewalls (`network`)

## Belongs here

ACI tenants / VRFs / BDs / EPGs / contracts, L3Outs, endpoint learning, APIC upgrades, faults and their meaning, how cluster node networks map onto the fabric.

## Not here

OVN-K / ingress inside the cluster → `networking`; firewall policy → `palo-alto`.

## Offline sources

`aci-containers` (noironetworks/aci-containers — only if the ACI CNI is used; planned), `ansible-aci` / Terraform provider docs for object models (planned); APIC configuration guides → vendor-drop. Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<tenant>`, `<vrf>`, `<bd>`, `<epg>`, `<l3out>`, `<vlan>`, `<subnet>`, `<ip>`, leaf/spine names → `<leaf>`. General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- EPG / BD layout for an OpenShift cluster (machine, ingress VIP, storage networks); what a new cluster needs from the fabric

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
