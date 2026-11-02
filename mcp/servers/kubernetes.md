---
title: Kubernetes MCP server (kubernetes-mcp-server) — full cluster access with your kubeconfig, pass the context every time
type: mcp
area: openshift
tags: [mcp, kubernetes, openshift, cluster-admin, kubeconfig]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [platform-team]
source: claude-session
---

# Kubernetes MCP (`kubernetes-mcp-server`)

- **Upstream:** `containers/kubernetes-mcp-server` (Go, Apache-2.0), pinned **v0.0.67**. Talks to the API server
  directly (no `oc`/`kubectl` needed) and understands OpenShift (`projects_list`).
- **Installed with the plugin:** archives for linux-x86_64, darwin-arm64 and windows-x86_64 in
  `plugins/team-brain/mcp-servers/vendor/kubernetes/`, sha256 in `vendor/manifest.json`, started by
  `mcp-servers/launch.py kubernetes`. Updating: `scripts/fetch-mcp-binaries.py` on a connected host.
- **Registered in:** `plugins/team-brain/.mcp.json` as `kubernetes`. Tool names in Claude Code:
  `mcp__plugin_team-brain_kubernetes__<tool>`.
- **Credentials:** whatever `KUBECONFIG` (or `~/.kube/config`) the shell that started Claude has. It acts as
  *you*. With no context in the kubeconfig the server refuses to start — `/mcp` shows it as failed; that is
  expected on a machine without cluster access.

## How we start it (and why)

`--config mcp-servers/kubernetes.toml` — **full access**: read, write, exec and Secrets, with your own rights.
The team are cluster admins and decide per call in Claude Code's permission prompt.

- That prompt is the only gate. **Don't add the write tools to an allow-list** (`pods_exec`, `pods_run`,
  `pods_delete`, `resources_create_or_update`, `resources_delete`, `resources_scale`); allow-listing the read
  tools is fine.
- `configuration_view` stays disabled: it prints the kubeconfig *including user tokens* and adds nothing over
  `configuration_contexts_list`.
- Telemetry (OpenTelemetry export) is off.
- To restrict one machine again (shared jump host), add `read_only = true` and/or a `denied_resources` block
  for `Secret` in `kubernetes.toml` — the file shows how.

## Usage rules

1. **Name the cluster on every call.** With more than one context in the kubeconfig every tool takes a `context`
   argument; without it the call goes to the *current* context, which is whatever the last `oc login` left.
   `configuration_contexts_list` first, then pass `context`. Say which cluster each result is from. This matters
   most for writes: state the cluster and the object in the same sentence as the change you propose.
2. **Look first, change second.** Read the object, say what you will change and why, then make one change.
3. **Changes that must last go through GitOps.** Argo CD owns what the day1/day2 repos declare and will revert a
   manual edit on its next sync; a direct write is for diagnosis and emergencies, and the fix still belongs in
   the repo (`knowledge/gitops/day2-sites-tree-discovery-and-version-layers.md`).
4. **Secret values enter the conversation once read.** Read a Secret only when the value is needed, and never
   copy it into a brain page, commit message or MR (`<REDACTED>`).
5. Hosted clusters: the HostedCluster/NodePool objects live on the **MCE** cluster, the workloads on the hosted
   cluster — two different contexts (`knowledge/openshift/fleet-topology-hub-mce-hosted.md`).
6. Prefer narrow reads (`resources_get`, a namespace, a label selector) over cluster-wide lists on big clusters.
7. Metrics come from the Grafana MCP (`mcp/servers/grafana.md`), not from `pods_top`/`nodes_top` alone.

## Tools (20, listed from the vendored binary with our config)

Read: `configuration_contexts_list`, `namespaces_list`, `projects_list`, `events_list`, `pods_list`,
`pods_list_in_namespace`, `pods_get`, `pods_log`, `pods_top`, `nodes_top`, `nodes_log`, `nodes_stats_summary`,
`resources_list` and `resources_get` (any kind, by `apiVersion` + `kind`: HostedCluster, NodePool, BareMetalHost,
ClusterOperator, Application, Secret…).

Write: `pods_exec`, `pods_run`, `pods_delete`, `resources_create_or_update`, `resources_delete`,
`resources_scale`.

### KubeVirt toolset (enabled since 2026-11-02 — we run OpenShift Virtualization)

`kubernetes.toml` enables `toolsets = ["core", "config", "kubevirt"]`, which adds 6 tools (25 in total with the
dummy single-context kubeconfig used for the check; `configuration_contexts_list` appears with several contexts):

| Tool | Does | Changes state |
|---|---|---|
| `vm_troubleshoot` | collects VM + VMI status, volumes, virt-launcher pod, its logs and events into one report | no |
| `vm_guest_info` | guest-agent data of a running VM | no |
| `vm_lifecycle` | `start` / `stop` / `restart` by setting `runStrategy` (`Always` / `Halted`) | **yes** |
| `vm_create`, `vm_create_from_template` | create a VirtualMachine (instance types, preferences, Multus NICs) | **yes** |
| `vm_clone` | creates a `VirtualMachineClone` | **yes** |

Air-gap caveat: `vm_create` resolves OS names (`fedora`, `rhel9` …) to container disks on `quay.io/containerdisks`,
which our clusters cannot reach — pass an image from the mirror registry or use an in-cluster DataSource.
Approve every write call; VM guidance: `knowledge/kubevirt/README.md`.

Other toolsets exist upstream (`helm`, `tekton`, `kiali`, `netobserv`, `kcp`); enable one in
`kubernetes.toml` only when we use that product.

## What is verified

- 2026-11-02, linux x86_64 (vendored v0.0.67) with `kubevirt` enabled: starts and lists the 25 tools including the
  6 `vm_*` tools; not run against a cluster with KubeVirt.

- 2026-10-03, macOS arm64: the binary starts from the plugin with this config and lists the 20 tools above;
  `configuration_view` is absent; `context` appears on tools when the kubeconfig has several contexts.
- The restricted variant (`read_only` + denied `Secret`) was tested against a throwaway local Kubernetes cluster:
  Secret reads refused, write tools absent.
- **Not verified:** any write or Secret read in full-access mode, any OpenShift cluster of ours, the
  linux/windows binaries (checksum only), behaviour with the fleet's real kubeconfigs (many contexts, token expiry).

## History

- 2026-10-03: added, vendored v0.0.67.
- 2026-10-03: switched from read-only to full access at the platform team's request (cluster admins, per-call approval).
- 2026-11-02: KubeVirt toolset enabled (6 vm_* tools)
