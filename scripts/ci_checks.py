#!/usr/bin/env python3
"""team-brain CI gate. Stdlib only (Python >= 3.9). Same script for GitLab CI, GitHub Actions and local runs.

    python3 scripts/ci_checks.py                 # everything
    python3 scripts/ci_checks.py --skip smoke    # skip a check (names are printed below)
    BASE_REF=origin/main python3 scripts/ci_checks.py     # also enforce the plugin version bump
    BRAIN_DENYLIST_FILE=/path/denylist.txt python3 ...    # real site/region/cluster names (never committed)

Checks: validate, index, graph, teams, route, json, sources, parity, frontmatter, leaks, upstream, mcpbin, syntax, version, smoke.
Exit code 1 if any check fails.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "plugins/team-brain/mcp-servers/team-knowledge/server.py"
TEXT_SUFFIX = {".md", ".json", ".yaml", ".yml", ".sh", ".py", ".txt", ".toml", ".cfg", ".ini", ".tpl"}
UPSTREAM = "docs/upstream/"

# placeholder hostnames that are allowed in committed files (real ones are classified)
HOST_ALLOW = {"gitlab.internal", "rhokp.internal", "registry.internal", "docs-mirror.internal", "grafana.internal",
              "team-knowledge-team-knowledge.apps.mgmt.internal", "rhokp-team-knowledge.apps.mgmt.internal",
              "mgmt.internal", "apps.mgmt.internal"}
RFC1918 = re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")
INTERNAL_HOST = re.compile(r"\b[a-z0-9][a-z0-9.-]*\.internal\b")
REAL_CLUSTER = re.compile(r"\bocp4-(?:prod|prep|test)-(?!<)[a-z0-9][a-z0-9-]*")
APPLIES_OK = re.compile(r"^(?:ocp-4\.\d+|k8s-1\.\d+|mce-2\.\d+|acm-2\.\d+|vsphere-\d+|sno|hosted-cp|upi|standalone|[a-z][a-z0-9.-]*)$")
# storage identifiers that point at one real host/array (placeholders: <iqn>, <nqn>, <wwn>)
IQN = re.compile(r"\biqn\.\d{4}-\d{2}\.[a-z0-9-]+\.[a-z0-9.-]+")
NQN = re.compile(r"\bnqn\.\d{4}-\d{2}\.[a-z0-9.-]+:[^\s`'\"]+")
WWN = re.compile(r"\b(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}\b")
ALLOW_LEAK = "ci:allow-leak"

results: list[tuple[str, bool, str]] = []


def record(name: str, errors: list[str], note: str = "") -> None:
    ok = not errors
    results.append((name, ok, note))
    print(f"{'✅' if ok else '❌'} {name}{(' — ' + note) if note else ''}")
    for e in errors[:40]:
        print(f"    {e}")
    if len(errors) > 40:
        print(f"    … and {len(errors) - 40} more")


def tracked_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        files = [ROOT / p for p in out.splitlines() if p]
    except Exception:
        files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    return [f for f in files if f.exists()]


def text_files() -> list[Path]:
    return [f for f in tracked_files() if f.suffix in TEXT_SUFFIX and not str(f.relative_to(ROOT)).startswith(UPSTREAM)]


def glob_rx(g: str) -> re.Pattern:
    p = re.escape(g).replace(r"\*\*/", r"(?:.*/)?").replace(r"\*\*", r".*").replace(r"\*", r"[^/]*")
    return re.compile("^" + p + "$")


def run(cmd: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env={**os.environ, **(env or {})})


# --------------------------------------------------------------------------- checks
def check_validate():
    p = run([sys.executable, "scripts/brain.py", "validate"])
    last = (p.stdout.strip().splitlines() or [""])[-1]
    m = re.search(r"(\d+) errors?, (\d+) warnings?", last)
    errs = []
    if p.returncode != 0:
        errs.append(p.stdout.strip()[-1500:] + p.stderr.strip()[-500:])
    elif m and int(m.group(2)) > 0:
        errs.append(f"{m.group(2)} warning(s) — CI treats warnings as errors:\n" + p.stdout.strip()[-1500:])
    record("validate", errs, last)


def check_index():
    p = run([sys.executable, "scripts/brain.py", "index", "--check"])
    record("index", [] if p.returncode == 0 else ["INDEX.md is stale: run `python3 scripts/brain.py index` and commit"],
           p.stdout.strip())


def check_graph():
    p = run([sys.executable, "scripts/brain_graph.py", "graph", "--check"])
    record("graph", [] if p.returncode == 0 else
           ["graphify-out/graph.json is stale: run `python3 scripts/brain_graph.py graph` and commit"], p.stdout.strip())


def check_teams():
    """teams.json is consistent, every area has a folder with a tracked file, every content folder is an area,
    and .gitlab/CODEOWNERS is generated from the current registry."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import brain  # noqa: E402
    reg = brain.REGISTRY
    errs = []
    for a, spec in reg["areas"].items():
        if spec.get("owner") != "all" and spec.get("owner") not in reg["teams"]:
            errs.append(f"teams.json: area {a}: owner {spec.get('owner')!r} is not a team")
        for c in spec.get("consulted", []):
            if c not in reg["teams"]:
                errs.append(f"teams.json: area {a}: consulted team {c!r} is not a team")
        if not spec.get("description"):
            errs.append(f"teams.json: area {a}: missing description")
        if spec.get("domain") not in reg.get("domains", {}):
            errs.append(f"teams.json: area {a}: domain {spec.get('domain')!r} is not in 'domains'")
    for t, spec in reg["teams"].items():
        for k in ("name", "codeowners", "serves"):
            if not spec.get(k):
                errs.append(f"teams.json: team {t}: missing {k!r}")
    files = [str(f.relative_to(ROOT)) for f in tracked_files()]
    for a in reg["areas"]:
        if not any(f.startswith(f"knowledge/{a}/") for f in files):
            errs.append(f"area {a}: no tracked file under knowledge/{a}/ (add its README.md charter)")
    for top in ("knowledge", "runbooks"):
        for d in sorted({f.split("/")[1] for f in files if f.startswith(top + "/") and f.count("/") >= 2}):
            if d not in reg["areas"]:
                errs.append(f"{top}/{d}/ is not an area in teams.json")
    p = run([sys.executable, "scripts/brain.py", "codeowners", "--check"])
    if p.returncode:
        errs.append(".gitlab/CODEOWNERS is stale: run `python3 scripts/brain.py codeowners` and commit")
    record("teams", errs, f"{len(reg['teams'])} teams, {len(reg['areas'])} areas")


