---
title: server-scan configuration reference — INVENTORY_* environment variables by group (managers, sites, auth, tokens, Mongo/Redis, iDRAC reset, MCP) and their Helm values
type: knowledge
area: server-scan
tags: [server-scan, configuration, env-vars, settings, helm-values, pydantic-settings]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (.env.example, backend/app/config/settings.py, deploy/README.md)
---

# server-scan configuration reference

Everything is an `INVENTORY_*` environment variable (`.env.example` lists every one; the Helm chart renders them
from `values.yaml`). Names only here — values belong in the deployment's own secrets.

**Trap:** a pydantic-settings field's name *is* its variable and unknown variables are ignored silently — a
misspelt `INVENTORY_*` is a no-op, not an error (the GPU catalog shipped once under the wrong name). Check
`.env.example`, the Helm values and the field together.

| Group | Variables |
|---|---|
| Runtime | `INVENTORY_ENVIRONMENT` (`production` enforces non-default secrets), `INVENTORY_HOST`, `INVENTORY_PORT`, `INVENTORY_LOG_LEVEL`, `INVENTORY_SERVICE_NAME`, `INVENTORY_CORS_ALLOWED_ORIGINS`, `INVENTORY_CURSOR_SECRET` |
| Sites & naming | `INVENTORY_SITES` (codes:names, `\|` aliases), `INVENTORY_COLLECTOR_NAME_PATTERN`, per-manager `INVENTORY_<MGR>_NAME_PATTERN` |
| Catalogs | `INVENTORY_GPU_MODELS`, `INVENTORY_NIC_OS_NAMES`, `INVENTORY_CAPACITY_ALIASES` |
| Paging & limits | `INVENTORY_DEFAULT_PAGE_SIZE`, `INVENTORY_MAX_PAGE_SIZE`, `INVENTORY_MAX_AVAILABLE_COUNT`, `INVENTORY_REGEX_MAX_PATTERN_LENGTH`, `INVENTORY_REGEX_MATCH_TIMEOUT_SECONDS`, `INVENTORY_AVAILABLE_RECHECK_TIMEOUTS` |
| Freshness & pruning | `INVENTORY_STALE_AFTER_SECONDS` (12 h), `INVENTORY_PRUNE_ENABLED`, `INVENTORY_PRUNE_AFTER_SECONDS`, `INVENTORY_PRUNE_MAX_FRACTION`, `INVENTORY_PRUNE_MAX_RUN_AGE_SECONDS`, `INVENTORY_AUDIT_RETENTION_DAYS` (180), `_REPORT_ONLY`, `_BATCH_SIZE`, `_MAX_BATCHES` |
| MongoDB | `INVENTORY_MONGO_URI`, `INVENTORY_MONGO_DB`, `INVENTORY_MONGO_*_TIMEOUT_MS`, `INVENTORY_MONGO_MIN_POOL_SIZE` / `_MAX_POOL_SIZE` |
| Redis | `INVENTORY_REDIS_URI`, `INVENTORY_REDIS_*_TIMEOUT_SECONDS`, `INVENTORY_REDIS_MAX_CONNECTIONS`, `INVENTORY_CACHE_DEFAULT_TTL_SECONDS` |
| UCS | `INVENTORY_UCS_CENTRAL_IP` / `_USERNAME` / `_PASSWORD` / `_DOMAIN_CONCURRENCY`, `INVENTORY_UCS_MANAGER_USERNAME` / `_PASSWORD` (login for every discovered domain) |
| Intersight | `INVENTORY_INTERSIGHT_IP`, `_API_KEY_ID`, `_API_KEY_PEM`, `_MANAGEMENT_MODES`, `_PAGE_SIZE`, `_READ_TIMEOUT_SECONDS`, `_RUN_BUDGET_SECONDS` |
| Dell | `INVENTORY_OME_IP` / `_USERNAME` / `_PASSWORD`, `INVENTORY_OME_BMC_USERNAME` / `_PASSWORD` / `_PORT` / `_VERIFY_TLS` |
| HPE | `INVENTORY_ONEVIEW_IP` / `_USERNAME` / `_PASSWORD` / `_API_VERSION` / `_VERIFY_TLS` / `_PAGE_SIZE`, `_COLLECT_CPU_THREADS`, `_COLLECT_PSUS`, concurrency knobs |
| Standalone Redfish | `INVENTORY_REDFISH_INVENTORY_FILE`, `INVENTORY_REDFISH_CREDENTIALS_FILE` (TOML, CronJob-only), default `_USERNAME` / `_PASSWORD`, `_CA_BUNDLE`, `_TLS_MIN_VERSION`, timeouts and budgets, `_FLEET_CONCURRENCY`, PCIe GPU detection knobs |
| Collector network | `INVENTORY_COLLECTOR_CONNECT_TIMEOUT_SECONDS` |
| iDRAC reset | `INVENTORY_IDRAC_RESET_REPORT_ONLY`, `_COOLDOWN_HOURS`, `_MAX_PER_RUN` (`knowledge/server-scan/server-scan-dell-ome-redfish-collection-and-idrac-reset.md`) |
| Cluster membership | `INVENTORY_OPENSHIFT_CLUSTER_NAME`, `_MCE_NAME`, `_EXCLUDE_NAME_PARTS`, `_REQUEST_TIMEOUT_SECONDS`, `_SSH_USER`, `_SSH_KEY_FILE`, `_SSH_CONCURRENCY`, `_SSH_CONNECT_TIMEOUT_SECONDS` |
| Auth | `INVENTORY_AUTH_ENABLED`, `INVENTORY_LDAP_SERVER` / `_PORT` / `_USE_SSL` / `_DOMAIN` / `_RECEIVE_TIMEOUT_SECONDS`, `INVENTORY_AD_API_URL` / `_CLIENT_ID` / `_CA_BUNDLE` / `_VERIFY_TLS` / `_RETRIES`, `INVENTORY_AUTH_*_TIMEOUT_SECONDS`, `INVENTORY_AUTH_LOGIN_DEADLINE_SECONDS`, `INVENTORY_AUTH_GROUP_CACHE_TTL_SECONDS`, `INVENTORY_SESSION_SECRET`, `INVENTORY_SESSION_TTL_SECONDS`, `INVENTORY_LOGIN_MAX_FAILURES`, `INVENTORY_LOGIN_LOCKOUT_SECONDS` |
| Role lists | `INVENTORY_ADMIN_GROUPS` / `_USERS`, `INVENTORY_AUDITOR_GROUPS` / `_USERS`, `INVENTORY_VIEW_GROUPS`, `INVENTORY_VIEWER_USERS` (each also as `*_FILE`) |
| Tokens | `INVENTORY_API_TOKEN_ADMIN` / `_AUDITOR` / `_VIEWER` (must differ), `INVENTORY_PERSONAL_TOKEN_TTL_DAYS` |
| Metrics | `INVENTORY_METRICS_ENABLED`, `INVENTORY_METRICS_FLEET_REFRESH_SECONDS` |
| Claude skill | `INVENTORY_SKILL_DIR` (default `/app/skill` in the image) |
| MCP server | `INVENTORY_MCP_API_URL`, `INVENTORY_MCP_PORT` (8090), `INVENTORY_MCP_ALLOWED_HOSTS`; local stdio reads `SERVER_SCAN_TOKEN` |

Matching Helm areas: `config.*` (sites, catalogs, page sizes, stale), `collectors.<vendor>.*` and
`collectors.existingSecret`, `auth.*` (incl. `auth.apiTokens.*`), `db.*`, `backend.cursorSecret`, `mcp.*`, `metrics.*`.
Chart shape: `knowledge/server-scan/server-scan-deployment-helm-charts-and-gitops.md`.

## Scope & caveats

Variable set at `08d284c`; new variables arrive with features — `.env.example` on the deployed tag is the authority.

## How we know

`team-redbull/server-scan:.env.example`, `:backend/app/config/settings.py`, `:deploy/README.md` (Configuration notes).

## History

- 2026-11-02: created
