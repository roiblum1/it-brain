#!/usr/bin/env python3
"""Download the release archives of the third-party MCP servers we ship inside the plugin (connected host only).

The air-gapped network has no GitHub, so the binaries travel inside this repo:
plugins/team-brain/mcp-servers/vendor/<server>/<archive> plus vendor/manifest.json (version + sha256 of
every archive). plugins/team-brain/mcp-servers/launch.py verifies the sha256, unpacks the archive for the
engineer's OS/CPU on first use and runs it — nothing to install by hand.

    python3 scripts/fetch-mcp-binaries.py                  # all servers at the pinned versions
    python3 scripts/fetch-mcp-binaries.py grafana          # only this one
    VERSION_grafana=v2.1.0 python3 scripts/fetch-mcp-binaries.py grafana   # bump (then commit + bump plugin version)

Every archive is checked against the checksums file published with the release before it is kept.
On macOS with python.org Python: SSL_CERT_FILE=/etc/ssl/cert.pem.
"""
import hashlib, json, os, sys, urllib.request
from pathlib import Path

BASE = os.environ.get("UPSTREAM_RELEASE_BASE", "https://github.com")
ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "plugins/team-brain/mcp-servers/vendor"

# server: repo, pinned version, binary name, platform -> asset ({v} = version without "v").
# "checksums" = name of the checksums file published with the release; without it the sha256 comes from the
# asset digest GitHub records for the release (API). .mcpb bundles are zip files with the binary inside.
SERVERS = {
    "grafana": {
        "repo": "grafana/mcp-grafana",
        "version": "v2.0.0",
        "binary": "mcp-grafana",
        "license": "Apache-2.0",
        "checksums": "mcp-grafana_{v}_checksums.txt",
        "assets": {
            "linux-x86_64": "mcp-grafana_Linux_x86_64.tar.gz",
            "darwin-arm64": "mcp-grafana_Darwin_arm64.tar.gz",
            "windows-x86_64": "mcp-grafana_Windows_x86_64.zip",
        },
    },
    "kubernetes": {
        "repo": "containers/kubernetes-mcp-server",
        "version": "v0.0.67",
        "binary": "kubernetes-mcp-server",
        "license": "Apache-2.0",
        "assets": {
            "linux-x86_64": "kubernetes-mcp-server-{v}-linux-x64.mcpb",
            "darwin-arm64": "kubernetes-mcp-server-{v}-darwin-arm64.mcpb",
            "windows-x86_64": "kubernetes-mcp-server-{v}-windows-x64.mcpb",
        },
    },
    # Read-only Temporal MCP (pre-release upstream). No Windows build is published.
    "temporal": {
        "repo": "temporalio/temporal-mcp",
        "version": "v0.0.5",
        "binary": "temporal-mcp",
        "license": "MIT",
        "checksums": "checksums.txt",
        "assets": {
            "linux-x86_64": "temporal-mcp_{v}_linux_amd64.tar.gz",
            "darwin-arm64": "temporal-mcp_{v}_darwin_arm64.tar.gz",
        },
    },
}
API = os.environ.get("UPSTREAM_API_BASE", "https://api.github.com")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "team-brain-fetch"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def fetch(name):
    spec = SERVERS[name]
    version = os.environ.get("VERSION_" + name.replace("-", "_"), spec["version"])
    rel = f"{BASE}/{spec['repo']}/releases/download/{version}"
    v = version.lstrip("v")
    sums = {}
    if spec.get("checksums"):
        for line in get(f"{rel}/{spec['checksums'].format(v=v)}").decode().splitlines():
            parts = line.split()
            if len(parts) == 2:
                sums[parts[1].lstrip("*")] = parts[0]
    else:
        release = json.loads(get(f"{API}/repos/{spec['repo']}/releases/tags/{version}"))
        sums = {a["name"]: (a.get("digest") or "").removeprefix("sha256:") for a in release["assets"]}
    dest = VENDOR / name
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.iterdir():
        old.unlink()
    assets = {}
    for platform, asset in spec["assets"].items():
        asset = asset.format(v=v)
        data = get(f"{rel}/{asset}")
        digest = hashlib.sha256(data).hexdigest()
        if sums.get(asset) != digest:
            sys.exit(f"{name}: sha256 of {asset} does not match the checksum published with the release — not keeping it")
        (dest / asset).write_bytes(data)
        assets[platform] = {"file": asset, "sha256": digest, "bytes": len(data)}
        print(f"{name} {version} {platform}: {asset} {len(data) / 1e6:.1f} MB sha256 ok")
    return {"repo": spec["repo"], "version": version, "binary": spec["binary"], "license": spec["license"],
            "assets": assets}


def main():
    names = sys.argv[1:] or list(SERVERS)
    bad = [n for n in names if n not in SERVERS]
    if bad:
        sys.exit(f"unknown: {', '.join(bad)}; known: {', '.join(SERVERS)}")
    path = VENDOR / "manifest.json"
    manifest = json.loads(path.read_text()) if path.is_file() else {}
    for n in names:
        manifest[n] = fetch(n)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
