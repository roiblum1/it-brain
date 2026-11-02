---
title: OCP ↔ Network — firewall flows an OpenShift cluster needs through Palo Alto (registry, DNS, NTP, LDAP, arrays, S3, egress IP)
type: interface
area: palo-alto
teams: [ocp, network, storage]
tags: [palo-alto, pan-os, panorama, firewall, flows, egress, egressip, snat, app-id, ports]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp, network]
source: it-brain-design
---

# OCP ↔ Network: firewall flows for a cluster

> **Draft contract.** The flow table is the useful part: when a new cluster is built or something "suddenly"
> times out, this is the list to compare against the policy. Ports marked *vendor default* must be confirmed
> against what we actually configured.

## How cluster traffic looks to the firewall

- **Pods leave with the node's IP** (OVN-Kubernetes SNAT) unless the namespace has an **EgressIP**, in which case
  they leave with that IP. So a rule "allow app X" needs an EgressIP; otherwise it is "allow every pod on these nodes".
- Hosted clusters (HyperShift): control-plane traffic comes from the **MCE's** nodes, workload traffic from the hosted
  cluster's own nodes — both sets of sources must be in the rules.
- App-ID: many of these flows are TLS; decide per rule whether App-ID or service/port is used, and whether the
  flow is decrypted (decryption breaks mutual TLS and pinned CAs).

## Flow table

| From | To | Port / proto | Purpose | Owner of the destination |
|---|---|---|---|---|
| cluster nodes | DNS `<ip>` | 53 udp/tcp | name resolution | network |
| cluster nodes | NTP `<ip>` | 123 udp | time (etcd and certificates depend on it) | network |
| cluster nodes | mirror registry | 443 tcp | images (air gap) | ocp |
| cluster nodes | LDAP / AD | 636 tcp | OAuth identity provider | `<…>` |
| cluster nodes (Trident controller) | ONTAP mgmt LIF | 443 tcp | Trident backend (REST) | storage |
| cluster nodes | ONTAP data LIFs | 2049 tcp (NFS), 3260 tcp (iSCSI), 4420 tcp (NVMe/TCP) | data path — ideally not through the firewall at all (`interfaces/storage-network-data-paths.md`) | storage |
| cluster nodes (CSI controller) | Unisphere for PowerMax | 8443 tcp (*vendor default*) | PowerMax CSI | storage |
| cluster nodes (CSI controller) | PowerFlex gateway | 443 tcp | PowerFlex CSI | storage |
| cluster nodes (CSI controller) | PowerScale OneFS API | 8080 tcp (*vendor default*) | PowerScale CSI | storage |
| cluster nodes | S3 endpoints | 443 tcp | OADP, Loki, registries (`interfaces/ocp-storage-object-s3.md`) | storage |
| Commvault media agents | cluster API | 6443 tcp | Commvault Kubernetes protection, if used | ocp |
| engineers / hub | cluster API | 6443 tcp | `oc`, Argo CD, Kubernetes MCP | ocp |
| hub Argo CD | cluster API | 6443 tcp | GitOps | ocp |
| Grafana | cluster Prometheus / Thanos | 443 / 9091 tcp | metrics | ocp |

## Who provides what

| Item | Provided by | Requested how | Lead time |
|---|---|---|---|
| Address objects / groups per `<cluster>` (node subnet, EgressIPs) | network | `<ticket queue>` | `<…>` |
| Rules for the flow table above, per site | network | one request per new cluster, from this table | `<…>` |
| EgressIP plan per namespace that needs its own rule | ocp | `<…>` | — |
| Notice before PAN-OS upgrades, HA failovers, decryption policy changes | network → ocp | `<channel>` | `<…>` |

## How each side checks its half (read-only)

OCP side: from a debug pod on the right node, test TCP reachability only (`curl -v telnet://<ip>:<port>` or
`nc -vz <ip> <port>`) — never put credentials on a command line.
Network side: traffic log for the source `<ip>` and port, the rule it hit (or `interzone-default` deny), session
table; read-only in Panorama / PAN-OS (`show session all filter source <ip>`).

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| New cluster: pulls / CSI / OAuth time out (ocp) | network: rules not created for its subnet | traffic log for the node subnet |
| One namespace's egress blocked after a reschedule (ocp) | EgressIP moved / unassigned, or rule only on the old IP | `oc get egressip` |
| Long-lived connections drop after N minutes (ocp) | network: session timeout shorter than the app's keepalive | rule's application timeout |
| TLS errors only through the firewall (ocp) | network: decryption on a flow that must not be decrypted | decryption policy for the rule |

## History

- 2026-11-02: drafted as part of the it-brain architecture (`docs/it-brain/ARCHITECTURE.md`)
