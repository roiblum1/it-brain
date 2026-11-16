# Manage ACM Disaster Recovery using GitOps

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/acm-dr/gitops-workflow (Portworx Enterprise latest)

Manage ACM Disaster Recovery using GitOps | Portworx Enterprise Documentation

ACM-based disaster recovery (DR) supports GitOps workflows. You define the DR configuration as Kubernetes custom resources (CRs) in a Git repository, and a GitOps controller, such as OpenShift GitOps or Argo CD, synchronizes these resources with the ACM hub cluster. Runtime operations, such as failover and failback, are not declarative and remain separate operational tasks that you perform from the OpenShift console.

This topic describes which ACM DR resources you manage through GitOps and provides an end-to-end workflow for protecting and recovering applications.

## What you manage through GitOps​

The following table lists the ACM DR objects and whether you manage them through GitOps:

ObjectManaged through GitOpsDescription

`DisasterRecoveryPair`YesDefines the DR relationship between the source and destination clusters.

`ProtectionGroup`YesDefines the applications or namespaces to protect and their protection policy.

`ReverseProtectionGroup`Yes (optional)Defines the reverse protection configuration used for failback. You create this resource in advance and activate it later. For more information, see Step 2 and Step 4 of the workflow.

ClustersNoACM discovers and manages clusters. They are not created through ACM DR GitOps resources.

DR actions (failover, prepare for failback, and failback)NoThese are runtime operations that you invoke through the OpenShift console or API.

note

GitOps manages the disaster recovery configuration, not runtime operations. You can manage `DisasterRecoveryPair`, `ProtectionGroup`, and, optionally, `ReverseProtectionGroup` through GitOps. Perform failover and failback separately when required.

For resource definitions and sample manifests of these resources, see ACM DR CRD Reference.

## Prerequisites​

GitOps begins after the Multi Cluster Disaster Recovery environment is configured. It does not replace the initial environment setup.

Ensure that your environment meets the following requirements:

- The OpenShift clusters participating in DR are imported into ACM.

- Network connectivity and required ports are configured between participating clusters.

- The Portworx MultiCluster Operator is installed on the ACM hub cluster, and the hub is configured as the storage hub. For more information, see Install the Portworx MultiCluster Operator.

- A supported GitOps controller, such as OpenShift GitOps or Argo CD, is available.

For the complete list of environment requirements, see Prerequisites for Multi Cluster Disaster Recovery.

## End-to-end DR workflow​

The following workflow shows how to protect applications through GitOps and recover them when required. You perform the configuration steps declaratively through GitOps, and the recovery steps as runtime operations from the OpenShift console. Complete the recovery steps only when you need to fail over to the destination cluster and later fail back to the source cluster.

The workflow consists of the following steps:

- Create the DR pair

- Create the protection group

- Perform a failover

- Prepare for failback

- Perform a failback

### Step 1. Create the DR pair​

Using GitOps, create a `DisasterRecoveryPair` resource in your Git repository to define the relationship between the source and destination clusters. After your GitOps controller applies the resource to the ACM hub cluster, ACM propagates the configuration to the workload clusters. For information about the DR pair configuration, see Manage a Disaster Recovery Pair.

important

Ensure that you deploy the `DisasterRecoveryPair` and `ProtectionGroup` resources in the same namespace.

### Step 2. Create the protection group​

Using GitOps, create a `ProtectionGroup` resource in your Git repository to define the applications or namespaces to protect. For information about the protection group configuration, see Manage Protection Groups.

To support failback later, you can also create a `ReverseProtectionGroup` resource at this stage. Creating a `ReverseProtectionGroup` resource does not enable reverse protection immediately. You activate reverse protection in Step 4 by referencing the resource from the `ProtectionGroup`.

### Step 3. Perform a failover​

When the source cluster becomes unavailable, or when you want to migrate workloads to the destination cluster, perform a failover from the OpenShift console. For more information, see Failover.

### Step 4. Prepare for failback​

Before you fail back, prepare the protection group for failback from the OpenShift console. For more information, see Prepare for failback.

note

If you created a `ReverseProtectionGroup` resource in Step 2, activate reverse protection by adding the following annotation to the `ProtectionGroup` resource:

```

metadata:

  annotations:

    multicluster.purestorage.com/reverse-protection-group-ref: "<namespace>/<reverse-protection-group-name>"

```

Replace `<namespace>/<reverse-protection-group-name>` with the namespace and name of your `ReverseProtectionGroup` resource.

### Step 5. Perform a failback​

After the source cluster is available again, perform a failback from the OpenShift console to return the workloads to the source cluster. For more information, see Initiate a failback.

In this topic:
