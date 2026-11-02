# Area `kubevirt`

KubeVirt / OpenShift Virtualization: virtual machines on OpenShift — virt components, VM lifecycle, CDI and
DataVolumes, VM networking, live migration, scheduling and performance, migration from VMware (MTV), backup,
debugging, upgrades.

- **Owner (approves MRs):** Virtualization team (`virtualization`)
- **Consulted:** `ocp`, `storage`, `network`
- **Domain:** hypervisors (`virtualization`)

Red Hat ships KubeVirt as **OpenShift Virtualization** (operator namespace usually `openshift-cnv`, the
HyperConverged CR `kubevirt-hyperconverged`). Upstream names are used in these pages because the offline sources are
upstream; where Red Hat's build differs, **RHOKP wins** (filter by the OCP minor — check RHOKP for the CNV version).

## Map of this area

| Page | What it answers |
|---|---|
| `knowledge/kubevirt/kubevirt-architecture-components-virt-launcher-hco-cdi.md` | what runs where: virt-operator/api/controller/handler/launcher, virtqemud, VM vs VMI vs VMIM, HCO and the operators it owns, CDI |
| `knowledge/kubevirt/kubevirt-vm-lifecycle-runstrategy-printablestatus.md` | runStrategy values, every `printableStatus` and what it means when troubleshooting |
| `knowledge/kubevirt/kubevirt-storage-datavolumes-storageprofiles-clone-per-backend.md` | DataVolumes, StorageProfiles, clone strategies, Block vs Filesystem, RWX, overhead, per-backend (Trident, Dell, ODF, Portworx) |
| `knowledge/kubevirt/kubevirt-networking-masquerade-bridge-multus-localnet-sriov.md` | pod network bindings, Multus, Linux bridge, OVN-K localnet/layer2, SR-IOV, MAC pool, MTU |
| `knowledge/kubevirt/kubevirt-live-migration-requirements-limits-policies-failures.md` | what makes a VM migratable, limits/timeouts, MigrationPolicies, post-copy, reading VMIM status |
| `knowledge/kubevirt/kubevirt-node-drain-eviction-strategy-and-pdbs.md` | evictionStrategy, the eviction webhook, PDBs, why drains (and MCO rollouts) block |
| `knowledge/kubevirt/kubevirt-upgrades-hco-workload-updates-outdated-launchers.md` | control-plane updates, workload updates, outdated virt-launcher pods, OCP node upgrades with VMs |
| `knowledge/kubevirt/kubevirt-scheduling-performance-cpu-model-dedicated-cpus-hugepages-numa.md` | CPU models, dedicated CPUs, hugepages, NUMA, overcommit, memory overhead, host devices / GPUs |
| `knowledge/kubevirt/kubevirt-instancetypes-preferences-templates-cloud-init-sysprep.md` | instance types and preferences, templates, cloud-init / Ignition / Sysprep, rollout strategies |
| `knowledge/kubevirt/kubevirt-snapshots-clones-export-and-oadp-backup.md` | VM snapshots, restore, Clone API, Export API, backup with OADP's KubeVirt plugin |
| `knowledge/kubevirt/kubevirt-mtv-forklift-migrating-vms-from-vmware.md` | MTV/Forklift: providers, plans, cold vs warm, VDDK, maps, ports, copy offload, common errors |
| `knowledge/kubevirt/kubevirt-debugging-toolkit-virtctl-logs-virsh-alerts.md` | virtctl, virt-launcher/virt-handler logs, virsh in the launcher, guestfs, alerts → runbooks, error → cause table |
| `knowledge/kubevirt/kubevirt-hypershift-kubevirt-platform-hosted-clusters-on-vms.md` | HyperShift KubeVirt platform: hosted-cluster workers as VMs, storage/network/ingress requirements |
| `knowledge/kubevirt/kubevirt-kubernetes-mcp-kubevirt-toolset.md` | the `kubevirt` toolset of our vendored Kubernetes MCP: tools, what they write, air-gap caveats |

