---
title: server-scan deployment — Helm charts server-scan and nodes-status, GHCR images, redbull-platform GitOps copy, Argo OutOfSync from missing values keys
type: knowledge
area: server-scan
tags: [server-scan, deployment, helm, argocd, gitops, redbull-platform, ghcr, images, cronjob, mongodb, redis, air-gap, outofsync]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (deploy/README.md, deploy/helm/*/values.yaml, ADR-0010/0031, docs/air-gap.md)
---

# server-scan deployment

Procedure: `runbooks/server-scan/deploy-or-upgrade-server-scan-with-helm.md`. Variables: `knowledge/server-scan/server-scan-configuration-env-vars-reference.md`.

## Two charts

| Chart | Deploys | Releases |
|---|---|---|
| `deploy/helm/server-scan` | API (Deployment/Service/ConfigMap, Route when no frontend), optional frontend, optional MCP server, optional bundled MongoDB / Redis (Bitnami subcharts, vendored `.tgz`), collector CronJobs, prune jobs, PrometheusRule / ServiceMonitor | one per environment |
| `deploy/helm/nodes-status` | the two membership CronJobs (`knowledge/server-scan/server-scan-cluster-membership-nodes-status-jobs.md`) | **one per OpenShift cluster**, via an Argo CD Application each |

Toggles in `server-scan` (all default **off**): `frontend.enabled`, `mcp.enabled` (needs the frontend),
`mongodb.enabled`, `redis.enabled`, `collectors.<vendor>.enabled` for `ucsCentral`, `intersight`, `ome`,
`oneview`, `redfishStandalone` (deployed **suspended** until its manual steps are done), `fake`, plus
`collectors.prune` and `collectors.auditRetention` (on, but **report-only**). Collector schedule default
`0 */3 * * *`; collector `namePattern` default `^ocp`.

Exactly one Route: the frontend's when enabled (its nginx forwards `/api/`, `/health/`, `/metrics`, `/docs`,
`/redoc`, `/openapi.json`, `/mcp` in-cluster), else the API's. To expose another path add a `location` block to
`frontend-api-proxy-configmap.yaml`.

## Databases

MongoDB is the system of record and in production is an **operated service** (its own backup/replication), not the
chart's pod; Redis is an optional cache (every read degrades to Mongo). Unbundled connection strings come from a
Secret (`db.secretName`, default `server-scan-db`, keys `mongo-uri` / `redis-uri`) — either rendered from
`db.mongoUri` / `db.redisUri` (plaintext in values: only in a trusted private repo) or provisioned outside.
`db.dbName` (default `server-scan`) is the database actually used — the URI's path is ignored — and must match the
`nodes-status` chart's. Bundled passwords must be set explicitly (Argo renders with `helm template`, which has no
`lookup`, so a generated password is re-minted each sync); prefer `existingSecret`.

## Images and release flow

- Every green push to `main` publishes `ghcr.io/team-redbull/server-scan-api` and `server-scan-frontend`, versioned
  from Conventional Commits (`feat!` = major); tags are `X.Y.Z` without `v`. Release notes are the commit subjects (ADR-0010).
- Images default to the chart `appVersion`; **never use `latest`** (with `IfNotPresent` a node keeps the first
  `latest` it pulled — the chart's first deployment failed that way).
- Production: `team-redbull/redbull-platform` holds a copy under `gitops/charts/server-scan`; CI's deploy job syncs
  **only `templates/` and `files/`**, pins image tags and `appVersion` (ADR-0031). That repo's `values.yaml` is
  hand-maintained. Argo CD does the rest — a green push reaches the cluster on its own.
- The MCP server runs from the API image with another command; the frontend image is nginx on UBI; the API image is
  UBI9 minimal with a standalone CPython 3.13 and must run under OpenShift's arbitrary UID.

## Traps (each cost a release)

- **A ConfigMap key missing from the downstream `values.yaml` renders as YAML null and Kubernetes drops it**, so Argo
  diffs forever (`server-scan-api-config` permanently `OutOfSync`, auto-syncing every few minutes). Int/bool/enum
  keys are now `required`; `sites`, `gpuModels`, `nicOsNames`, `corsAllowedOrigins`, `capacityAliases` are not
  (blank is legitimate) — check them by hand when new.
- **A whole new values block absent downstream is a Go-template nil-pointer panic**, not a clean error: adding
  `auth:` once turned the deploy job red for a day and froze the cluster on the old image. New templates must read
  keys with `default` / `hasKey`.
- `INVENTORY_ENVIRONMENT=production` refuses the committed dev cursor secret (and session secret when auth is on);
  an empty `secretKeyRef` counts as "set" and fails the same way.
- Air gap: Python wheels (`requirements.txt` / `pylock.toml`, hash-pinned exports), npm (`npm ci --offline`), the
  CPython tarball and the Bitnami subcharts must be mirrored (`docs/air-gap.md`, `deploy/air-gapped-images.txt`).
  Confirm the mirror carries `mcp==1.30.0` before enabling the MCP server.

## Scope & caveats

Chart behaviour at `08d284c`; our real values are in `redbull-platform` (not read here). Fleet GitOps conventions:
`knowledge/gitops/day2-sites-tree-discovery-and-version-layers.md`.

## How we know

`team-redbull/server-scan:deploy/README.md`, `:deploy/helm/server-scan/values.yaml`, `:deploy/helm/nodes-status/values.yaml`,
`:docs/air-gap.md`, `:.github/workflows/ci.yml`.

## History

- 2026-11-02: created
