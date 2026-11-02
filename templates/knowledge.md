---
title: <Sentence an engineer would grep for during an outage>
type: knowledge
area: <a key of teams.json → areas; python3 scripts/brain.py teams lists them>
teams: []   # optional: other teams this concerns (keys of teams.json → teams)
tags: []
applies_to: []   # ranges of fleet versions, e.g. [ocp-4.16, ocp-4.20, ocp-4.22]; see knowledge/meta/fleet-versions.md
confidence: observed
last_verified: YYYY-MM-DD
owners: []
source: claude-session
---

# <Title>

## Symptom

<What you see. Paste the exact error text / condition message / event so grep finds it.>

## Cause

<Why it happens. Link the upstream code or doc if you found it (team-knowledge `read_code` URLs are fine).>

## Fix / workaround

```bash
# commands, with placeholders instead of real names/secrets
```

## Scope & caveats

<Versions, hardware, topology where this applies — and where it is known NOT to apply.>

## How we know

<What was observed, on which cluster, when. Links to incidents/ or MRs.>

## History

- YYYY-MM-DD: created
