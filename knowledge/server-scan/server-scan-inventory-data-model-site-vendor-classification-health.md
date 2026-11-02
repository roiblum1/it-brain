---
title: server-scan inventory fields — site parsed from hostname, vendor vs source_provider, installation type vs OpenShift state, UNKNOWN health, stale
type: knowledge
area: server-scan
tags: [server-scan, data-model, site, vendor, classification, installation-type, openshift-state, health, unknown, stale, maintenance, reservation]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (README.md, CLAUDE.md, backend/app/domain/enums/core.py, ADR-0011/0016/0018/0024/0027/0037)
---

# server-scan inventory fields and what they really mean

Most "server-scan is wrong" reports are a field meaning something other than its name suggests. Architecture:
`knowledge/server-scan/server-scan-architecture-collectors-mongodb-api.md`.

## Identity

| Field | Meaning | Trap |
|---|---|---|
| `id` | `srv_<hex>` document id | stable per document, not per hostname |
| `name` | hostname as the manager reports it | **not unique**: one hostname can span several documents (re-serialled, moved vendor, seen by two collectors) |
| `vendor` | `dell` / `cisco` / `hp` / `standalone` — no `UNKNOWN` | `standalone` = a maker not modelled *or* not reported by the BMC, not "collected without a manager". HPE is `hp` |
| `source_provider` | the collector that found it: `UCS_CENTRAL`, `INTERSIGHT`, `OPENMANAGE`, `ONEVIEW`, `REDFISH_STANDALONE` | a Dell reached directly at its BMC is still `vendor: dell` |
| correlation key | `(vendor, serial_normalized)`; a serial-less standalone stub by `(source_provider, BMC host)` | moving a machine between vendors splits it into two documents |

## Site

`site_id` is **parsed from the server's own name** (`parse_site_code`) against `INVENTORY_SITES` (codes and names,
`|`-separated aliases allowed), never configured per manager (ADR-0018). Matching is substring-within-a-token; a
name with no site token (or two real codes) is `unassigned`. A Cisco name with no token falls back to the profile's
org DN. Known collision: a site code that is a substring of `infra` makes every `-infra-` server ambiguous.
`INVENTORY_SITES` lives in the shared `api-config` ConfigMap so API and collectors agree.

## What a server is for — two different fields

| Field | Source | Values |
|---|---|---|
| `classification.installation_type` | regex rules on the **hostname** (what it was *named* to be) | `UPI`, `HOSTED_CLUSTER`, `MCE`, `UNCLASSIFIED` |
| `openshift.lifecycle_state` | reported **by the clusters** (`nodes-status` jobs) | `AVAILABLE` (default, the only state reached by absence), `INSTALLED` (a node, or an Agent bound to a hosted cluster), `INSTALLED_TO_INVENTORY` (registered to an MCE, bound to nothing — spare capacity) |

When they disagree the server is misnamed or misplaced — that disagreement is the signal (ADR-0024). **Availability
is `openshift_state`, never the name.** Details: `knowledge/server-scan/server-scan-cluster-membership-nodes-status-jobs.md`.

## Health

- Severities, best to worst: `HEALTHY`, `WARNING`, `MAJOR` ("redundancy gone, still serving"), `CRITICAL`; plus
  `UNKNOWN` = nothing could be read. **`UNKNOWN` is not a verdict** (ADR-0027).
- Scored per category — `memory`, `storage`, `raid`, `network`, `connectivity`, `power`, `gpu`, `bmc` — worst wins.
  A category with no data read is `UNKNOWN` and its policies are skipped.
- Consequence that bites provisioning: **the less that was read, the healthier a server can look** — a server whose
  NIC read failed has no network facts to fail and can come out `HEALTHY`. Exception since 2026-10-21: every NIC
  link `UNKNOWN` makes `overall` `UNKNOWN` (OneView exempt). Every drive `UNKNOWN` only makes the storage row `UNKNOWN`.
- An unreachable BMC (`reachable=false`, with `unreachable_reason`: `network_unreachable`, `auth_rejected`,
  `tls_error`, `timeout`, `protocol_error`) is `CRITICAL` (ADR-0037).
- RAID is judged only where the management layer can report it (Dell via OME/iDRAC, standalone Redfish, Cisco UCS):
  no RAID 1 for the OS disk is `CRITICAL`, anything it cannot see is `UNKNOWN` (ADR-0048). Connectivity (fabric
  paths) only for Cisco behind a fabric interconnect.
- Policies are declarative, shipped with the platform, keyed by `policy_key` (e.g. `bmc.unreachable`,
  `raid.os_mirror_missing`, `network.single_link_up`, `storage.os_disk_bad_critical`), scoped to sets of collectors
  (ADR-0030); read-only in the UI (Rules & Policies page) and via `GET /api/v1/health-policies`.
- GPU VRAM comes from a built-in catalog when the API does not report it (OneView, Intersight, UCS); a read value
  always wins; `INVENTORY_GPU_MODELS` overrides rows (ADR-0021).
- A PSU's health is `UP`/`DOWN`/`DISABLED`/`UNKNOWN`; an absent supply is dropped, not failed.

## Freshness and operator state

| Field | Meaning |
|---|---|
| `last_seen_at` | last time a collector confirmed it (`touch_seen` even when unchanged) |
| `updated_at` / `revision` | last *content* change, not last run |
| `listed_at` | last time its manager listed it; pruning reads this, not `last_seen_at` |
| `stale` | not seen for `INVENTORY_STALE_AFTER_SECONDS` (default 12 h) |
| `unread_fields` | paths that could not be read this run (value carried forward) |
| `maintenance` | operator pause with a reason (admin-only write; "donor" is a maintenance reason, ADR-0038) |
| `reservation` | time-limited install lock (ADR-0035) — `knowledge/server-scan/server-scan-available-servers-and-install-reservation-lock.md` |

Every datetime is stored as an ISO **string** (ADR-0006) — anyone querying Mongo directly must compare strings.
Every health, classification, maintenance and reservation change is an audit event.

## Scope & caveats

Semantics as of `08d284c`; the health rules change often (dated exceptions above). Check
`GET /api/v1/health-policies` on the running instance before relying on a specific policy.

## How we know

`team-redbull/server-scan:README.md` (Key concepts), `:CLAUDE.md` (Key technical facts),
`:backend/app/domain/enums/core.py`, `:backend/app/domain/services/health/evaluate.py`, ADRs named above.

## History

- 2026-11-02: created
