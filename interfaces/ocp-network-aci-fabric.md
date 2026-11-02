---
title: OCP ↔ Network — what an OpenShift cluster needs from the Cisco ACI fabric (EPG, BD, subnets, VIPs, MTU, endpoint learning)
type: interface
area: cisco-aci
teams: [ocp, network]
tags: [aci, apic, epg, bridge-domain, vrf, l3out, mtu, vip, endpoint-learning, garp, ovn-kubernetes]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp, network]
source: it-brain-design
---

# OCP ↔ Network: what a cluster needs from ACI

> **Draft contract.** Assumes ACI is the underlay and OVN-Kubernetes is the cluster CNI. If any cluster uses
> the ACI CNI plugin (`aci-containers`), that changes most rows — record it here first.

## Parties

| Side | Team | Systems |
|---|---|---|
| consumer | `ocp` | node NICs and bonds (NMState), OVN-Kubernetes, ingress/API VIPs, AKO service VIPs, EgressIPs |
| provider | `network` | ACI fabric: `<tenant>`, `<vrf>`, `<bd>`, `<epg>`, contracts, `<l3out>` |

## What a new cluster needs

| Item | Provided by | Notes |
|---|---|---|
| Machine network: EPG + BD + `<subnet>` per `<cluster>` (or shared per site — decide) | network | node count + growth decides the subnet size |
| VLAN(s) on the leaf ports of the cluster's servers / ESXi / AHV hosts | network | bonds/LACP must match the leaf config |
| Storage networks (NFS, iSCSI, NVMe/TCP) as separate EPGs | network | `interfaces/storage-network-data-paths.md` |
| VIP ranges: API / ingress (UPI, bare metal), AKO / Avi service engines, EgressIPs | network | VIPs move between nodes — see endpoint learning below |
| Contracts between cluster EPGs and the services they need | network | the flow list lives in `interfaces/ocp-network-palo-alto-flows.md` |
| L3Out / routing to other sites and to the firewall | network | |
| MTU end to end | network + ocp | OVN-Kubernetes Geneve uses 100 bytes: pod MTU = node MTU − 100 |
| Notice before APIC / leaf upgrades and port changes | network → ocp | maintenance windows per site |

## Endpoint learning and moving IPs

Floating IPs (API/ingress VIPs, EgressIPs, AKO VIPs) move between nodes by gratuitous ARP. If the bridge domain
does not detect the move quickly, traffic keeps going to the old leaf until the endpoint ages out. Settings to
review with the network team (hypothesis — check against our APIC version): endpoint move detection based on
GARP on the BD, IP aging, "limit IP learning to subnet", and endpoint loop protection / rogue endpoint control
(a VIP flapping between nodes can look like a rogue endpoint and get quarantined).

## How each side checks its half (read-only)

```bash
oc get network.config cluster -o jsonpath='{.status.clusterNetworkMTU}{"\n"}'
oc get nncp,nnce                                   # NMState policies / per-node enactments
oc get egressip                                    # which node holds each EgressIP
oc debug node/<node> -- chroot /host ip -d link show <bond>
```

Network side: APIC endpoint tracker for `<ip>` (which leaf/port, move history), faults on the EPG/BD, contract hit counts.

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| API / ingress VIP unreachable for minutes after a node reboot (ocp) | network: endpoint not moved (GARP detection off) | APIC endpoint tracker for the VIP |
| Small requests work, large transfers hang (both) | MTU mismatch somewhere on the path | `ping -M do -s <size>` between nodes |
| One node isolated after a leaf upgrade (ocp) | network: port / VLAN / bond config | leaf port state, LACP |
| Rogue endpoint / loop fault on a VIP (network) | ocp: VIP flapping (keepalived / EgressIP rebalancing) | node events at the same time |

## Open questions

- Does any cluster use the ACI CNI (`aci-containers`)? If yes, which, and who owns the ACI CNI operator?
- EPG per cluster vs per site — and who allocates subnets (IPAM source of truth)?

## History

- 2026-11-02: drafted as part of the it-brain architecture (`docs/it-brain/ARCHITECTURE.md`)
