---
title: OCP ↔ Storage — NetApp ONTAP volumes for OpenShift through Trident (SVM, export policy, backend, PVC Pending)
type: interface
area: trident
teams: [ocp, storage]
tags: [trident, ontap, csi, nfs, iscsi, svm, export-policy, pvc-pending, backend]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp, storage]
source: it-brain-design
---

# OCP ↔ Storage: ONTAP volumes through Trident

> **Draft contract.** Written from general Trident/ONTAP behaviour, not yet checked against our estate.
> Both teams fill the `<…>` cells and raise `confidence` in an MR approved by both.

## Parties

| Side | Team | Systems |
|---|---|---|
| consumer | `ocp` | Trident operator and CSI pods on each cluster, StorageClasses, PVCs, VolumeSnapshotClasses |
| provider | `storage` | ONTAP clusters (`<array>`), one or more SVMs (`<svm>`), data LIFs, aggregates, export policies, igroups |

## What crosses the boundary

- A **Trident backend** (`TridentBackendConfig`) points at an SVM's management LIF with an ONTAP account; Trident
  then creates volumes/qtrees/LUNs itself. The account's role decides what Trident can do on the array.
- **NAS (ontap-nas / -economy):** every worker's IP on the storage network must be allowed by the SVM's export policy.
- **SAN (ontap-san):** nodes log in over iSCSI (or NVMe/TCP); Trident manages igroups per backend/node.
- Capacity: Trident is limited by the aggregates the SVM may use and any volume/qtree limits on the SVM.

## Who provides what

| Item | Provided by | Requested how | Lead time |
|---|---|---|---|
| SVM per `<cluster>` or shared SVM (decide) | storage | `<ticket queue>` | `<…>` |
| ONTAP account for Trident + role (least privilege) | storage | `<…>` — credential delivered as a Secret, never in git or the brain | `<…>` |
| Data LIFs on the storage network, routing to workers | storage + network | see `interfaces/storage-network-data-paths.md` | `<…>` |
| Export-policy rule covering the cluster's node subnet `<subnet>` | storage | `<…>` | `<…>` |
| Trident version, backend and StorageClass definitions | ocp | day2 GitOps repo | — |
| Notice before ONTAP upgrades / LIF migrations / SVM changes | storage → ocp | `<channel>` | `<…>` |
| Notice before adding nodes on a new subnet | ocp → storage | `<channel>` | `<…>` |

Version support: the Trident ↔ ONTAP ↔ OCP combination must be on NetApp's support matrix; record our rows in
`knowledge/meta/fleet-versions.md`, not here.

## How each side checks its half (read-only)

OCP side (`<trident-ns>` is wherever the operator is installed):

```bash
oc get tridentorchestrator                         # operator state
oc -n <trident-ns> get tridentbackendconfig        # phase Bound / Failed, message
tridentctl -n <trident-ns> get backend -o wide     # online / offline per backend
oc get pvc -A | grep -v Bound                      # stuck claims
oc -n <ns> describe pvc <pvc>                      # ProvisioningFailed message
tridentctl -n <trident-ns> logs                    # controller logs
```

Storage side (ONTAP CLI, read-only `show` commands):

```text
vserver show -vserver <svm>
network interface show -vserver <svm>
vserver export-policy rule show -vserver <svm>
volume show -vserver <svm> -fields size,available,state
```

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| Backend `offline` / TBC `Failed` (ocp) | storage: account locked/expired, mgmt LIF moved, cert or TLS change | `tridentctl get backend -o wide` message, then the ONTAP account |
| PVC `Pending`, `ProvisioningFailed` (ocp) | either: aggregate full / SVM limits (storage) or wrong StorageClass parameters (ocp) | PVC events, then `volume show` / aggregate space |
| Pod `ContainerCreating`, mount error `access denied by server` (ocp) | storage: export policy doesn't include the node's IP (often new nodes on a new subnet) | export-policy rules vs the node IP |
| Mount hangs / times out (ocp) | network or storage: LIF not reachable from the node's storage network, MTU mismatch | `interfaces/storage-network-data-paths.md` |
| Many new volumes/qtrees appearing on the SVM (storage) | ocp: a workload creating PVCs in a loop | `oc get pvc -A` sorted by creation time |

## Escalation

OCP → storage: `teams.json` → `storage.channel`, with `<cluster>`, backend name, time window and the exact error.
Storage → OCP: `ocp.channel` before changes listed in "Who provides what".

## Open questions

- One SVM per cluster, per site, or per tenant? (affects blast radius and export policies)
- Which Trident drivers we allow (ontap-nas, ontap-nas-economy, ontap-san, NVMe/TCP).
- Who rotates the Trident ONTAP account credential, and how the cluster Secret is updated.
- Do we run Trident Protect, and does it overlap with OADP / Commvault (`interfaces/ocp-storage-backup.md`)?

## History

- 2026-11-02: drafted as part of the it-brain architecture (`docs/it-brain/ARCHITECTURE.md`)