def check_route():
    """tests/routing.json: cross-team questions must reach every listed area / team / interface page."""
    sys.path.insert(0, str(ROOT / "plugins/team-brain/mcp-servers/team-knowledge"))
    from tk import route as r  # noqa: E402
    cases = json.loads((ROOT / "tests/routing.json").read_text(encoding="utf-8"))["cases"]
    errs = []
    for c in cases:
        res = r.route(ROOT, c["question"])
        got = {a["area"] for a in res["areas"]}
        miss = [a for a in c.get("areas", []) if a not in got]
        if miss:
            errs.append(f"{c['question']!r}: missing areas {miss} (got {sorted(got)})")
        tmiss = [t for t in c.get("teams", []) if t not in res["teams"]]
        if tmiss:
            errs.append(f"{c['question']!r}: missing teams {tmiss}")
        if c.get("interface") and c["interface"] not in [i["page"] for i in res["interfaces"]]:
            errs.append(f"{c['question']!r}: expected {c['interface']} among {[i['page'] for i in res['interfaces']]}")
    record("route", errs, f"{len(cases)} cross-team routing cases")


def check_json():
    errs = []
    n = 0
    for f in tracked_files():
        if f.suffix == ".json" and not str(f.relative_to(ROOT)).startswith(UPSTREAM):
            n += 1
            try:
                json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:
                errs.append(f"{f.relative_to(ROOT)}: {e}")
    record("json", errs, f"{n} files")


