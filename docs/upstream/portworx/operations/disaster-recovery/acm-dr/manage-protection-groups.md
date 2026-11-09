# Manage Protection Groups

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/acm-dr/manage-protection-groups (Portworx Enterprise latest)

Manage Protection Groups | Portworx Enterprise Documentation

A protection group defines what is protected, how often it is migrated, and the hooks that apply.

This topic explains how to create, update, and delete a protection group by using the OpenShift console.

## Prerequisites​

- A disaster recovery pair between the source and destination workload clusters in a healthy state.
For more information, see Manage a Disaster Recovery Pair.

- One or more namespaces on the source cluster that you want to protect.

## Create a Protection Group​

To create a protection group, perform the following steps:

- Log in to the OpenShift console.

- Switch to the multicluster management view (All Clusters on OpenShift 4.18 and 4.19, or Fleet management on 4.20 and later) and select the Portworx tab.

- Click Protection Groups.
The system displays the Protection Groups page that lists all existing protection groups.

- Click Create Protection Group.
The system displays the Create Protection Group page.

- In the Protection Details page of the Create Protection Group window, do the following:

- In the Protection group name field, enter a name for the protection group.

- From the Disaster Recovery Pair dropdown, select the DR pair that you want to use for this protection group.

- Under Namespace, choose one of the following options:

- To manually select namespaces, select the Select from namespace list option, and choose one or more namespaces to protect from the list.

note

The user must have at least one of the following permissions to view namespace list:

- `view` permission at the cluster set level

- The OpenShift Container Platform (OCP) `view` role

- `view` permission for the namespace where the `ManagedCluster` custom resource (CR) is created

- To select namespaces that match specific labels, select the Use label selector option, and enter the Label Key and Label Value.
To add more labels, click the Add more labels button.

- Click Next.

- In the Resource Configuration page that opens, do the following:

- Under Resources to protect, select one of the following options:

- All resources: To protect all resources in the selected namespaces.

- Custom resources: To select specific resource types to protect.

- No resources: To exclude Kubernetes resources from protection.

- Based on your selection in the previous step, do the following:

- If you selected All resources, do the following:

- Select the Include Application Volumes (PVCs) checkbox to protect persistent volume claims associated with applications in the protection group migrations.
Clear this checkbox to protect only Kubernetes resources and exclude PVCs.

- Select the Include CIDR-based NetworkPolicies checkbox to include network policies that use CIDR rules in the protection group migrations.
Clear this checkbox to exclude network policies with CIDR rules.

- If you selected Custom resources, do the following:

- (Optional) Under Include resource labels, specify the label criteria to protect only Kubernetes resources that match the specified labels.

- Key: The label key to match.

- Operator: The comparison operator to use.

- Value: The label value to match.
Click Add rule to add additional label-based inclusion rules.

- (Optional) Under Exclude resource labels, specify the label criteria to omit specific resources from protection, even if they match an inclusion rule.

- Key: The label key to match.

- Operator: The comparison operator to use.

- Value: The label value to match.
Click Add rule to add additional label-based exclusion rules.

- (Optional) Under Include additional resource types, select one or more resource types from the dropdown menu.

- (Optional) Under Exclude resource types, select one or more Kubernetes resource types to exclude from the dropdown menu.

- (Optional) Enter additional resource types in the Add custom resource types field.
Separate multiple custom resource types with commas.

- Select the Include Application Volumes (PVCs) checkbox to protect persistent volume claims associated with applications in the protection group migrations.
Clear this checkbox to protect only Kubernetes resources and exclude PVCs.

- Select the Include CIDR-based NetworkPolicies checkbox to include network policies that use CIDR rules in the protection group migrations.
Clear this checkbox to exclude network policies with CIDR rules.

- Click Next.

- If you selected No resources, do the following:

- Select the Include Application Volumes (PVCs) checkbox to protect persistent volume claims associated with applications in the protection group migrations.
Clear this checkbox to protect only Kubernetes resources and exclude PVCs.

- Select the Include CIDR-based NetworkPolicies checkbox to include network policies that use CIDR rules in the protection group migrations.
Clear this checkbox to exclude network policies with CIDR rules.

- In the Advanced Settings page that opens, do the following:

- (Optional) Under Synchronization behavior, do the following:

- Select the Remove resources deleted at source checkbox to remove resources from the DR cluster when they are deleted on the source cluster.

- Select the Ignore deleted namespaces from source checkbox to prevent namespace deletions from propagating to the DR cluster.

- Select the Skip Service updates checkbox to prevent service updates from being applied on the DR cluster.

- Select the Ignore owner-reference validation checkbox to apply resources without validating owner references.

- (Optional) Under Migration lifecycle rules, add any pre-migration and post-migration rules as needed.

- Click Next.

- In the Replication Settings page that opens, do the following:

- Under Replication interval, enter the desired interval for replicating resources.

- Click Next.

- In the Review page that opens, review the protection group configuration details.

- Click Save to create the protection group.
The system creates the protection group and displays the Protection Groups page that lists the protection group.

### What to do next​

- Review the Sync Status field in the Protection Groups page to confirm that migrations are running on schedule and that the most recent migration completed successfully.

- After the protection group is created, you can trigger a failover when needed.

## Update a Protection Group​

To update a protection group, complete the following steps:

- Sign in to the OpenShift web console.

- Switch to the multicluster management view, and from the left navigation pane, select the Portworx option.

- Select Protection Groups.
 The system displays the Protection Groups page that lists all existing protection groups.

- Click the vertical ellipsis menu associated with the protection group to update, and select Edit.
The system displays the Edit Protection Group page.

- The update workflow uses the same fields and options described in Create a Protection Group. Modify the required values and click Update.
The system updates the protection group.

## Delete a Protection Group​

To delete a protection group, perform the following steps:

- Sign in to the OpenShift web console.

- Switch to the multicluster management view, and from the left navigation pane, select the Portworx option.

- Select Protection Groups.
 The system displays the Protection Groups page that lists all existing protection groups.

- Click the vertical ellipsis menu associated with the protection group to delete, and select Remove protection group.

- In the confirmatory dialog box that appears, enter the name of the protection group in the field provided, select the I understand, remove this protection group checkbox, and click Remove.
The system deletes the protection group.

In this topic:
