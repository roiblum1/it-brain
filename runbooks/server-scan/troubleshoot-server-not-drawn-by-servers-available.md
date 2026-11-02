---
title: Troubleshoot install-server getting no server, the wrong server, or a 404/409 from server-scan GET /servers/available
type: runbook
area: server-scan
tags: [server-scan, servers-available, install-server, temporal, reservation, 404, 409, baremetalhost, troubleshooting]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (ADR-0032 + updates, ADR-0035) and the Redbull Workflows install-server docs
---

# Server not drawn (or wrongly drawn) by `/servers/available`

**When to use:** `install-server` fails with `ServerReservedError`, `ServerScanAuthError`, no candidates, or picked an
unexpected machine; or a direct call answers 404 / 409.
**Impact while running:** step 3 calls `/servers/available`, which **live-rechecks a vendor manager and writes back** —
keep `count` small. Everything else is read-only.
**Prerequisites:** a token (admin for reservation questions, auditor for events). Contract:
`knowledge/server-scan/server-scan-available-servers-and-install-reservation-lock.md`.

## Pre-checks

```bash
api() { curl -sS -H "Authorization: Bearer $TOKEN" "https://<server-scan-host>/api/v1$1"; }
api "/servers?search=<server or serial>" | jq '.items[] | {id, name, vendor, source_provider, openshift_state, health: .health.overall, maintenance: .maintenance.enabled, stale}'
```

## Procedure

1. **Read the error `code` and `detail`** (RFC 9457). 404 says whether the *name* matched nothing or the *filters*
   (vendor, health, availability) emptied it; 409 `AVAILABLE_SERVER_NAME_AMBIGUOUS` lists several documents with that
   name — pass `vendor` / `source_provider`.
2. **Check each gate on the server record** (`GET /servers/{id}`): `openshift.lifecycle_state` must be `AVAILABLE`
   (`INSTALLED_TO_INVENTORY` and `INSTALLED` are never drawn), not in maintenance, `reachable`, health not
   `CRITICAL`/`UNKNOWN`, no live `reservation` held by another workflow, and — with `min_nic_macs=2` — at least two MACs
   *read this run* (`identity.nic_macs` not in `unread_fields`). `install-server` also wants the network category
   `HEALTHY` (two links up).
3. **Reproduce the draw** with the workflow's parameters, small count:
   ```bash
   api "/servers/available?pattern=^ocp-<infraEnv>&health=HEALTHY&min_nic_macs=2&count=1" | jq '{items: [.items[] | {name, live_recheck_performed}], mode, requested, returned}'
   ```
   `live_recheck_performed: false` = that manager type isn't configured on the API pod (answer is Mongo-only).
4. **Reservation held:** the row / detail shows `holder`, `mce_cluster`, `infra_env`, `expires_at`, `workflow_id`. A
   lock from a crashed run expires on its own (2 h, or 24 h after success); release early only when you are sure the
   run is dead: `DELETE /servers/{id}/reservation` (admin) with the same `workflow_id`.
5. **`ServerScanAuthError`:** the workflow's `SERVER_SCAN_API_TOKEN` is a viewer/auditor token — the lock needs the
   static **admin** token.
6. **Machine is on another MCE already:** look for a stale BareMetalHost; server-scan says where it is
   (`openshift.cluster_name` / `mce_name`). See `knowledge/server-scan/server-scan-cluster-membership-nodes-status-jobs.md`.

## Verification

The draw in step 3 returns the expected server with `live_recheck_performed: true`; the re-run of `install-server`
reaches its `reserving-server` and later `holding-server` phases.

## Rollback

Nothing to roll back; a released reservation can be re-taken by the next run.

## History

- 2026-11-02: created
