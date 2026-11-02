---
title: HyperShift KubeVirt platform — hosted clusters whose worker nodes are KubeVirt VMs on the management (or an external infra) cluster — storage (RWX Block, KubeVirt CSI), networking (NAD in the HCP namespace), ingress (baseDomainPassthrough), troubleshooting
type: knowledge
area: kubevirt
teams: [ocp]
tags: [kubevirt, hypershift, hosted-cluster, nodepool, kubevirt-platform, kubevirt-csi, hcp, external-infrastructure, basedomainpassthrough, ingress, nad, etcd]
applies_to: []
confidence: observed
last_verified: 2026-11-02
owners: [virtualization]
source: openshift/hypershift docs/content/how-to/kubevirt/{create-kubevirt-cluster,configuring-storage,configuring-network,external-infrastructure,ingress-and-dns,troubleshooting-kubevirt-cluster}.md
---

# HyperShift on KubeVirt (hosted clusters on VMs)

We run HyperShift with bare-metal (Agent) workers (`knowledge/openshift/fleet-topology-hub-mce-hosted.md`). HyperShift
also has a **KubeVirt platform**: the hosted cluster's control plane runs as pods in the HCP namespace (as usual) and
its **worker nodes are KubeVirt VMs** created by the NodePool on the management cluster — or on a separate
**infrastructure cluster** ("external infrastructure", `--infra-kubeconfig-file`, `--infra-namespace`). Whether we use or
plan this is an open question (`knowledge/kubevirt/README.md`).

## Requirements (from the HyperShift docs)

- Management cluster with OpenShift Virtualization, **OVN-Kubernetes** default CNI, a default StorageClass,
  **LoadBalancer Service support** (the docs say MetalLB — in our environment that is **AKO**,
  `knowledge/networking/ingress-load-balancing-is-ako-not-metallb.md`), and wildcard routes allowed on the default
  IngressController (`routeAdmission.wildcardPolicy: WildcardsAllowed`) for the default ingress mode.
- MTU **9000 or more** recommended on the cluster hosting the VMs (works with less, slower).
- External infra: the infra kubeconfig user needs full rights on `virtualmachines`, `virtualmachineinstances`,
  `virtualmachines/finalizers`, `datavolumes` (and more listed in the doc) in the infra namespace — not cluster-admin.

## Storage — three different needs

| What | Needs | Note |
|---|---|---|
| etcd of the hosted control plane | fast storage on the management cluster | local storage (LVM Storage) preferred; HA etcd replicates across 3 nodes |
| VM root volumes (worker disks) | **RWX + Block** recommended | lets worker VMs live-migrate when infra nodes are drained |
| Guest PVCs via **KubeVirt CSI** | maps infra StorageClasses into the guest | infra RWX Block → guest RWO (Block/FS) and RWX Block, migration OK; infra RWO → guest RWO only, no live migration |

Which of our backends give RWX Block: `knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md`.

## Networking

Worker VMs sit on the pod network by default; extra networks via `--additional-network name:<namespace>/<nad>`. The
**NAD must live in the HCP namespace** (`<hc-namespace>-<hc-name>`, dots → hyphens), where virt-launcher pods run — not
the HostedCluster namespace; Multus namespace isolation (OpenShift default) rejects it otherwise.

## Ingress

The guest's default IngressController uses `NodePortService`. **`baseDomainPassthrough`** (auto-enabled when no
`baseDomain` is given; **immutable** after creation) makes HyperShift create a wildcard passthrough Route on the
management cluster plus a selector-less Service with EndpointSlices pointing at the VMs' machine-network IPs. With a
custom `baseDomain` you build the LoadBalancer Service yourself — with **no pod selector** (a `kubevirt.io: virt-launcher`
selector resolves to pod IPs, while the guest router listens on VM IPs) — and the wildcard DNS for
`*.apps.<cluster>.<baseDomain>`. Guest LoadBalancer Services are served by the kubevirt-cloud-controller-manager in the
HCP namespace.

## Troubleshooting order

HostedCluster/NodePool conditions → `oc get vm -n <hcp-namespace>` → stuck provisioning: CDI importer pods → stuck
starting: virt-launcher pods → running but not a node: VNC/console to check Ignition, `guest-console-log` container
logs → guest `oc get co`/nodes. PVC problems in the guest: kubevirt-csi-node (guest) and kubevirt-csi-controller (HCP
namespace) logs.

## Scope & caveats

HyperShift docs on `main` (2026-11): prerequisites say OCP and OpenShift Virtualization 4.14+. Read the HyperShift
mirror at our `release-4.NN` ref (`knowledge/meta/fleet-versions.md`) for the exact behaviour per minor.

## History

- 2026-11-02: created
