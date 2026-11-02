---
title: server-scan integrations — Temporal install-server / uninstall-server / provision-dell-server, BareMetalHost and InfraEnv on the MCE, OME, redbull-platform, Grafana
type: knowledge
area: server-scan
tags: [server-scan, integration, temporal, install-server, uninstall-server, provision-dell-server, baremetalhost, metal3, infraenv, agent, mce, ome, bmh-generator]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (ADR-0032/0035/0024) and the Redbull Workflows docs site (install-server, uninstall-server, provision-dell-server)
---

# How server-scan fits into the platform

server-scan is the **authority on where a physical server is and whether it can be used**. Other systems read it;
only a handful write to it. Topology terms: `knowledge/openshift/fleet-topology-hub-mce-hosted.md`. Provisioning
background: `knowledge/baremetal/README.md`. Workflows: `knowledge/temporal/README.md`.

```
 technician racks a Dell, sets iDRAC IP
        │
        ▼
 provision-dell-server (Temporal) ── guard: GET /servers?search=<service tag> (viewer token; must not be INSTALLED)
        │   configures the Dell in OME (discover, template, RAID 1, profile name = server name)
        ▼
 OPENMANAGE collector (server-scan CronJob) ── lists it on its next run (schedule-bound delay)
        ▼
 install-server (Temporal, per-MCE worker) ── GET /servers/available?pattern=^ocp-<infraEnv>&health=HEALTHY&min_nic_macs=2
        │                                     POST /servers/{id}/reservation   (admin token, keyed on workflow id)
        │   creates BareMetalHost + BMC Secret + NMStateConfig on the MCE (Assisted Installer / Metal3)
        ▼
 nodes-status agents job on that MCE ── marks it INSTALLED_TO_INVENTORY / INSTALLED within ~15 min
        ▼
 uninstall-server (Temporal) ── reads server-scan for where it is, locks it, tears down, releases the lock
```

## Who reads, who writes

| System | Reads | Writes | Token |
|---|---|---|---|
| Vendor collectors (CronJobs) | UCS Central, Intersight, OME + iDRAC, OneView, Redfish | servers (hardware, identity, health) | Mongo directly |
| `nodes-status` jobs (per cluster) | the cluster's Nodes / Agents | `Server.openshift` only | Mongo directly |
| `install-server` | `/servers/available` | reservation take / extend / release | **admin** static token (`SERVER_SCAN_API_TOKEN`; a viewer token fails with `ServerScanAuthError`) |
| `uninstall-server` | the server's record (where it is), `/servers/available` semantics | reservation | admin |
| `provision-dell-server` | `GET /servers?search=` + `GET /servers/{id}` (never `/servers/available` — it would live-recheck a vendor for a yes/no guard) | nothing | viewer is enough (`SERVER_SCAN_URL` includes `/api/v1`) |
| Humans / Claude | everything read-only | maintenance (admin session) | personal `ssk_` token (`runbooks/server-scan/connect-claude-to-server-scan-mcp-and-personal-token.md`) |
| Grafana / Prometheus | `/metrics`, fleet gauges | — | — |

## Contracts that other systems rely on

- **Naming:** server-scan parses the site from the server name, so a provisioning `region` override must be a site
  code server-scan knows; install-server's pool query is the InfraEnv name behind an `ocp-` prefix. Names carry an
  uppercase vendor serial and are lowercased for Kubernetes resource names.
- **BMC driver:** `bmc_vendor` (`HP`/`DELL`/`CISCO`/`INTERSIGHT`) decides the Ironic `bmc.address` scheme (e.g.
  IPMI for UCS-managed blades vs Redfish virtual media); server-scan never holds Ironic's BMC credentials.
- **NICs:** ordered `nic_macs` and per-interface `os_name` / `link_state` feed the NMState bond; Dell NPAR is already
  reduced to physical ports. IPMI (UCS) blades additionally get their first link-up MAC registered on the site's PXE VM.
- **The lock** closes the cross-MCE double-install gap; a crash mid-create strands a BareMetalHost while the 2 h
  lock expires — clean up by hand or re-run the same named install
  (`knowledge/server-scan/server-scan-available-servers-and-install-reservation-lock.md`).
- **Membership** must run on every cluster and the agents job on every MCE, or availability is wrong
  (`knowledge/server-scan/server-scan-cluster-membership-nodes-status-jobs.md`).

## Replaced systems

`bmh-generator-operator` (BareMetalHostUCS, a Kopf operator querying four vendor SDKs live per reconcile) is replaced
by install-server + `/servers/available`. The DC team's manual OME steps are replaced by provision-dell-server.

## Scope & caveats

From server-scan's ADRs and the Redbull Workflows documentation as of 2026-11-02; phases and token rules may change
with the workflows (their docs site is versioned). Not observed on a live run from the brain.

## How we know

`team-redbull/server-scan:docs/adr/0032-available-server-lookup-api.md`, `:docs/adr/0035-install-reservation-lock.md`,
`:docs/adr/0024-openshift-cluster-membership.md`; Redbull Workflows docs pages `install-server`, `uninstall-server`,
`provision-dell-server` (site URL kept out of the brain — ask the OCP team).

## History

- 2026-11-02: created
