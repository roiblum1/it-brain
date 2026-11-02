---
title: install-server workflow — draw a healthy server from server-scan into an MCE InfraEnv (BareMetalHost + BMC Secret + NMStateConfig bond), wait for an Agent, roll back and try the next candidate
type: knowledge
area: temporal
tags: [temporal, redbull-workflows, server-lifecycle, install-server, server-scan, baremetalhost, nmstateconfig, infraenv, agent, bmac, metal3, bond, lacp, install-lock, ironic]
applies_to: [hosted-cp]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# install-server

| | |
|---|---|
| Trigger | `POST /workflows/server-lifecycle/install-server` — 202; 409 only if a **named** machine is already installing |
| Workflow id | pool draw: `install-server-<mce>_<infraEnv>_<slot>` (first free slot); named: `install-server-<mce>_<server>` |
| Queues | workflow `install-server-workflow`; activities on `server-lifecycle-activity-<mce>` (+ one on `segment-lifecycle-activity`) |
| Writes | on the MCE: BMC `Secret`, `BareMetalHost`, `NMStateConfig`; in server-scan: the install lock; (IPMI blades) the site PXE VM |
| Way back | `knowledge/temporal/uninstall-server-workflow.md` |

Replaced **bmh-generator-operator** (BareMetalHostUCS, a Kopf operator querying HP OneView, UCS Central, Dell OME and
Intersight on every reconcile): server-scan already collects that every 6 h, so one HTTP call replaced four vendor
SDKs. server-scan: `knowledge/server-scan/README.md`. Metal3 / Agent background: `knowledge/baremetal/README.md`.
Architecture and the per-MCE queue: `knowledge/temporal/redbull-workflows-orchestrator-architecture.md`.

## Request (`InstallServerRequest`)

`infra_env` (required; also the hardware query), `mce_cluster` (required; picks the INVENTORY segment **and** the
activity queue), `namespace` (default `inventory`; **must be the InfraEnv's own namespace** — BMAC looks for the
InfraEnv beside the BareMetalHost), `server_names` (one or a list of 1–20; turns off the already-installed skip),
`count` (1–20 pool runs in parallel), `candidate_count` (1–20; default runs on the pool + new runs + 2, so 3 for a lone
install), `labels`. Unknown fields are 422 — notably `vlan_id` (the VLAN belongs to the MCE's segment), the old
`server_name`, and `count`/`candidate_count` next to `server_names`. `count` is **not retry-safe**: sent twice it starts 2N runs.

Pool query: server-scan `GET /servers/available?pattern=^ocp-<infraEnv>&health=HEALTHY&count=N` — an InfraEnv name
(vendor-model-site-cores-memory) is the prefix of the server-scan names it wants, escaped as regex. Named:
`?name=<server>&count=1`. Every server is its own run; a second pool trigger takes the next slot (never 409).

## The run in plain terms

1. `resolving-vlan` — `get_inventory_segment`: the MCE's **one** `INVENTORY` segment, by cluster name (matched
   client-side; re-checked in the workflow). Missing / two / another cluster's → `InventorySegmentNotFoundError` /
   `AmbiguousInventorySegmentError` / `InventorySegmentMismatchError`, all non-retryable, before any draw.
2. `acquiring-server` — one server-scan read; it live-rechecks each candidate (seconds to ~1 min). `HEALTHY` is asked
   server-side (otherwise it fills with WARNING/MAJOR). Nothing → `ServerNotAvailableError`.
3. `selecting-server` → `reserving-server` — per candidate, first that passes: name valid as a k8s name once
   lowercased; `bmc_vendor` has an Ironic driver; a BMC host was collected; **two link-up NICs on two distinct physical
   ports**; MACs well-formed; no BareMetalHost already on this MCE (skipped when named); then take server-scan's
   **install lock** (`POST /servers/{id}/reservation`, 2 h, keyed on the workflow id). Each failure is a **skip**, not a failed run.
4. `creating-secret` → `creating-baremetalhost` → `creating-nmstateconfig` — `<vendor>-cred-<server>`,
   `baremetalhosts/<server>` with `customDeploy: start_assisted_install`, `nmstate-config-<server>` (802.3ad bond +
   tagged VLAN). Names byte-identical to bmhgen's (converges with resources it created) but **lowercased** (server-scan
   names carry an uppercase serial). Existing resources are success if identity fields match (BMC address, credential
   Secret, boot MAC, InfraEnv, VLAN, MAC set unordered); otherwise non-retryable `BmhConflictError`.
   IPMI (UCS) blades add `registering-pxe-boot` / `publishing-pxe-boot` (boot MAC → `<mce>/<infraenv>.ipxe` on the site's
   PXE VM; waits ≤ 10 min for a fresh discovery image, else `InfraEnvImageNotUpdatedError`).
5. `awaiting-agent` — `find_agent_for_host` every 30 s, **≤ 1 h**. An Agent proves BMC virtual media, bond, VLAN and DHCP
   all worked. Matched by **bond MAC**, never by name (BMAC names Agents by inventory UUID; `agent.spec` has no BMH ref).
   Lock renewed to 2 h as the wait starts. Agent → `holding-server` (lock extended to **24 h**) → `completed`.
