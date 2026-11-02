---
title: Fix a KubeVirt VM with no connectivity on a secondary network (Multus NAD, Linux bridge via NMState, OVN-K localnet VLAN, MAC conflicts, fabric VLAN missing)
type: runbook
area: kubevirt
teams: [network, ocp]
tags: [kubevirt, networking, multus, nad, localnet, linux-bridge, nmstate, nncp, vlan, mac, kubemacpool, aci, troubleshooting]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: kubevirt/user-guide docs/network/interfaces_and_networks.md; ovn-org/ovn-kubernetes docs/features/multiple-networks/multi-homing.md
---

# VM has no network on a secondary network

**When to use:** VM boots but cannot reach its VLAN; virt-launcher stuck `ContainerCreating` with a CNI/NAD error;
connectivity lost after a live migration.
**Impact while running:** read-only until the fix step.
**Prerequisites:** `oc`; the network team for the fabric side (`interfaces/virtualization-network-kubevirt-vm-networks.md`).
Background: `knowledge/kubevirt/kubevirt-networking-masquerade-bridge-multus-localnet-sriov.md`.

## Pre-checks

```bash
oc get vm <vm> -n <namespace> -o jsonpath='{.spec.template.spec.networks}{"\n"}{.spec.template.spec.domain.devices.interfaces}{"\n"}'
oc get net-attach-def -n <namespace>
oc get net-attach-def <nad> -n <namespace> -o jsonpath='{.spec.config}{"\n"}'
oc get vmi <vm> -n <namespace> -o jsonpath='{.status.interfaces}' | jq
oc get vmi <vm> -n <namespace> -o wide                          # node
```

## Procedure

1. **Pod not starting, Multus error** — the NAD must exist in the VM's namespace (or `default`) with the exact name the VM
   references; `oc describe pod <virt-launcher>` shows Multus' message.
2. **Linux bridge NAD** (`"type": "bridge"`) — the bridge must exist on **that node**:
   ```bash
   oc get nncp; oc get nnce | grep <node>                          # policy applied on the node?
   oc debug node/<node> -- chroot /host ip -d link show <bridge>
   ```
   VLAN set in the NAD (`"vlan"`) vs what the fabric carries on the node's port.
3. **OVN-K localnet NAD** — `"topology": "localnet"`: the node needs the OVS bridge mapping for `physicalNetworkName`
   (or the NAD `name`) — NMState `ovn.bridge-mappings` policy; `vlanID` must be trunked to every node that can run the VM.
   All NADs with the same network `name` must have identical config.
4. **Guest side** — is the interface up and configured (DHCP on that VLAN, or static)? Console:
   `virtctl console <vm> -n <namespace>`; IPs only show in `status.interfaces` with the guest agent.
5. **Fabric** — ask the network team to check the VLAN on the node's leaf port and the endpoint table for the VM's MAC
   (`<mac>` from `status.interfaces`). After a migration, a stale endpoint on the old leaf looks exactly like this
   (`interfaces/ocp-network-aci-fabric.md`, endpoint learning).
6. **MAC conflict** — alerts `KubemacpoolMACCollisionDetected`; the same MAC used by another VM (another cluster on the
   same VLAN?). Give the VM a new MAC (`spec.template.spec.domain.devices.interfaces[].macAddress`) and restart.
7. **MAC spoof check** (`macspoofchk` on bridge NADs, OVN `macSecurityMode`) drops frames from MACs the guest invents
   (nested bridges, VRRP, bonding inside the guest) — disable only for that network, with the network team's agreement.

## Verification

From inside the guest: ping the VLAN gateway; from the fabric: the MAC is learned on the right port.

## Rollback

Revert NAD/NNCP changes through GitOps; a changed MAC can be set back (restart needed).

## History

- 2026-11-02: created
