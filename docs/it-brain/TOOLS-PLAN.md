---
title: it-brain live tools plan — read-only MCP access to arrays, fabric, firewalls and hypervisors, and the safety rules
type: reference
area: meta
tags: [it-brain, mcp, tools, read-only, ontap-mcp, safety, service-accounts]
applies_to: []
confidence: hypothesis
last_verified: 2026-11-02
owners: [ocp]
source: it-brain-design
---

# it-brain live tools plan

Today's MCP servers: `mcp/servers/kubernetes.md` (full access, every call approved by a human) and
`mcp/servers/grafana.md` (read-only). How they are shipped (sha256-pinned archives, `launch.py`, no downloads in the
air gap): `docs/ADMIN.md` and `scripts/fetch-mcp-binaries.py`.

## Rules for every new live tool

1. **Read-only first, per system.** A dedicated read-only account per system and site; the MCP server runs in its
   read-only mode if it has one, and the account cannot write even if the server tries.
2. **One system per server instance, named by placeholder** (`<array>`, `<fw>`, `<vcenter>`) in docs; the real
   endpoint comes from the engineer's environment, never from the repo.
3. **Credentials** come from environment variables or a file outside the repo, like `GRAFANA_SERVICE_ACCOUNT_TOKEN`.
   Nothing returned by a tool that looks like a credential, a serial or a real name goes into a page.
4. **Every call is approved by a human** in the permission prompt — don't allow-list these tools.
5. **Pinned and vendored** like the existing servers: version + sha256 in `vendor/manifest.json`, CI `mcpbin` check.
6. **Writes are a separate decision** for each system, with a blast-radius review in `mcp/servers/<name>.md`.
   Out of scope for firewalls and arrays until a team asks.

## Candidates

| System | Team | Candidate | Status | Notes |
|---|---|---|---|---|
| NetApp ONTAP | storage | [`NetApp/ontap-mcp`](https://github.com/NetApp/ontap-mcp) (Go, Apache-2.0) | evaluate first | its `docs/tools.md` describes `--read-only` (only `readOnlyHint` tools registered) and multi-cluster config — read from the docs on 2026-11-02, not run |
| Dell PowerMax | storage | Unisphere REST API | find / build | in-house read-only wrapper if no vendor MCP fits |
| Dell PowerFlex | storage | PowerFlex gateway REST API | find / build | |
| Dell PowerScale | storage | OneFS platform API (PAPI) | find / build | |
| Ceph / RGW | storage | `ceph` / `radosgw-admin` (read-only caps) or the Ceph Manager REST API | find / build | a read-only cephx user / admin-API user |
| Commvault | storage | Commvault REST API | find / build | |
| Cisco ACI | network | APIC REST API | find / build | read-only APIC user; class queries (`/api/class/fvAEPg.json`) are enough for most questions |
| Palo Alto | network | PAN-OS / Panorama XML + REST API | find / build | read-only admin role; API keys are secrets (validate flags `LUFRPT…`) |
| VMware | ocp (provisional) | vCenter REST API | find / build | read-only role |
| Nutanix | ocp (provisional) | Prism Central v3/v4 API | find / build | viewer role |

**In-house fallback:** one stdlib Python MCP server (`it-infra-readonly`, Phase 3) with a per-system allow-list of
`GET` endpoints, response size limits and a redaction pass (IPs, serials, WWNs/IQNs → placeholders) before results
reach Claude. One code path to review instead of eight third-party servers.

## Order

1. `ontap-mcp --read-only` against a lab or non-production ONTAP (needs a storage-team owner and a read-only account).
2. APIC read-only (network team).
3. The rest, by which team asks first.

Each becomes `mcp/servers/<name>.md` (`type: mcp`) + an entry in `plugins/team-brain/.mcp.json` + a plugin version bump.

## History

- 2026-11-02: created
