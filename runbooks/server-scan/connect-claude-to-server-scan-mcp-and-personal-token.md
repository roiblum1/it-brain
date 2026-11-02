---
title: Connect Claude Code to server-scan — create a personal ssk_ token, add the read-only MCP at /mcp or install the server-scan-api skill
type: runbook
area: server-scan
tags: [server-scan, claude, mcp, personal-token, skill, read-only]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (ADR-0052/0053/0054, frontend/src/features/skill/McpSection.tsx)
---

# Connect Claude Code to server-scan

**When to use:** you want Claude to answer fleet questions ("which Dell servers at `<site>` are free and healthy",
"what changed on `<server>`") from server-scan.
**Impact while running:** none — read-only.
**Prerequisites:** server-scan deployed with `auth.enabled: true` (token endpoints answer 404 with auth off), your AD
account in a viewer/auditor/admin list, and for the MCP path `mcp.enabled: true` on the deployment
(`mcp/servers/server-scan.md`).

## Procedure

1. Sign in to the server-scan UI and open the **Claude** page (`/skill`).
2. Create your personal token (`POST /api/v1/auth/token` behind the button). It is shown **once**; it is read-only
   (viewer, or auditor if you are auditor/admin) and expires after 90 days by default. Creating another replaces it.
3. **Either** add the MCP server (the page prints the exact line):
   ```bash
   claude mcp add --transport http server-scan https://<server-scan-host>/mcp \
     --header "Authorization: Bearer <your token>"
   ```
   **or** download the skill zip from the same page (base URL pre-filled) into `~/.claude/skills/` and put the token on
   its `AUDITOR_TOKEN` / `VIEWER_TOKEN` line locally. Never commit either file.
4. Keep the token out of shell history and logs; treat it like a password.

## Verification

In Claude Code: `/mcp` shows `server-scan` connected; ask "fleet summary by site from server-scan". With a viewer-capped
token, event questions return a 403 explanation — expected.

## Rollback

Revoke on the same page (`DELETE /api/v1/auth/token`) and `claude mcp remove server-scan`. An admin can revoke anyone's
token with `DELETE /api/v1/auth/tokens/<username>` — do this for leavers, because AD membership is not re-checked.

## History

- 2026-11-02: created
