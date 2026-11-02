---
title: Fleet version map — which OCP minor runs which Kubernetes, HyperShift ref and component versions
type: knowledge
area: meta
tags: [versions, fleet, refs, ocp, kubernetes]
applies_to: [ocp-4.16, ocp-4.20, ocp-4.22]
confidence: observed
last_verified: 2026-11-02
owners: [platform-team]
source: claude-session
---

# Fleet version map

**This is the one place versions live.** Every other page and skill points here instead of hard-coding
a version. When the fleet moves (e.g. to 4.24), add a row and an `applies_to` token — nothing else changes.

## Versions in the fleet

| OCP minor | Kubernetes | HyperShift ref | MCE | CAPI | Notes |
|---|---|---|---|---|---|
| 4.16 | 1.29 | `release-4.16` | look up | look up | oldest in fleet |
| 4.20 | 1.33 | `release-4.20` | look up | look up | |
| 4.22 | 1.35 | `release-4.22` | look up | look up | newest in fleet; matches pinned `docs/upstream/kubernetes` |

"look up" = not recorded yet; don't guess. Find it, then fill the cell (bump `last_verified`):

- MCE for a hub: `oc get multiclusterengine -o jsonpath='{.items[0].status.currentVersion}'`
- CAPI vendored in a HyperShift branch: `search_code repo=hypershift ref=release-4.NN path="go.mod" pattern="sigs.k8s.io/cluster-api "`
- Kubernetes for a cluster: `oc version` (Server Version → Kubernetes Version)

## Upgrade ladder (day1 `upgrade/ladder.yaml`, used by the upgrade-cluster workflow)

Read from the Redbull Workflows docs on 2026-11-02 (`knowledge/temporal/upgrade-cluster-workflow.md`); the workflow
itself has only run on a sandbox fleet — **observed, not verified on our clusters**.

| Rung | Kind | Note |
|---|---|---|
| 4.15.41 → 4.16.55 → 4.17.58 → 4.18.56 → 4.19.53 → 4.20.44 → 4.21.40 | all `must` | checked against Red Hat's update graph on 2026-10-31 |
| 4.21 → 4.22 | — | **no rung**: those edges are only in `candidate-4.22`, so 4.22 clusters can only take 4.22 z-streams through the workflow |

- `maxWorkerSkew: 2` (HyperShift itself allows 3).
- Admin-ack gate `ack-4.19-admissionregistration-v1beta1-api-removals-in-4.20` applies from 4.19.15.
- Sandbox MCE in the docs' examples: 2.17.3 (not a fleet fact).

## How to pick a ref (applies to every `git_repo` source)

1. Identify the cluster's OCP minor, then use this table.
2. `list_refs` with a filter to confirm the ref exists in the mirror (`release-4.22`, `v1.9`).
3. Pass `ref` on `search`, `search_code`, `find_definition`, `read_code`. Never rely on `main` for a
   specific cluster — it describes the future.
4. For add-ons that are **not** versioned with OCP (AKO, KServe/RHOAI, Portworx, GPU operator, Gateway API CRDs,
   vLLM image), read the installed version from the cluster and use the matching tag. See
   `knowledge/meta/doc-sources-catalog.md` for where each one's version comes from.

## Kubernetes docs mirror is 1.35 only

`docs/upstream/kubernetes` is a single mirror at the newest fleet version. For 4.16 (1.29) and 4.20 (1.33)
clusters, a feature described there may be alpha/beta, behind a feature gate, or absent. Check the page's
"feature state" banner against the table above before advising a change.

## Writing version-generic pages

- State ranges, not "current": "since 4.18", "up to 4.20", "all fleet versions".
- Put the same range in `applies_to` (`ocp-4.16`, `ocp-4.20`, …). `[]` means genuinely version-independent.
- If behaviour differs per version, use a small table in the page, not separate pages.

## History

- 2026-10-03: created (fleet = 4.16 / 4.20 / 4.22; Kubernetes mapping as stated by the platform team).
