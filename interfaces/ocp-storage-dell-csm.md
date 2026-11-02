---
title: OCP ↔ Storage — Dell PowerMax, PowerFlex and PowerScale volumes for OpenShift through Dell CSM CSI drivers
type: interface
area: dell-powermax
teams: [ocp, storage]
tags: [dell, csm, powermax, powerflex, powerscale, isilon, csi, multipath, sdc, iscsi, fc, nvme-tcp]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp, storage]
source: it-brain-design
---

# OCP ↔ Storage: Dell arrays through Dell CSM

> **Draft contract.** Based on general Dell CSM behaviour; check every row against the driver versions we run
> (`dell-csm-docs` once the snapshot exists, `docs/it-brain/SOURCES-PLAN.md`).

## Parties

| Side | Team | Systems |
|---|---|---|
| consumer | `ocp` | Dell CSM operator / CSI drivers on each cluster, node multipath / iSCSI / NVMe config (MachineConfig), StorageClasses |
| provider | `storage` | PowerMax (`<array>`, Unisphere), PowerFlex (`<array>`, gateway, MDMs), PowerScale (`<array>`, access zones) |

## What crosses the boundary

| Array | Driver (CSI name) | Data path | What the node needs |
|---|---|---|---|
| PowerMax | csi-powermax (with its reverse proxy to Unisphere) | FC, iSCSI or NVMe/TCP | multipathd, iscsid or NVMe/TCP enabled through MachineConfig; zoning (FC) or storage VLAN (IP) |
| PowerFlex | csi-vxflexos | SDC (or NVMe/TCP) | SDC on every node that mounts volumes — how it gets onto RHCOS must be agreed |
| PowerScale | csi-isilon | NFS over SmartConnect | node IPs allowed in the access zone's exports |

Credentials (Unisphere user, PowerFlex gateway user, OneFS user) are Secrets in the driver namespace — never in git
or in the brain.

## Who provides what

| Item | Provided by | Requested how | Lead time |
|---|---|---|---|
| Array account per cluster + role | storage | `<ticket queue>` | `<…>` |
| Storage group / SRP / protection domain / access zone for the cluster | storage | `<…>` | `<…>` |
| FC zoning for new worker WWNs (`<wwn>`) | storage (SAN) | `<…>` | `<…>` |
| Storage VLANs / EPGs to the nodes | network | `interfaces/storage-network-data-paths.md` | `<…>` |
| Driver versions, ContainerStorageModule CRs, StorageClasses | ocp | day2 GitOps repo | — |
| MachineConfigs for multipath / iSCSI / NVMe | ocp | day2 GitOps repo | — |
| Notice before array code upgrades, Unisphere upgrades, cert changes | storage → ocp | `<channel>` | `<…>` |

## How each side checks its half (read-only)

OCP side:

```bash
oc get containerstoragemodule -A                   # CSM operator view of each driver
oc -n <driver-ns> get pods -o wide                 # controller + node pods per node
oc -n <driver-ns> logs deploy/<controller> -c driver --since=1h
oc get csidrivers; oc get sc
oc debug node/<node> -- chroot /host multipath -ll # paths per device (SAN)
```

Storage side: Unisphere / PowerFlex / OneFS UI or REST, read-only views of the cluster's hosts, volumes and sessions.

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| Controller cannot reach Unisphere / gateway / OneFS API (ocp) | network (firewall flow) or storage (account, cert) | `interfaces/ocp-network-palo-alto-flows.md`, then the account |
| Volume created but attach fails, no paths (ocp) | storage (masking / zoning / host group) or network (storage VLAN) | `multipath -ll` on the node, then masking view / zone |
| Half the paths down after a switch or array maintenance (both) | network or storage | which fabric / switch / director the dead paths share |
| PowerFlex mounts fail on new nodes only (ocp) | ocp: SDC missing on those nodes | SDC presence on the node |
| NFS mount denied on PowerScale (ocp) | storage: export / access-zone client list | node IP vs export clients |

## Escalation

`teams.json` → channels. Include `<cluster>`, node, volume handle (not array serials) and the exact error.

## Open questions

- Which protocols per array (FC vs iSCSI vs NVMe/TCP) and whether a cluster may mix them.
- How SDC is delivered to RHCOS for PowerFlex, and what an OCP upgrade does to it.
- Whether CSM modules beyond the driver (replication, observability, resiliency, authorization) are used.

## History

- 2026-11-02: drafted as part of the it-brain architecture (`docs/it-brain/ARCHITECTURE.md`)
