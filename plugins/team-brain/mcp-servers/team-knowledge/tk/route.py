"""Cross-team routing: which areas, teams and interface pages a question touches (it-brain).

Deterministic and stdlib only. Reads <brain>/teams.json (each area's `keywords`) and the frontmatter of
<brain>/interfaces/*.md. Used by the `route` MCP tool and by `scripts/brain.py route`.

The point: a session can carry one team's profile and still answer a problem that spans teams. "PVC on OpenShift
stuck with PowerFlex" must lead to the PowerFlex area (storage team), the cluster storage and OpenShift areas
(ocp team) and the Dell CSM interface page between them — not to one of the three.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def _frontmatter(text: str) -> dict:
    m = FM.match(text)
    out: dict = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        v = v.split(" #", 1)[0].strip()
        out[k.strip()] = ([x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                          if v.startswith("[") and v.endswith("]") else v.strip("'\""))
    return out


def _hits(text: str, keywords: list[str]) -> list[str]:
    found = []
    for kw in keywords:
        k = kw.lower()
        if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", text):
            found.append(kw)
    return found


def route(brain_root: str | Path, question: str) -> dict:
    root = Path(brain_root)
    reg = json.loads((root / "teams.json").read_text(encoding="utf-8"))
    q = question.lower()
    areas = []
    for name, spec in reg["areas"].items():
        if name == "meta":
            continue
        kws = list(dict.fromkeys([name.replace("-", " "), name] + spec.get("keywords", [])))
        hit = _hits(q, kws)
        if hit:
            score = sum(2 if (" " in h or "-" in h or "/" in h) else 1 for h in hit)
            areas.append({"area": name, "score": score, "matched": hit, "owner": spec["owner"],
                          "consulted": spec.get("consulted", []), "domain": spec["domain"],
                          "description": spec["description"]})
    areas.sort(key=lambda a: (-a["score"], a["area"]))
    matched = {a["area"] for a in areas}
    teams = sorted({a["owner"] for a in areas if a["owner"] != "all"})

    interfaces = []
    for p in sorted((root / "interfaces").glob("*.md")):
        if p.name == "README.md":
            continue
        fm = _frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        hay = " ".join([fm.get("title", "")] + (fm.get("tags") or [])).lower()
        # product areas (PowerFlex, Trident, ACI…) decide which contract applies; platform areas (pvc, openshift)
        # only break ties — otherwise every storage contract would match every PVC question
        specific = generic = 0
        for a in areas:
            n = len(_hits(hay, a["matched"])) + (1 if fm.get("area") == a["area"] else 0)
            if a["domain"] == "platform":
                generic += n * a["score"]
            else:
                specific += n * a["score"]
        shared = set(fm.get("teams") or []) & set(teams)
        if len(teams) >= 2 and len(shared) >= 2:
            generic += len(shared)
        interfaces.append({"page": p.relative_to(root).as_posix(), "title": fm.get("title", p.stem),
                           "teams": fm.get("teams") or [], "specific": specific, "generic": generic})
    interfaces.sort(key=lambda i: (-i["specific"], -i["generic"], i["page"]))
    if any(i["specific"] for i in interfaces):
        interfaces = [i for i in interfaces if i["specific"]]
    else:
        interfaces = [i for i in interfaces if i["generic"] >= 4]
    return {"question": question, "areas": areas, "teams": teams, "interfaces": interfaces[:3],
            "charters": [f"knowledge/{a['area']}/README.md" for a in areas
                         if (root / "knowledge" / a["area"] / "README.md").exists()]}


def render(r: dict, team_names: dict | None = None) -> str:
    if not r["areas"]:
        return ("No area keyword matched. Search every source with the exact error text (`search`), then "
                "`related` from the best hit; if the topic belongs to an area, add its keywords to teams.json.")
    tn = team_names or {}
    lines = [f"**Areas this touches** ({len(r['areas'])}):", "",
             "| area | owner team | consulted | matched on |", "|---|---|---|---|"]
    for a in r["areas"]:
        lines.append(f"| `{a['area']}` | {a['owner']} | {', '.join(a['consulted']) or '—'} | {', '.join(a['matched'])} |")
    lines += ["", "**Teams involved:** " + (", ".join(f"{t} ({tn.get(t, t)})" for t in r["teams"]) or "—")]
    if len(r["teams"]) >= 2:
        lines.append("This spans teams: answer with each side's checks, say which side the evidence points to, "
                     "and name the team to involve. Use every team's pages — a team profile only orders the search.")
    if r["interfaces"]:
        lines += ["", "**Read first — the contract between these teams:**"]
        lines += [f"- `{i['page']}` — {i['title']} (teams: {', '.join(i['teams'])})" for i in r["interfaces"]]
    lines += ["", "**Then:** `search` the exact error across all sources; `read` the area charters for scope "
              "(" + ", ".join(f"`{c}`" for c in r["charters"]) + "); follow `related` from the best hits."]
    return "\n".join(lines)
