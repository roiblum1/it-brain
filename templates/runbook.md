---
title: <Verb phrase: Replace a failed control-plane node on a bare-metal cluster>
type: runbook
area: <a key of teams.json → areas; python3 scripts/brain.py teams lists them>
teams: []   # optional: other teams this concerns (keys of teams.json → teams)
tags: []
applies_to: []
confidence: observed
last_verified: YYYY-MM-DD
owners: []
---

# <Title>

**When to use:** <trigger / alert / situation>
**Impact while running:** <what users see, expected duration>
**Prerequisites:** <access, tools, images mirrored, maintenance window>

## Pre-checks

```bash
oc get clusterversion
oc get nodes
```

## Procedure

1. <step> — <why>
   ```bash
   <command>
   ```
2. …

## Verification

```bash
<commands that prove it worked>
```

## Rollback

<how to undo, or "not reversible after step N">

## History

- YYYY-MM-DD: created
