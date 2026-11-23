# Prerequisites for Synchronous Disaster Recovery

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/px-metro/prerequisites (Portworx Enterprise latest)

Prerequisites for Synchronous Disaster Recovery | Portworx Enterprise Documentation

The prerequisites provided in this section ensure a stable foundation for data replication and failover when you enable synchronous disaster recovery between the source and destination clusters. Review them carefully to prevent configuration issues during deployment.

Ensure that your cluster meets the following prerequisites in addition to the System Requirements:

-
An active Portworx Enterprise Disaster Recovery (DR) license.

-
You must have a user role with cluster-admin access to perform failover, failback, or other disaster recovery operations, as these operations require access to multiple namespaces (including `kube-system`) and full cluster-wide permissions.

-
A highly available network connection between the source and destination clusters.

-
The network latency between the source and destination clusters (Site 1 ↔ Site 2) must not exceed 10 ms.

-
Deploy a witness node in a third site to maintain cluster quorum during a site failure. The round-trip time (RTT) between the witness site and each primary site must not exceed 100 ms.

-
Your environment must meet the following network requirements:

- All worker nodes in the source and destination clusters must be able to access the Kubernetes API endpoints (for example, ports 6443 and 443).

- The source and destination clusters must be able to access ports in the 9001–9020 range to enable communication between Portworx worker nodes.

- The source and destination clusters must be able to access ports in the 17001–17020 range to reach Portworx API endpoints.

For more information on the list of required ports for your environment, see Network Requirements.

-
KubeVirt VMs with PX ReadWriteMany (RWX) block volumes must run OpenShift Virtualization 4.18.5 or later with OpenShift Container Platform 4.18.x to enable synchronous disaster recovery. Running earlier OCP versions, such as 4.16.x, can cause I/O errors that may pause virtual machines.

-
An external etcd-based KVDB must be installed outside of the deployed Kubernetes clusters.
 For more information, see External KVDB for Portworx on Kubernetes.

-
If you use any custom container images, make sure the custom images are available from a registry that is accessible to both the source and destination clusters.

-
GitOps tools such as ArgoCD, FluxCD, or Rancher Fleet do not overwrite the Kubernetes custom resources (CRs) migrated by Portworx disaster recovery (DR) `MigrationSchedules` on the destination cluster.

important

For certain Kubernetes applications, an ApplicationRegistration custom resource (CR) is created before initiating migration. For more information, see the ApplicationRegistrations.
