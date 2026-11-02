---
title: server-scan alerts and fleet gauges — ServerScanCollectorSilent, ServersStale, ClusterSilent, MembershipUnmatched, and which Prometheus evaluates a PrometheusRule
type: knowledge
area: server-scan
tags: [server-scan, observability, prometheus, prometheusrule, alerts, grafana, fleet-gauges, metrics, thanos-ruler, user-workload-monitoring]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (ADR-0029, deploy/helm/server-scan/templates/backend-prometheusrule.yaml, backend/app/observability/, deploy/grafana/)
---

# server-scan alerts and fleet gauges

"Did the collector stop?" has no answer in a single request log, so the API exports **fleet gauges computed from
MongoDB** (ADR-0029), refreshed every `INVENTORY_METRICS_FLEET_REFRESH_SECONDS`, plus request metrics at `/metrics`.
A Grafana dashboard ships in `deploy/grafana/server-scan-dashboard.json`. How we query metrics in general:
`knowledge/observability/grafana-one-datasource-per-cluster-prometheus.md`.

## Metrics worth knowing

| Family | Examples |
|---|---|
| Fleet | `server_scan_servers`, `server_scan_servers_by_health`, `server_scan_servers_stale`, `server_scan_servers_unreachable`, `server_scan_servers_in_maintenance`, `server_scan_servers_partial`, `server_scan_policy_active` |
| Collectors | `server_scan_collector_last_run_timestamp_seconds`, `_duration_seconds`, `_servers_fetched`, `_servers_unchanged`, `_collection_errors`, `_ingest_errors`, `_partial`, `server_scan_collector_last_seen_timestamp_seconds` |
| Cluster membership | `server_scan_membership_last_run_*` (`observed`, `matched`, `matched_by_serial`, `unmatched`, `unresolved`, `partial`), `server_scan_cluster_last_reported_timestamp_seconds`, `server_scan_cluster_servers_held`, `server_scan_openshift_contested_servers`, `server_scan_openshift_name_mismatch_servers` |
| Data quality | `server_scan_duplicate_name_groups`, `server_scan_duplicate_name_servers` |
| Audit | `server_scan_audit_events`, `server_scan_audit_oldest_event_timestamp_seconds` |

## Alerts (PrometheusRule from the chart)

| Alert | Fires when |
|---|---|
| `ServerScanCollectorSilent` | a collector has not run for longer than its threshold |
| `ServerScanCollectorRunPartial` | the last run of a collector was partial |
| `ServerScanServersStale` | stale servers above threshold for 30 min |
| `ServerScanServersWithoutRaid` | policy `raid.os_mirror_missing` active on any server for 1 h |
| `ServerScanClusterSilent` / `ServerScanMembershipRunSilent` | a cluster's `nodes-status` job stopped reporting |
| `ServerScanMembershipUnmatched` | a membership job keeps seeing hosts that match no server (1 h) |
| `ServerScanFleetSnapshotFailing` | the gauge refresh itself fails |
| `ServerScanLoginDependencyFailing` / `ServerScanLoginSlow` | LDAP / AD API failing or login p95 slow |
| `ServerScanAvailableRecheckFailing` | live rechecks against vendor managers failing |
| `ServerScanAuditRetentionBehind` | audit pruning not keeping up |
| `ServerScanApi*`, `ServerScanFrontend*`, `ServerScanPod*` | replicas unavailable, down, restarting, OOMKilled, near memory limit, scrape down |

## The evaluator trap (cost real time)

On OpenShift a PrometheusRule is evaluated by **exactly one** of two components, chosen by a label: with
`openshift.io/prometheus-rule-evaluation-scope: leaf-prometheus` the user-workload Prometheus (sees only user
namespaces — no `kube_*` / `container_*` series); without it a Thanos Ruler that may have no Alertmanager or
remote-write. **Nothing in `oc get prometheusrule` shows which.** Verify every series a rule uses exists in its
evaluator. Also assume every series is duplicated per HA replica in the central store: dashboards reduce with
`max without (prometheus, prometheus_replica)` before any sum or join. Chart values: `metrics.serviceMonitor.*`
and the thresholds near `config.*` / `metrics.*` in `values.yaml`.

## Scope & caveats

Alert names and series from the chart at `08d284c`; thresholds are values-driven and differ per deployment.

## How we know

`team-redbull/server-scan:deploy/helm/server-scan/templates/backend-prometheusrule.yaml`,
`:backend/app/observability/fleet_gauges.py`, `:docs/adr/0029-fleet-gauges-from-mongodb.md`, `:CLAUDE.md`,
`:deploy/README.md` (Metrics section).

## History

- 2026-11-02: created
