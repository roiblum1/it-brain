---
title: KubeVirt VM networking — pod network masquerade vs bridge vs passt, Multus secondary networks, Linux bridge, OVN-Kubernetes localnet and layer2 (VLAN, persistent IPs), SR-IOV, kubemacpool, MTU
type: knowledge
area: kubevirt
teams: [network, ocp]
tags: [kubevirt, networking, masquerade, bridge, passt, multus, networkattachmentdefinition, nad, localnet, layer2, ovn-kubernetes, vlan, sriov, kubemacpool, mac, mtu, nmstate]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/user-guide docs/network/interfaces_and_networks.md; ovn-org/ovn-kubernetes docs/features/multiple-networks/multi-homing.md; openshift/runbooks alerts/openshift-virtualization-operator/KubeMacPool*.md
---

# VM networking

A VM has `spec.networks` (the backend) and `spec.domain.devices.interfaces` (the NIC model and binding), matched by
name. Network types: `pod` (the cluster network, `eth0` of the virt-launcher pod) and `multus` (a
NetworkAttachmentDefinition — secondary network, or primary when Multus is the default).

## Binding to the pod network

| Binding | How | Live migration | Notes |
|---|---|---|---|
| `masquerade` | VM gets an internal IP behind NAT; traffic leaves with the **pod IP** | **yes** | the default to use. Expose the VM with a Service (its pod IP changes on migration/restart). `ports` list limits forwarded ports; ports 49152–49153 are used by migration and must not be listed. Only allowed on the pod network |
| `bridge` (on pod network) | pod IP delegated to the guest by DHCP; pod has no IP | **no** — `InterfaceNotLiveMigratable` (`cannot migrate VMI which does not use masquerade to connect to the pod network`) | breaks things that expect the pod IP (Istio). Admins can forbid it |
| `passtBinding` (beta since v1.8) | user-space translation L2 ↔ sockets | yes | no extra capabilities, service-mesh friendly, pod IP in guest |

## Secondary networks (Multus)

The admin creates a `NetworkAttachmentDefinition` (NAD) in the VM's namespace (or `default`); the VM references it as
`multus.networkName: <namespace>/<nad>` and usually binds it with `bridge: {}`. Our two practical options for putting
VMs on a real VLAN:

**1. Linux bridge on the node + bridge CNI.** A Linux bridge (e.g. `br1` on a bond/VLAN) is created on the nodes —
in OpenShift through an NMState `NodeNetworkConfigurationPolicy` — and the NAD uses `"type": "bridge"`, optionally
`"vlan": <vlan>` and `"macspoofchk": true` (the bridge CNI's MAC-spoof check uses nftables, so `nft` must exist on
the node). Simple and fast; IPs come from the guest (DHCP on the VLAN or static).

**2. OVN-Kubernetes `localnet` topology.** A cluster-wide logical switch connected to a physical network:
`"type": "ovn-k8s-cni-overlay"`, `"topology": "localnet"`, optional `"vlanID"`, `"subnets"` (OVN-K IPAM),
`"excludeSubnets"`, `"allowPersistentIPs": true` (IPs kept in `ipamclaims.k8s.cni.cncf.io` so a VM keeps its IP
across migration/restart), `"physicalNetworkName"`, `"mtu"`. It needs the node's OVS **bridge mapping** for that
physical network (in OpenShift done with NMState `ovn.bridge-mappings`). All NADs that name the same network must have
identical config, and changing it needs the workloads restarted. `macSecurityMode: disabled` turns off MAC security
and requires `subnets` unset. `multi-network` must be enabled in OVN-K.

**`layer2` topology** (overlay, east-west only, no physical network): good for VM-to-VM networks across nodes without
the fabric; also supports `allowPersistentIPs`.

Example localnet NAD (placeholders — the VLAN and subnet come from the network team,
`interfaces/virtualization-network-kubevirt-vm-networks.md`):

```yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: vm-<vlan>
  namespace: <namespace>
spec:
  config: |
    {"cniVersion": "1.0.0", "name": "vm-<vlan>", "type": "ovn-k8s-cni-overlay",
     "topology": "localnet", "vlanID": <vlan>, "physicalNetworkName": "<physnet>",
     "netAttachDefName": "<namespace>/vm-<vlan>"}
```

**CNIs that do not work with `bridge` binding**: `macvlan` and `ipvlan` (the binding moves the pod interface's MAC to
the VM; those CNIs need the original MAC).

## SR-IOV

VFs are passed into the guest through VFIO: SR-IOV network operator policy with `deviceType: vfio-pci`, a NAD for
the SR-IOV network, interface binding `sriov: {}`. VMs with SR-IOV **can** live-migrate: the VF is hot-unplugged
before and hot-plugged after the migration (the guest loses that link meanwhile). Some NICs need a guest driver.
Dedicated CPUs with SR-IOV need the CPU manager on those workers.

## MAC addresses — kubemacpool

KubeMacPool (part of the Cluster Network Addons operator) allocates VM MACs from a pool and prevents duplicates in
managed namespaces. Alerts: `KubemacpoolDown`, `KubemacpoolMACCollisionDetected` (and the deprecated
`KubeMacPoolDuplicateMacsFound`; its logs say `mac address <mac> already allocated to vm/<ns>/<vm>`). Two clusters
on the **same VLAN** have separate pools — they can hand out the same MAC; give each cluster its own range or keep
VMs of different clusters on different VLANs (`interfaces/virtualization-network-kubevirt-vm-networks.md`).

## MTU

MTU reaches the guest via libvirt (virtio driver new enough) or DHCP. Windows guests with non-virtio NICs need the MTU
set by hand. On OVN-K overlays, pod network MTU is the node MTU minus the Geneve overhead
(`interfaces/ocp-network-aci-fabric.md`).

## Guest agent and IPs

`oc get vmi <vm> -o jsonpath='{.status.interfaces}'` lists IPs per interface; secondary-network IPs assigned inside the
guest are only visible when the **qemu-guest-agent** runs (`AgentConnected` condition; `infoSource: domain, guest-agent`).

## Where it goes wrong

Procedure: `runbooks/kubevirt/vm-no-network-on-secondary-network.md`. Quick hints:

| Symptom | Likely |
|---|---|
| virt-launcher pod stuck `ContainerCreating`, event mentions the NAD | NAD missing/wrong namespace, or the bridge / bridge mapping missing on that node |
| VM up, no traffic on the VLAN | VLAN not trunked to that node's port on the fabric (network team), wrong `vlanID`, or MAC security drops the guest's MAC |
| Works until migration, then not | upstream switch learned the MAC on the old port (ACI endpoint learning — `interfaces/ocp-network-aci-fabric.md`), or IPs not persistent |
| Two VMs flap | duplicate MAC (kubemacpool alerts) |

## Scope & caveats

Upstream KubeVirt and OVN-K docs (main, 2026-11). OpenShift-specific setup of localnet (NMState bridge mappings,
`multi-network` enablement) — check RHOKP for the OCP minor. Which option we use is an open question in
`knowledge/kubevirt/README.md`.

## History

- 2026-11-02: created
