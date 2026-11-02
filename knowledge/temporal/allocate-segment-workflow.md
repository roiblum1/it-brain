---
title: allocate-segment workflow — reserve an HC VLAN segment and push vlanId + dhcp_values to the day1 branch ([skip ci]), ClusterValuesConflictError, SegmentPoolExhaustedError, /24 only
type: knowledge
area: temporal
tags: [temporal, redbull-workflows, segment-lifecycle, allocate-segment, segments-manager, day1, dhcp_values, vlanId, dhcp, crossplane, gitlab-ci, generate_mc_files]
applies_to: [hosted-cp]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
teams: [network]
source: Redbull Workflows docs site v1.0.61
---

# allocate-segment

| | |
|---|---|
| Trigger | `POST /workflows/segment-lifecycle/allocate-segment` `{cluster, values_branch, type?}` — 202, 409 if running |
| Workflow id | `allocate-segment-<TYPE>-<cluster>` (type in the id: one segment per type per cluster; **branch not in the id**) |
| Queues | workflow `allocate-segment-workflow`, activity `segment-lifecycle-activity` |
| Writes | Segments Manager allocation; one commit on the **pipeline's branch** of the day1 values repo |
| Caller today | the day1 repo's GitLab pipeline (job `generate_mc_files`), replacing its old in-house VLAN allocator |

Context: `knowledge/gitops/day1-platform-config-values.md` (values files, `dhcp_values`, the push → values flow).
Architecture: `knowledge/temporal/redbull-workflows-orchestrator-architecture.md`.

## Steps and phases

| Phase | Activity | What / why |
|---|---|---|
| `pending` | — | Type gate: only `HC` (else `UnsupportedSegmentType`); no `values_branch` → `ValuesBranchMissing` (no fallback to `main`) |
| `resolving-site` | `get_valid_sites`, `locate_cluster_file` | `ls-remote` the branch, shallow-clone it, require exactly one `sites/<site>/**/<cluster>.yaml`; site = path segment under `sites/`, cross-checked with `GET /api/sites`. **No `site` input** — the repo layout is the source of truth |
| `allocating-segment` | `allocate_segment` | `POST /api/segments/allocate`; idempotent per `(cluster, site, type)`; the pool is shared by all types, type stamped on allocation |
| `verifying-allocation` | `get_segment` | read-back must be `Allocated`, same cluster, VLAN and type — **before** any git write, so the repo never records an unconfirmed VLAN |
| `updating-values-repo` | `append_allocation_to_cluster_values` | fresh clone, append the marker block, commit `[skip ci]`, push to the **same branch, never `main`** |
| `completed` | — | result: segment, VLAN, EPG, branch, `commit_sha` (null on a no-op re-run), `values_updated` |

After the run (not part of it): the pipeline generates MachineConfigs from `vlanId`; a human merges to `main`; Argo CD
(reads `main` only) renders the Crossplane `Request`; Crossplane creates the DHCP scope. The run does **not** wait for
the scope — the merge comes after the pipeline that is waiting on the run (a deadlock, not a slow wait).

## What gets appended to `sites/<site>/mces/<mce>/hostedClusters/<cluster>.yaml`

```yaml
                                   # one blank line, always
# === Added By Segment-Allocation Workflow ===
vlanId: <vlan>                     # audit only — no chart reads it
dhcp_values:
  network: "<network>"             # mask stripped; no start/endRange — the DHCP API derives .1-.253
  exclusions:                      # ascending, required by the DHCP API; omitted if the type's policy excludes nothing
    - startAddress: "<network .1>"
      endAddress: "<network .10>"
    - startAddress: "<network .241>"
      endAddress: "<network .254>"
```

Everything else the DHCP stack needs (`leaseDurationDays`, `dns`, `subnetMask`, `failover`) comes from upstream
values layers; `scopeName` derives from the file name. The one policy knob is `DHCP_EXCLUSION_OCTET_RANGES`, per type in
last-octet values (e.g. `{"HC":[[1,10],[241,254]]}`), validated at worker start (a bad edit crash-loops the pod rather
than mis-rendering a scope). **Only /24 segments**: anything else is `UnsupportedSegmentPrefix` — supporting another
mask needs `subnetMask` and `gateway` emitted too (a code change, not config).

## Re-runs and conflicts

- Re-run after completion converges: same allocation, marker block already records that vlan + network → nothing pushed
  (`values_updated: false`). The comparison is the allocation, not the text, so hand-tuned scope edits survive;
  a later exclusion-policy change is never retrofitted onto an allocated cluster.
- A different allocation under the marker, an unreadable marker block, or a hand-written top-level `dhcp_values`/`vlanId`
  without the marker → `ClusterValuesConflictError` on every run until a human reconciles the file (a duplicate
  top-level YAML key would silently drop the first block).
- A rejected non-fast-forward push retries from a fresh clone and converges (`ValuesRepoGitError` is transient).
- On failure nothing is rolled back: the allocation and any pushed commit stand; a re-run reclaims them.

## Pipeline integration gotchas

- Pipeline: `POST {cluster: <file stem>, values_branch: $CI_COMMIT_BRANCH}` → poll `GET /workflows/runs/{id}` until
  COMPLETED; fail the job on FAILED/CANCELED/TERMINATED printing `error` and the last `progress.phase`; on **409** poll
  `allocate-segment-HC-<cluster>`. Then `git pull --ff-only origin "$CI_COMMIT_BRANCH"` before generating MachineConfigs.
- The pipeline's later push-back job **must expect the workflow's commit**: a plain `git pull` refuses because the same
  file changed — use `--autostash`, or `git fetch` + `git reset --soft FETCH_HEAD` before `git add`.
- The worker pushes to `DAY1_REPO_URL`, the pipeline pulls from its own `origin`: they must be the same repo, and the
  host must accept a token as password with user `x-access-token`. Fix a mismatch in the chart's `config.day1RepoUrl`.
- `[skip ci]` on the workflow's commit prevents a second pipeline re-running the allocator.

## Errors

Permanent (fail the run): `UnsupportedSegmentType`, `ValuesBranchMissing`, `ValuesBranchNotFoundError`,
`ClusterFileNotFoundError`, `AmbiguousClusterFileError`, `UnknownSite`, `SegmentValidationError`,
`SegmentPoolExhaustedError` (503: empty pool — an operator creates segments with initialize-segment, retrying won't
help), `AllocationNotConfirmed`, `ClusterValuesConflictError`, `UnsupportedSegmentPrefix`, `InvalidSegmentCidr`,
`SegmentsManagerAuthError`, `SegmentNotFoundError`. Transient: `ValuesRepoGitError`, Segments Manager outages.

Config: `DHCP_EXCLUSION_OCTET_RANGES`, `DAY1_REPO_URL` (`segment-lifecycle-config`), `DAY1_GIT_TOKEN`
(Secret `day1-git-token`, scrubbed from every git error), `SEGMENTS_MANAGER_URL` / `_API_TOKEN`.

The type check on read-back is skipped only when the payload has no `type` key (history replayed from an older brain,
or a limb one rollout behind — CI ships the brain first); a reported `null` still fails.

## History

- 2026-11-02: created from the allocate-segment page of the Redbull Workflows docs site v1.0.61
