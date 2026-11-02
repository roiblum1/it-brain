---
title: Offline doc sources catalog — what each team-knowledge source is authoritative for and which ref to use
type: knowledge
area: meta
tags: [sources, team-knowledge, refs, catalog]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [platform-team]
source: claude-session
---

# Offline doc sources catalog

Config: `mcp/sources.json` (per engineer) and `deploy/openshift/shared-sources.json` (shared server).
Version → ref rules: `knowledge/meta/fleet-versions.md`. **When Red Hat's downstream docs (RHOKP) and an
upstream source disagree, RHOKP/KCS wins for what we run**; upstream tells you how it works internally.

| Source | Area | Good for | Ref to use |
|---|---|---|---|
| `rhokp` | all | OCP/ACM/MCE docs, KCS, CVEs, errata | filter `version: "4.NN"` |
| `hypershift`, `cluster-api` | hypershift | HostedCluster/NodePool/CAPI behaviour and code | `release-4.NN` / CAPI tag from go.mod |
| `cluster-api-provider-agent`, `cluster-api-provider-metal3`, `baremetal-operator`, `metal3-docs`, `ip-address-manager`, `ironic-standalone-operator`, `ironic-image`, `ironic` | baremetal | Agent/Metal3 machines, BareMetalHost API and states, BMC drivers, Metal3 IPAM, Ironic image settings. `metal3-docs` is the complete source of book.metal3.io (`docs/user-guide/src`, start at `SUMMARY.md`); the API references the book links to live in each component's `docs/api.md` | tag matching OCP's baremetal components; `main` for concepts |
| `assisted-service` | baremetal | Agent-based installs, InfraEnv/Agent CRs | `release-ocm-*` / tag of the installed MCE |
| `ako` | networking | our L4/L7 load balancing and ingress (**not MetalLB** — see `knowledge/networking/ingress-load-balancing-is-ako-not-metallb.md`) | tag = AKO version installed on the cluster |
| `envoy`, `envoy-gateway`, `gateway-api` | networking | proxy config, Gateway API semantics, CRD fields | Envoy `release/v1.NN` as used by the product; Gateway API tag = installed CRD bundle |
| `envoy-ai-gateway`, `gateway-api-inference-extension` | networking / ai | LLM traffic through Envoy: AIGatewayRoute, AIServiceBackend, provider/model routing, token rate limits, MCP gateway; InferencePool and the endpoint picker (shared with `llm-d`) | snapshot of `main`; compare with the installed release in `docs/upstream/VERSIONS.md` |
| `ovn-kubernetes`, `multus-cni` | networking | default CNI behaviour, secondary networks | match OCP minor where a release branch exists |
| `kserve`, `kserve-website` | gpu / ai | `kserve-website` = the live site's `/docs/next/` (latest; all 147 pages checked against its sitemap on 2026-10-03, incl. LLMInferenceService and the CRD API reference). `kserve` = repo docs plus the sample manifests and code under `docs/samples`. InferenceService/ServingRuntime APIs. RHOAI ships its own build — verify against RHOKP | tag of KServe in the installed RHOAI/ODH |
| `vllm` | gpu / ai | serving flags, quantization, parallelism, engine code | tag = vLLM version in the serving image |
| `lmcache`, `mooncake` | gpu / ai | KV-cache reuse for vLLM: LMCache = cache layer (CPU/disk/remote offload, sharing across replicas, configuration, operator samples, example configs and scripts); Mooncake = the RDMA transfer engine and distributed store it can use as a backend | snapshot of the default branch (LMCache `dev`, Mooncake `main`); pin with `REF_<name>=<tag>` to the version in the serving image |
| `lws`, `kueue` | gpu / ai | multi-node inference (LeaderWorkerSet), quotas/queueing | tag = installed operator version |
| `gpu-operator`, `node-feature-discovery` | gpu | ClusterPolicy, drivers, MIG, NFD labels | tag = installed operator version |
| `prometheus-docs`, `prometheus-operator` | observability | PromQL, alerting, ServiceMonitor/PrometheusRule | OCP bundles its own build; docs are general |
| `openshift-runbooks` | observability | per-alert runbooks (check first when an alert fires) | `master` (runbooks are not versioned per minor) |
| `kubernetes-mcp-server`, `okp-mcp` | meta | the MCP servers themselves: flags, config, tool behaviour (`mcp/servers/kubernetes.md`, `mcp/servers/okp-mcp.md`) | snapshot; the vendored binary's version is in `plugins/team-brain/mcp-servers/vendor/manifest.json` |
| `grafana-docs`, `mcp-grafana` | observability | dashboards, datasources, provisioning; MCP tool names and flags | tag = Grafana / mcp-grafana version we run |
| `llm-d`, `sglang`, `tensorrt-llm`, `dynamo`, `ray-docs` | gpu / ai | distributed inference stacks beyond vLLM: prefill/decode disaggregation, wide-EP, routing, KubeRay | snapshot; match the image version we deploy |
| `nccl`, `ucx`, `rdma-core` | gpu / networking | collectives env vars and tuning, RDMA/UCX transports, InfiniBand/RoCE userspace | snapshot |
| `nvidia-cloud-native-docs`, `nvidia-network-operator-docs`, `sriov-network-operator` | gpu / networking | GPU Operator (OpenShift), MIG, DCGM; NicClusterPolicy/MOFED/RDMA device plugin; SR-IOV policies | snapshot; operator versions come from the cluster |
| `tuned`, `linux-kernel-docs` | gpu / openshift | kernel and OS tuning: hugepages, NUMA, CPU topology, IRQ affinity, sysctl — **kernel docs are upstream master, not the RHCOS kernel**; OCP applies tuning via the Node Tuning Operator (RHOKP) | snapshot |
| `portworx-docs` | storage | Portworx install, upgrades, storage classes, DR. Pinned mirror of the **latest** docs (3.7 at last sync) in `docs/upstream/portworx`, no public repo — refresh with `scripts/sync-portworx-docs.py` | latest only; check older installs against the support matrix |
| `etcd-docs` | openshift | etcd defrag, backup/restore, tuning (OCP wraps etcd with its own operator) | general |
| `kubernetes-docs` | kubernetes | Kubernetes concepts and APIs | pinned 1.35 only (see fleet-versions) |
| `argocd-docs`, `argo-cd` | gitops | Argo CD docs / source | `stable` docs; tag of installed Argo CD for source |
| `gitops-day1-platform-config`, `gitops-day2-prod`, `cluster-navigator` | gitops | our own repos: day1 values/versions, day2 ARCHITECTURE.md and charts, Navigator. **Disabled until the real GitLab remotes are set** (`GITOPS_DAY1_REMOTE`, `GITOPS_DAY2_REMOTE`, `NAVIGATOR_REMOTE`) | `main`; version of a cluster = day1 `mastertag` |
| `brain` | all | **our** quirks, runbooks, incidents — read first | — |
| *planned (it-brain)* | storage, network, virtualization, workflow, data | NetApp / Trident, Dell CSM, Ceph, Rook / ODF, Velero / OADP, SMB CSI, ACI CNI, Palo Alto pan.dev, vSphere / Nutanix CSI, Temporal, Prefect, Airflow, Spark, ECK, Solr, MongoDB docs; our `server-scan` repo; licensed vendor manuals as *vendor-drop*. Not enabled yet — repos, paths, licences and status in `docs/it-brain/SOURCES-PLAN.md` | — |

