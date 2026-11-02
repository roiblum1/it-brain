# Area `server-scan`

server-scan: our platform (`team-redbull/server-scan`) to discover, inventory and manage bare-metal servers — API,
UI, scanners (collectors), MCP, deployment.

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** `network`

## What server-scan is, in one paragraph

An air-gapped inventory of every physical server in the estate (~2,500 today, sized for 5,000), across Dell, Cisco,
HPE and standalone BMCs. Per-vendor collectors (Kubernetes CronJobs) read UCS Central / Intersight / Dell OpenManage
Enterprise + iDRAC Redfish / HPE OneView / plain Redfish, **classify** each server from its hostname, **score its
health** with declarative policies and upsert it into **MongoDB** (the only source of truth). Jobs inside every
OpenShift cluster (`nodes-status` chart) report which servers each cluster really uses, so "available" means no
cluster holds it. A FastAPI REST API (Redis cache-aside) and a React UI serve it; `GET /api/v1/servers/available`
plus an install **reservation lock** feed the Temporal `install-server` workflow, which replaced
`bmh-generator-operator`. A read-only MCP server and a Claude skill let Claude query the fleet.

## Page map

| Page | Read it when |
|---|---|
| `knowledge/server-scan/server-scan-architecture-collectors-mongodb-api.md` | you need the big picture: components, data flow, layering |
| `knowledge/server-scan/server-scan-inventory-data-model-site-vendor-classification-health.md` | a field means something surprising (site, vendor, installation type vs OpenShift state, `UNKNOWN`, stale) |
| `knowledge/server-scan/server-scan-rest-api-endpoints-filters-auth-tokens.md` | calling the API: endpoints, filters, paging, errors, roles, tokens |
| `knowledge/server-scan/server-scan-available-servers-and-install-reservation-lock.md` | a server is (not) handed out for install, or two MCEs fight over one machine |
| `knowledge/server-scan/server-scan-cluster-membership-nodes-status-jobs.md` | a server shows `AVAILABLE`/`INSTALLED` wrongly, or a cluster's job reports nothing |
| `knowledge/server-scan/server-scan-dell-ome-redfish-collection-and-idrac-reset.md` | Dell servers: identity from OME, hardware from iDRAC, the automatic iDRAC restart |
| `knowledge/server-scan/server-scan-deployment-helm-charts-and-gitops.md` | deploying or upgrading; Argo shows `OutOfSync` or the deploy job is red |
| `knowledge/server-scan/server-scan-configuration-env-vars-reference.md` | which `INVENTORY_*` variable / Helm value controls what |
| `knowledge/server-scan/server-scan-observability-alerts-and-fleet-gauges.md` | an alert fired, or "did the collector stop?" |
| `knowledge/server-scan/server-scan-platform-integrations-temporal-metal3-ome.md` | how server-scan connects to Temporal workflows, Metal3 / MCE, OME and the naming service |
| `knowledge/server-scan/server-scan-development-testing-and-ci-gate.md` | working *in* the server-scan repo: local stack, tests, CI, its conventions |
| `runbooks/server-scan/deploy-or-upgrade-server-scan-with-helm.md` | rolling out a release or a values change |
| `runbooks/server-scan/connect-claude-to-server-scan-mcp-and-personal-token.md` | giving Claude read access to the fleet |
| `runbooks/server-scan/troubleshoot-collector-run-and-stale-servers.md` | a collector failed, servers are stale or `UNKNOWN` |
| `runbooks/server-scan/troubleshoot-server-not-drawn-by-servers-available.md` | install-server cannot get a machine, or gets the wrong one |
| `mcp/servers/server-scan.md` | the read-only MCP server at `/mcp` |

## Belongs here

server-scan behaviour, API contracts, collectors and their vendor quirks *as server-scan sees them*, deployment of the
two charts, its alerts, and how other systems (Temporal workflows, Metal3, OME, Grafana) consume it.

## Not here

Bare-metal provisioning itself (BareMetalHost, Ironic, InfraEnv, Agents) → `knowledge/baremetal/README.md`; the
Temporal workflows that call server-scan → `knowledge/temporal/README.md`; Dell OME / iDRAC as products → a future
Dell compute area; fleet topology → `knowledge/openshift/fleet-topology-hub-mce-hosted.md`.

## Offline sources

The repo itself: `team-redbull/server-scan` — `README.md`, `CLAUDE.md`, `docs/arc42.md` (overview + ADR index in §9),
`docs/architecture.md`, `docs/adr/` (54 ADRs), `docs/*-collectors.md`, `deploy/README.md`,
`.claude/skills/server-scan-api/`. Planned as a `git_repo` source (docs + code at any ref). A running instance also
serves `/docs` (OpenAPI) and `/openapi.json`.

## Redact

Server names that carry real site codes or cluster names → `<server>`, `<site>`, `<cluster>`, `<mce>`; manager and
BMC addresses → `<ome>`, `<idrac>`, `<ip>`; service tags / serials → `<serial>`; the server-scan host →
`<server-scan-host>`. Tokens (`ssk_...`, `INVENTORY_API_TOKEN_*`), BMC/manager credentials, Mongo/Redis URIs and the
session / cursor secrets are secrets. Placeholders: `teams.json`.

## First pages we want

- the real `INVENTORY_SITES` shape (codes as placeholders) and naming convention, cross-checked with day1
- a verified record of one `install-server` run end to end (which phases touched server-scan)
- the `reportOnly: false` decision for iDRAC reset and audit retention, once taken

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
