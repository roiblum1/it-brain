---
name: brain-learn
description: Capture durable, non-obvious knowledge into the team brain via a merge request — a root cause, a workaround, a version- or hardware-specific quirk, a working procedure, or a correction to an existing brain page. Use after solving or learning something a teammate would otherwise have to rediscover.
---

# Capture a learning into the team brain

## 0. Is it worth capturing?

Capture if a teammate hitting the same situation in 3 months would save real time.
**Yes:** root causes, workarounds, "X only happens on Y hardware / version Z", commands that
finally worked, wrong assumptions corrected, decisions with their reasons, a brain page that was
wrong. **No:** generic Kubernetes facts already in upstream docs, one-off typos, session
chatter, anything you can't state with a scope.

## 1. Search first — update beats create

```bash
BRAIN="${TEAM_BRAIN_DIR:-$HOME/team-brain}"
grep -rilE '<key terms>' "$BRAIN/knowledge" "$BRAIN/runbooks" "$BRAIN/inbox"
```

If a page covers it, you will **edit that page** (add the new case, narrow/widen
`applies_to`, adjust `confidence`, bump `last_verified`, add a line under `## History`).

## 2. Open a capture worktree

```bash
BRAIN="${TEAM_BRAIN_DIR:-$HOME/team-brain}"
WT="$(bash "$BRAIN/plugins/team-brain/scripts/brain-git.sh" start learn '<short-slug>')"
echo "$WT"
```

Write **only inside `$WT`** (never in `$BRAIN` directly — that's the engineer's main checkout).

## 3. Write it

Destination (see `$WT/CLAUDE.md`):
- confident + clear area → `knowledge/<area>/<topic>.md` or `runbooks/<area>/<task>.md` (areas and their owning
  team: `$WT/teams.json`; each `knowledge/<area>/README.md` says what belongs there)
- about the seam between two teams (who provides what, a symptom on one side caused on the other) → update the
  matching `interfaces/<page>.md` (`type: interface`, `teams: [..]`) instead of writing it into one area
- unsure, partial, or needs human judgement → `inbox/<yyyy-mm-dd>-<slug>.md`

Start from `$WT/templates/knowledge.md` or `$WT/templates/runbook.md`. Required frontmatter is in
`$WT/docs/FRONTMATTER.md`. Set `source: claude-session` and `confidence` honestly:
`verified` only if the fix was confirmed working on a cluster in this session.

Body structure: **Symptom** (exact error text, so grep finds it) → **Cause** → **Fix / Workaround**
(commands in code blocks) → **Scope & caveats** → **How we know** (what was observed).

### Redaction — mandatory

Replace with `<REDACTED>` or a placeholder: tokens, passwords, pull secrets, kubeconfigs,
certificates/keys, BMC credentials, management-network IPs, serial numbers, and any project or
customer names the user hasn't said are fine to record. Cluster names are OK unless told otherwise.

## 4. Confirm with the user, then submit

Show the user the file path(s) and a 2–4 line summary of what will be proposed. Unless
`BRAIN_AUTO_SUBMIT=1` is set in the environment, wait for a go-ahead. Then:

```bash
bash "$BRAIN/plugins/team-brain/scripts/brain-git.sh" submit "$WT" "brain(<area>): <what was learned>"
```

`submit` regenerates the index, runs validation (frontmatter + secret scan), commits, pushes the
`learn/*` branch and opens a merge request. If validation fails, fix the files in `$WT` and run
`submit` again. If the user declines: `brain-git.sh abort "$WT"`.

Finish with one line: what was captured and the MR/branch name.