def load_sources(rel: str) -> list[dict]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))["sources"]


REQUIRED_BY_KIND = {"markdown_dir": ["root"], "git_repo": ["path"], "mkdocs_site": ["url"], "rhokp_solr": ["url"]}


def check_sources():
    errs = []
    for rel in ("mcp/sources.json", "deploy/openshift/shared-sources.json"):
        names = set()
        for s in load_sources(rel):
            n = s.get("name", "?")
            if n in names:
                errs.append(f"{rel}: duplicate source {n}")
            names.add(n)
            kind = s.get("kind")
            if kind not in REQUIRED_BY_KIND:
                errs.append(f"{rel}: {n}: unknown kind {kind!r}")
                continue
            for k in REQUIRED_BY_KIND[kind]:
                if k not in s:
                    errs.append(f"{rel}: {n}: missing {k!r}")
            if not s.get("description"):
                errs.append(f"{rel}: {n}: missing description")
            if kind == "git_repo" and "remote" not in s and not s.get("path", "").endswith("/team-brain.git"):
                errs.append(f"{rel}: {n}: git_repo without remote (not syncable)")
            if not s.get("enabled", True):
                continue
            # enabled sources that read files from this repo must actually match something
            files = [str(f.relative_to(ROOT)) for f in tracked_files()]
            if kind == "markdown_dir" and "${TEAM_BRAIN_DIR" in s["root"]:
                sub = re.sub(r"^\$\{TEAM_BRAIN_DIR[^}]*\}/?", "", s["root"]).strip("/")
                inc = [glob_rx(g) for g in s.get("include", ["**/*.md"])]
                hits = [f for f in files if f.startswith(sub + "/" if sub else "")
                        and any(r.match(f[len(sub) + 1:] if sub else f) for r in inc)]
                if not hits:
                    errs.append(f"{rel}: {n}: no tracked files match root {sub!r} include {s.get('include')}")
            if kind == "git_repo" and s.get("path", "").endswith("/team-brain.git"):
                rx = [glob_rx(g) for g in s.get("docs", [])]
                if not any(r.match(f) for r in rx for f in files):
                    errs.append(f"{rel}: {n}: no tracked file matches docs globs {s.get('docs')}")
    record("sources", errs)


def check_parity():
    a = {s["name"]: s for s in load_sources("mcp/sources.json")}
    b = {s["name"]: s for s in load_sources("deploy/openshift/shared-sources.json")}
    errs = [f"only in mcp/sources.json: {n}" for n in sorted(set(a) - set(b))]
    errs += [f"only in shared-sources.json: {n}" for n in sorted(set(b) - set(a))]
    for n in sorted(set(a) & set(b)):
        if a[n].get("enabled", True) != b[n].get("enabled", True):
            errs.append(f"{n}: 'enabled' differs between the two files")
    record("parity", errs, f"{len(a)} sources")


def check_frontmatter():
    sys.path.insert(0, str(ROOT / "scripts"))
    import brain  # noqa: E402
    errs = []
    for f in text_files():
        rel = str(f.relative_to(ROOT))
        if f.suffix != ".md" or not rel.startswith(("knowledge/", "runbooks/", "interfaces/", "incidents/", "inbox/", "mcp/servers/")):
            continue
        fm = brain.parse_frontmatter(f.read_text(encoding="utf-8"))
        if not fm:
            continue  # validate reports it
        for t in fm.get("applies_to", []) or []:
            if not APPLIES_OK.match(t):
                errs.append(f"{rel}: applies_to token {t!r} (use ocp-4.NN, k8s-1.NN, mce-2.NN, vsphere-N, sno, hosted-cp…)")
        if fm.get("area") not in brain.AREAS:
            errs.append(f"{rel}: unknown area {fm.get('area')!r} (add to AREAS in scripts/brain.py and CLAUDE.md)")
        # runners use UTC while authors are up to +14h ahead: allow a 2-day margin before calling a date "future"
        limit = (dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=2)).isoformat()
        if fm.get("last_verified", "") > limit:
            errs.append(f"{rel}: last_verified {fm['last_verified']} is in the future (limit {limit})")
    record("frontmatter", errs)


