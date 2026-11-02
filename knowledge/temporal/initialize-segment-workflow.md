---
title: initialize-segment workflow — create a network segment in the Segments Manager (born Available, typeless), 400 conflict resolution, /bulk, no firewall flow any more
type: knowledge
area: temporal
tags: [temporal, redbull-workflows, segment-lifecycle, initialize-segment, segments-manager, vlan, epg, aci, cidr, idempotency]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
teams: [network]
source: Redbull Workflows docs site v1.0.61
---

# initialize-segment

| | |
|---|---|
| Trigger | `POST /workflows/segment-lifecycle/initialize-segment` (and `/bulk`) — 202, 409 if running |
| Workflow id | `initialize-segment-<network>` (CIDR **mask dropped**, so `/24` vs `/25` spelling dedups) |
| Queues | workflow `initialize-segment-workflow`, activity `segment-lifecycle-activity` |
| Writes | Segments Manager `POST /api/segments` only |

Architecture and shared rules: `knowledge/temporal/redbull-workflows-orchestrator-architecture.md`.

## What it does

One activity, `create_segment`, retried until it succeeds. The segment is **Available** when the run completes.
A workflow at all because the retry, the dedup id and the per-segment status *are* the product: a Segments Manager
outage is out-waited, a duplicate trigger is a 409, and `/bulk` starts one run per segment with its own outcome.

Body (`InitializeSegmentInput`, mirrors the Segments Manager's `POST /api/segments` schema):
`segment` (CIDR), `site`, `vlan_id` (1–4094), `epg_name` (the ACI endpoint group), `dhcp` (default `true`).
A body carrying `type` is a **422**: type (`HC`, `MCE`, `INVENTORY`, `PXE`) is allocation state, stamped by
allocate-segment and cleared by release — every created segment joins one shared pool per site.

The **Segments Manager is the validator of record** (site known, CIDR in the site pool, no overlap, VLAN free); the
orchestrator re-derives none of it. So an invalid definition is a **FAILED run** (with the manager's error text) on
`GET /workflows/runs/{id}`, not a 4xx on the trigger.

## Re-submitting is not an error

The Segments Manager answers **400** both for "CIDR already taken" and "definition invalid", so `create_segment` looks
the CIDR up after a 400:

| Stored record | Outcome |
|---|---|
| absent | `SegmentValidationError` (definition rejected) — fails the run |
| present, same `site`, `vlan_id`, `epg_name` | success (an earlier attempt applied it) |
| present, different identity | `SegmentConflictError` — fails the run |

`dhcp` is not compared (the one field editable after creation — difference logged, stored value kept); nor `type`,
status or cluster (allocation state).

## Errors

Permanent: `SegmentValidationError`, `SegmentConflictError`, `SegmentsManagerAuthError` (bad
`SEGMENTS_MANAGER_API_TOKEN`, 401/403). Everything else is a retryable `SegmentsManagerError`, including a failing lookup
during conflict resolution. Nothing to clean up on failure.

Phases: `pending` → `creating-segment` (also where an outage is out-waited) → `completed`.
Config: `SEGMENTS_MANAGER_URL` (global ConfigMap), `SEGMENTS_MANAGER_API_TOKEN` (Secret; GETs are public).

## The firewall flow is gone

Older versions discovered same-site peer segments, requested firewall rules from the "next connectivity" service
(plus MCE↔BMC rules), waited for human approval with `continue_as_new`, and flipped the segment Locked → Available.
**All firewalls between segments are open now**, so that flow, the `Locked` status and its config (`NEXT_*`,
`PORTS_*`, `SITE_NETWORKS`, `SITES_WITH_OPEN_CONNECTIVITY`) were removed. If the firewall policy changes again, see
`interfaces/ocp-network-palo-alto-flows.md`.

## History

- 2026-11-02: created from the initialize-segment page of the Redbull Workflows docs site v1.0.61
