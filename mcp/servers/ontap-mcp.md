---
title: NetApp ONTAP MCP (ontap-mcp) — candidate, read-only mode, runs as a container on the shared deployment, not vendored
type: mcp
area: netapp-ontap
tags: [mcp, ontap, netapp, ontap-mcp, read-only, candidate, storage]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [storage]
source: NetApp/ontap-mcp (README.md, docs/install.md, docs/tools.md) read on 2026-11-02
---

# NetApp ONTAP MCP (`ontap-mcp`) — candidate

- **Upstream:** [`NetApp/ontap-mcp`](https://github.com/NetApp/ontap-mcp), NetApp's own server, Apache-2.0, Go.
  Tags follow `vYY.MM.N` (latest seen `v26.10.0`). Published as a **container image** (`ghcr.io/netapp/ontap-mcp`)
  and a Helm chart (`charts/`); no release binaries with checksums were found, so it is **not vendored in the plugin**.
- **Read-only:** `--read-only` registers only the tools annotated `readOnlyHint` (volumes, snapshots, SVMs, export
  policies, QoS, SnapMirror … can then only be *listed*). The full tool set includes `delete_volume`, `delete_svm`,
  `break_snapmirror` and similar — never run it without `--read-only` against our arrays.
- **Where it would run:** on the shared OpenShift deployment (`deploy/openshift/`), image mirrored into the internal
  registry, one read-only ONTAP account per array (`<array>`), config from a Secret; engineers connect over HTTP.
- **Status:** not deployed, not run. Owner: storage team. Plan: `docs/it-brain/TOOLS-PLAN.md`.

## History

- 2026-11-02: evaluated from its docs
