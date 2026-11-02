---
title: server-scan Dell collection — identity from OpenManage Enterprise, hardware from each iDRAC over Redfish, automatic iDRAC restart on all-UNKNOWN disks or NICs (report-only by default)
type: knowledge
area: server-scan
tags: [server-scan, dell, openmanage, ome, idrac, redfish, collector, idrac-reset, unknown, raid, npar]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (ADR-0020, ADR-0050, docs/dell-collectors.md, CLAUDE.md)
---

# Dell in server-scan: OME for identity, iDRAC for hardware, and the iDRAC restart

## Two passes (ADR-0020)

1. **OME says who exists**: two bulk calls give each server its profile name (the hostname everything keys off —
   site, classification), deployment template, service tag and iDRAC address.
2. **Each server's iDRAC says what it is**: those addresses become Redfish targets and the hardware pass is the
   standalone Redfish provider unchanged (CPU threads, `CapacityBytes`, `MediaType`, NICs, PSUs, RAID).
3. Joined on the BMC host; OME's identity fields are put back on the record.

Why: OME's `InventoryDetails` returned guessable shapes (wrong `InventoryType` names, ambiguous size units, NVMe as
`UNKNOWN` media, no thread count) — ~400 lines of heuristics were deleted in favour of measured Redfish values.

Configuration (names only): `INVENTORY_OME_IP` / `_USERNAME` / `_PASSWORD` for OME, `INVENTORY_OME_BMC_USERNAME` /
`_PASSWORD` / `_PORT` / `_VERIFY_TLS` for the iDRACs, `INVENTORY_OME_NAME_PATTERN` to restrict names. The API pod
gets the same credentials for live rechecks (`knowledge/server-scan/server-scan-available-servers-and-install-reservation-lock.md`).

Dell NPAR partitions are reduced to one entry per physical port; a port with no link state is stored `UNKNOWN`.
The OEM serial was confirmed on iDRAC9 only; Dell iDRAC GPU VRAM reporting is still an open field check.

## Automatic iDRAC restart (ADR-0050)

Field observation: Dell servers that read **every disk or every NIC `UNKNOWN`** usually recover after an **iDRAC**
restart (not a host reboot) — the iDRAC's inventory service had gone stale. So the `OPENMANAGE` collector run can now
write to hardware:

- Trigger: a reachable Dell collected by `OPENMANAGE` with `storage.all_unknown` and/or `network.all_unknown`. Only
  from the CronJob's `IngestService.ingest()` — never `ingest_one`, never `--dry-run`, never the API pod.
  `REDFISH_STANDALONE` is out of scope.
- Checks first: the iDRAC job queue (any job not `Completed`/`CompletedWithErrors`/`Failed`/`RebootFailed`/
  `Scheduled` blocks; unknown states block). A powered-off host is powered **on** first (and a host in maintenance is
  never powered on — that is a `failed` event).
- Action: `Manager.Reset` `GracefulRestart`, sent once, never retried; a dropped connection after the POST is
  `unconfirmed`, not failed.
- Limits (Helm `collectors.ome.idracReset`, env `INVENTORY_IDRAC_RESET_*`): **report-only by default** (logs
  `idrac_reset.not_sent outcome=would_reset`), 12 h cooldown per server (read from the newest `IDRAC_RESET` audit
  event), at most 10 per run, five concurrent workers; resets never block the collection.
- Needs the BMC account to hold Configure Manager and Power Control privileges.
- Every attempt is an audit event `IDRAC_RESET` (`trigger`, `outcome`, `bmc_host`, `power_state`, `powered_on`).

**Before setting `reportOnly: false`:** read a real run's report-only log for `would_reset` and
`skipped_active_jobs`, and confirm the `JobState` values and that `$expand` is honoured (ADR-0050 says these are not
verified live). This is a write against production BMCs from a scheduled job — decide it as a team and record it here.

## Scope & caveats

Dell PowerEdge with iDRAC (iDRAC9 confirmed for the OEM serial). Related: the Temporal `provision-dell-server`
workflow configures new Dells in OME so this collector picks them up
(`knowledge/server-scan/server-scan-platform-integrations-temporal-metal3-ome.md`).

## How we know

`team-redbull/server-scan:docs/adr/0020-dell-identity-from-ome-hardware-from-redfish.md`,
`:docs/adr/0050-idrac-reset-on-all-unknown.md`, `:docs/dell-collectors.md`, `:CLAUDE.md`.

## History

- 2026-11-02: created
