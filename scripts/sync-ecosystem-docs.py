#!/usr/bin/env python3
"""Fetch ONLY the documentation of ecosystem projects into docs/upstream/<name>/ (pinned snapshots).

HyperShift, Ironic, Cluster API and the Agent provider are full git mirrors (code + docs at any ref,
see mcp/sources.json). Everything below is docs-only: sparse, shallow, blobless clone of the default
branch (or REF override), keep only .md/.rst/.adoc files. Run on a connected host, or inside the air
gap with UPSTREAM_GIT_BASE pointing at an internal mirror, then commit the result.

    python3 scripts/sync-ecosystem-docs.py              # all whose upstream moved since the last sync
    python3 scripts/sync-ecosystem-docs.py --force      # re-fetch even if the recorded commit is still current
    python3 scripts/sync-ecosystem-docs.py --versions   # only rewrite docs/upstream/VERSIONS.md
    python3 scripts/sync-ecosystem-docs.py vllm kserve  # only these
    REF_vllm=v0.11.0 python3 scripts/sync-ecosystem-docs.py vllm   # pin one to the installed version

A source is skipped when `git ls-remote` shows the commit recorded in its .upstream file is still the tip,
so running this on every commit is cheap (.github/workflows/docs-refresh.yml does). A sync that would
produce no files leaves the existing snapshot alone. docs/upstream/VERSIONS.md lists what every snapshot
is: repo, ref, commit, the newest upstream release tag at sync time, file count.

docs/upstream is generated: don't hand-edit it.
"""
import os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

BASE = os.environ.get("UPSTREAM_GIT_BASE", "https://github.com")
ROOT = Path(__file__).resolve().parent.parent
EXT = (".md", ".markdown", ".rst", ".adoc", ".txt", ".mdx")  # .mdx is stored as .md (the indexer reads .md)