Runbooks: `runbooks/kubevirt/vm-wont-start-pending-errorunschedulable-datavolumeerror.md`,
`runbooks/kubevirt/live-migration-fails-or-stuck.md`, `runbooks/kubevirt/drain-or-upgrade-a-node-with-running-vms.md`,
`runbooks/kubevirt/datavolume-import-or-clone-stuck.md`, `runbooks/kubevirt/vm-no-network-on-secondary-network.md`,
`runbooks/kubevirt/mtv-migration-plan-failing.md`.

Interfaces: `interfaces/virtualization-storage-kubevirt-vm-disks.md`,
`interfaces/virtualization-network-kubevirt-vm-networks.md`, `interfaces/ocp-virtualization-kubevirt-platform.md`.

## Not here

- The VMware platform itself (vCenter, ESXi, vSAN, NSX) → `knowledge/vmware/README.md`; PowerCLI scripting →
  `knowledge/powercli/README.md`. MTV's *source* side preparation (CBT, snapshots, VDDK licence) is written in
  `knowledge/kubevirt/kubevirt-mtv-forklift-migrating-vms-from-vmware.md` and linked from `vmware`.
- Cluster networking in general (OVN-K, ingress, AKO, NMState for non-VM use) → `knowledge/networking/README.md`.
- The arrays and their CSI drivers → `knowledge/trident/README.md`, `knowledge/dell-powerflex/README.md`,
  `knowledge/dell-powermax/README.md`, `knowledge/dell-powerscale/README.md`, `knowledge/odf/README.md`,
  `knowledge/storage/README.md` (Portworx). VM-disk requirements on those backends are in
  `interfaces/virtualization-storage-kubevirt-vm-disks.md`.
- OADP itself → `knowledge/oadp/README.md`; HyperShift in general → `knowledge/hypershift/README.md`.

## Offline sources

Docs-only snapshots in `docs/upstream/`: `kubevirt-user-guide` (kubevirt/user-guide `docs/`), `kubevirt-docs`
(kubevirt/kubevirt `docs/`), `cdi-docs` (kubevirt/containerized-data-importer `doc/`), `hco-docs`
(kubevirt/hyperconverged-cluster-operator `docs/`), `forklift-docs` (kubev2v/forklift-documentation, AsciiDoc),
`openshift-runbooks` (`alerts/openshift-virtualization-operator/` — the CNV alert runbooks), `ovn-kubernetes`
(`docs/features/multiple-networks/` for localnet / layer2), `kubernetes-mcp-server` (`docs/upstream/kubernetes-mcp-server/docs/kubevirt.md`). Product
docs: `rhokp` (OpenShift Virtualization, MTV). All upstream snapshots track `main`: check behaviour against the
installed CNV version.

## Redact

Use `<vm>`, `<namespace>`, `<vlan>`, `<subnet>`, `<ip>`, `<cluster>`, `<node>`; MAC addresses of real VMs are
identifying — write `<mac>`. Cloud-init user data and Sysprep files often carry passwords and keys: never paste them.

## In our environment — to fill

These are open questions; answer them in pages (with `confidence`) as the team learns:

- Which clusters run VMs (hosted clusters, MCEs, UPI)? Which CNV version on each (`oc get csv -n openshift-cnv`)?
- Which storage backends hold VM disks, with which StorageClass / StorageProfile (`oc get storageprofile`)? Do they give RWX Block?
- Which networks do VMs use (pod network only, Linux bridge, OVN-K localnet with which VLANs)? Who allocates VM IPs?
- Is there a dedicated live-migration network?
- Is MTV used, from which vCenters, cold or warm, with VDDK or copy offload?
- Does any HostedCluster use the HyperShift **KubeVirt platform** (workers as VMs)?
- Is OADP's KubeVirt plugin enabled, and is Commvault also protecting VMs (`interfaces/ocp-storage-backup.md`)?
