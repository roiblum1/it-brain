---
title: provision-dell-server workflow — racked Dell with an iDRAC IP to configured machine via OME (discovery, template, root password, BOSS RAID 1 + PERC Non-RAID, profile name), iDRAC9 login lockout, no passwords in history
type: knowledge
area: temporal
tags: [temporal, redbull-workflows, server-provisioning, provision-dell-server, dell, idrac, idrac9, ome, openmanage, redfish, boss, perc, raid, server-template, naming-service, server-scan]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# provision-dell-server

| | |
|---|---|
| Trigger | `POST /workflows/server-provisioning/provision-dell-server` `{idrac_ip, region?}` and `/bulk` `{servers: [...]}` — 202, 409 running, 422 no region |
| Workflow id | `provision-dell-server-<idrac ip>` (address normalised; `010.001.002.003` is refused, not reinterpreted) |
| Queues | workflow `provision-dell-server-workflow`, activity `server-provisioning-activity` (one deployment for the whole estate) |
| Writes | iDRAC (Redfish), Dell OME, the naming service. Reads server-scan once. **No Kubernetes writes, no RBAC** |
| Next | install-server can draw the machine once server-scan has collected it: `knowledge/temporal/install-server-workflow.md` |

Replaces the DC team's manual OME work (discover, build a profile, attach a template, rename) plus the BIOS RAID 1.
A technician racks the server and gives the iDRAC an IP — the last manual step. Dell PowerEdge only.

## Steps

| # | Phase(s) | What | Deadline |
|---|---|---|---|
| 1 | `probing-idrac` | which root password works: target first, then each factory password (`GET /redfish/v1/Systems/System.Embedded.1`, Basic) | 3 rounds; unreachable: every 2 min for 30 min → `IdracUnreachableError` |
| 2 | `reading-identity` → `checking-server-scan` | service tag, model, iDRAC firmware (non-Dell → `NotADellServerError`). Guard: server-scan document (`GET /servers?search=<service tag>` then `/servers/{id}`) not `AVAILABLE` → `ServerAlreadyInstalledError` — a mistyped IP must not reboot a production node. Never `/servers/available` (live vendor recheck) | seconds |
| 3 | `discovering-in-ome` | skipped if OME knows the service tag; else a one-target discovery (group named deterministically from tag + purpose + run id, so a retry finds it), job polled every 30 s | 30 min |
| 4 | `deploying-template` | template for the (Redfish model, iDRAC firmware) pair from `DELL_TEMPLATES` — no fallback (`TemplateNotConfiguredError`); may reboot. A device already carrying this template's profile returns that profile's `DeploymentTaskId`; another template's profile → `ProfileConflictError` | 2 h, polled each minute |
| 5 | `verifying-root-password` → `rediscovering-in-ome` | log in with the target password (the template enforces it); failing → `TemplatePasswordNotAppliedError` (almost always: template lacks the iDRAC **user-2** password attribute). If it arrived on a factory password, re-run OME discovery with the target one or OME loses the machine | 20 min / 30 min |
| 6 | `configuring-storage` → `applying-storage` → `verifying-storage` | RAID 1 across the BOSS pair, every PERC drive Non-RAID, both staged `OnReset` and applied by **one** `ForceRestart`; wait for PERC real-time jobs first (the limb refuses the reset while any job is active); read back and re-plan — convergence is the only success | 90 min apply |
| 7 | `naming-server` → `verifying-name` | the naming service reads cores/memory/disks from OME and renames the profile; the run verifies against the convention, the run's region and the service tag, read back from the OME profile (what server-scan reads) | 30 min → `ServerNameNotAppliedError` |

The run **ends on its own work**: server-scan lists the machine on its next six-hourly OME collection, which the run
deliberately doesn't wait for. Healthy runs take minutes, dominated by the template reboot and Lifecycle Controller RAID.
Name shape: `ocp-dell-<model>-<region>-<cores>c-<mem>gb-<disk>tb-<service tag>`.

## iDRAC9 login lockout

