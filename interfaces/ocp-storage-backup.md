---
title: OCP ↔ Storage — who backs up what on OpenShift — OADP / Velero vs Commvault vs array snapshots, restore responsibility
type: interface
area: oadp
teams: [ocp, storage]
tags: [backup, restore, oadp, velero, commvault, snapshot, snapmirror, retention, dr]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp, storage]
source: it-brain-design
---

# OCP ↔ Storage: who backs up what

> **Draft contract.** The main risk at this seam is a gap (nobody backs it up) or an overlap (two tools, two
> retentions, nobody sure which restore is authoritative). The table below must end up with exactly one owner per row.

## Parties

| Side | Team | Systems |
|---|---|---|
| consumer / operator of OADP | `ocp` | OADP (Velero, Kopia data mover, CSI snapshots), etcd backups, GitOps repos as the source of truth for config |
| provider | `storage` | Commvault (`area commvault`), array snapshots and replication (SnapMirror, SRDF, SyncIQ…), S3 targets |

## What is protected, by whom

| What | Tool | Owner | Retention | Restore tested |
|---|---|---|---|---|
| Cluster config (objects in git) | GitOps repos — re-apply, not restore | ocp | git history | `<…>` |
| etcd of standalone / UPI clusters | etcd backup | ocp | `<…>` | `<…>` |
| Hosted control planes (HyperShift) | `<OADP on the MCE? — decide>` | ocp | `<…>` | `<…>` |
| Namespaced app objects + PV data | `<OADP or Commvault — decide per class of app>` | `<…>` | `<…>` | `<…>` |
| Array volumes outside OpenShift | Commvault / array snapshots | storage | `<…>` | `<…>` |
| Backup copies off-site | `<SnapMirror / Commvault aux copy / S3 replication>` | storage | `<…>` | `<…>` |

## Who provides what

| Item | Provided by | Requested how |
|---|---|---|
| S3 bucket / target for OADP | storage | `interfaces/ocp-storage-object-s3.md` |
| VolumeSnapshotClass per CSI driver (Trident, Dell, Ceph CSI) | ocp, with the driver area | day2 repo |
| Commvault access to clusters (service account, scope) | ocp → storage | `<…>` — token is a Secret, never in the brain |
| Restore request path for app teams | both | `<…>` |

## How each side checks its half (read-only)

```bash
oc -n openshift-adp get backups.velero.io --sort-by=.metadata.creationTimestamp | tail
oc -n openshift-adp get schedules.velero.io
oc -n openshift-adp get backupstoragelocations
```

Storage side: Commvault job history for the cluster's subclients; array snapshot schedules for the volumes behind PVs.

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| Backup `PartiallyFailed` on volume snapshots (ocp) | ocp (VolumeSnapshotClass) or storage (snapshot reserve / limits) | Velero backup logs for the PV |
| Data mover slow / nightly window overrun (ocp) | network path to S3, or S3 throughput | transfer rate vs other buckets |
| Commvault job fails after a cluster upgrade (storage) | ocp: API/RBAC change, token expired | Commvault job error vs cluster version |

## Open questions

- Is Commvault used for OpenShift workloads at all, or only for storage outside the clusters?
- Do we need restore drills per quarter, and who signs them off?

## History

- 2026-11-02: drafted as part of the it-brain architecture (`docs/it-brain/ARCHITECTURE.md`)
