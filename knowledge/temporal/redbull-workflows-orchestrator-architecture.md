---
title: Redbull Workflows orchestrator — Temporal brain on the hub, one activity limb per domain, task-queue routing, per-MCE queues, workflow ids and the catalogue
type: knowledge
area: temporal
tags: [temporal, redbull-workflows, orchestrator, architecture, task-queue, worker, brain, limb, domain, workflow-id, mce, routing]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: Redbull Workflows docs site v1.0.61
---

# Redbull Workflows — how the orchestrator is built

Repo `team-redbull/workflows` (Python 3.12, `temporalio`, `pydantic`, FastAPI). It runs long-lived
cluster-lifecycle operations as Temporal workflows on the **Temporal server on the hub**
(`knowledge/openshift/fleet-topology-hub-mce-hosted.md`). Docs site: `<workflows-docs-url>` (the repo's
`CLAUDE.md` is named there as the authoritative rule set). SDK gotchas: `knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`.

## The catalogue (docs v1.0.61)

| Domain (= one limb) | Activity queue | Workflow | Workflow queue | Workflow id | Page |
|---|---|---|---|---|---|
| segment-lifecycle | `segment-lifecycle-activity` | initialize-segment | `initialize-segment-workflow` | `initialize-segment-<network>` | `knowledge/temporal/initialize-segment-workflow.md` |
| | | allocate-segment | `allocate-segment-workflow` | `allocate-segment-<TYPE>-<cluster>` | `knowledge/temporal/allocate-segment-workflow.md` |
| | | release-segment | `release-segment-workflow` | `release-segment-<TYPE>-<cluster>` | `knowledge/temporal/release-segment-workflow.md` |
| server-lifecycle | `server-lifecycle-activity-<mce>` (one per MCE) | install-server | `install-server-workflow` | `install-server-<mce>_<infraEnv>_<slot>` or `install-server-<mce>_<server>` | `knowledge/temporal/install-server-workflow.md` |
| | | uninstall-server (+ child remove-server) | `uninstall-server-workflow`, `remove-server-workflow` | `uninstall-server-<server>`, `remove-server-<server>` | `knowledge/temporal/uninstall-server-workflow.md` |
| server-provisioning | `server-provisioning-activity` (one for the estate) | provision-dell-server | `provision-dell-server-workflow` | `provision-dell-server-<idrac ip>` | `knowledge/temporal/provision-dell-server-workflow.md` |
| cluster-upgrade | `upgrade-gitops-activity` (hub), `cluster-upgrade-activity-<mce>`, `upgrade-agent-activity-<mce>` | upgrade-cluster (+ child upgrade-control-plane) | `upgrade-cluster-workflow`, `upgrade-control-plane-workflow` | `upgrade-cluster-<cluster>`, `upgrade-control-plane-<mce>_<n>` | `knowledge/temporal/upgrade-cluster-workflow.md` |

The site's own catalogue (`assets/nav.js`) is the one list of workflows; `href: null` entries are planned ones.
upgrade-cluster is built and run on a sandbox HostedCluster, **not in production yet**.

## Three layers that never call each other

| Layer | Holds | May depend on | Ships as |
|---|---|---|---|
| `shared/` (the contract) | Pydantic models, activity **signatures with empty bodies** (`shared/interfaces/<domain>.py`), task-queue constants (`shared/consts.py`), workflow-id builders (`shared/workflow_ids.py`), typed settings, error classes | `temporalio`, `pydantic`, `pydantic-settings` only — never `httpx` or a cloud SDK | baked into both images |
| `workflow_domains/` (the **brain**) | one folder per domain (workflows + `router.py`), `main_worker_init.py`, `api.py` | `shared` + FastAPI/uvicorn; no HTTP client, no SDK, **no credentials** | Deployment `workflows-orchestrator`, plus `workflows-orchestrator-api` from the same image |
| `activities/<domain>/` (the **limbs**) | the real implementations + that domain's `worker_init.py` | `shared` + whatever the domain needs | one Deployment + ServiceAccount + Secret + ConfigMap per domain |

A workflow imports the **signature**; the limb registers the implementation under the same name; Temporal matches them
at runtime. So the brain never pulls in a limb's dependencies or credentials, and a typo in an activity name is an
import error, not a runtime mystery.

## What happens on a trigger

1. A caller POSTs to a trigger route on `workflows-orchestrator-api`. The API derives a **deterministic workflow id**
   and starts the run on that workflow's queue, answering **202** at once (never waits for the outcome). A duplicate
   trigger while a run with that id is open is refused by the Temporal server → **409**.
2. The brain (polling the workflow queue) runs workflow code until it needs the outside world, then returns a command
   "schedule activity X on queue Y".
3. The limb polling queue Y makes the real call and returns the result, retrying on its own.
4. The result lands in history; the brain continues. Repeats across sleeps of hours or days.
5. Anyone can `GET /workflows/runs/{workflow_id}` — run status plus a Temporal **query** (`progress`) for the live
   `phase` (and per-workflow fields such as `waiting_on`, `waiting_for`, `activity_queue`).

Brain and limbs connect only to the Temporal server. A limb can be redeployed, scaled or crash-loop without touching
workflow logic; queued work waits.

## The routing rule: activity queue per domain, workflow queue per workflow

