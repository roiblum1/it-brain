---
title: it-brain offline sources plan — vendor docs for storage, network and virtualization (repos, paths, licences, status)
type: reference
area: meta
tags: [it-brain, sources, team-knowledge, snapshots, vendor-docs, licence]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: it-brain-design
---

# it-brain offline sources plan

How sources work today: `knowledge/meta/doc-sources-catalog.md` and `mcp/README.md`. Architecture: `docs/it-brain/ARCHITECTURE.md` §3.3.

**Checked on 2026-11-02** from a connected host: every repo below exists (`git ls-remote`), its docs live at the
listed path (tree listing of the default branch), and its licence file says what the *Licence* column says. Nothing
here is fetched or enabled yet. That is why this page is `observed`: repo facts are checked, fit for our versions is not.

## A. Docs-only snapshots (public git → `docs/upstream/<name>`)

To add one: put the row's repo and paths into `SOURCES` in `scripts/sync-ecosystem-docs.py`, run it on a connected
host, add the `markdown_dir` entry to **both** `mcp/sources.json` and `deploy/openshift/shared-sources.json`, a row in
`knowledge/meta/doc-sources-catalog.md`, and a golden query if a page must stay findable. CI (`sources`, `parity`,
`upstream`) then checks it.

| Proposed name | Area(s) | Repo | Paths to keep | Format | Licence | Notes |
|---|---|---|---|---|---|---|
| `trident-docs` | trident | `NetAppDocs/trident` | whole repo (`trident-*` folders, `troubleshooting.adoc`, `known-issues.adoc`, `trident-rn.adoc`) | AsciiDoc | no licence file — NetApp's docs; internal use only | latest release only; older releases are on NetApp's site |
| `ontap-docs` | netapp-ontap, smb-cifs | `NetAppDocs/ontap` | start with `nfs-*`, `smb-*`, `san-*`, `s3-*`, `networking`, `network-management`, `volumes`, `snapmirror-active-sync`, `data-protection`, `upgrade`, `error-messages`, `release-notes` | AsciiDoc | no licence file — internal use only | very large; select folders to keep search quality |
| `ontap-mcp-docs` | netapp-ontap, meta | `NetApp/ontap-mcp` | `docs`, `README.md` | Markdown | Apache-2.0 | needed before vendoring the server (`docs/it-brain/TOOLS-PLAN.md`) |
| `dell-csm-docs` | dell-powermax, dell-powerflex, dell-powerscale | `dell/csm-docs` | `content/docs` (latest); `content/v1..v3` are older versions | Markdown (Hugo) | no licence file found at top level — check before sharing | includes the support matrix per driver |
| `ceph-docs` | ceph, odf | `ceph/ceph` | `doc/radosgw`, `doc/rados`, `doc/rbd`, `doc/cephfs`, `doc/cephadm`, `doc/mgr`, `doc/security` | reStructuredText | CC-BY-SA-3.0 (`doc/*` in `COPYING`) | pin `REF_ceph_docs=<release tag>` to the release we run |
| `rook-docs` | odf | `rook/rook` | `Documentation` | Markdown | Apache-2.0 | ODF ships Red Hat's build — RHOKP wins |
| `ocs-operator-docs` | odf | `red-hat-storage/ocs-operator` | `docs` | Markdown | Apache-2.0 | developer docs; product docs are in RHOKP |
| `velero-docs` | oadp | `vmware-tanzu/velero` | `site/content/docs/<version>` | Markdown | Apache-2.0 | docs are one folder per Velero version: keep the ones matching our OADP releases' Velero |
| `oadp-operator-docs` | oadp | `openshift/oadp-operator` (default branch `oadp-dev`) | `docs`, `README.md` | Markdown | Apache-2.0 | troubleshooting, credentials, API reference; product docs in RHOKP |
| `csi-driver-smb` | smb-cifs | `kubernetes-csi/csi-driver-smb` | `docs`, `README.md`, `known-issues.md` | Markdown | Apache-2.0 | only if we use the upstream SMB CSI driver |
| `vsphere-csi-driver` | vsphere, vmware | `kubernetes-sigs/vsphere-csi-driver` | `docs` | Markdown | Apache-2.0 | OCP ships its own build; check against RHOKP |
| `nutanix-csi` | nutanix | `nutanix/csi-plugin` | whole repo (small) | Markdown | MIT | |
| `aci-containers` | cisco-aci | `noironetworks/aci-containers` | `README.md`, `docs` if present | Markdown | Apache-2.0 | **only if** a cluster uses the ACI CNI |
| `pan-dev` | palo-alto | `PaloAltoNetworks/pan.dev` | `products/panos`, `products/terraform`, `products/ansible` (API, automation) | Markdown/MDX | MIT | developer/API docs, not the admin guide |

**Workflow and data platforms** (checked the same way on 2026-11-02):