# name: (repo, [paths in repo][, extra extensions])  — default branch unless REF_<name> (dashes -> underscores) is set.
# Extra extensions are for projects whose documentation is largely example manifests/code (KServe samples).
CODE = (".yaml", ".yml", ".py")
SKIP_DIRS = {"zh_archive"}  # archived translations: outdated, and they outrank the English page in search
SOURCES = {
    "ako": ("vmware/load-balancer-and-ingress-services-for-kubernetes", [
        "docs", "README.md", "CHANGELOG.md", "AKO_GATEWAY_CHANGELOG.md", "ako-operator/README.md",
        "ako-crd-operator/README.md", "ako-crd-operator/CHANGELOG.md"]),
    "envoy": ("envoyproxy/envoy", ["docs/root"]),
    "envoy-gateway": ("envoyproxy/gateway", ["site/content/en/latest"]),
    "envoy-ai-gateway": ("envoyproxy/ai-gateway", ["site/docs", "release-notes", "README.md"]),
    "gateway-api-inference-extension": ("kubernetes-sigs/gateway-api-inference-extension", [
        "site-src", "docs/proposals", "README.md"]),
    "kserve": ("kserve/kserve", [
        "docs", "README.md", "charts", "kernelcache/mcv/docs", "ROADMAP.md", "config/runtimes", "config/configmap",
        "config/llmisvc", "config/storagecontainers"], CODE),
    "kserve-website": ("kserve/website", ["docs"], CODE),  # docs/ = the site's /docs/next/ (latest)
    "prometheus-docs": ("prometheus/docs", ["docs"]),
    "prometheus-operator": ("prometheus-operator/prometheus-operator", ["Documentation", "README.md"]),
    "grafana-docs": ("grafana/grafana", ["docs/sources"]),
    "mcp-grafana": ("grafana/mcp-grafana", ["README.md", "docs"]),
    "kubernetes-mcp-server": ("containers/kubernetes-mcp-server", ["README.md", "docs"]),
    "okp-mcp": ("rhel-lightspeed/okp-mcp", ["README.md", "docs", "quadlet/README.md"]),
    "vllm": ("vllm-project/vllm", ["docs", "examples", "README.md"]),
    "lmcache": ("LMCache/LMCache", [
        "docs/source", "docs/design", "examples", "operator/README.md", "operator/DESIGN.md",
        "operator/config/samples", "README.md"], CODE),
    "mooncake": ("kvcache-ai/Mooncake", [
        "docs/source", "README.md", "monitoring/README.md", "mooncake-store/src/hf3fs/README.md"]),
    "lws": ("kubernetes-sigs/lws", ["site/content/en/docs", "docs", "keps", "README.md"]),
    "metal3-docs": ("metal3-io/metal3-docs", ["docs", "design"]),
    "baremetal-operator": ("metal3-io/baremetal-operator", [
        "docs", "README.md", "config/README.md", "ironic-deployment/README.md"]),
    "cluster-api-provider-metal3": ("metal3-io/cluster-api-provider-metal3", ["docs", "README.md"]),
    "ip-address-manager": ("metal3-io/ip-address-manager", ["docs", "README.md"]),
    "ironic-standalone-operator": ("metal3-io/ironic-standalone-operator", ["docs", "README.md"]),
    "ironic-image": ("metal3-io/ironic-image", ["docs", "README.md"]),
    "gateway-api": ("kubernetes-sigs/gateway-api", ["site/content", "geps"]),
    "gpu-operator": ("NVIDIA/gpu-operator", ["README.md", "docs"]),
    "node-feature-discovery": ("kubernetes-sigs/node-feature-discovery", ["docs"]),
    "kueue": ("kubernetes-sigs/kueue", ["site/content/en/docs", "keps"]),
    "ovn-kubernetes": ("ovn-org/ovn-kubernetes", ["docs"]),
    "multus-cni": ("k8snetworkplumbingwg/multus-cni", ["docs", "README.md"]),
    "openshift-runbooks": ("openshift/runbooks", ["alerts"]),
    "assisted-service": ("openshift/assisted-service", ["docs"]),
    "etcd-docs": ("etcd-io/website", ["content/en/docs"]),
    # inference / HPC / fabrics / kernel tuning
    "llm-d": ("llm-d/llm-d", ["docs", "guides", "README.md"]),
    "sglang": ("sgl-project/sglang", ["docs/docs", "docs/cookbook"]),
    "tensorrt-llm": ("NVIDIA/TensorRT-LLM", ["docs/source"]),
    "dynamo": ("ai-dynamo/dynamo", ["docs"]),
    "ray-docs": ("ray-project/ray", ["doc/source/serve", "doc/source/cluster/kubernetes"]),
    # it-brain: virtualization (KubeVirt / OpenShift Virtualization, MTV, PowerShell / PowerCLI)
    "kubevirt-user-guide": ("kubevirt/user-guide", ["docs"]),
    "kubevirt-docs": ("kubevirt/kubevirt", ["docs"]),
    "cdi-docs": ("kubevirt/containerized-data-importer", ["doc", "README.md"]),
    "hco-docs": ("kubevirt/hyperconverged-cluster-operator", ["docs", "README.md"]),
    "forklift-docs": ("kubev2v/forklift-documentation", ["documentation", "modules"]),
    "powershell-docs": ("MicrosoftDocs/PowerShell-Docs", ["reference/docs-conceptual", "reference/7.4/Microsoft.PowerShell.Core"]),
    "powercli-examples": ("vmware/PowerCLI-Example-Scripts", ["README.md", "Modules", "Scripts"]),
    # it-brain: platform tools (Temporal, Pydantic) and storage (Dell CSM, Trident)
    "temporal-docs": ("temporalio/documentation", [
        "docs/encyclopedia", "docs/develop/python", "docs/production-deployment/self-hosted-guide",
        "docs/troubleshooting", "docs/references", "docs/cli", "docs/best-practices"]),
    "temporal-mcp-docs": ("temporalio/temporal-mcp", ["README.md", "REQUEST_FOR_COMMENT.md", "docs"]),
    "pydantic-docs": ("pydantic/pydantic", ["docs"]),
    "pydantic-settings-docs": ("pydantic/pydantic-settings", ["docs", "README.md"]),
    "dell-csm-docs": ("dell/csm-docs", ["content/docs"]),
    "trident-docs": ("NetAppDocs/trident", [
        "trident-concepts", "trident-get-started", "trident-install", "trident-managing-k8s", "trident-protect",
        "trident-reco", "trident-reference", "trident-use", "troubleshooting.adoc", "known-issues.adoc",
        "trident-rn.adoc", "faq.adoc"]),
    "nccl": ("NVIDIA/nccl", ["docs"]),
    "ucx": ("openucx/ucx", ["docs"]),
    "rdma-core": ("linux-rdma/rdma-core", [
        "Documentation", "README.md", "infiniband-diags/man", "libibverbs/man", "librdmacm/man",
        "libibumad/man", "providers/mlx5/man"]),
    "nvidia-cloud-native-docs": ("NVIDIA/cloud-native-docs", [
        "gpu-operator", "openshift", "mig", "gpu-telemetry", "container-toolkit", "driver-containers", "kubernetes"]),
    "nvidia-network-operator-docs": ("Mellanox/network-operator-docs", ["docs"]),
    "sriov-network-operator": ("k8snetworkplumbingwg/sriov-network-operator", ["doc"]),
    "tuned": ("redhat-performance/tuned", ["doc"]),
    "linux-kernel-docs": ("torvalds/linux", [
        "Documentation/admin-guide/mm", "Documentation/admin-guide/kernel-parameters.txt",
        "Documentation/admin-guide/cputopology.rst", "Documentation/admin-guide/numastat.rst",
        "Documentation/admin-guide/pm", "Documentation/scheduler", "Documentation/infiniband",
        "Documentation/core-api/irq", "Documentation/networking/ip-sysctl.rst",
        "Documentation/networking/scaling.rst", "Documentation/networking/rds.rst",
        "Documentation/networking/tcp-thin.rst", "Documentation/admin-guide/perf",
        "Documentation/admin-guide/sysctl"]),
}


