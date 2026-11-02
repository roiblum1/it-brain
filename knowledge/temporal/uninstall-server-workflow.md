---
title: uninstall-server workflow — take a server out of its hosted cluster (delete Machine, CAPI drain, Agent unbind) and the MCE (remove-server child), finish broken HyperShift deletions, AgentRetakenError
type: knowledge
area: temporal
tags: [temporal, redbull-workflows, server-lifecycle, uninstall-server, remove-server, hypershift, capi, agentmachine, machine, agent, nodepool, drain, finalizer, baremetalhost, server-scan]
applies_to: [hosted-cp]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# uninstall-server (and its child remove-server)

| | |
|---|---|
| Trigger | `POST /workflows/server-lifecycle/uninstall-server` `{server_names, mce_cluster, namespace?, keep_inventory?}` — 202, 409 if that server is uninstalling, 502 if Temporal refuses |
| Workflow id | `uninstall-server-<server, lowercased>`; child `remove-server-<server>` on `remove-server-workflow`, awaited |
| Queues | workflow `uninstall-server-workflow`; activities `server-lifecycle-activity-<mce>` |
| Way in | `knowledge/temporal/install-server-workflow.md` |

What an operator otherwise does from the console's host list: take the node out of its hosted cluster, then *Remove
host*. Nothing has to be done first — no scale-down, no annotation. `mce_cluster` is accepted with or without `ocp4-`.
`count`, `node_pool`, `hosted_cluster`, `server_name` are 422: server-scan and the Agent's binding say where a server is.
HyperShift background: `knowledge/hypershift/README.md`.

## Two paths, chosen by the binding observed (never by a state string)

| | Hosted cluster's node | Inventory host (Agent Available) |
|---|---|---|
| Seen | Agent bound (`spec.clusterDeploymentName`) + AgentMachine; or an AgentMachine whose `status.agentRef` names the Agent (deletion under way); or leftovers of a broken deletion | nothing links the Agent to a hosted cluster (or no Agent) |
| Hosted half | delete the Machine; CAPI drains (PDBs respected, 20 min); provider releases the Agent, host reboots into discovery (1 h until `known-unbound`); verify no Machine / AgentMachine / Node left | skipped (named in `skipped`), but checked **again** fresh right before remove-server |
| Inventory half | remove-server: power off (`spec.online: false`, wait `status.poweredOn: false`, 10 min) → delete NMStateConfig → BMH (`detached` first; metal3 finalizer dropped if stuck) and its Secret → **Agent last** → clear MACs from the site PXE VM → verify (5 min) | same |