def check_leaks():
    errs = []
    deny = []
    dfile = os.environ.get("BRAIN_DENYLIST_FILE")
    if dfile and Path(dfile).is_file():
        for ln in Path(dfile).read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                deny.append(re.compile(ln, re.I))
    for f in text_files():
        rel = str(f.relative_to(ROOT))
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if ALLOW_LEAK in line:
                continue
            if RFC1918.search(line):
                errs.append(f"{rel}:{i}: private IP address (use a placeholder)")
            for h in INTERNAL_HOST.findall(line):
                if h not in HOST_ALLOW:
                    errs.append(f"{rel}:{i}: internal hostname {h!r} not in the placeholder allowlist (scripts/ci_checks.py HOST_ALLOW)")
            for label, rx in (("iSCSI IQN", IQN), ("NVMe NQN", NQN), ("Fibre Channel WWN", WWN)):
                if rx.search(line):
                    errs.append(f"{rel}:{i}: looks like a real {label}: use the <iqn>/<nqn>/<wwn> placeholder")
            if REAL_CLUSTER.search(line):
                errs.append(f"{rel}:{i}: looks like a real cluster name (ocp4-<env>-<name>…): use <cluster>/<mce>/<site> placeholders")
            for k, rx in enumerate(deny, 1):
                if rx.search(line):  # never echo the matched term into CI logs
                    errs.append(f"{rel}:{i}: matches denylist entry #{k}")
    record("leaks", errs, "denylist " + ("active" if deny else "not configured (set BRAIN_DENYLIST_FILE in internal CI)"))


def check_upstream():
    errs = []
    base = ROOT / "docs/upstream"
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        if not (d / ".upstream").is_file():
            errs.append(f"docs/upstream/{d.name}: missing .upstream metadata (generated by the sync scripts)")
        if not any(f.suffix in (".md", ".rst", ".adoc", ".markdown") for f in d.rglob("*") if f.is_file()):
            errs.append(f"docs/upstream/{d.name}: no documentation files")
    record("upstream", errs)


