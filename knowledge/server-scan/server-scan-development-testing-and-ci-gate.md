---
title: Working in the server-scan repo — local stack (compose, uv, seeded fake fleet), pytest/ruff/ty/comment-density gate, CI audits, the repo's own conventions
type: knowledge
area: server-scan
tags: [server-scan, development, testing, ci, pytest, ruff, ty, uv, compose, fake-data, conventions, github-actions]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (README.md, CLAUDE.md, .github/workflows/ci.yml, .claude/skills/gate)
---

# Working in the server-scan repo

For changing server-scan itself (not for operating it). The repo's own `CLAUDE.md` is the authority and is loaded
by Claude Code in that repo; this page is the short version for someone arriving from the brain.

## Local stack

```bash
docker compose up -d mongo redis                 # or scripts/dev-up.sh up   (not "podman compose" with a space)
uv sync --all-groups && cp .env.example .env     # .env is gitignored; .env.example is committed
uv run python -m tools.seed_inventory --count 1000 --seed 42    # fake fleet through the real ingest path
uv run uvicorn app.main:app --reload --port 8080 --app-dir backend
cd frontend && npm install && npm run dev        # UI on :5173, OpenAPI on :8080/docs
uv run python -m tools.run_collector --manager-type <TYPE> --dry-run   # one collector by hand
```

Auth is off by default locally (every caller is admin). Needs uv, Node 24+, Docker or Podman. A domain change must
also update the fake provider (`backend/app/infrastructure/providers/fake/`) — every demo and dev environment runs on it.

## The gate (what CI runs)

```bash
uv run pytest -q                                   # unit + integration + api; CI uses -n 4
uv run ruff check . && uv run ruff format --check . && uv run ty check backend/app tools tests
uv run python scripts/check_comment_density.py   # >3 consecutive comment lines or a >3-line docstring summary fails
uv run lint-imports                                # layering contracts
uv run --with pip-audit pip-audit --skip-editable; uv run --with deptry==0.24.0 deptry . --known-first-party app
cd frontend && npm run lint && npm run typecheck && npm run test -- --run && npm run build && npm audit
```

`/gate` (repo skill) runs all of it in CI's order, including `helm lint` / `helm template`. The dependency audits
can turn CI red **with no code change** (a new advisory) — judge them by exit code, fix with a pin bump and
re-export `requirements.txt` / `pylock.toml`. Integration tests skip quickly when Mongo/Redis are down; a *stuck*
suite usually means the containers were reaped. CI's Mongo jobs are pinned to an older Ubuntu runner because
`mongod` refuses to start on Linux 6.19+ kernels.

## Conventions the repo enforces (surprising ones)

- **Commits:** Conventional Commits (the subject is the release note and picks the version bump); the repo's
  `CLAUDE.md` requires the project owner as the only visible author and **forbids agent-attribution trailers**
  (a hook refuses them) — this overrides the brain's own commit footer when working in that repo.
- Google-style docstrings everywhere; explanation goes to `docs/` (ADRs), not long comments.
- Every change updates the docs it makes wrong in the same commit (README, `docs/architecture.md`, `docs/arc42.md` §9
  ADR index, `deploy/README.md`, `.env.example`, and the `server-scan-api` skill for any API change).
- Type checker is `ty` (pinned, beta), not mypy; suppressions are `# ty: ignore[rule]`.
- No `.mcp.json` in the repo on purpose: MCP servers are user-level config.

## Scope & caveats

As of `08d284c`; the repo's `CLAUDE.md` "Where to continue right now" section names the open work.

## How we know

`team-redbull/server-scan:CLAUDE.md`, `:README.md`, `:.github/workflows/ci.yml`, `:.claude/skills/gate/SKILL.md`.
Architecture: `knowledge/server-scan/server-scan-architecture-collectors-mongodb-api.md`.

## History

- 2026-11-02: created