- **Activity queue = domain**, because what forces a separate deployment is a shared credential/dependency set
  (segment-lifecycle: Segments Manager URL + token and the day1 git push token; server-lifecycle: a Kubernetes client
  with RBAC for BareMetalHosts/Secrets/NMStateConfigs, per-vendor BMC credentials, a server-scan token).
- **Workflow queue = workflow**, so one workflow can be paused (stop polling its queue), isolated on its own worker or
  drained without touching siblings. All workflow code still runs in the one brain deployment.
- Every `execute_activity` passes `task_queue=` explicitly. **Forgetting it sends the activity to the workflow's own
  queue, where nothing can run it** — the run sits with an activity that never starts.
- One activity may deliberately run on **another domain's** queue: install-server reads the MCE's `INVENTORY`
  segment on the segment-lifecycle queue, because that limb already holds the Segments Manager token.

### The per-MCE exception: the queue carries the cluster

The brain runs on the hub, but BareMetalHosts (and upgrade reads/syncs) belong on an MCE's own API server. So the
queue is `server-lifecycle-activity-<mce>` (likewise `cluster-upgrade-activity-<mce>`, `upgrade-agent-activity-<mce>`),
one worker runs **inside each MCE** as its own ServiceAccount and dials out to Temporal, and the brain picks the
target cluster purely by which queue it dispatches to. No cross-cluster kubeconfig exists anywhere and the hub needs
no inbound access to any MCE. The worker's `MCE_CLUSTER` setting builds the queue name, so it must equal what callers
send as `mce_cluster`.

A queue nobody polls is visible: those activities carry a **5-minute schedule-to-start timeout**, history shows
repeated timeouts, and `progress.activity_queue` names the queue (= the MCE to go and look at). This is the documented
exception to Temporal's advice against schedule-to-start timeouts (queues served by specific hosts).

## Design rules that apply to every workflow

1. **The workflow is the entry point** — the caller POSTs the full definition and the workflow creates the thing as
   its first, retried step. (Segments used to be created by the Segments Manager, which then fired a best-effort call
   at the orchestrator: invisible, unretried, silently skipped when the call failed.)
2. **A run may last days.** Waits on a human have **no timeout by design**; durable timers cost nothing and
   `continue_as_new` keeps history bounded. Never "fix" a slow run with a deadline — read its phase first. Waits on
   *machine convergence* do get deadlines and fail loudly by name.
3. **Every activity is idempotent.** Activities retry with **no attempt limit** (1 s, doubling, capped at 1 min), so
   each will run twice: UPSERT, check-before-create, treat "already exists/already done" as success, compare identity
   fields and fail only on genuine disagreement. Within one run finished steps are replayed, not redone; a **new** run
   starts from step 1, so re-running a completed workflow is only as safe as its activities.
4. **No compensating rollback** in the current workflows: a failed run leaves what it did, and a re-run converges.

## Naming: domain or workflow?

Could a sibling workflow in the domain reuse it unchanged? Yes → named after the **domain** (activity queue,
`activities/<domain>/`, `shared/models|interfaces/<domain>.py`, route prefix `/workflows/<domain>`, the Deployment,
ServiceAccount, ConfigMap, Secret). No → named after the **workflow** (`<workflow>-workflow` queue,
`<Workflow>RunArgs/ResumeState/Progress/Result`, route `/<workflow>` under the prefix, workflow ids).
Traps: a domain is a prefix, never an endpoint; **workflow ids must carry the workflow name** (two workflows on one
segment would otherwise collide). Models mirroring an external API keep that API's names (`SegmentEntry`,
`SegmentAllocation` mirror the Segments Manager).

## Deployment and configuration

- Helm charts are **not** in this repo: they are vendored into `redbull-platform` at `gitops/charts/<service>/`, where
  pushing `main` deploys via Argo CD; CI here bumps image tags across repos. (The three cluster-upgrade worker charts
  are still installed by hand from `deploy/charts/`.)
- Global ConfigMap `workflows-orchestrator-config` (`TEMPORAL_*`, `SEGMENTS_MANAGER_URL`); per-domain
  `<domain>-config` + Secret. Settings fail fast at worker start; only limbs hold credentials.
- **Install the brain release before any limb** (limbs mount the global ConfigMap). **Roll limbs out before using a new
  route**: CI ships the brain first, and a brain calling an activity an old limb doesn't register retries until it does.
- Temporary operator pages on the API until the ClickCluster Platform UI exists: `/ui/server-lifecycle`, `/ui/cluster-upgrade`.
  Swagger at `/docs`. The API has no auth of its own (release-segment page).

## Systems the workflows touch

Segments Manager, the DHCP scope API, the day1 values repo (git), Argo CD on each MCE, MCE APIs (Metal3, Agent,
NMState, CAPI, HyperShift), hosted-cluster APIs, server-scan (`knowledge/server-scan/README.md`), Dell OME and iDRACs,
the naming service, site PXE VMs, the release mirror, the upgrade agent service, and "Brain" (the upgrade workflow writes
agent incidents there). Day1/day2 behaviour: `knowledge/gitops/day1-platform-config-values.md`,
`knowledge/gitops/day2-sites-tree-discovery-and-version-layers.md`.

## History

- 2026-11-02: created from the Redbull Workflows docs site v1.0.61 (orchestrator guide + every workflow page)
