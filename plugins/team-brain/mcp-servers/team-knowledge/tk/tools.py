"""MCP tool definitions and handlers. Output is compact Markdown text, sized for an LLM context."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from . import route as _route
from .sources import GitRepo, MarkdownDir, Source, SourceError

MAX_READ_CHARS = 40_000


class ToolError(Exception):
    pass


class Toolbox:
    def __init__(self, sources: dict[str, Source]):
        self.sources = sources
        self.pool = ThreadPoolExecutor(max_workers=8)

    # ---------------------------------------------------------------------------- definitions
    def definitions(self) -> list[dict]:
        names = sorted(self.sources)
        repos = sorted(n for n, s in self.sources.items() if isinstance(s, GitRepo))
        listing = "; ".join(f"{n} ({s.kind}{': ' + s.description if s.description else ''})"
                            for n, s in sorted(self.sources.items()))
        src_prop = {"type": "array", "items": {"type": "string", "enum": names},
                    "description": "Limit to these sources. Omit to search all document sources."}
        repo_prop = {"type": "string", "enum": repos or ["(none configured)"], "description": "Repository source name."}
        ref_prop = {"type": "string", "description": "Git branch/tag/commit, e.g. 'release-4.17' or 'v1.8.4'. "
                                                     "Match the cluster's version. Defaults to the repo's default_ref."}
        return [
            {
                "name": "list_sources",
                "description": "List the offline knowledge sources this server can search, whether each is reachable, "
                               "and what it contains. Call once if unsure which source fits.",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "search",
                "description": "Full-text search across the team's offline knowledge: " + listing + ". "
                               "Returns ranked hits grouped by source, each with an id to pass to `read`. "
                               "Search exact error messages first, then component names. Team brain hits describe "
                               "OUR environment; RHOKP is Red Hat product docs + KCS solutions + CVEs/errata.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keywords or an exact error message."},
                        "sources": src_prop,
                        "per_source": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                        "ref": {**ref_prop, "description": "For git_repo sources: branch/tag whose docs to search."},
                        "product": {"type": "string", "description": "RHOKP only: product filter, e.g. "
                                    "'Red Hat OpenShift Container Platform'. Pass '' to search all products."},
                        "version": {"type": "string", "description": "RHOKP only: documentation version, e.g. '4.17'."},
                        "doc_kind": {"type": "string", "description": "RHOKP only: documentKind, e.g. 'Solution', "
                                     "'Article', 'documentation', 'Cve', 'Errata'."},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "read",
                "description": "Read a document returned by `search` (by source + id). Long documents are paged: "
                               "use `offset` to continue.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "enum": names},
                        "id": {"type": "string", "description": "The `id` from a search hit."},
                        "ref": ref_prop,
                        "offset": {"type": "integer", "minimum": 0, "default": 0},
                        "max_chars": {"type": "integer", "minimum": 1000, "maximum": MAX_READ_CHARS, "default": 20000},
                    },
                    "required": ["source", "id"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "route",
                "description": "Which areas, teams and cross-team interface pages a problem touches (it-brain). "
                               "Call it FIRST for any problem that may involve more than one system — e.g. "
                               "'PVC stuck on OpenShift with PowerFlex', 'VM live migration fails on Trident', "
                               "'firewall blocks cluster egress'. Returns the areas (with owner team), the "
                               "interface pages to read first and what to search next. Never limits search.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"question": {"type": "string", "description": "The problem in the user's words, "
                                                                                  "with product names and the error."}},
                    "required": ["question"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "related",
                "description": "Neighbours of a document in its source's link graph: pages it links to, pages that "
                               "link to it, and (team brain) pages sharing its tags. Use after `search`/`read` to "
                               "follow a topic instead of searching again — e.g. from a knowledge page to its "
                               "runbook and the incidents that cite it. Omit `id` for graph statistics and the "
                               "most-linked pages of the source.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "enum": names},
                        "id": {"type": "string", "description": "The `id` from a search hit."},
                        "ref": ref_prop,
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 15},
                    },
                    "required": ["source"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "search_code",
                "description": "git grep a mirrored repository (" + (", ".join(repos) or "none") + ") at a specific "
                               "branch/tag — e.g. find where HyperShift sets a condition, which controller emits an "
                               "error, or how CAPI handles a field, in the version the cluster actually runs. "
                               "Excludes vendor/ unless `path` targets it.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo": repo_prop,
                        "pattern": {"type": "string", "description": "Extended regex (or fixed string if regex=false)."},
                        "ref": ref_prop,
                        "path": {"type": "string", "description": "Glob to restrict files, e.g. 'api/**/*.go' "
                                 "or 'vendor/sigs.k8s.io/cluster-api/**'."},
                        "regex": {"type": "boolean", "default": True},
                        "ignore_case": {"type": "boolean", "default": False},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 300, "default": 60},
                    },
                    "required": ["repo", "pattern"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "read_code",
                "description": "Read a file (or a line range) from a mirrored repository at a branch/tag.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo": repo_prop,
                        "path": {"type": "string"},
                        "ref": ref_prop,
                        "start_line": {"type": "integer", "minimum": 1, "default": 1},
                        "end_line": {"type": "integer", "minimum": 1},
                    },
                    "required": ["repo", "path"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "find_definition",
                "description": "Find a Go type/func/field or CRD kind by name in a mirrored repo at a ref and return "
                               "its definition block — e.g. HostedClusterSpec, NodePoolManagement, MachineHealthCheck.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"repo": repo_prop, "symbol": {"type": "string"}, "ref": ref_prop},
                    "required": ["repo", "symbol"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "list_refs",
                "description": "List branches and tags of a mirrored repo (newest version first), optionally filtered "
                               "by substring — use to pick the ref that matches a cluster's OCP/MCE/CAPI version.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"repo": repo_prop, "filter": {"type": "string"},
                                   "limit": {"type": "integer", "minimum": 1, "maximum": 300, "default": 60}},
                    "required": ["repo"],
                    "additionalProperties": False,
                },
            },
        ]

    # ---------------------------------------------------------------------------- dispatch
    def call(self, name: str, args: dict) -> str:
        fn = getattr(self, f"t_{name}", None)
        if not fn:
            raise ToolError(f"unknown tool {name}")
        try:
            return fn(**(args or {}))
        except (SourceError, ToolError) as e:
            raise ToolError(str(e)) from e
        except TypeError as e:
            raise ToolError(f"bad arguments for {name}: {e}") from e

    def _src(self, name: str) -> Source:
        s = self.sources.get(name)
        if not s:
            raise ToolError(f"unknown source {name!r}; known: {', '.join(sorted(self.sources))}")
        return s

    def _repo(self, name: str) -> GitRepo:
        s = self._src(name)
        if not isinstance(s, GitRepo):
            raise ToolError(f"{name} is not a git_repo source")
        return s

    # ---------------------------------------------------------------------------- tools
    def t_route(self, question: str) -> str:
        brain = self.sources.get("brain")
        if not isinstance(brain, MarkdownDir) or not (brain.root / "teams.json").is_file():
            raise ToolError("route needs the `brain` source with a teams.json (it-brain); use `search` instead")
        import json
        names = {k: v.get("name", k) for k, v in json.loads((brain.root / "teams.json").read_text())["teams"].items()}
        return _route.render(_route.route(brain.root, question), names)

    def t_list_sources(self) -> str:
        futs = {n: self.pool.submit(s.available) for n, s in self.sources.items()}
        lines = ["| source | kind | status | description |", "|---|---|---|---|"]
        for n, s in sorted(self.sources.items()):
            try:
                ok, detail = futs[n].result(timeout=15)
            except Exception as e:  # noqa: BLE001
                ok, detail = False, str(e)
            lines.append(f"| {n} | {s.kind} | {'✅' if ok else '❌'} {detail} | {s.description} |")
        return "\n".join(lines)

    def t_search(self, query: str, sources=None, per_source: int = 5, ref=None, product=None, version=None,
                 doc_kind=None) -> str:
        targets = [self._src(n) for n in (sources or sorted(self.sources))]
        if not sources:  # default: skip code-only repos
            targets = [s for s in targets if not (isinstance(s, GitRepo) and not s.docs)]
        kw = {"ref": ref, "product": product, "version": version, "doc_kind": doc_kind}

        def run(s: Source):
            return s.search(query, per_source, **kw)

        futs = [(s, self.pool.submit(run, s)) for s in targets]
        out, errors, total = [], [], 0
        for s, f in futs:
            try:
                hits = f.result(timeout=90)
            except Exception as e:  # noqa: BLE001
                errors.append(f"- {s.name}: {e}")
                continue
            if not hits:
                continue
            total += len(hits)
            out.append(f"## {s.name}")
            for h in hits:
                head = f" › {h['heading']}" if h["heading"] else ""
                meta = ", ".join(f"{k}={v}" for k, v in (h.get("meta") or {}).items())
                out.append(f"- **{h['title']}**{head}  \n  id: `{h['id']}`  ·  {h['location']}"
                           + (f"  ·  {meta}" if meta else "") + f"\n  {h['snippet']}")
        if not total:
            out.append(f"No results for {query!r}. Try fewer or different terms, an exact error substring, "
                       "or another source.")
        if errors:
            out.append("\nSources that failed:\n" + "\n".join(errors))
        return "\n".join(out)

    def t_read(self, source: str, id: str, ref=None, offset: int = 0, max_chars: int = 20000) -> str:  # noqa: A002
        doc = self._src(source).read(id, ref=ref)
        text = doc["text"]
        max_chars = min(int(max_chars), MAX_READ_CHARS)
        part = text[offset:offset + max_chars]
        more = offset + max_chars < len(text)
        footer = (f"\n\n[… {len(text) - offset - max_chars} more chars — call read with offset={offset + max_chars}]"
                  if more else "")
        if not more:  # last page: point at the neighbours so the next step is a read, not another search
            footer += self._neighbours(source, id, ref)
        return f"# {doc['title']}\nsource: {source} · {doc['location']} · chars {offset}-{offset + len(part)} of {len(text)}\n\n{part}{footer}"

    def _neighbours(self, source: str, doc_id: str, ref) -> str:
        try:
            g = self._src(source).graph(ref)
        except Exception:  # noqa: BLE001 — the graph is a convenience, never a reason to fail a read
            return ""
        if doc_id not in g.title:
            return ""
        links = list(dict.fromkeys(g.back.get(doc_id, []) + g.out.get(doc_id, [])))[:8]
        if not links:
            return ""
        return ("\n\n---\nLinked pages (read with the same source; `related` lists all): "
                + ", ".join(f"`{x}`" for x in links))

    def t_related(self, source: str, id: str = "", ref=None, limit: int = 15) -> str:  # noqa: A002
        g = self._src(source).graph(ref)
        limit = min(int(limit), 50)

        def fmt(doc_id, note=""):
            return f"- `{doc_id}` — {g.title.get(doc_id, doc_id)}" + (f"  ({note})" if note else "")

        if not id:
            top = sorted(g.back, key=lambda d: (-len(g.back[d]), d))[:limit]
            return (f"{source}: {g.stats()}\n\n## Most linked pages\n"
                    + ("\n".join(fmt(d, f"{len(g.back[d])} links in") for d in top) or "(no links)"))
        if id not in g.title:
            raise ToolError(f"{id!r} is not a document in {source}; use an id from `search`")
        out = [f"# {g.title[id]}\nsource: {source} · id: `{id}`"
               + (f" · area: {g.area[id]}" if g.area.get(id) else "")
               + (f" · tags: {', '.join(g.tags[id])}" if g.tags.get(id) else "")]
        for head, items in (("Links to", g.out.get(id, [])), ("Linked from", sorted(g.back.get(id, [])))):
            if items:
                out.append(f"\n## {head}\n" + "\n".join(fmt(d) for d in items[:limit])
                           + (f"\n… {len(items) - limit} more" if len(items) > limit else ""))
        linked = set(g.out.get(id, [])) | set(g.back.get(id, []))
        sim = [(d, tags) for d, tags in g.similar(id, limit + len(linked)) if d not in linked][:limit]
        if sim:
            out.append("\n## Shares tags\n" + "\n".join(fmt(d, ", ".join(tags)) for d, tags in sim))
        if len(out) == 1:
            out.append("\nNo links or shared tags. Use `search`.")
        return "\n".join(out)

    def t_search_code(self, repo: str, pattern: str, ref=None, path=None, regex=True, ignore_case=False,
                      limit: int = 60) -> str:
        r = self._repo(repo).grep(pattern, ref=ref, path=path, regex=regex, ignore_case=ignore_case,
                                  limit=min(int(limit), 300))
        head = f"{repo} @ {r['ref']} ({r['sha'][:10]}) — {len(r['hits'])} hits" + (" (truncated)" if r["truncated"] else "")
        if not r["hits"]:
            return head + "\nNo matches."
        return head + "\n" + "\n".join(f"{h['path']}:{h['line']}: {h['text']}" for h in r["hits"])

    def t_read_code(self, repo: str, path: str, ref=None, start_line: int = 1, end_line=None) -> str:
        r = self._repo(repo).show(path, ref=ref, start=start_line, end=end_line)
        body = "\n".join(f"{i:>5}  {ln}" for i, ln in enumerate(r["lines"], start=r["start"]))
        more = f"\n[… file has {r['total']} lines; continue with start_line={r['end'] + 1}]" if r["end"] < r["total"] else ""
        return f"{repo} @ {r['ref']} ({r['sha'][:10]}) {r['path']} lines {r['start']}-{r['end']} of {r['total']}\n{r['url']}\n```\n{body}\n```{more}"

    def t_find_definition(self, repo: str, symbol: str, ref=None) -> str:
        r = self._repo(repo).definition(symbol, ref=ref)
        out = [f"{repo} @ {r['ref']} ({r['sha'][:10]}) — `{symbol}`"]
        d = r.get("definition")
        if d:
            body = "\n".join(f"{i:>5}  {ln}" for i, ln in enumerate(d["lines"], start=d["start"]))
            out.append(f"\nDefinition: {d['path']}:{d['start']}\n```go\n{body}\n```")
        if r["hits"]:
            out.append("\nAll matches:\n" + "\n".join(f"{h['path']}:{h['line']}: {h['text']}" for h in r["hits"][:40]))
        else:
            out.append("No definition found. Try search_code with a broader pattern or another ref.")
        return "\n".join(out)

    def t_list_refs(self, repo: str, filter: str = "", limit: int = 60) -> str:  # noqa: A002
        refs = self._repo(repo).refs(filter, limit=min(int(limit), 300))
        return f"{repo}: {len(refs)} refs" + (f" matching {filter!r}" if filter else "") + "\n" + "\n".join(refs)