`keep_inventory: true` stops after the hosted half: the server stays powered on in discovery as a free Agent (like the
console's *Remove from the cluster*); lock held 24 h and kept; `kept_in_inventory: true`.

**NodePool replicas are never changed**, so the NodePool creates a replacement Machine and the provider binds another
free matching Agent — the cluster keeps its size on a different server. If this server is the only free Agent the
NodePool matches, the replacement takes it back: the run stops with `AgentRetakenError` naming the new AgentMachine and
writes nothing more. Free another matching Agent (or lower replicas), then re-run. Why two checks for an inventory host:
an Available Agent can be taken by any NodePool at any moment and the server-scan lock means nothing to the provider.

## Phases

`checking-inventory` (server-scan record by exact name via `GET /servers?search=` then `/servers/{id}` — never
`/servers/available`) → `inspecting` (reads: BMH, Agents by BMAC label or any MAC, AgentMachines, Machines,
HostedClusters — all namespaces) → `checking-hosted-node` (hosted cluster Nodes, via its admin kubeconfig) →
`reserving-server` (server-scan lock, holder `uninstall-server`, TTL 2 h 5 min) → hosted half: `draining-node`,
`deleting-machine`, `awaiting-machine-deletion` (`sub_phase` `draining` ≤ 20 min / `releasing` / `unbinding` ≤ 1 h),
`verifying-agentmachine`, `verifying-node`, `verifying-agent` (≤ 5 min each) → `holding-server` (24 h) →
`removing-from-inventory` (child) → `releasing-server` (own lock given back so the server is installable again at once —
operator decision 2026-10-31; kept if PXE cleanup failed) → `completed`.

## Finishing what HyperShift left behind

| Left | Why nothing finishes it | The run |
|---|---|---|
| AgentMachine + Machine, no Node | not broken (CAPI skips the drain) | normal path; still looks for the Node by providerID and hostname |
| AgentMachine, no Machine | the provider unbinds only from a Machine's pre-terminate hook; its finalizer is dropped without unbinding, or stays for ever with no owner | makes the provider's exact unbind write, deletes the AgentMachine, drops `agentmachine.agent-install.openshift.io/deprovision` if stuck a minute later |
| Machine, no AgentMachine | found by providerID `agent://<agent>`; the provider's hook stays for ever | deletes the Machine; at its pre-terminate hook releases the Agent, then removes `pre-terminate.delete.hook.machine.cluster.x-k8s.io/agentmachine` |
| Agent still bound, both gone | nothing references it | releases it (binding into the HCP namespace) |
| Node, no Machine/AgentMachine | CAPI drains/deletes only through a Machine | Ready: cordon + evict (CAPI's rules) before the release, delete once NotReady. Ready with nothing on the MCE to release through: refused (`HostedNodeStillPresentError`) |

Only the Agent provider's own hook and finalizer are ever removed, and only after its unbind is done. Result fields
`leftovers_at_start` and `cleaned_up` say what was found and every write made on a controller's behalf, and why.

## Facts read off upstream code (useful beyond this workflow)

- An Agent's `clusterDeploymentName.namespace` is the **hosted control-plane namespace** `<hc-ns>-<hc>` (HyperShift
  creates the AgentCluster/ClusterDeployment there), found by HyperShift's rule `<namespace>-<name with dots as dashes>`
  — ambiguous (`clusters-a-b`), hence matching against a list of HostedClusters.
- On Machine deletion, cluster-api-provider-agent first clears the Agent's `clusterDeploymentName`, `agentMachineRef`
  label and namespace annotation, then holds the Machine on the pre-terminate hook until the Agent is unbound — during
  that stretch only `AgentMachine.status.agentRef` links them.
- The unbind lives only in `handleDeletionHook` (owner Machine must exist and reach its pre-terminate hook).
- `spec.providerID` = `agent://<agent name>` on AgentMachine and Machine; CAPI links the Node by providerID; the Node
  registers under the Agent's hostname.
To check these at our version: the `hypershift` and `cluster-api-provider-agent` mirrors at the ref from
`knowledge/meta/fleet-versions.md`.

## Errors

Refused, nothing changed: `ServerNotInServerScanError`, `ClusterMembershipMismatchError` (server-scan disagrees — other
MCE, other cluster, `INSTALLED_TO_INVENTORY` while bound: re-run once its 15-min agents job agrees), `MultipleBoundAgentsError`,
`NotHostedClusterNodeError` (e.g. an early-bound ACM/ZTP Agent), `ConflictingHostedObjectsError`, `HostedNodeStillPresentError`,
`ServerReservedError` (typically install-server's 24 h hold — release it in server-scan, re-run), `AmbiguousServerNameError`.
After the Machine delete (a re-run resumes; no undo): `NodeDrainTimeoutError` (Node left cordoned; names Pods/PDBs),
`MachineDrainTimeoutError` (names `pre-drain`/`pre-terminate` hook annotations), `AgentRetakenError`, `AgentBindingChangedError`,
`AgentUnbindTimeoutError`, `MachineDeletionTimeoutError`, `ServerStillPresentError`, `AgentStillBoundError`,
`RemoveServerAlreadyRunningError`, `RemoveServerFailedError` (carries the child's error). Transient forever:
server-scan / MCE / hosted API unreachable (`HostedClusterUnreachableError`); permanent: `HostedClusterAccessError`.

## Access the worker needs (beyond install-server's Role)

ClusterRole (rendered by `rbac.hostedClusters`, default true): machines and agentmachines get/list/delete/patch, agents
patch, hostedclusters get/list, **secrets get on the whole MCE** (hosted admin kubeconfigs — the widest grant). The worker
reads the Secret in `HostedCluster.status.kubeconfig`, replaces the server with
`https://kube-apiserver.<hc-ns>-<hc>.svc:6443` (TLS still verified against the kubeconfig's CA), writes key material to a
per-call temp dir deleted after the call, and never puts kubeconfig content in errors, logs or history. If
`verifying-node` keeps retrying `HostedClusterUnreachableError`, check NetworkPolicies on the control-plane namespaces.
Roll the limb (and ClusterRole) out before using the route: a new brain with an old limb sits in `checking-inventory`.

## History

- 2026-11-02: created from the uninstall-server page of the Redbull Workflows docs site v1.0.61