def run(*cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True,
                          env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}).stdout.strip()


STABLE_TAG = re.compile(r"^v?\d+\.\d+(\.\d+)?$")


def meta(name):
    f = ROOT / "docs/upstream" / name / ".upstream"
    if not f.is_file():
        return {}
    return dict(line.split(": ", 1) for line in f.read_text().splitlines() if ": " in line)


def remote_tip(repo, ref):
    """Commit the ref (or the default branch) points at upstream, without cloning."""
    out = run("git", "ls-remote", f"{BASE}/{repo}.git", *( [ref, f"{ref}^{{}}"] if ref else ["HEAD"] ))
    lines = [l.split() for l in out.splitlines() if l]
    peeled = [sha for sha, r in lines if r.endswith("^{}")]  # annotated tag -> the commit it points at
    return (peeled or [sha for sha, _ in lines] or [""])[0]


def latest_tag(repo):
    out = run("git", "ls-remote", "--tags", "--refs", "--sort=-version:refname", f"{BASE}/{repo}.git")
    for line in out.splitlines():
        tag = line.split("refs/tags/", 1)[-1]
        if STABLE_TAG.match(tag):
            return tag
    return ""


def sync(name, work, force=False):
    repo, paths, *extra = SOURCES[name]
    exts = EXT + (extra[0] if extra else ())
    ref = os.environ.get("REF_" + name.replace("-", "_"))
    old = meta(name)
    if not force and old.get("commit") and old.get("paths") == ", ".join(paths) and old.get("repo") == repo \
            and (not ref or old.get("ref") == ref) and remote_tip(repo, ref) == old["commit"]:
        return None
    clone = Path(work) / name
    cmd = ["git", "clone", "--quiet", "--depth", "1", "--filter=blob:none", "--no-checkout"]
    if ref:
        cmd += ["--branch", ref]
    run(*cmd, f"{BASE}/{repo}.git", str(clone))
    run("git", "sparse-checkout", "set", "--no-cone", *[f"/{p}" for p in paths], cwd=clone)
    run("git", "checkout", "--quiet", cwd=clone)
    sha = run("git", "rev-parse", "HEAD", cwd=clone)
    branch = ref or run("git", "rev-parse", "--abbrev-ref", "HEAD", cwd=clone)
    dest = ROOT / "docs/upstream" / name
    new = Path(work) / (name + ".out")
    n = 0
    for p in paths:
        src = clone / p
        files = [src] if src.is_file() else [f for f in src.rglob("*") if f.is_file()]
        for f in files:
            if f.suffix.lower() in exts and not SKIP_DIRS.intersection(f.parts):
                # examples yes, generated bulk no: Helm templates and CRD schemas are huge and say nothing a doc doesn't
                if f.suffix.lower() not in EXT and (f.stat().st_size > 200_000 or "templates" in f.parts
                                                      or "crd" in f.name.lower()):
                    continue
                out = new / f.relative_to(clone)
                if out.suffix.lower() == ".mdx":
                    out = out.with_suffix(".md")
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, out)
                n += 1
    if not n:  # upstream moved its docs: keep what we have and fail loudly instead of committing an empty folder
        raise RuntimeError(f"no doc files under {paths} at {sha[:10]} — upstream layout changed, fix SOURCES")
    (new / ".upstream").write_text(
        f"repo: {repo}\nref: {branch}\ncommit: {sha}\nlatest_tag: {latest_tag(repo)}\npaths: {', '.join(paths)}\n"
        f"files: {n}\nsynced: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(str(new), str(dest))
    return n, branch, sha[:10], (old.get("commit") or "new")[:10]


def write_versions():
    """docs/upstream/VERSIONS.md: one row per snapshot, from the .upstream files (all sync scripts)."""
    base = ROOT / "docs/upstream"
    rows = []
    for d in sorted(p for p in base.iterdir() if (p / ".upstream").is_file()):
        m = dict(line.split(": ", 1) for line in (d / ".upstream").read_text().splitlines() if ": " in line)
        src = m.get("repo") or m.get("site", "")
        ver = m.get("ref") or m.get("version", "")
        n = m.get("files") or m.get("pages") or str(sum(1 for f in d.rglob("*") if f.is_file()) - 1)
        rows.append(f"| `{d.name}` | {src} | {ver} | {m.get('commit', '')[:10]} | {m.get('latest_tag', '')} "
                    f"| {n} | {m.get('synced', '')[:10]} |")
    (base / "VERSIONS.md").write_text(
        "# Snapshot versions\n\nGenerated by `scripts/sync-ecosystem-docs.py` from each folder's `.upstream` file — "
        "don't edit. **Ref** is what the\nsnapshot was taken from (usually the default branch, i.e. *newer* than any "
        "release); **Latest release** is the newest\nstable upstream tag at sync time, for comparison with the version "
        "installed on a cluster.\n\n| Snapshot | Source | Ref | Commit | Latest release | Files | Synced |\n"
        "|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if flags - {"--force", "--versions"}:
        sys.exit(__doc__)
    names = args or list(SOURCES)
    bad = [n for n in names if n not in SOURCES]
    if bad:
        sys.exit(f"unknown: {', '.join(bad)}; known: {', '.join(SOURCES)}")
    failed = []
    if "--versions" not in flags:
        with tempfile.TemporaryDirectory() as work:
            for n in names:
                try:
                    res = sync(n, work, force="--force" in flags)
                    if res is None:
                        print(f"{n}: up to date")
                    else:
                        files, branch, sha, old = res
                        print(f"{n}: UPDATED {old} -> {sha} ({files} files @ {branch})")
                    shutil.rmtree(Path(work) / n, ignore_errors=True)
                except (subprocess.CalledProcessError, RuntimeError) as e:
                    failed.append(n)
                    print(f"{n}: FAILED {(getattr(e, 'stderr', '') or str(e)).strip()[:300]}", file=sys.stderr)
    write_versions()
    if failed:
        sys.exit(f"failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
