#!/usr/bin/env python3
"""it-brain knowledge graph: graphify-compatible graph.json and an Obsidian vault. Stdlib only (Python >= 3.9).

    python3 scripts/brain_graph.py graph [--check]       write graphify-out/graph.json (--check: fail if stale)
    python3 scripts/brain_graph.py obsidian --out DIR    build an Obsidian vault of the brain in DIR
    python3 scripts/brain_graph.py stats                 node / edge counts, orphans, most-linked pages

The graph is built deterministically from what is already in the repo — no LLM pass, so it works in the air gap
and is identical on every machine:

  nodes  team · domain · area (from teams.json) · page (every knowledge/runbook/interface/incident/inbox/mcp page,
         area charter and docs page) · tag (only tags shared by >= 2 pages)
  edges  page -in_area-> area · area -owned_by-> team · area -consulted-> team · area -in_domain-> domain ·
         page -concerns-> team (frontmatter `teams:`) · page -links_to-> page (repo paths in backticks or Markdown
         links — the same references team-knowledge's `related` tool follows) · page -tagged-> tag

graph.json is networkx node-link JSON with the fields graphify reads (id, label, file_type, source_file; edges with
relation and confidence EXTRACTED), so `graphify query|path|explain --graph graphify-out/graph.json` and
`graphify export obsidian --graph graphify-out/graph.json` work on it without re-extracting. docs/upstream is not in
the graph (thousands of vendor pages); team-knowledge search covers it.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brain  # noqa: E402

ROOT = brain.ROOT
GRAPH_FILE = ROOT / "graphify-out/graph.json"
PAGE_DIRS = ("knowledge", "runbooks", "interfaces", "incidents", "inbox", "mcp/servers", "docs")
# a repo path to a page, as pages cite each other: `knowledge/<area>/<page>.md` or [text](knowledge/…md)
REF = re.compile(r"(?<![\w/.-])((?:knowledge|runbooks|interfaces|incidents|inbox|mcp/servers|docs)/[A-Za-z0-9_.\-/]+?\.md)\b")
DOMAIN_COLOURS = {  # Obsidian graph colour groups (RGB ints); unknown domains get grey
    "platform": 0xE0301E, "platform-tools": 0xF28C28, "workflow": 0x8E44AD, "data": 0x16A085, "storage": 0x2E86C1,
    "backup": 0x5DADE2, "network": 0x27AE60, "virtualization": 0xB7950B, "meta": 0x7F8C8D}


def pages() -> list[Path]:
    out = []
    for d in PAGE_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            rel = p.relative_to(ROOT).as_posix()
            if rel.startswith("docs/upstream/") or p.name.startswith("_template"):
                continue
            if p.name == "README.md" and not (rel.startswith("knowledge/") or rel.startswith("interfaces/")):
                continue  # area charters and the interfaces README are in; other READMEs are tooling docs
            out.append(p)
    return out


def page_meta(p: Path) -> dict:
    rel = p.relative_to(ROOT).as_posix()
    text = p.read_text(encoding="utf-8", errors="replace")
    fm = brain.parse_frontmatter(text) or {}
    if p.name == "README.md" and rel.startswith("knowledge/"):
        area = rel.split("/")[1]
        fm = {"title": f"Area charter: {area}", "type": "charter", "area": area, "tags": [], "teams": []}
    elif p.name == "README.md":
        fm = {"title": "Interfaces — contracts between teams", "type": "charter", "area": "meta", "tags": [], "teams": []}
    m = re.search(r"^# (.+)$", text, re.M)
    return {"rel": rel, "text": text, "fm": fm, "title": fm.get("title") or (m.group(1) if m else rel)}


def build() -> dict:
    reg = brain.REGISTRY
    nodes: dict[str, dict] = {}
    links: list[dict] = []

    def node(nid, label, kind, **kw):
        nodes.setdefault(nid, {"id": nid, "label": label, "file_type": "concept" if kind != "page" else "document",
                               "source_file": kw.pop("source_file", ""), "kind": kind, **kw})

    def edge(s, t, rel):
        links.append({"source": s, "target": t, "relation": rel, "confidence": "EXTRACTED", "weight": 1.0})

    for t, spec in sorted(reg["teams"].items()):
        node(f"team:{t}", spec["name"], "team", source_file="teams.json")
    for d, desc in sorted(reg["domains"].items()):
        node(f"domain:{d}", desc, "domain", source_file="teams.json")
    for a, spec in sorted(reg["areas"].items()):
        node(f"area:{a}", a, "area", source_file="teams.json", domain=spec["domain"], owner=spec["owner"],
             description=spec["description"], provisional=bool(spec.get("provisional")))
        edge(f"area:{a}", f"domain:{spec['domain']}", "in_domain")
        owners = sorted(reg["teams"]) if spec["owner"] == "all" else [spec["owner"]]
        for o in owners:
            edge(f"area:{a}", f"team:{o}", "owned_by")
        for c in spec.get("consulted", []):
            edge(f"area:{a}", f"team:{c}", "consulted")

    metas = [page_meta(p) for p in pages()]
    known = {m["rel"] for m in metas}
    tag_count = Counter(t for m in metas for t in set(m["fm"].get("tags") or []))
    for m in metas:
        fm, rel = m["fm"], m["rel"]
        node(rel, m["title"], "page", source_file=rel, type=fm.get("type", "?"), area=fm.get("area", ""),
             confidence=fm.get("confidence", ""), last_verified=fm.get("last_verified", ""))
        if fm.get("area") in reg["areas"]:
            edge(rel, f"area:{fm['area']}", "in_area")
        for t in fm.get("teams") or []:
            if t in reg["teams"]:
                edge(rel, f"team:{t}", "concerns")
        seen = set()
        for target in REF.findall(m["text"]):
            if target in known and target != rel and target not in seen:
                seen.add(target)
                edge(rel, target, "links_to")
        for t in sorted(set(fm.get("tags") or [])):
            if tag_count[t] >= 2:
                node(f"tag:{t}", f"#{t}", "tag")
                edge(rel, f"tag:{t}", "tagged")
    links.sort(key=lambda e: (e["source"], e["relation"], e["target"]))
    return {"directed": True, "multigraph": False,
            "graph": {"name": "it-brain", "generator": "scripts/brain_graph.py",
                      "note": "deterministic: built from teams.json, frontmatter and repo-path references; no LLM pass"},
            "nodes": [nodes[k] for k in sorted(nodes)], "links": links}


def render() -> str:
    return json.dumps(build(), indent=1, ensure_ascii=False) + "\n"


def cmd_graph(check: bool) -> int:
    new = render()
    if check:
        if not GRAPH_FILE.exists() or GRAPH_FILE.read_text(encoding="utf-8") != new:
            print("graphify-out/graph.json is out of date — run: python3 scripts/brain_graph.py graph")
            return 1
        print("graphify-out/graph.json up to date")
        return 0
    GRAPH_FILE.parent.mkdir(exist_ok=True)
    GRAPH_FILE.write_text(new, encoding="utf-8")
    g = json.loads(new)
    print(f"wrote {GRAPH_FILE.relative_to(ROOT)} — {len(g['nodes'])} nodes, {len(g['links'])} edges")
    return 0


def cmd_stats() -> int:
    g = build()
    kinds = Counter(n["kind"] for n in g["nodes"])
    rels = Counter(e["relation"] for e in g["links"])
    inbound = Counter(e["target"] for e in g["links"] if e["relation"] == "links_to")
    linked = {e["source"] for e in g["links"] if e["relation"] == "links_to"} | set(inbound)
    orphans = [n["id"] for n in g["nodes"] if n["kind"] == "page" and n["id"] not in linked]
    print("nodes:", dict(kinds))
    print("edges:", dict(rels))
    print("most linked-to pages:")
    for nid, c in inbound.most_common(8):
        print(f"  {c:3}  {nid}")
    print(f"pages with no page links in or out ({len(orphans)}): cite related pages by path to connect them")
    for o in orphans:
        print(f"  {o}")
    return 0


def wikilink(rel: str, label: str | None = None) -> str:
    target = rel[:-3] if rel.endswith(".md") else rel
    return f"[[{target}|{label}]]" if label else f"[[{target}]]"


def cmd_obsidian(out: Path) -> int:
    """Copy every page into a vault, turn repo-path references into [[wikilinks]], tag pages with their team and
    domain, add one hub note per team / domain / area, and colour the graph by domain."""
    reg = brain.REGISTRY
    out = out.expanduser().resolve()
    if out == ROOT or ROOT in out.parents:
        print("choose a vault directory outside the repository (e.g. ~/it-brain-vault)")
        return 2
    if out.exists() and not (out / ".it-brain-vault").exists() and any(out.iterdir()):
        print(f"{out} exists and is not an it-brain vault — refusing to overwrite it")
        return 2
    for child in (out.iterdir() if out.exists() else []):
        if child.name != ".obsidian":  # keep the user's Obsidian settings and workspace
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)
    (out / ".it-brain-vault").write_text("generated by scripts/brain_graph.py obsidian — rebuilt on every run\n")

    metas = [page_meta(p) for p in pages()]
    known = {m["rel"]: m["title"] for m in metas}
    by_area: dict[str, list] = {}
    for m in metas:
        fm, rel = m["fm"], m["rel"]
        area = fm.get("area", "")
        spec = reg["areas"].get(area, {})
        by_area.setdefault(area, []).append(m)

        def sub(mo):
            t = mo.group(1)
            return wikilink(t, t) if t in known else mo.group(0)
        body = REF.sub(sub, m["text"])
        body = re.sub(r"`(\[\[[^\]]+\]\])`", r"\1", body)  # `[[x]]` would render as code, not a link
        extra = [f"area/{area}"] if area else []
        if spec:
            extra += [f"domain/{spec['domain']}"] + [f"team/{t}" for t in
                                                      (sorted(reg["teams"]) if spec["owner"] == "all" else [spec["owner"]])]
        if brain.FM.match(body) and m["fm"].get("type") != "charter":
            body = re.sub(r"^tags:\s*\[(.*?)\]", lambda t: "tags: [" + ", ".join(
                [x for x in [s.strip() for s in t.group(1).split(",")] if x] + extra) + "]", body, count=1, flags=re.M)
        else:
            body = "---\ntags: [" + ", ".join(extra) + "]\n---\n" + body
        footer = f"\n\n---\nArea: {wikilink('_hubs/areas/' + area, area)}" if area in reg["areas"] else ""
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body.rstrip() + footer + "\n", encoding="utf-8")

    hubs = out / "_hubs"
    for t, spec in reg["teams"].items():
        own = [a for a, s in sorted(reg["areas"].items()) if s["owner"] in (t, "all")]
        cons = [a for a, s in sorted(reg["areas"].items()) if t in s.get("consulted", [])]
        ifaces = [m["rel"] for m in metas if m["fm"].get("type") == "interface" and t in (m["fm"].get("teams") or [])]
        lines = [f"# {spec['name']}", "", spec["serves"], "", "## Owns", ""]
        lines += [f"- {wikilink('_hubs/areas/' + a, a)}" for a in own] + ["", "## Consulted on", ""]
        lines += [f"- {wikilink('_hubs/areas/' + a, a)}" for a in cons] or ["- —"]
        lines += ["", "## Interfaces", ""] + ([f"- {wikilink(r, known[r])}" for r in ifaces] or ["- —"])
        (hubs / "teams").mkdir(parents=True, exist_ok=True)
        (hubs / "teams" / f"{t}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for d, desc in reg["domains"].items():
        lines = [f"# Domain: {desc}", ""] + [f"- {wikilink('_hubs/areas/' + a, a)}"
                                             for a, s in sorted(reg["areas"].items()) if s["domain"] == d]
        (hubs / "domains").mkdir(parents=True, exist_ok=True)
        (hubs / "domains" / f"{d}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for a, spec in reg["areas"].items():
        owners = sorted(reg["teams"]) if spec["owner"] == "all" else [spec["owner"]]
        lines = [f"# Area: {a}", "", spec["description"], "",
                 "Owner: " + ", ".join(wikilink("_hubs/teams/" + o, o) for o in owners),
                 "Consulted: " + (", ".join(wikilink("_hubs/teams/" + c, c) for c in spec.get("consulted", [])) or "—"),
                 "Domain: " + wikilink("_hubs/domains/" + spec["domain"], spec["domain"]), "", "## Pages", ""]
        lines += [f"- {wikilink(m['rel'], m['title'])}" for m in sorted(by_area.get(a, []), key=lambda m: m["rel"])] or ["- none yet"]
        (hubs / "areas").mkdir(parents=True, exist_ok=True)
        (hubs / "areas" / f"{a}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    home = ["# it-brain", "", "Generated vault — edit pages in the git repo, not here (changes here are lost on rebuild).", "",
            "## Teams", ""] + [f"- {wikilink('_hubs/teams/' + t, s['name'])}" for t, s in sorted(reg["teams"].items())]
    home += ["", "## Domains", ""] + [f"- {wikilink('_hubs/domains/' + d, desc)}" for d, desc in sorted(reg["domains"].items())]
    (out / "HOME.md").write_text("\n".join(home) + "\n", encoding="utf-8")

    cfg = out / ".obsidian"
    cfg.mkdir(exist_ok=True)
    gfile = cfg / "graph.json"
    gcfg = json.loads(gfile.read_text(encoding="utf-8")) if gfile.exists() else {}
    gcfg["colorGroups"] = [{"query": f"tag:#domain/{d}", "color": {"a": 1, "rgb": DOMAIN_COLOURS.get(d, 0x999999)}}
                           for d in sorted(reg["domains"])]
    gfile.write_text(json.dumps(gcfg, indent=2) + "\n", encoding="utf-8")
    n = sum(1 for _ in out.rglob("*.md"))
    print(f"Obsidian vault: {n} notes in {out} — open it with 'Open folder as vault'; start at HOME.md")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    gp = sub.add_parser("graph")
    gp.add_argument("--check", action="store_true")
    op = sub.add_parser("obsidian")
    op.add_argument("--out", type=Path, default=Path("~/it-brain-vault"))
    sub.add_parser("stats")
    a = ap.parse_args()
    return {"graph": lambda: cmd_graph(a.check), "obsidian": lambda: cmd_obsidian(a.out), "stats": cmd_stats}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())
