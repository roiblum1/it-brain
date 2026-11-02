---
title: OCP ↔ Storage — S3 object storage for cluster consumers (Ceph RGW, ONTAP S3, PowerScale S3, ODF NooBaa) — endpoint, CA, bucket, credentials
type: interface
area: ceph
teams: [ocp, storage]
tags: [s3, object-storage, ceph, rgw, ontap-s3, noobaa, mcg, oadp, velero, loki, bucket, tls, ca]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp, storage]
source: it-brain-design
---

# OCP ↔ Storage: S3 for cluster consumers

> **Draft contract.** One page for every S3 provider, because the consumer-side contract is the same.

## Parties

| Side | Team | Systems |
|---|---|---|
| consumer | `ocp` | OADP BackupStorageLocations, LokiStack, image/mirror registries, Thanos/metrics, application buckets |
| provider | `storage` | Ceph RGW (`area ceph`), ONTAP S3 (`netapp-ontap`), PowerScale S3 (`dell-powerscale`), ODF / NooBaa (`odf`), Nutanix Objects (`nutanix`) |

## What crosses the boundary

Per bucket: **endpoint URL**, **TLS CA** that signed the endpoint (internal CA must be trusted by the consumer),
**bucket name**, **access/secret key** (a Secret on the cluster — never in git or the brain), **quota**, and the
**addressing style** — S3-compatible stores usually need path-style requests (for Velero's AWS plugin:
`s3ForcePathStyle: "true"` and `s3Url`), and a `region` string even when the store ignores it.

## Who provides what

| Item | Provided by | Requested how | Lead time |
|---|---|---|---|
| Bucket + user/keys per consumer per `<cluster>` | storage | `<ticket queue>` | `<…>` |
| Endpoint URL and CA bundle | storage | published in `knowledge/<provider-area>/` (placeholders only) | — |
| Quota and lifecycle/retention rules | storage, with ocp's sizing | `<…>` | `<…>` |
| Key rotation schedule and procedure | storage → ocp | runbook in `runbooks/<provider-area>/` | `<…>` |
| Firewall flow cluster → endpoint | network | `interfaces/ocp-network-palo-alto-flows.md` | `<…>` |
| Consumer config (BSL, LokiStack secret, registry storage) | ocp | day2 GitOps repo | — |

## How each side checks its half (read-only)

OCP side:

```bash
oc -n openshift-adp get backupstoragelocations     # Phase Available / Unavailable + message
oc -n <ns> get lokistack -o yaml | grep -A5 conditions
# from a debug pod on the cluster network: TLS and reachability only, no credentials on the command line
curl -sS --cacert <ca.pem> -o /dev/null -w '%{http_code}\n' https://<s3-endpoint>/
```

Storage side: bucket exists, user enabled, quota usage, request/error rates for that user (RGW: `radosgw-admin bucket stats --bucket <bucket>`, read-only).

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|
| `x509: certificate signed by unknown authority` (ocp) | ocp: CA not in the consumer's trust (BSL `caCert`, proxy/trusted CA bundle) — or storage changed the endpoint cert | which CA signed the endpoint today |
| `SignatureDoesNotMatch` / `InvalidAccessKeyId` (ocp) | storage: key rotated / user disabled; or ocp: stale Secret | when the key last changed |
| `NoSuchBucket` or virtual-host DNS errors (ocp) | ocp: path-style not set | consumer config |
| `QuotaExceeded` / backups fail at the same time every night (ocp) | storage quota, or ocp retention too long | bucket usage vs quota |
| Endpoint unreachable from one site only (ocp) | network | the flow on that site's firewall |

## Open questions

- Which provider is the default for which consumer (OADP, Loki, registries)?
- One bucket per cluster per consumer, or shared buckets with prefixes?
- Who owns the CA bundle that clusters trust for S3 endpoints?

## History

- 2026-11-02: drafted as part of the it-brain architecture (`docs/it-brain/ARCHITECTURE.md`)
