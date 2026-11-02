---
title: server-scan architecture — vendor collectors (CronJobs) write MongoDB, FastAPI + React serve it, nodes-status jobs report cluster use
type: knowledge
area: server-scan
tags: [server-scan, architecture, collectors, mongodb, redis, fastapi, react, cronjob, inventory, bare-metal]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (README.md, docs/arc42.md, docs/architecture.md, ADR-0001/0023/0024)
---

# server-scan architecture

server-scan is the bare-metal inventory of the whole estate: one record per physical server, with what it is
(hardware, NICs, BMC), what it was named to be, whether a cluster uses it, and whether it is healthy. Charter and
page map: `knowledge/server-scan/README.md`.

## Components

```
 UCS Central ─┐                                           ┌─ FastAPI (backend/app) ── React SPA (frontend/)
 Intersight ──┤  one Kubernetes CronJob per manager type  │    Redis cache-aside        nginx proxies /api /health
 Dell OME ────┼─ tools/run_collector.py ─▶ MongoDB ───────┤    /servers/available ─▶ vendor manager (live recheck)
 HPE OneView ─┤  classify → health → audit → upsert       │    /mcp (optional, read-only MCP server)
 Redfish ─────┘                                ▲          └─ Prometheus /metrics, fleet gauges
                                               │
 nodes-status CronJobs, one release per OpenShift cluster ─┘ write Server.openshift only
```

| Piece | Where | What it does |
|---|---|---|
| Collectors | `tools/run_collector.py --manager-type <TYPE>`, `backend/app/infrastructure/providers/<vendor>/` | One `ServerInventoryProvider` per vendor; normalise to `ProviderServer`; feed `IngestService` |
| Ingest | `backend/app/application/services/ingest.py` | Classify (regex on hostname), evaluate health policies, write audit events, upsert — one write per server, revision compare-and-set |
| MongoDB | operated service (chart can bundle one for labs) | **The only source of truth** (ADR-0001). The only link between a collector run and what the API serves |
| Redis | optional, non-persistent | Cache-aside, login throttle, group-membership cache. Every read degrades to Mongo |
| API | `backend/app/api/v1/` (FastAPI, async PyMongo) | REST under `/api/v1`, RFC 9457 errors, AD login, tokens — `knowledge/server-scan/server-scan-rest-api-endpoints-filters-auth-tokens.md` |
| UI | `frontend/` (React + TypeScript, dark only for wall displays) | Sites, Servers, Events, Rules & Policies, Architecture, Claude (`/skill`) pages |
| nodes-status | `deploy/helm/nodes-status`, `tools/collect_openshift.py` | Per-cluster jobs that mark servers `INSTALLED` / free them — `knowledge/server-scan/server-scan-cluster-membership-nodes-status-jobs.md` |
| MCP server | `tools/mcp_server/` | Read-only MCP over the REST API — `mcp/servers/server-scan.md` |
| Maintenance jobs | `tools/prune_servers.py`, `tools/prune_events.py` | Delete servers no manager lists any more; delete old audit events (both report-only / dry-run by default) |

## Collectors (five, plus a login-only sixth)

| `ManagerType` | Vendor | How it reads |
|---|---|---|
| `UCS_CENTRAL` | Cisco | discovers every UCS domain, then logs into each UCS Manager (`UCS_MANAGER` is a login with no endpoint and no CronJob) |
| `INTERSIGHT` | Cisco | signed API requests (key id + PEM), not user/password |
| `OPENMANAGE` | Dell | identity (name, template, service tag, iDRAC address) from OME, **hardware from each iDRAC over Redfish** (ADR-0020) — `knowledge/server-scan/server-scan-dell-ome-redfish-collection-and-idrac-reset.md` |
| `ONEVIEW` | HPE | OneView only, every iLO generation; BMC reachability from an unauthenticated Redfish probe |
| `REDFISH_STANDALONE` | any | one BMC at a time from a TOML inventory + credentials file, for machines no manager owns |

A collector's whole connection config is one endpoint and one login per manager type, from env vars
(`EnvConnectionResolver`, ADR-0012); a half-configured vendor fails naming the missing variables. A failing
manager is counted but never aborts the run for the others. Every collector has had a live field pass on real
hardware (each found at least one defect the API contract alone could not). Adding a vendor = one provider class +
one CronJob.

## Layering and design rules that shape everything

- Hexagonal layout: `domain` (models, enums, health/classification engines) / `application` (services) /
  `infrastructure` (Mongo, Redis, providers, AD, OpenShift client) / `api`. Import contracts are enforced (`lint-imports`).
- **`None` from a provider means "not read this run"**, never zero; ingest carries the stored value forward and lists
  the path in `Server.unread_fields`. "Read, and nothing there" is `()`/`0`/`""`.
- **Ingest skips unchanged servers** (only `touch_seen`) and uses a revision CAS so a collector never overwrites a
  maintenance / reservation / membership write made mid-run (ADR-0044).
- **Fleet-sized responses bypass Pydantic validation** (`/servers/rows` reads a Mongo projection; ~16 ms vs ~544 ms
  for 2.5k servers, ADR-0033) and are byte-stable so the ETag yields 304s on the UI's 30 s poll.
- **Only one endpoint talks to a vendor manager:** `GET /servers/available` (ADR-0032).
- The API was load-verified at 10k and 50k servers as headroom (ADR-0007); the UI is built for 2.5k–5k.

## Scope & caveats

Read from the repo at commit `08d284c` (2026-11-01). Not exercised from the brain against our deployment. Schedules,
toggles and defaults are the chart's; production values live in `team-redbull/redbull-platform`
(`knowledge/server-scan/server-scan-deployment-helm-charts-and-gitops.md`).

## How we know

`team-redbull/server-scan:README.md`, `:docs/arc42.md`, `:docs/architecture.md`, `:CLAUDE.md`, `:.claude/rules/collectors.md`.

## History

- 2026-11-02: created
