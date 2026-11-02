# Area `temporal`

Temporal: the server on the hub and the Redbull Workflows orchestrator built on it (segment, server, provisioning and upgrade workflows, task queues, workers).

- **Owner (approves MRs):** OpenShift Container Platform team (`ocp`)
- **Consulted:** —

## Belongs here

The Temporal server on the hub (namespaces, UI, upgrades, persistence); the Redbull Workflows orchestrator
(`team-redbull/workflows`): its architecture, task queues and workers, every workflow's behaviour, failure modes and
operating procedures; Temporal Python SDK lessons.

## Not here

What the workflows act on has its own area: Metal3 / Agent / BareMetalHost behaviour → `baremetal`; HostedCluster,
NodePool, CAPI → `hypershift`; day1 / day2 / Argo CD → `gitops`; the inventory → `server-scan`; segments, VLANs and EPGs
seen from the fabric → `cisco-aci`. Prefect → `prefect`; Airflow → `airflow`.

## Offline sources

Temporal's own docs are not snapshotted yet (candidate: `temporalio/documentation`; the Python SDK `temporalio/sdk-python`).
The Redbull Workflows docs site (`<workflows-docs-url>`, an internal site — never write its real host) is the source of the
pages below; the workflows repo's `CLAUDE.md` is its authoritative rule set. Status: `docs/it-brain/SOURCES-PLAN.md`.

## Redact

Use `<cluster>`, `<mce>`, `<site>`, `<region>`, `<subnet>` / `<network>`, `<vlan>`, `<epg>`, `<idrac-ip>`, `<service-tag>`,
`<server>`, `<infra-env>`, `<task-queue>`, `<namespace>`. Example payloads in the docs carry real-looking cluster, MCE,
site, region and serial names and IP addresses: never copy them. Never paste a Temporal history containing tokens.

## Pages

| Page | What |
|---|---|
| `knowledge/temporal/redbull-workflows-orchestrator-architecture.md` | brain / limbs / contract, routing, per-MCE queues, ids, catalogue, deployment — **start here** |
| `knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md` | SDK gotchas: stuck RUNNING, ApplicationError, non-retryable, sandbox, converter, determinism |
| `knowledge/temporal/initialize-segment-workflow.md` | create a segment in the Segments Manager |
| `knowledge/temporal/allocate-segment-workflow.md` | reserve an HC VLAN and write `dhcp_values` to the day1 branch |
| `knowledge/temporal/release-segment-workflow.md` | give the VLAN back after decommission (PostDelete hook) |
| `knowledge/temporal/install-server-workflow.md` | server-scan → BareMetalHost + NMStateConfig → Agent, with rollback |
| `knowledge/temporal/uninstall-server-workflow.md` | out of the hosted cluster and the MCE; HyperShift leftovers |
| `knowledge/temporal/provision-dell-server-workflow.md` | racked Dell → OME template, RAID, name |
| `knowledge/temporal/upgrade-cluster-workflow.md` | HostedCluster upgrade via day1 + Argo CD (sandbox only so far) |
| `runbooks/temporal/start-watch-and-steer-a-redbull-workflow-run.md` | trigger, poll, decide, cancel |
| `runbooks/temporal/diagnose-a-workflow-run-stuck-in-running.md` | symptom → cause for a run that doesn't move |
| `runbooks/temporal/add-a-workflow-or-domain-to-the-orchestrator.md` | development recipe |
| `runbooks/temporal/deploy-server-lifecycle-worker-on-an-mce.md` | the per-MCE limb: config, credentials, RBAC |

## First pages we want

- The Temporal server itself: where it runs on the hub, persistence, namespace(s), UI access, upgrade procedure.
- A verified run of each workflow on our clusters, to raise these pages from `observed` to `verified`.

Write pages from `templates/` and the frontmatter in `docs/FRONTMATTER.md`; this README is the area's charter, not a knowledge page.