iDRAC9 blocks a source address after **3 failed logins** in its fail window. A probe round is at most three candidates
(target + at most **two** factory passwords — `IDRAC_FACTORY_PASSWORDS` may hold no more), so only an all-wrong round can
trip the block, and the next round waits the penalty out (11 min) instead of feeding it. Three rounds →
`IdracCredentialsRejectedError`.

## No password is ever in Temporal history

Inputs, results and errors are recorded verbatim and readable by anyone with Temporal UI access, so a run carries a
**credential index** (`IdracRef.credential`: `0` = target, `1…` = factory in order), resolved by the limb against its
Secret at call time. History, logs and result say `credential=1` / `factory-1`. An index with no password behind it →
`IdracCredentialsMissingError`. Only iDRAC **user 2 (root)** is touched — the OME service account on the iDRAC is never
read or changed (changing it would cut OME, and server-scan, off from the machine).

## Storage policy: nothing is deleted to make room

Builds: BOSS (M.2 boot pair) → one RAID 1 (OS disk); every PERC drive → Non-RAID (ODF / local storage want whole disks).
CPU-attached NVMe and embedded SATA are left alone. NVMe drives report RAID status under `DellPCIeSSD`, not
`DellPhysicalDisk` — read both or a drive silently drops. `StorageLayoutUnsupportedError` (before anything is staged) for:
a drive already in a volume, a BOSS volume that isn't exactly that RAID 1, a PERC already holding volumes, a drive neither
`Ready` nor `NonRAID`. Delete by hand if really unused.

> **Templates must not carry storage components.** A Dell server profile template with storage deploys with
> `RAIDresetConfig=True`, which wipes the controller at step 4 — before the workflow reads the layout. Capture templates
> from BIOS and iDRAC components only. Templates fit only the firmware they were captured from (hence per-firmware keys).

## Region

Resolved **at the edge** (the router), from the iDRAC address prefix table, and passed in as input — editing the table
never changes an in-flight run (a lookup inside the workflow would be non-deterministic on replay), and an unmatched
address is a 422 now (`rejected` in `/bulk`, the common case) instead of a failed run later. Explicit `region` overrides.
The region must be a **server-scan site code**: it becomes the `<region>` token of the name, from which server-scan
parses the site — wrong means filed under the wrong site.

## Errors and config

Activity-permanent: `IdracAuthError`, `IdracCredentialsMissingError`, `IdracRequestRejectedError`, `OmeAuthError`,
`OmeRequestRejectedError`, `TemplateNotConfiguredError`, `TemplateNotFoundError`, `ProfileConflictError`,
`ServerNamerRejectedError`, `ServerScanAuthError`. Workflow-raised: `RegionMissingError`, `NotADellServerError`,
`ServerAlreadyInstalledError`, `IdracUnreachableError`, `IdracCredentialsRejectedError`, `OmeDiscoveryFailedError`,
`TemplateDeployFailedError`, `TemplatePasswordNotAppliedError`, `StorageLayoutUnsupportedError`, `StorageJobFailedError`,
`StorageNotConvergedError`, `ServerNameNotAppliedError`. Each activity gets 5 min per attempt. No rollback: nothing is
destructive, so a half-provisioned machine is safe to leave and re-run (continues from the first missing thing).

`server-provisioning-config`: `OME_URL` (`https://` only, no default — a wrong one reboots another site's fleet),
`DELL_TEMPLATES` (model → firmware → template), `SERVER_NAMER_URL`, `SERVER_SCAN_URL` (incl. `/api/v1`, read-only).
Secret (worker credentials): `OME_USERNAME`/`OME_PASSWORD` (OME device-manager rights), `IDRAC_ROOT_PASSWORD`, `IDRAC_FACTORY_PASSWORDS` (≤ 2),
optional `SERVER_NAMER_API_TOKEN`, `SERVER_SCAN_API_TOKEN` (viewer is enough). Watch `progress.phase` and `waiting_on`.

## History

- 2026-11-02: created from the provision-dell-server page of the Redbull Workflows docs site v1.0.61
