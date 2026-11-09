# Role-Based Access Control for ACM Disaster Recovery

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/acm-dr/rbac (Portworx Enterprise latest)

Role-Based Access Control for ACM Disaster Recovery | Portworx Enterprise Documentation

Role-based access control (RBAC) for ACM disaster recovery (DR) controls who can view and manage the DR resources that the Portworx MultiCluster Operator creates on your Red Hat Advanced Cluster Management (ACM) hub. These resources include DR pairs, protection groups, and DR actions.

RBAC is a core ACM and OpenShift capability. Portworx doesn't add a separate DR role model or user-to-role assignment. Instead, Portworx extends your existing ACM and OpenShift roles to Portworx DR resources. If a user already has an ACM or OpenShift role, the user gets the matching DR permissions at the same scope.

With RBAC, you can:

- Give each team DR access only to the managed clusters that the team owns, without granting administrator access to every cluster.

- Separate the administrators who set up DR, such as DR pairs and protection groups, from the users who run DR actions, such as failover and failback.

- Give auditors and observers read-only access.

note

If you can give all users administrator access to all clusters, you don't need to configure additional roles. Use this guide if you're a platform administrator who needs to delegate DR access to other users and teams.

To understand how roles, role bindings, and managed cluster sets work in ACM, see Role-based access control in the Red Hat ACM documentation.

## Roles and DR access​

The following table lists the ACM and OpenShift roles that affect DR access and the access each role provides.

RoleDefinition and additional roles required for DR operations

`cluster-admin`OpenShift default super-user role with full access to all clusters. Users with this role can create, view, update, and delete all DR resources. No additional role is required.

`open-cluster-management:cluster-manager-admin`ACM super-user role with full access to all managed clusters. Users with this role can create, view, update, and delete DR resources. Assign `admin` role to user in the namespace in which the DR resources are created.

`open-cluster-management:managedclusterset:admin:<cluster_set_name>`Administrator access to a `ManagedClusterSet` and the managed clusters in it. Users with this role can create, view, update, and delete DR resources for those clusters.
 Both the source and destination clusters must be in the cluster set. Assign `admin` role to user in the namespace in which the DR resources are created. Assign `view` permission for the namespace where the `ManagedCluster` custom resource is created

`open-cluster-management:managedclusterset:view:<cluster_set_name>`View-only access to a `ManagedClusterSet` and the managed clusters in it. Users with this role can view DR resources but cannot perform DR operations.
 To perform DR operations, also assign `open-cluster-management:managedclusterset:admin:<cluster_set_name>` or `open-cluster-management:admin:<managed_cluster_name>` and `admin` role to user in the namespace in which the DR resources are created.

`open-cluster-management:admin:<managed_cluster_name>`Administrator access to one managed cluster. Users with this role can create, view, update, and delete DR resources tied to that cluster.
 Assign this role for both the source and the destination cluster, and `admin` role to user in the namespace in which the DR resources are created. Assign `view` permission for the namespace where the `ManagedCluster` custom resource is created.

`open-cluster-management:view:<managed_cluster_name>`View-only access to one managed cluster. Users with this role can view DR resources tied to that cluster but cannot perform DR operations.
 To perform DR operations, also assign `open-cluster-management:admin:<managed_cluster_name>` for the source and destination clusters and `admin` role to user in the namespace in which the DR resources are created.

OpenShift `admin` and `edit`Read and write access to resources in a namespace, or across the cluster if bound cluster-wide. Users with these roles can create, view, update, and delete DR resources within that scope.
 Assign `open-cluster-management:admin:<managed_cluster_name>` or `open-cluster-management:managedclusterset:admin:<cluster_set_name>` for the source and destination clusters. Assign `admin` role to user in the namespace in which the DR resources are created.

OpenShift `view`Read-only access to resources in a namespace, or across the cluster if bound cluster-wide. Users with this role can view DR resources but cannot perform DR operations.
 To perform DR operations, also assign an ACM admin role for the source and destination clusters and `admin` role to user in the namespace in which the DR resources are created.

A user's access is limited to the managed clusters that the user is already authorized to use through ACM or OpenShift roles. A role that is scoped to one cluster or cluster set never grants DR access to other clusters.

## Permissions required for DR operations​

Any user who needs to perform DR operations with ACM, whether setting up DR pairs and protection groups or running DR actions such as failover and failback, needs the following permissions:

- admin access to the source and destination clusters for which DR is performed.

- admin access to the namespace in which the DR CRDs are created or the Portworx MultiCluster Operator is installed.

User can create DR CRDs with GitOps or the CLI (`kubectl`) in a namespace they have access to. When they use the UI, the DR resources are created in the `Portworx` namespace. Based on the permissions, user can view or edit the resources on the ACM hub. The UI disables DR actions that user does not have permissions to perform.

One way to grant these permissions is to define roles in OpenShift and bind them to the user. For information about how to create roles and role bindings, see Using RBAC to define and apply permissions in the OpenShift documentation.

Users who have the required permissions can do the following:

- View the source and destination clusters on the Clusters page.

- View all DR resources, such as DR pairs and protection groups, for those clusters and namespaces.

- Perform all create, read, update, and delete (CRUD) operations on the DR resources in that namespace.

The UI lists only the DR resources in namespaces that you can access on the hub cluster. The list includes resources from up to 50 accessible namespaces. If you have access to more than 50 namespaces, the UI might not show all of your DR resources.

## Recommended roles by user personas​

User PersonaResponsibilitiesTypical roles

Global platform administratorManages all clusters, DR topologies, and DR operations`cluster-admin` or `open-cluster-management:cluster-manager-admin`

DR domain administratorOwns DR configuration and operations for a group of clusters`open-cluster-management:managedclusterset:admin:<cluster_set_name>`, plus `admin` or `edit` permissions in namespace where DR resources are created

Cluster DR operatorManages DR configuration and actions for one or a few clusters`open-cluster-management:admin:<managed_cluster_name>`, plus `admin` or `edit` permissions in namespace where DR resources are created

DR observer or auditorViews DR state without changing configuration or running actions`open-cluster-management:view:<managed_cluster_name>` or OpenShift `view`

## Related topics​

- Prerequisites for ACM Disaster Recovery

- Manage a Disaster Recovery Pair

- Manage Protection Groups

In this topic:
