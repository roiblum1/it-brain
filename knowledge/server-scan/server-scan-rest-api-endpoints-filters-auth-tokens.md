---
title: server-scan REST API — /api/v1 endpoints, filters and cursor paging, RFC 9457 errors, AD roles (admin/auditor/viewer), static and personal ssk_ tokens
type: knowledge
area: server-scan
tags: [server-scan, api, rest, fastapi, filters, paging, rfc9457, auth, ldap, active-directory, roles, api-token, personal-token]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (README.md, backend/app/api/v1/*.py, .claude/skills/server-scan-api, ADR-0034/0039/0043/0053)
---

# server-scan REST API, auth and tokens

Base: `https://<server-scan-host>` (one Route; the SPA's nginx forwards `/api/`, `/health/`, `/metrics`, `/docs`,
`/redoc`, `/openapi.json` and, when enabled, `/mcp`). Interactive docs at `/docs` work offline (assets vendored,
ADR-0040). Data meaning: `knowledge/server-scan/server-scan-inventory-data-model-site-vendor-classification-health.md`.

## Endpoints

| Method + path | Purpose | Role |
|---|---|---|
| `GET /api/v1/servers` | list with filters, `search`, `sort`, cursor paging | any |
| `GET /api/v1/servers/rows` | whole fleet as flat rows (what the UI loads; weak ETag → 304) | any |
| `GET /api/v1/servers/{id}` | full detail: hardware, NICs, BMC, health reasons | any |
| `GET /api/v1/servers/available` | live-verified assignable servers for BareMetalHost creation — **not a pure read** | any (machine callers) |
| `GET /api/v1/sites` | per-site and fleet counts | any |
| `GET /api/v1/events`, `/events/actors`, `/servers/{id}/events` | audit trail | admin, auditor (viewer → 403) |
| `GET /api/v1/health-policies[/{id}]`, `/health-metrics`, `/classification-rules[/{id}]` | the rules applied | any |
| `PUT` / `DELETE /api/v1/servers/{id}/maintenance` | maintenance on/off (`reason`, `expected_end`) | admin |
| `POST` / `DELETE /api/v1/servers/{id}/reservation` | install lock take/release | admin |
| `POST /api/v1/servers/{id}/reclassify`, `/health/recalculate` | re-run the engines on one server | admin |
| `POST /api/v1/auth/login`, `/logout`, `GET /auth/me` | AD session cookie | — |
| `GET/POST/DELETE /api/v1/auth/token`, `GET /auth/tokens`, `DELETE /auth/tokens/{username}` | personal tokens | session only (admin for the fleet-wide two) |
| `GET /api/v1/skill`, `/skill/download?base_url=` | the Claude skill, live from disk (ADR-0052) | any |
| `GET /health/live`, `/health/ready`, `/metrics` | probes, Prometheus | none |

`/servers/available` and the reservation contract: `knowledge/server-scan/server-scan-available-servers-and-install-reservation-lock.md`.

## Filters, search, paging

- `/servers` filter keys are **exactly** `site_id`, `vendor`, `manager_id`, `installation_type`, `health_overall`,
  `maintenance`, `source_provider`, `openshift_state`, `cluster_name`, `stale` — anything else is
  `400 UNKNOWN_FILTER` (listing the allowed keys). For other fields (model, MCE, MAC, BMC host, reachability) read
  `/servers/rows` and filter client-side.
- Values are case-sensitive (`vendor=hp`, `health_overall=CRITICAL`, `site_id` lowercase, `unassigned` for none).
- `search` is a word-boundary token search over name / serial / model (ADR-0025, 0046 for exact and regex modes).
- Paging is by cursor: `page_size` (default 50, max 200), pass `cursor=<page.next_cursor>` with the **same filters**
  until `page.has_more` is false (`CURSOR_FILTER_MISMATCH` otherwise); `with_count=true` for a total; `sort`
  (`name`, `serial`, `model`, `updated_at`, `last_seen_at`, `openshift_state`, `cluster_name`, `mce_name`) + `sort_desc`.
- Errors are RFC 9457 `application/problem+json` with a stable `code` to branch on (`UNKNOWN_FILTER`,
  `PAGE_SIZE_TOO_LARGE`, `NOT_FOUND`, `AVAILABLE_SERVER_NAME_AMBIGUOUS`, …).

## Authentication and roles

- **`INVENTORY_AUTH_ENABLED` is false by default**: every caller is a fixed dev-admin, no login page. Turn it on for
  any shared deployment.
- With auth on, users log in with AD: an LDAP simple bind as `DOMAIN\user` checks the password, then the operator's
  REST "AD API" resolves recursive group membership. A stateless session cookie follows (a Redis restart logs nobody out).
- Three roles (ADR-0043), from six group/user lists checked in this order: **admin** (everything, incl. the
  mutations) → **auditor** (read-only + audit trail) → **viewer** (read-only, no audit trail). A login matching none
  is rejected (403), never silently read-only. Upgrading to the auditor model took the audit trail away from
  existing viewers.
- Login throttle: 5 wrong passwords per username → 429 for 15 min, in Redis, **fails open** if Redis is down
  (ADR-0039). Every call on the login path has a timeout and a 503 says which dependency failed (ADR-0042). Every
  login is an audit event (`LOGIN_SUCCEEDED`, `LOGIN_DENIED`); a wrong password deliberately is not.
- Every router except `health`/`auth`/`metrics` needs a resolved caller; each write additionally needs `require_admin`.

## Tokens

| Kind | What | Use |
|---|---|---|
| Static `INVENTORY_API_TOKEN_ADMIN` / `_AUDITOR` / `_VIEWER` | shared bearer tokens; must all differ or the API refuses to start | machine callers — e.g. Temporal `install-server` needs **admin** (it takes the reservation lock); `provision-dell-server` needs only viewer |
| Personal `ssk_...` (ADR-0053) | one per user, created on the UI's Claude page (`POST /auth/token`), SHA-256 hashed at rest, expires after `INVENTORY_PERSONAL_TOKEN_TTL_DAYS` (default 90, max 365) | humans and their Claude: role capped at `VIEWER` (viewer) or `AUDITOR` (auditor and admin) — **never admin**; acts as `token:<username>` in the audit trail |

Personal-token caveats: a token cannot create a token; AD membership is **not re-checked** (an admin revokes a
leaver's with `DELETE /auth/tokens/{username}`); a bad `ssk_` token is a 401 even next to a valid cookie; a
user has only one token, so two machines share it. With auth off the token endpoints answer 404.

## Scope & caveats

From code and docs at `08d284c`. Use `$BASE_URL/openapi.json` on the instance as the authority for the version
deployed. Never paste a token into a brain page or a command line that is logged.

## How we know

`team-redbull/server-scan:backend/app/api/v1/servers.py`, `:tokens.py`, `:auth.py`, `:.claude/skills/server-scan-api/SKILL.md`,
`:deploy/README.md` (Auth), ADRs named above.

## History

- 2026-11-02: created
