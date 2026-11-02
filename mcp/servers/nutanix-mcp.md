---
title: Nutanix MCP (ntnx-api-mcp-server) — candidate, Prism Central v4 API, read-only by default, Python package, not vendored
type: mcp
area: nutanix
tags: [mcp, nutanix, prism, read-only, candidate, virtualization]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: nutanix/ntnx-api-mcp-server (README.md, pyproject.toml) read on 2026-11-02
---

# Nutanix MCP (`ntnx-api-mcp-server`) — candidate

- **Upstream:** [`nutanix/ntnx-api-mcp-server`](https://github.com/nutanix/ntnx-api-mcp-server), Nutanix's own
  server, Apache-2.0, Python ≥ 3.11. Exposes Prism Central v4 API namespaces as tools (e.g. `clustermgmt_execute`,
  `storage_execute`).
- **Read-only:** `READ_ONLY_MODE=true` (the default) blocks every non-GET operation server-side.
- **Why not vendored:** it needs third-party Python packages (`mcp`, `httpx`, `pydantic`, `pydantic-settings`,
  `pyyaml`, `tenacity`, `python-dotenv`), and the plugin ships only stdlib Python and single binaries. Options:
  a container image built on a connected host and run on the shared deployment, or a wheelhouse from the internal
  PyPI mirror. Owner: virtualization team. Plan: `docs/it-brain/TOOLS-PLAN.md`.
- **Status:** not deployed, not run.

## History

- 2026-11-02: evaluated from its README and pyproject