6. No Agent → `rolling-back` → `releasing-server` → next candidate. Pool exhausted → `AgentNeverAppearedError`, with
   candidates grouped by reason (different reasons belong to different people). Worst case ≈ 1 h per candidate.

Replaced a 10-minute Ironic-registration deadline: on an unreachable BMC Metal3 reports `registering` with
`operationalStatus: OK` and no `errorType` — seen unchanged for **14 h** on a live cluster; a host with a wrong
bond/VLAN registers fine and is never heard from again. Only an Agent distinguishes slow from dead.

## Rollback order (learned on live clusters)

1. **Detach first** — `baremetalhost.metal3.io/detached` set *after* `deletionTimestamp` is inert (measured 4 min).
2. Delete the NMStateConfig explicitly (no finalizer, no ownerReference).
3. Delete the host and wait, bounded.
4. Drop **metal3's** finalizer `baremetalhost.metal3.io` if it won't release (it tries to deprovision through the BMC
   that never answered — the expected path here). Never BMAC's `bmac.agent-install.openshift.io/deprovision` (releases in < 1 s).
5. Confirm the Secret is gone (ownerReference to the BMH; name read from the host's `credentialsName`).
Teardown never reports success while the host still stands (`BmhTeardownError`, retryable).

## Bond selection — the subtle part

- Members come from server-scan `network.interfaces[]`, **never** `identity.nic_macs`: Dell NPAR partitions are reduced
  to one interface per physical port there, but `nic_macs` keeps all (4 ports → 4 interfaces, 16 MACs). bmhgen indexed
  `nic_macs` positionally and could bond two partitions of one port — one wire, no redundancy. Distinctness is by
  port: `controller/port/partition` collapses to `controller/port`.
- Link state must be **`UP`**, not "not DOWN": HPE OneView `portMap` has no link state (server-scan stores `UNKNOWN`),
  Intersight vNICs mostly none — such servers **fail** bond selection by design; the error names provider and states.
- server-scan's overall health is `max(category severities)` with `UNKNOWN` below `HEALTHY`, so a failed NIC read could
  look HEALTHY; since 2026-09-26 `/servers/available` also requires the network category HEALTHY (≥ 2 links UP).

| server-scan `bmc_vendor` | Managed by | Ironic driver |
|---|---|---|
| HP | OneView | `redfish-virtualmedia` |
| DELL | OpenManage | `idrac-virtualmedia` |
| INTERSIGHT | Intersight | `redfish-virtualmedia` |
| CISCO | UCS Central | `ipmi` |
| null (standalone) | — | refused |

One INVENTORY network per MCE (a split into `INVENTORY_REDFISH` / `INVENTORY_IPMI` was reverted on 2026-09-27;
allocations still carrying a split value must be re-typed).

## The install lock and its known gap

server-scan learns a machine is taken only when a cluster reports it (membership jobs every 15 min); the BMH probe
sees only its own MCE. Without the lock a run for another MCE could draw the same machine → two clusters on one BMC
(server-scan ADR-0035). `/servers/available` never hands out a locked machine. The 24 h hold writes nothing to a
cluster; it relies on server-scan's `nodes-status` `agents` job (every 15 min on every target MCE) marking the server
`INSTALLED_TO_INVENTORY`. uninstall/remove-server releases install-server's lock for its MCE early.

Gap: a **crash mid-create strands resources** — the BMH stays while the 2 h lock expires, so the machine becomes drawable
while pointing at one cluster. Clean up by hand or re-run the **named** install to converge (a named run accepts its
own workflow id's lock and extends it; any other refusal fails saying which).

## Watching and config

`GET /workflows/runs/{id}` → `phase`, `server_name`, `activity_queue`. A phase that never advances = nothing polls
`activity_queue` (no `server-lifecycle-worker` on that MCE, or it cannot reach Temporal). Page: `/ui/server-lifecycle`.

Worker per MCE (`server-lifecycle-config` / `server-lifecycle-credentials`): `MCE_CLUSTER` (required, = callers'
`mce_cluster`), `SERVER_SCAN_URL` (incl. `/api/v1`), `SERVER_SCAN_API_TOKEN` (**admin** token — the lock uses mutation
endpoints; a viewer token fails every run with `ServerScanAuthError`), `{HP,DELL,CISCO,INTERSIGHT}_BMC_USERNAME/_PASSWORD`
(missing pair → `BmcCredentialsMissingError`). Namespaced Role: secrets get/create/delete; baremetalhosts
get/create/delete/patch; nmstateconfigs get/create/delete; agents get/list (list: Agents are matched by MAC). No `update`.
Missing verb → non-retryable `BmhPrerequisiteMissingError`. Runbook: `runbooks/temporal/deploy-server-lifecycle-worker-on-an-mce.md`.

## History

- 2026-11-02: created from the install-server page of the Redbull Workflows docs site v1.0.61
