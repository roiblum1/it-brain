---
title: server-scan GET /servers/available and the install reservation lock — live recheck, min_nic_macs, 409 ambiguous name, two MCEs drawing one server
type: knowledge
area: server-scan
tags: [server-scan, servers-available, reservation, lock, install-server, baremetalhost, bmh, live-recheck, min-nic-macs, temporal, mce, infraenv]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (ADR-0032 incl. 2026-09-25/26 updates, ADR-0035, backend/app/api/v1/reservation_schemas.py)
---

# `/servers/available` and the install reservation lock

The two pieces of server-scan that provisioning depends on. They replaced `bmh-generator-operator`
(BareMetalHostUCS), which queried OneView, UCS Central, OME and Intersight live on every reconcile; the Temporal
`install-server` workflow now makes one call here instead (`knowledge/server-scan/server-scan-platform-integrations-temporal-metal3-ome.md`).

## `GET /api/v1/servers/available`

**The one endpoint that reaches a vendor manager, and not a pure read.** It ranks candidates in Mongo, live-rechecks
only the few it returns through the provider's `get_one()`, and persists the refreshed record through
`IngestService.ingest_one` before answering.

| Parameter | Meaning |
|---|---|
| `name=<exact>` **or** `pattern=<regex>` | exactly one of the two (400 otherwise). `name` = case-insensitive exact match; more than one document with that name → **409 `AVAILABLE_SERVER_NAME_AMBIGUOUS`** listing the ids (narrow with `vendor` / `source_provider`). `pattern` = a real Mongo `$regex` on the name (unanchored allowed; slower than token search, accepted because it is per install) |
| `count` | pattern mode only; default 1, max `INVENTORY_MAX_AVAILABLE_COUNT` (chart default 20) |
| `vendor`, `source_provider` | narrow; `source_provider` is what tells `UCS_CENTRAL` from `INTERSIGHT` Cisco |
| `health` | restrict the draw to one tier (`HEALTHY`, `WARNING`, `MAJOR`); `CRITICAL`/`UNKNOWN` → 400 |
| `min_nic_macs` | require ≥ N MACs **actually read this run**; default 0 imposes nothing; `install-server` passes 2 |

Selection: `openshift.lifecycle_state == AVAILABLE`, not in maintenance, `reachable`, no live reservation, then
best-first by health tier (never `CRITICAL`, never `UNKNOWN`), random `$sample` within a tier, live recheck, replace
a candidate the recheck downgrades (bounded retries). Fewer than `count` is a 200 with requested-vs-returned
metadata; 404 only when nothing qualified at all, and the `detail` says whether the **name** or the **filters**
emptied it.

Capacity aliases (`INVENTORY_CAPACITY_ALIASES`, default `5tb:hypershift(?!-data),10tb:hypershift-data`) expand a
pattern that **equals** an alias key into an `$or` with the alias regex.

The item (`AvailableServerItem`) is deliberately only what a BMH/NMState generator consumes: `id`, `name`,
`vendor`, `source_provider`, `bmc_vendor` (`HP`/`DELL`/`CISCO`/`INTERSIGHT`, `None` for standalone — UCS and
Intersight Cisco need different `bmc.address` schemes), `bmc` (bare host), ordered `nic_macs` (natural order of the
interface name, `eno2` before `eno10`), `interfaces[]` (`name`, `mac`, `location`, `os_name`, `link_state`,
`speed_mbps`), `site_id`, `health_overall`, **`live_recheck_performed`**. It never returns BMC credentials —
server-scan does not hold them for Ironic; the caller supplies its own `{VENDOR}_BMC_USERNAME`/`_PASSWORD`.

**`live_recheck_performed: false`** means that manager type is not configured on the API pod and the answer trusts
Mongo; a caller needing freshness should treat it as a failure. The API pod mounts the collector-credentials Secret
for this (except `REDFISH_STANDALONE`'s per-host files, which stay CronJob-only).

### Traps found building `install-server` (ADR-0032, 2026-09-25)

- **`HEALTHY` was not evidence a server can be installed:** ~10 % of assignable servers on one instance had **no
  NIC MACs** (a failed NIC read leaves no network facts to fail a policy) and were drawn first. Use `min_nic_macs`.
- `?name=` used to return an arbitrary match when a hostname spanned several documents — now a 409.
- A tier fill handed `WARNING` servers to a caller that wanted only `HEALTHY` — use `?health=`.
- Not yet done: a per-manager concurrency cap on live rechecks (a retry-looping caller could exhaust a vendor
  manager's session cap). Parked by the operator.

## The reservation lock (ADR-0035)

Why: a server stays `AVAILABLE` until a cluster reports it, and each `install-server` worker only sees its **own**
MCE — so without a lock a machine installed into MCE-A is drawn again for MCE-B and both drive one BMC, with
nothing reporting a conflict. server-scan is the only thing both sides talk to.

- `POST /api/v1/servers/{id}/reservation` (admin) body: `holder` (≤ 64), **`mce_cluster`** (required),
  `infra_env`, `namespace`, `workflow_id`, `ttl_seconds` (default 7200, bounded **300 – 86 400**).
  `DELETE …/reservation` with `holder` / `workflow_id` releases it.
- A sub-document like `maintenance`, **not** a lifecycle state (that field is a reading and would be reset by the
  next collector run). Ingest carries it forward.
- Mutual exclusion is the repository's revision compare-and-set; the loser is told the server is taken.
- A repeat claim with the **same `workflow_id`** extends the lock (Temporal retries activities); sameness keys on
  the workflow id, not the holder.
- It expires on its own; an expired reservation stays on the document as the record of who last held it.
- `/servers/available` excludes live reservations (with `$nor`, and comparing ISO **strings** — two bugs the ADR
  records). The UI shows a badge with the target MCE under the Installation badge; `/servers/rows` carries
  `holder`, `infra_env`, `expires_at`, `mce_cluster`.
- `install-server` takes 2 h, renews while waiting for the Agent, extends to a day on success; after that the
  `nodes-status` agents job marks the machine `INSTALLED_TO_INVENTORY` within ~15 min. An MCE without that job would
  see the machine `AVAILABLE` again after 24 h.

## Scope & caveats

Contract at `08d284c`. Intersight's `get_one()` owner-relation `$filter`s were never run live. Concurrent callers
without a reservation can still be handed the same server — the lock is opt-in for the caller.

## How we know

`team-redbull/server-scan:docs/adr/0032-available-server-lookup-api.md`, `:docs/adr/0035-install-reservation-lock.md`,
`:backend/app/api/v1/servers.py`, `:backend/app/api/v1/reservation_schemas.py`; the Redbull Workflows
`install-server` documentation (`knowledge/temporal/README.md`).

## History

- 2026-11-02: created
