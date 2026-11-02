---
title: Troubleshoot a failing server-scan collector run, stale servers or servers stuck at UNKNOWN health (ServerScanCollectorSilent, ServersStale)
type: runbook
area: server-scan
tags: [server-scan, collector, cronjob, stale, unknown, troubleshooting, ome, ucs, intersight, oneview, redfish, alerts]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (.claude/rules/collectors.md, tools/run_collector.py, ADR-0027/0037/0050, docs/field-test-checklist.md)
---

# Troubleshoot a collector run or stale / UNKNOWN servers

**When to use:** `ServerScanCollectorSilent`, `ServerScanCollectorRunPartial` or `ServerScanServersStale` fired; servers
show `stale=true`, `reachable=false` or health `UNKNOWN`.
**Impact while running:** none for the read-only steps; step 5 (manual run without `--dry-run`) writes to MongoDB.
**Prerequisites:** `oc` access to the server-scan namespace; metrics via Grafana
(`knowledge/server-scan/server-scan-observability-alerts-and-fleet-gauges.md`).

## Pre-checks

```bash
oc -n <server-scan-ns> get cronjob                 # schedule, SUSPEND, LAST SCHEDULE per collector
oc -n <server-scan-ns> get jobs --sort-by=.metadata.creationTimestamp | tail
oc -n <server-scan-ns> logs job/<collector-job> | tail -100
```

## Procedure

1. **Did it run?** CronJob suspended (standalone Redfish ships suspended), not enabled, or the schedule moved. A job that
   exits immediately with code 2 is **not configured**: the log names the missing `INVENTORY_<MGR>_*` variables.
2. **Did it finish?** Exit 1 = total failure (manager unreachable, login rejected, API shape changed); exit 3 = partial.
   One failing manager never aborts the others of the same type — read per-manager errors in the log and
   `server_scan_collector_last_run_collection_errors`.
3. **Per-server unreachable:** `reachable=false` with `unreachable_reason` (`network_unreachable`, `auth_rejected`,
   `tls_error`, `timeout`, `protocol_error`) is the BMC, not server-scan. Check the flow from the collector pod to the
   manager / BMC (`interfaces/ocp-network-palo-alto-flows.md`) and the account.
4. **`UNKNOWN` is "not read"**, not "bad": look at the server's `unread_fields` (UI detail page or
   `GET /api/v1/servers/{id}`). Dell servers with every disk or every NIC `UNKNOWN` are the iDRAC-restart case —
   check the report-only `idrac_reset` log lines (`knowledge/server-scan/server-scan-dell-ome-redfish-collection-and-idrac-reset.md`).
5. **Reproduce by hand** from a pod with the same image and env:
   ```bash
   python -m tools.run_collector --manager-type <TYPE> --dry-run     # reads and normalises, writes nothing
   ```
6. **Stale but the collector is green:** the manager no longer lists the server (decommissioned, moved to another
   manager → a new document under another `source_provider`/vendor), or it is filtered by `namePattern`. Pruning
   (`tools/prune_servers.py`, dry-run unless enabled) deletes servers whose `listed_at` is old, with guards.

## Verification

After the next scheduled run: `server_scan_collector_last_run_timestamp_seconds` advanced, `_partial` is 0, the server's
`last_seen_at` is recent and `stale=false`.

## Rollback

Nothing to roll back for read-only checks. If you changed collector values, revert them in `redbull-platform`
(`runbooks/server-scan/deploy-or-upgrade-server-scan-with-helm.md`).

## History

- 2026-11-02: created