What each snapshot actually is (repo, ref, commit, newest upstream release at sync time): `docs/upstream/VERSIONS.md`
(generated). Snapshots are refreshed automatically on GitHub — see `README.md`, "Automatic doc refresh".

**Full git mirrors (code + docs at any ref):** `hypershift`, `ironic`, `cluster-api`, `cluster-api-provider-agent`,
`argo-cd` (optional). **Every other source is a docs-only snapshot** in `docs/upstream/<name>` (default branch unless
pinned with `REF_<name>`), so the "Ref to use" column above applies only to the full mirrors; for snapshots, check the
doc against the version actually installed (and prefer RHOKP for Red Hat's builds).

## Coverage audit (2026-10-03)

Every snapshot was compared with all doc files of its upstream repo. Metal3 was the test case: all 76 pages of
the book are in `metal3-docs`; what was missing were the component repos the book links out to. Added then:
Metal3 IPAM, IrSO and ironic-image; READMEs of BMO/CAPM3; rdma-core man pages (`infiniband-diags`, libibverbs,
librdmacm, mlx5); NVIDIA Container Toolkit and driver containers; Kueue and LWS KEPs; vLLM example READMEs; AKO
changelogs and operator READMEs; KServe chart READMEs.

Left out on purpose — don't "fix" these without a reason:

- `vendor/**`, release notes, changelog fragments, `.github`, contributor/agent files, translations, blogs.
- Older versioned copies of a site (Envoy Gateway `v0.x`–`v1.x`, KServe website `versioned_docs`): the snapshot
  is `latest` only. For an older install re-sync with `REF_<name>=<tag>`.
- Generated references that exist upstream only as code: Envoy's v3 API reference (`api/envoy/**/*.proto`),
  Gateway API and KServe Go types. If a field-level question can't be answered from the docs, that is why.
- Images and diagrams (text only), and anything a site renders from another repo at build time.
- Linux kernel docs: a hand-picked subset (mm, scheduler, IRQ, networking sysctl, InfiniBand), not the tree.

To re-run the audit after upstream moves: list `git ls-tree -r --name-only HEAD` of a blobless clone, keep
`.md/.rst/.adoc/.mdx`, and compare with the paths in `scripts/sync-ecosystem-docs.py`.

## Gotchas when mixing sources

- Upstream default branches are ahead of what we run. Say which ref your claim comes from.
- Operators on OCP (monitoring, ingress, CNI) are managed by CVO — upstream flags often can't be set directly.
  Check RHOKP for the supported way before suggesting a change.
- Repo names, default branches and doc globs were verified against GitHub on 2026-10-03. Upstream layouts drift
  (e.g. Gateway API docs moved to `site/content`); if a source returns nothing, check `list_sources` doc counts,
  fix the globs, and record the fix here.

## History

- 2026-10-03: created with the initial source set.
- 2026-10-03: coverage audit against upstream repos; added three Metal3 component sources and widened eight snapshots.
- 2026-10-03: added Envoy AI Gateway and Gateway API Inference Extension; snapshots now refresh automatically.
- 2026-10-03: KServe snapshots now include example manifests/code (`.yaml`, `.py`); website verified against the site's sitemap.