def check_mcpbin():
    """Vendored MCP server archives: every server .mcp.json starts through launch.py is in the manifest,
    and every archive is present with the sha256 the manifest records."""
    import hashlib
    errs = []
    vendor = ROOT / "plugins/team-brain/mcp-servers/vendor"
    manifest = json.loads((vendor / "manifest.json").read_text(encoding="utf-8"))
    mcp = json.loads((ROOT / "plugins/team-brain/.mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    for name, spec in mcp.items():
        args = spec.get("args", [])
        if args and args[0].endswith("launch.py") and (len(args) < 2 or args[1] not in manifest):
            errs.append(f".mcp.json: server {name} runs launch.py {args[1:2]} which is not in vendor/manifest.json")
    n = 0
    for name, spec in manifest.items():
        for platform, asset in spec["assets"].items():
            f = vendor / name / asset["file"]
            n += 1
            if not f.is_file():
                errs.append(f"{name} {platform}: {asset['file']} missing (run scripts/fetch-mcp-binaries.py on a connected host)")
            elif hashlib.sha256(f.read_bytes()).hexdigest() != asset["sha256"]:
                errs.append(f"{name} {platform}: {asset['file']} does not match the sha256 in manifest.json")
    record("mcpbin", errs, f"{n} archives")


def check_syntax():
    errs = []
    n = 0
    for f in tracked_files():
        rel = str(f.relative_to(ROOT))
        if rel.startswith(UPSTREAM):
            continue
        if f.suffix == ".py":
            n += 1
            try:
                compile(f.read_text(encoding="utf-8"), rel, "exec")
            except SyntaxError as e:
                errs.append(f"{rel}:{e.lineno}: {e.msg}")
        elif f.suffix == ".sh":
            n += 1
            p = run(["bash", "-n", str(f)])
            if p.returncode:
                errs.append(f"{rel}: {p.stderr.strip()[:300]}")
    record("syntax", errs, f"{n} scripts")


def check_version():
    base = os.environ.get("BASE_REF")
    if not base:
        record("version", [], "skipped (set BASE_REF to enforce the plugin version bump)")
        return
    p = run(["git", "diff", "--name-only", f"{base}...HEAD"])
    if p.returncode:
        record("version", [f"cannot diff against {base}: {p.stderr.strip()[:200]}"])
        return
    changed = p.stdout.splitlines()
    plugin = [c for c in changed if c.startswith(("plugins/team-brain/skills/", "plugins/team-brain/hooks/",
                                                  "plugins/team-brain/mcp-servers/"))
              or c == "plugins/team-brain/.mcp.json"]
    bumped = "plugins/team-brain/.claude-plugin/plugin.json" in changed
    errs = []
    if plugin and not bumped:
        errs.append("skills/hooks/mcp-servers/.mcp.json changed but plugins/team-brain/.claude-plugin/plugin.json version was not bumped: "
                    + ", ".join(plugin[:5]))
    record("version", errs)


def check_smoke():
    gq = json.loads((ROOT / "tests/golden-queries.json").read_text(encoding="utf-8"))
    errs = []
    with tempfile.TemporaryDirectory() as cache:
        env = {"TEAM_BRAIN_DIR": str(ROOT), "TEAM_KNOWLEDGE_CACHE": cache}
        for q in gq["queries"]:
            args = json.dumps({"query": q["query"], "sources": ["brain"], "per_source": gq.get("top", 3)})
            p = run([sys.executable, str(SERVER), "--call", "search", args], env)
            ids = re.findall(r"id: `([^`]+)`", p.stdout)
            if p.returncode or q["expect"] not in ids[: gq.get("top", 3)]:
                errs.append(f"query {q['query']!r}: expected {q['expect']} in top {gq.get('top', 3)}, got {ids[:gq.get('top', 3)] or p.stderr.strip()[:200]}")
        p = run([sys.executable, str(SERVER), "--call", "related",
                 json.dumps({"source": "brain", "id": "knowledge/meta/fleet-versions.md"})], env)
        if p.returncode or "## Linked from" not in p.stdout:
            errs.append(f"related: fleet-versions page has no backlinks in the link graph: {(p.stderr or p.stdout).strip()[:200]}")
    record("smoke", errs, f"{len(gq['queries'])} golden queries + link graph via the real server")


CHECKS = {"validate": check_validate, "index": check_index, "graph": check_graph, "teams": check_teams, "route": check_route, "json": check_json, "sources": check_sources,
          "parity": check_parity, "frontmatter": check_frontmatter, "leaks": check_leaks,
          "upstream": check_upstream, "mcpbin": check_mcpbin, "syntax": check_syntax, "version": check_version, "smoke": check_smoke}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip", action="append", default=[], choices=list(CHECKS))
    ap.add_argument("--only", action="append", default=[], choices=list(CHECKS))
    a = ap.parse_args()
    for name, fn in CHECKS.items():
        if (a.only and name not in a.only) or name in a.skip:
            continue
        try:
            fn()
        except Exception as e:  # a crashing check is a failing check
            record(name, [f"check crashed: {type(e).__name__}: {e}"])
    bad = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(bad)}/{len(results)} checks passed" + (f"; FAILED: {', '.join(bad)}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
