---
name: it-triage
description: Cross-team triage for problems that span OpenShift, storage, network and virtualization — e.g. a PVC on OpenShift stuck with PowerFlex or Trident, a KubeVirt VM whose disk or network fails, cluster traffic blocked by the firewall or the ACI fabric, backups to S3 failing, a workflow that can't find servers in server-scan. Use when `route` names more than one team, or when it is unclear which team's system is at fault.
---

# Cross-team triage

Goal: one answer that uses **every** team's knowledge, keeps each side's facts separate, and ends with which side
the evidence points to and who to involve. Don't let one team's view win by default.

## 1. Route

`route` (team-knowledge MCP) with the user's words, product names and the exact error. Note:
- the **areas** and their owner teams — each is a side to check;
- the **interface page(s)** — the contract between those teams. `read` it first: its *Symptoms that cross the line*
  table often names the side directly, and *How each side checks its half* gives the read-only checks.

## 2. Search each side, then together

1. `search` the exact error across all sources (no `sources` filter).
2. For each routed area, `search` with that area's product words + the symptom, and `read` its charter
   (`knowledge/<area>/README.md`) for scope and what is known *not* to belong there.
3. `related` from the best hits (knowledge page → runbook → incidents).
4. Version-match every source (`knowledge/meta/fleet-versions.md`, the area's own version notes, RHOKP `version`).

## 3. Check, one side at a time, read-only

Use only checks on systems the engineer may read: Kubernetes MCP (`context` on every call), Grafana (resolve the
`Moby / <cluster>` datasource first), Temporal / server-scan MCPs if configured, vendor UIs through the engineer.
Record for each side: **what was checked → what it showed**.

## 4. Answer in this shape

```
Areas: <area (team)>, …        Interface: interfaces/<page>.md
Evidence
  <team A> side: <check> → <result>
  <team B> side: <check> → <result>
Most likely at fault: <side>, because <evidence>; confidence <high|medium|low>
Next step: <read-only check or fix>  ·  Involve: <team> in <teams.json channel>, with <what to send>
```

Never paste real names, IPs, serials, WWNs/IQNs, tokens: use the placeholders in `teams.json`.

## 5. Close the loop

- A symptom → cause pair that crossed teams and is not in the interface page → propose adding it to that page
  (`team-brain:brain-learn`; interface pages need approval from every team in `teams:`).
- `route` missed an area → add the missing words to that area's `keywords` in `teams.json` and a case to
  `tests/routing.json`.
