---
title: The kubevirt toolset of our Kubernetes MCP — vm_troubleshoot, vm_create, vm_lifecycle, vm_clone, vm_guest_info, vm_console_screenshot, prompts — what each reads or writes, and air-gap caveats
type: knowledge
area: kubevirt
tags: [kubevirt, mcp, kubernetes-mcp-server, toolset, vm_troubleshoot, vm_create, vm_lifecycle, vm_clone, vm_guest_info, claude]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: containers/kubernetes-mcp-server docs/kubevirt.md and README.md (snapshot docs/upstream/kubernetes-mcp-server); plugins/team-brain/mcp-servers/kubernetes.toml
---

# KubeVirt tools in the Kubernetes MCP

Our plugin ships `kubernetes-mcp-server` (`mcp/servers/kubernetes.md`); its optional **`kubevirt` toolset** is enabled in
`plugins/team-brain/mcp-servers/kubernetes.toml` (`toolsets = ["core", "config", "kubevirt"]`). It needs no extra
configuration: it uses the engineer's kubeconfig context, with the engineer's rights, and **every call is approved by a
human** like every other call of that server. Pass the `context` on each call.

## Tools (from the upstream docs)

| Tool | Reads / writes | Notes |
|---|---|---|
| `vm_troubleshoot` | read | collects VM, VMI, volumes, DV/PVC state, cloud-init config, pod state, logs and events, then runs heuristic checks — start here |
| `vm_guest_info` | read | OS, filesystems, interfaces, users from the **guest agent** (needs it running) |
| `vm_console_screenshot` | read | PNG of the VNC console (firmware, bootloader, login prompt); never sends input |
| `vm_lifecycle` | **write** | `start` (runStrategy `Always`), `stop` (`Halted`), `restart`, `pause`, `unpause` |
| `vm_create` | **write** | resolves OS name → container disk image, size/performance → instance type, preference; VM created `Halted` unless `autostart` |
| `vm_create_from_template` | **write** | processes a VirtualMachineTemplate server-side and creates the VM |
| `vm_clone` | **write** | creates a `VirtualMachineClone` (`knowledge/kubevirt/kubevirt-snapshots-clones-export-and-oadp-backup.md`) |

Prompts: `vm-troubleshoot` (step-by-step guide), `hco-status` (HyperConverged health report), `windows-golden-image`
(needs the `tekton` toolset too).

## Caveats for us

- The docs snapshot tracks upstream `main`; the **vendored binary is pinned** (`plugins/team-brain/mcp-servers/vendor/manifest.json`)
  and may have fewer tools — trust the tool list the running server reports.
- **Air gap:** `vm_create`'s OS-name resolution points at public container-disk images, and `windows-golden-image` uses the
  Tekton **hub resolver** and an ISO download URL — neither works without mirrored images / an internal hub. Prefer
  `vm_create_from_template` with our templates and DataSources from the mirror registry.
- `vm_lifecycle stop` changes runStrategy to `Halted` — the VM stays off until started again; say so when proposing it.
- Writes to VMs are lasting changes: if VMs are defined in GitOps (day2), change them there — Argo reverts manual edits.

## Scope & caveats

Read from the upstream docs; the toolset has **not been exercised against our clusters** yet.

## History

- 2026-11-02: created
