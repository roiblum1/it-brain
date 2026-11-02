---
title: Deploy or upgrade server-scan with Helm and Argo CD (server-scan and nodes-status charts, redbull-platform values, OutOfSync checks)
type: runbook
area: server-scan
tags: [server-scan, helm, argocd, deploy, upgrade, redbull-platform, nodes-status, gitops]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: team-redbull/server-scan@08d284c (deploy/README.md, ADR-0010/0031)
---

# Deploy or upgrade server-scan

**When to use:** a new server-scan release must reach a cluster, a values change (new collector, auth, MCP), or a new
OpenShift cluster needs its `nodes-status` release.
**Impact while running:** API/UI rolling restart (2 replicas recommended); collectors are CronJobs and pick up the new
image on their next schedule.
**Prerequisites:** write access to the GitOps repo (`team-redbull/redbull-platform`), Argo CD access, `helm` locally for
rendering, images mirrored into the air-gapped registry. Background: `knowledge/server-scan/server-scan-deployment-helm-charts-and-gitops.md`.

## Pre-checks

```bash
oc -n <server-scan-ns> get deploy,cronjob,route
oc -n <server-scan-ns> get pods -o wide
# which image tag is running
oc -n <server-scan-ns> get deploy -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.spec.template.spec.containers[0].image}{"\n"}{end}'
```

Read the release notes (commit subjects) between the running and the target version; any `feat!` / `BREAKING CHANGE`
says what an operator must do.

## Procedure

1. **Normal release — nothing to do by hand.** A green push to server-scan `main` publishes the images and CI's deploy
   job bumps the chart copy in `redbull-platform` (templates, files, image tags, `appVersion`); Argo syncs it. Check
   the deploy job is green before assuming the cluster has it.
2. **Values change** — edit only `redbull-platform`'s hand-maintained `values.yaml` for server-scan. For any **new key**
   the release introduced, add it there too (keys missing downstream render as null and Argo goes `OutOfSync`; a missing
   whole block can crash the render).
3. Render locally the way Argo will, before committing:
   ```bash
   helm template server-scan <redbull-platform>/gitops/charts/server-scan -f <redbull-platform values.yaml> > /tmp/render.yaml
   grep -n ': *$' /tmp/render.yaml | head      # bare "KEY:" lines in ConfigMaps are dropped keys
   ```
4. Commit to `redbull-platform` through its normal MR; Argo syncs.
5. **New cluster — nodes-status:** add an Argo Application pointing at the `nodes-status` chart with
   `nodes.enabled: true`, `nodes.clusterName: <cluster>` (and on an MCE hub also `agents.enabled: true`,
   `agents.mceName: <mce>`), `db.dbName` equal to the platform's, the Mongo URI Secret, and optionally `nodes.ssh.*`
   for serial fallback.
6. **Enabling a collector:** set `collectors.<vendor>.enabled: true`, its endpoint, and credentials via
   `collectors.existingSecret`; the API pod mounts the same Secret for live rechecks. Standalone Redfish needs its
   inventory TOML (ConfigMap) and stays `suspend: true` until verified.

## Verification

```bash
oc -n <server-scan-ns> rollout status deploy/<release>-api
curl -sS -o /dev/null -w '%{http_code}\n' https://<server-scan-host>/health/ready
oc -n <server-scan-ns> get jobs --sort-by=.metadata.creationTimestamp | tail     # next collector runs succeed
```

Argo shows the app `Synced` and stays so (a sync loop every few minutes = dropped ConfigMap key). On a cluster with a
new `nodes-status` release, `server_scan_cluster_last_reported_timestamp_seconds` for it appears within 15 min.

## Rollback

Revert the `redbull-platform` commit (image tag / values) and let Argo sync. Data in MongoDB is not migrated by
releases in a way that needs rollback, but check the release notes for a stored-field change before downgrading.

## History

- 2026-11-02: created
