---
title: Storage ↔ Network — storage data paths (NFS, iSCSI, NVMe/TCP, FC) from cluster nodes to arrays — VLANs, MTU, multipath, zoning
type: interface
area: netapp-ontap
teams: [storage, network, ocp]
tags: [storage-network, nfs, iscsi, nvme-tcp, fc, zoning, mtu, jumbo-frames, multipath, lif, vlan, epg]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [storage, network]
source: it-brain-design
---

# Storage ↔ Network: data paths from nodes to arrays

> **Draft contract.** Three teams meet here: the node (ocp), the fabric (network), the array (storage). Most
> "the storage is slow" incidents are decided by which hop is at fault, so each hop needs an owner and a check.

## The path, hop by hop

| Hop | Owner | What can go wrong |
|---|---|---|
| Node NIC / bond / VLAN interface (NMState), multipathd, iscsid, NVMe/TCP config | ocp | wrong VLAN, bond mode mismatch, multipath not configured, MTU |
| Leaf ports, storage EPG/BD (ACI), uplinks | network | VLAN not on the port, MTU, congestion, a leaf in maintenance |
| FC fabric and zoning (if FC) | storage (SAN) — confirm | zone missing for new WWNs (`<wwn>`) |
| Array ports / data LIFs (`<array>`, `<svm>`) | storage | LIF on a degraded port, failover migrated LIFs to one node |

Design principles (to confirm): storage traffic stays on its own VLANs/EPGs and does **not** cross the firewall;
jumbo frames are either end to end or not at all; every SAN volume has paths through both fabrics.

## Who provides what

| Item | Provided by | Requested how |
|---|---|---|
| Storage VLAN / EPG per site, with subnets for nodes and LIFs | network | `interfaces/ocp-network-aci-fabric.md` |
| Data LIFs / target ports and their IPs | storage | `<…>` |
| Node-side config (NMState, MachineConfig for multipath/iSCSI/NVMe) | ocp | day2 repo |
| FC zoning for new nodes | storage (SAN) | `<…>` |
| Agreed MTU per storage network | network + storage + ocp | recorded in `knowledge/<array-area>/` |

## How each side checks its half (read-only)

```bash
# node (ocp)
oc debug node/<node> -- chroot /host sh -c 'ip -br addr; multipath -ll; iscsiadm -m session; nvme list-subsys'
oc debug node/<node> -- chroot /host ping -M do -s 8972 -c 3 <lif-ip>   # 9000-byte path test (8972 + 28 header bytes)
```

Network: interface errors/drops and MTU on the leaf ports of the node and the array. Storage: port / LIF state,
sessions per host, latency per volume.

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| Mount or login works, large I/O hangs (ocp) | MTU mismatch on some hop | the jumbo ping above, then each hop's MTU |
| Half the paths `failed` (ocp) | one fabric / switch / array port | which paths fail together |
| Latency on every volume of one array at once (storage) | network congestion or array | leaf port counters vs array latency |
| New nodes cannot see LUNs, old nodes fine (ocp) | storage: zoning / igroup / host group not updated | host entries on the array |

## History

- 2026-11-02: drafted as part of the it-brain architecture (`docs/it-brain/ARCHITECTURE.md`)
