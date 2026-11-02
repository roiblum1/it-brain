---
title: PowerCLI storage and networking — datastores, storage policies (SPBM, Get-SpbmStoragePolicy), vDS and port groups, VLAN IDs, and which team owns what
type: knowledge
area: powercli
teams: [virtualization, storage, network]
tags: [powercli, datastore, spbm, storage-policy, vds, portgroup, vlan, mtu, vmkernel, iscsi, nfs]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [virtualization]
source: vmware/PowerCLI-Example-Scripts (Get-SpbmStoragePolicy, Get-VDSwitch, Get-VDPortgroup, Get-Datastore usage); property names to confirm with Get-Member
---

# Storage and networking with PowerCLI

vSphere is where the storage and network teams' work meets the VMs. The team seams are written down in
`interfaces/storage-network-data-paths.md` (node/host → fabric → array) and `interfaces/ocp-network-aci-fabric.md`
(VLANs / EPGs for clusters); this page is how to *see* the vSphere side of them.

## Datastores

```powershell
Get-Datastore | Select-Object Name, Type, CapacityGB, FreeSpaceGB, State
Get-Datastore <datastore> | Get-VMHost | Select-Object Name                     # which hosts mount it (should be the whole cluster)
Get-Datastore <datastore> | Get-VM | Select-Object Name                          # who lives there
Get-VMHost <esxi> | Get-VMHostStorage -RescanAllHba -WhatIf                      # rescan is a change-ish operation: do it in a window
```

- A datastore mounted on only some hosts of a cluster breaks vMotion / DRS / HA for VMs on it — and breaks vSphere CSI
  volumes for OpenShift nodes on the hosts that miss it.
- `Type`: `VMFS` (block: FC / iSCSI / NVMe-oF LUN from an array), `NFS` / `NFS41` (ONTAP, PowerScale), `vsan`.
  Which array and which path → the storage team (array areas: `netapp-ontap`, `dell-powermax`, `dell-powerflex`, `dell-powerscale`).

## Storage policies (SPBM)

```powershell
Get-SpbmStoragePolicy | Select-Object Name, Description
Get-VM <vm> | Get-SpbmEntityConfiguration           # which policy each VM / disk uses and whether it is compliant
```

OpenShift on vSphere uses a storage policy name in its vSphere CSI StorageClass (`storagePolicyName`); a policy
renamed or removed in vCenter makes new PVCs fail on the cluster side (`knowledge/vsphere/README.md`).

## Distributed switches, port groups, VLANs

```powershell
Get-VDSwitch | Select-Object Name, Version, Mtu, NumUplinkPorts
Get-VDPortgroup | Select-Object Name, VDSwitch, VlanConfiguration, NumPorts
Get-VMHostNetworkAdapter -VMHost <esxi> -VMKernel | Select-Object Name, IP, SubnetMask, Mtu, PortGroupName,
    VMotionEnabled, ManagementTrafficEnabled
Get-VM <vm> | Get-NetworkAdapter | Select-Object Name, NetworkName, Type, MacAddress, Connected
```

- `VlanConfiguration` shows the VLAN ID / trunk range of a port group. The VLAN itself must exist on the fabric
  (ACI EPG / static port binding) — that half belongs to the network team (`interfaces/ocp-network-aci-fabric.md`).
- MTU must match end to end: vDS MTU, VMkernel adapters (iSCSI / NFS / vMotion), the fabric, the array. A jumbo
  ping from the host: `$esxcli.network.diag.ping.Invoke(@{ host = '<ip>'; size = 8972; df = $true })` (hypothesis — argument names
  vary; check `CreateArgs()`), or `vmkping -d -s 8972` over SSH.
- MAC addresses of VMs are in `Get-NetworkAdapter`; they matter for ACI endpoint learning and for MTV mapping.

## Who to call

| You see | Likely owner |
|---|---|
| datastore full / latency on all VMs of one datastore | storage (array) |
| datastore missing on some hosts after a change | storage (masking / exports) or virtualization (rescan) |
| port group exists, VMs on it can't reach their gateway | network (VLAN not on the fabric / EPG) |
| VMkernel iSCSI / NFS paths down on one host | virtualization (host) → storage-network data path |

## History

- 2026-11-02: created
