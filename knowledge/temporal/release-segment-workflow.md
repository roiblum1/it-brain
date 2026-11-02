---
title: release-segment workflow — give a decommissioned hosted cluster's VLAN back after Argo CD teardown (PostDelete hook), DHCP scope removed first, failed hook Job is final
type: knowledge
area: temporal
tags: [temporal, redbull-workflows, segment-lifecycle, release-segment, segments-manager, dhcp, postdelete-hook, argocd, crossplane, decommission]
applies_to: [hosted-cp]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
teams: [network]
source: Redbull Workflows docs site v1.0.61
---

# release-segment

| | |
|---|---|
| Trigger | `POST /workflows/segment-lifecycle/release-segment` `{cluster, type?}` — 202, 409 if running (body with `segment`/`site` = 422) |
| Workflow id | `release-segment-<TYPE>-<cluster>` |
| Queues | workflow `release-segment-workflow`, activity `segment-lifecycle-activity` |
| Writes | DHCP API `DELETE` (only if the scope survived), Segments Manager release |
| Caller today | a **PostDelete hook** Job in the `hostedcluster-setup` chart |

The inverse of `knowledge/temporal/allocate-segment-workflow.md`. Architecture:
`knowledge/temporal/redbull-workflows-orchestrator-architecture.md`.

## Before the run: the decommission

Deleting `<cluster>.yaml` from day1 `main` makes the ApplicationSet delete the Application; its resources finalizer
deletes what it managed, including the Crossplane `Request`, whose deletion makes provider-http `DELETE` the DHCP
scope. When every resource is gone Argo CD runs the PostDelete hook Job `release-segment-<cluster>`, which POSTs
`{"cluster": "<clusterName>", "type": "HC"}` (`clusterName` is the ApplicationSet parameter, so it survives the file's
deletion). A hook, not an Argo CD notification: `on-deleted` fires when deletion **starts**, before the Request (and
in production the HostedCluster and NodePools) are gone, and is fire-and-forget.

Hook behaviour: 202 or 409 → Job succeeds (doesn't wait for the run). Anything else → retries with backoff ≤ 60 s for up
to **55 min** while Argo CD holds the Application. Still failing → the Job fails and **Argo CD deletes the Application
anyway; it does not retry a failed PostDelete hook** (verified by the team on OpenShift GitOps 1.18 / Argo CD 3.1).

> **A failed hook is final.** The only trace is a Failed `release-segment-<cluster>` Job in the Argo CD namespace; its
> log ends with the exact POST to send by hand once the API is back. The segment stays Allocated until then. Starting
> release-segment late is safe (no-op if nothing is allocated).

## Steps and phases

| Phase | Activity | What / why |
|---|---|---|
| `pending` | — | type gate: HC only (`UnsupportedSegmentType`) |
| `locating-allocation` | `find_cluster_allocation` | `GET /api/segments?status=Allocated&type=HC&fresh=true` and match `cluster_name` **exactly, client-side** — the list ignores a `cluster_name` parameter and its search is a substring match (`c1` hits `c10`). None → completes `released: false`, touches nothing. Two → `AmbiguousAllocationError` |
| `removing-dhcp-scope` | `get_dhcp_scope` → `delete_dhcp_scope` → `get_dhcp_scope` | by network address; normally one 404 (teardown already deleted it). Survived → delete, then confirm absence. Still there → `DhcpScopeStillPresentError` (a Crossplane Request still exists — the Application isn't gone). The orchestrator's **only** DHCP write, and only ever a delete |
| `releasing-segment` | `get_segment` → `release_segment` | re-read the owner first (release checks nobody's ownership): another cluster holds it → `AllocationOwnerMismatchError`, nothing released; already Available → success |
| `verifying-release` | `get_segment` | `Available`, no `cluster_name`, no `type`, else `ReleaseNotConfirmedError` |
| `completed` | — | segment, VLAN, site, `released`, `dhcp_scope_removed` (normally false). No git step |

The scope goes **before** the segment: a segment handed to a new cluster while its old scope still serves leases would
collide. So a DHCP API outage (or a 503 because no DHCP server is configured behind it) holds the run in
`removing-dhcp-scope` with the segment Allocated — deliberately.

## Errors and config

Permanent: `UnsupportedSegmentType`, `AmbiguousAllocationError`, `DhcpScopeStillPresentError`, `DhcpApiAuthError`
(worker's copy of the DHCP token wrong/rotated), `DhcpScopeInvalidError` (400), `AllocationOwnerMismatchError`,
`ReleaseNotConfirmedError`, `SegmentsManagerAuthError`, `SegmentValidationError`, `SegmentNotFoundError`.
Transient: `DhcpApiError`, `SegmentsManagerError`.
Config: `DHCP_API_URL` (`segment-lifecycle-config`; scope GETs anonymous), `DHCP_API_TOKEN` (Secret `dhcp-api-token`, a
copy of the DHCP API's own token — **rotate both together**).

Call it only after the Application is gone; a manual caller posting too early can have the scope re-created by a
Request that still exists. The hook is a bridge until a deprovision-cluster workflow owns teardown.

## History

- 2026-11-02: created from the release-segment page of the Redbull Workflows docs site v1.0.61
