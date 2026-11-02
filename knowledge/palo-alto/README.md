# Area `palo-alto`

Palo Alto firewalls and Panorama: zones, security and NAT policy, App-ID, HA.

- **Owner (approves MRs):** Network team (`network`)
- **Consulted:** `ocp`
- **Domain:** fabric and firewalls (`network`)

## Belongs here

PAN-OS / Panorama: zones, security and NAT rules, App-ID quirks, decryption, HA, upgrades, commit behaviour; how cluster egress and ingress cross the firewall.

## Not here

egress IPs / EgressFirewall inside OCP → `networking`.

## Offline sources

`pan-dev` (PaloAltoNetworks/pan.dev `products/panos`, `products/terraform`, `products/ansible` — developer/API docs, planned); PAN-OS admin guides → vendor-drop. Status of each: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<fw>`, `<device-group>`, `<zone>`, `<vsys>`, `<ip>`, rule names that reveal customers → `<rule>`; **API keys are secrets** (validate flags PAN-OS keys). General rules: `CLAUDE.md`, placeholders: `teams.json`.

## First pages we want

- flows an OpenShift cluster needs (mirror registry, NTP, DNS, LDAP, arrays, Grafana) as a table in `interfaces/ocp-network-palo-alto-flows.md`

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
