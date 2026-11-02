---
title: Virtualization ↔ Network — VLANs / EPGs for KubeVirt VM networks, VM MAC and IP ownership, live-migration traffic, endpoint moves on the fabric, firewall rules for VMs
type: interface
area: kubevirt
teams: [virtualization, network, ocp]
tags: [kubevirt, vm-networks, vlan, epg, aci, localnet, linux-bridge, mac, kubemacpool, ip, live-migration, migration-network, endpoint-learning, firewall, palo-alto]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization, network]
source: it-brain-design
---

# Virtualization ↔ Network: VM networks

> **Draft contract.** VMs on secondary networks behave like servers on the fabric, not like pods: they have their own
> MACs and IPs on real VLANs and they move between nodes. Fill the `<…>` cells in an MR approved by all three teams.

## Parties

| Side | Team | Systems |
|---|---|---|
| consumer | `virtualization` | VM NICs, NADs, MTV network maps |
| platform | `ocp` | node bonds/VLANs and bridges (NMState NNCP), OVN-K localnet bridge mappings, Multus |
| provider | `network` | ACI (`<tenant>`, `<bd>`, `<epg>`, `<vlan>`), Palo Alto rules, IPAM |

## What crosses the boundary

- **VLANs to every worker that may run the VM** (not just one node — VMs migrate). For localnet, every node with the
  bridge mapping (`knowledge/kubevirt/kubevirt-networking-masquerade-bridge-multus-localnet-sriov.md`).
- **MAC addresses**: kubemacpool allocates per cluster; two clusters on one VLAN can collide — agree a range per cluster
  or separate VLANs. MTV keeps the source VM's MAC (VMware OUI) when migrating.
- **IP addresses**: guest DHCP on the VLAN, static, or OVN-K IPAM (`subnets`, `allowPersistentIPs`). Who owns the range: `<…>`.
- **Endpoint moves**: a live migration moves the VM's MAC/IP to another leaf port; the fabric must re-learn quickly
  (`interfaces/ocp-network-aci-fabric.md`, endpoint learning / GARP detection) — otherwise traffic is lost after each migration.
- **Live-migration traffic**: node to node, on the pod network or a dedicated migration network (a NAD on separate NICs);
  bandwidth-heavy during drains and upgrades.
- **Firewall**: VMs on localnet/bridge networks bypass cluster egress (no EgressIP SNAT) — rules are per VM IP/subnet
  (`interfaces/ocp-network-palo-alto-flows.md`). MTV needs nodes → vCenter 443, ESXi 443 and 902.

## Who provides what

| Item | Provided by | Requested how | Lead time |
|---|---|---|---|
| VLAN / EPG per VM network, trunked to all VM-capable workers | network | `<ticket queue>` | `<…>` |
| Node bridge / bond config (NNCP), localnet bridge mappings | ocp | day2 GitOps | — |
| NAD per VM network and namespace | virtualization (or ocp) | day2 GitOps | — |
| IP range / DHCP for each VM network | network | `<…>` | `<…>` |
| MAC range per cluster (kubemacpool) | virtualization, agreed with network | HyperConverged / CNAO config `<…>` | — |
| Dedicated migration network (optional) | network + ocp | `<…>` | `<…>` |
| Firewall rules for VM subnets | network | per-cluster flow table | `<…>` |

## How each side checks its half (read-only)

```bash
oc get nncp; oc get nnce                                   # node network config applied
oc get net-attach-def -A
oc get vmi -A -o json | jq -r '.items[] | .metadata.name as $n | .status.interfaces[]? | "\($n) \(.name) \(.mac) \(.ipAddress // "-")"'
```

Network side: endpoint table for `<mac>`/`<ip>` (which leaf, move history), VLAN on the node ports, faults on the EPG.

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| VM unreachable right after a migration, recovers minutes later (virtualization) | network: endpoint move not detected | endpoint tracker for the VM MAC |
| VM works on some nodes only (virtualization) | network: VLAN not on all worker ports; or ocp: NNCP not applied there | NNCE per node, leaf ports |
| MAC flapping / duplicate MAC faults (network) | virtualization: two clusters' MAC pools overlap | kubemacpool ranges |
| Drains slow, other traffic suffers (ocp) | migration traffic on the pod network | dedicated migration network |

## Open questions

- Linux bridge or OVN-K localnet as our standard for VM VLANs?
- Who allocates VM IPs — network IPAM, DHCP on the VLAN, or OVN-K IPAM?
- Do we need a dedicated migration network?

## History

- 2026-11-02: drafted with the KubeVirt deep dive (`knowledge/kubevirt/README.md`)
