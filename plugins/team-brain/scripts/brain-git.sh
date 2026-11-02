#!/usr/bin/env bash
# Deterministic git plumbing for brain captures, so every session does it the same way.
# Each capture gets its own git worktree, so concurrent Claude sessions and the engineer's own
# checkout of main never collide.
#
#   brain-git.sh start <kind> <slug>         -> prints the worktree path to write files into
#                                               kind: learn | curate | incident
#   brain-git.sh submit <worktree> "<msg>"   -> validate, commit, push, open MR, remove worktree
#   brain-git.sh abort <worktree>            -> discard the worktree and its branch
set -euo pipefail

BRAIN="${TEAM_BRAIN_DIR:-$HOME/team-brain}"
WT_ROOT="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/team-brain}/worktrees"
TRAILER="${BRAIN_COMMIT_TRAILER:-Captured-By: Claude Code (team-brain)}"

die() { echo "brain-git: $*" >&2; exit 1; }
[ -d "$BRAIN/.git" ] || die "brain clone not found at $BRAIN (set TEAM_BRAIN_DIR)"

cmd="${1:-}"; shift || true
case "$cmd" in
  start)
    kind="${1:?kind}"; slug="${2:?slug}"
    case "$kind" in learn|curate|incident) ;; *) die "kind must be learn|curate|incident";; esac
    slug="$(echo "$slug" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-' | cut -c1-50)"
    branch="$kind/$(date +%F)-$slug"
    git -C "$BRAIN" fetch --quiet origin main 2>/dev/null || echo "brain-git: fetch failed, branching from local main" >&2
    base="origin/main"; git -C "$BRAIN" rev-parse --verify --quiet "$base" >/dev/null || base="main"
    mkdir -p "$WT_ROOT"
    wt="$WT_ROOT/${branch//\//_}"
    [ -e "$wt" ] && die "worktree already exists: $wt"
    git -C "$BRAIN" worktree add --quiet -b "$branch" "$wt" "$base"
    echo "$wt"
    ;;

  submit)
    wt="${1:?worktree}"; msg="${2:?message}"
    [ -d "$wt" ] || die "no such worktree: $wt"
    cd "$wt"
    branch="$(git rev-parse --abbrev-ref HEAD)"
    [ "$branch" != "main" ] || die "refusing to commit on main"
    python3 scripts/brain.py index >/dev/null
    python3 scripts/brain.py codeowners >/dev/null
    python3 scripts/brain_graph.py graph >/dev/null
    python3 scripts/brain.py validate || die "validation failed — fix the files above, then submit again"
    git add -A
    git diff --cached --quiet && die "nothing to commit"
    git commit --quiet -m "$msg" -m "$TRAILER"
    git push --quiet -u origin "$branch" || die "push failed — branch kept in $wt"
    if command -v glab >/dev/null 2>&1; then
      glab mr create --source-branch "$branch" --target-branch main \
        --title "$msg" --description "$(git log -1 --pretty=%b)" --remove-source-branch --yes \
        || echo "brain-git: glab mr create failed; open the MR manually for branch $branch" >&2
    else
      echo "brain-git: pushed $branch — open a merge request into main (glab not installed)"
    fi
    git -C "$BRAIN" worktree remove --force "$wt"
    echo "brain-git: submitted $branch"
    ;;

  abort)
    wt="${1:?worktree}"
    branch="$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
    git -C "$BRAIN" worktree remove --force "$wt"
    [ -n "$branch" ] && [ "$branch" != "main" ] && git -C "$BRAIN" branch -D "$branch" >/dev/null
    echo "brain-git: aborted $branch"
    ;;

  *) die "usage: brain-git.sh start <kind> <slug> | submit <worktree> <msg> | abort <worktree>";;
esac