| Proposed name | Area(s) | Repo | Paths to keep | Format | Licence | Notes |
|---|---|---|---|---|---|---|
| `temporal-docs` | temporal | `temporalio/documentation` | `docs/encyclopedia`, `docs/develop`, `docs/production-deployment`, `docs/troubleshooting`, `docs/best-practices`, `docs/cli`, `docs/references` | Markdown/MDX | MIT | the Temporal concepts and SDK rules the Redbull Workflows orchestrator depends on |
| `temporal-helm` | temporal | `temporalio/helm-charts` | `README.md`, `UPGRADING.md`, `charts` READMEs | Markdown | MIT | server deployment and upgrades on the hub |
| `prefect-docs` | prefect | `PrefectHQ/prefect` | `docs/v3` | Markdown/MDX | Apache-2.0 | |
| `prefect-helm` | prefect | `PrefectHQ/prefect-helm` | `README.md`, `charts` | Markdown | Apache-2.0 | server and worker charts |
| `airflow-docs` | airflow | `apache/airflow` | `airflow-core/docs`, `chart/docs` | reStructuredText | Apache-2.0 | core docs + the official Helm chart docs |
| `spark-docs` | spark | `apache/spark` (default branch `master`) | `docs` | Markdown | Apache-2.0 | pin `REF_spark_docs=v<version>` to the Spark we run (`running-on-kubernetes.md` is the key page) |
| `spark-operator-docs` | spark | `kubeflow/spark-operator` (default `master`) | `docs`, `README.md`, `examples` | Markdown | Apache-2.0 | |
| `eck-docs` | elastic | `elastic/docs-content` | `deploy-manage/deploy/cloud-on-k8s`, `deploy-manage/deploy/self-managed`, `troubleshoot` | Markdown | CC BY-NC-ND 4.0 — internal use, unmodified | ECK and self-managed (VM) Elasticsearch docs moved here |
| `eck-reference` | elastic | `elastic/cloud-on-k8s` | `docs/reference`, `docs/release-notes` | Markdown | Elastic License 2.0 | CRD reference and release notes |
| `solr-ref-guide` | solr | `apache/solr` | `solr/solr-ref-guide/modules` | AsciiDoc (Antora) | Apache-2.0 | pin to our Solr major |
| `solr-operator-docs` | solr | `apache/solr-operator` | `docs`, `README.md` | AsciiDoc/Markdown | Apache-2.0 | |
| `mongodb-kubernetes-docs` | mongodb | `mongodb/mongodb-kubernetes` (default `master`) | `docs`, `README.md`, `RELEASE_NOTES.md` | Markdown | Apache-2.0 (+ `LICENSE-MCK` — read it) | replaces the **deprecated** `mongodb/mongodb-kubernetes-operator` (its README says so) |
| `mongodb-manual` | mongodb | `mongodb/docs` | `content/manual` (replication, sharding, backup, upgrade sections), `content/kubernetes` | reStructuredText | no top-level licence file — internal use only | very large; select sections |

Optional full git mirror (code at any tag): `NetApp/trident` (default branch `master`) — useful when Trident
behaviour has to be read from the code, like HyperShift today.

## B. Red Hat products (already in RHOKP)

ODF, OADP, OpenShift on vSphere and on Nutanix, the vSphere CSI driver as shipped in OCP: use `rhokp` with
`version: "4.NN"`. RHOKP wins over the upstream snapshots above where they disagree.

## C. Vendor-drop (licensed docs, never committed)

No public git source; manuals come from the vendor portal and are usually licensed to the organisation, not for
redistribution. Convention (`docs/it-brain/ARCHITECTURE.md` §3.3):

```
${IT_BRAIN_VENDOR_DOCS:-~/.cache/it-brain/vendor-docs}/<name>/   ← Markdown converted from PDF/HTML, plus a SOURCE.txt
                                                                    (title, version, date fetched, who fetched)
```

and a `markdown_dir` source with `"root": "${IT_BRAIN_VENDOR_DOCS:-~/.cache/it-brain/vendor-docs}/<name>"`,
`enabled: false` until the folder exists on the shared server. Candidates, with the version to fetch decided by
the owning team:

| Name | Area | What to fetch |
|---|---|---|
| `commvault-docs` | commvault | Kubernetes / OpenShift protection, storage policies / plans, media agent sizing, troubleshooting |
| `panos-admin` | palo-alto | PAN-OS administrator's guide, Panorama admin guide, CLI quick start, upgrade guide (our major.minor) |
| `apic-guides` | cisco-aci | APIC basic / layer 2 / layer 3 configuration guides, troubleshooting guide, upgrade guide (our release) |
| `powermax-docs` | dell-powermax | Unisphere for PowerMax REST API and product guide, host connectivity guide for Linux |
| `powerflex-docs` | dell-powerflex | PowerFlex deployment and admin guides (SDC on Linux) |
| `onefs-docs` | dell-powerscale | OneFS web admin, CLI and API reference for our OneFS version |
| `ontap-kb` | netapp-ontap | selected NetApp KB articles we rely on (only the ones cited by brain pages) |
| `vmware-docs` | vmware | vSphere / vSAN / NSX docs for our versions |
| `nutanix-docs` | nutanix | AOS / Prism / Files / Objects guides for our versions |

**Licence gate:** before a vendor-drop goes onto the shared server, the owning team confirms the licence allows
internal offline copies. Record the decision in `knowledge/meta/doc-sources-catalog.md`.

## D. Our own repos

| Name | Area | Kind | Status |
|---|---|---|---|
| `server-scan` | server-scan | `git_repo` full mirror of `team-redbull/server-scan` (public GitHub; mirrored into GitLab under `$GIT_MIRROR_BASE`) | entry added to `mcp/sources.json`, **disabled** until the mirror exists — `knowledge/server-scan/README.md` |
| `redbull-workflows-docs` | temporal | the orchestrator's docs site (`<workflows-docs-url>`, a static site, served from the cluster) | read once on 2026-11-02 and turned into `knowledge/temporal/` pages; the site's source repo should become a `git_repo` source when we know its remote |

Later:

Each team's automation repos (array provisioning, ACI / firewall as code, Ansible) become `git_repo` sources the way
`gitops-day1-platform-config` is today — disabled until the real GitLab remotes are set.

## History

- 2026-11-02: created; repos, paths and licences checked from a connected host
