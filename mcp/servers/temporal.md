---
title: Temporal MCP server (temporal-mcp) — read-only workflow runs, histories and task-queue pollers of the Redbull Workflows orchestrator
type: mcp
area: temporal
tags: [mcp, temporal, temporal-mcp, read-only, workflows, task-queue, redbull-workflows]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: temporalio/temporal-mcp v0.0.5 (README.md, docs/config.md), vendored archive
---

# Temporal MCP (`temporal-mcp`)

- **Upstream:** [`temporalio/temporal-mcp`](https://github.com/temporalio/temporal-mcp), MIT, Go — Temporal's own
  server, **pre-release** ("not ready for production use" per its README). Vendored at **v0.0.5** for linux-x86_64
  and darwin-arm64 (no Windows build is published) in `plugins/team-brain/mcp-servers/vendor/temporal/`, sha256
  checked against the release's `checksums.txt` (`scripts/fetch-mcp-binaries.py`).
- **Read-only by design:** every tool is annotated `readOnlyHint`. It cannot start, signal, cancel or terminate a
  workflow — steering a run stays with the orchestrator's API (`runbooks/temporal/start-watch-and-steer-a-redbull-workflow-run.md`).
- **Optional:** the plugin starts it only when `TEMPORAL_MCP_CONFIG` points at a config file. Without one,
  `launch.py --needs-file` serves a stub with a single `how_to_configure` tool, so nobody sees a failed server.

## Tools (listed from the vendored binary, 2026-11-02)

`list_available_targets`, `check_connection`, `get_workflows`, `get_workflow_history`, `search_workflows`,
`count_workflows`, `get_task_queues` (pollers and backlog), `list_search_attributes`.

Good questions for it: *why is this run stuck* (history → last activity, its retries and failure), *is any worker
polling `server-lifecycle-activity-<mce>`* (the per-MCE limb is down when this shows no pollers —
`knowledge/temporal/redbull-workflows-orchestrator-architecture.md`), *which upgrade-cluster runs failed today*.

## Setup (per engineer)

```bash
mkdir -p ~/.config/it-brain
cp "$TEAM_BRAIN_DIR/plugins/team-brain/mcp-servers/temporal-mcp.example.yaml" ~/.config/it-brain/temporal-mcp.yaml
# fill <temporal-frontend-host> and <namespace>; keep the file out of git
export TEMPORAL_MCP_CONFIG=~/.config/it-brain/temporal-mcp.yaml     # shell profile; absolute path
export SSL_CERT_FILE=<bundle with public CAs + the internal CA>      # only if the frontend uses TLS
```

Config rules (from upstream `docs/config.md`): one `targets` entry per namespace (`name`, `description`,
`address: host:port`, `namespace`); unknown keys are rejected; secrets are never inline — `api_key: {env: VAR}` or
`{file: path}`; with neither `api_key` nor `tls` the connection is **plaintext without credentials** (fine for a
dev server, check how our hub's frontend is exposed); `payload_handling` defaults to `omit`, which keeps workflow
inputs (names, VLANs, IPs) out of the conversation — leave it so.

## What is verified

- 2026-11-02, linux x86_64: the vendored binary starts through `launch.py` with a minimal config and lists the 8
  tools above, all read-only; the not-configured stub answers `initialize`, `tools/list` and `tools/call`.
- **Not verified:** any connection to our Temporal (address, TLS, auth on the hub are unknown here), darwin build
  (checksum only). A centrally hosted HTTP deployment with OIDC (upstream `docs/deployment.md`) is possible later.

## History

- 2026-11-02: vendored v0.0.5 and added to the plugin as an optional server
