# Portworx ACM Dynamic Console Plugin Dashboards

Source: https://docs.portworx.com/portworx-enterprise/platform/configure-portworx-components/install-multicluster-operator/acm-cluster-dashboards (Portworx Enterprise latest)

Portworx ACM Dynamic Console Plugin Dashboards | Portworx Enterprise Documentation

This topic describes the dashboards available in the Portworx ACM Dynamic Console Plugin. These dashboards provide centralized visibility into the health, performance, and disaster recovery status of Portworx clusters managed through Red Hat Advanced Cluster Management (ACM).

Portworx ACM Dynamic Console Plugin displays the following dashboards:

- Clusters dashboard: Displays the health and DR readiness of each workload cluster.

- Disaster Recovery Pairs dashboard: Displays the replication relationships between paired workload clusters.

- Protection Groups dashboard: Displays the namespaces and resources protected on each source cluster and their replication state.

- Disaster Recovery Actions dashboard: Displays the failover and failback actions and their status.

## Prerequisites​

To view the dashboards, your environment must meet the following prerequisites:

- The Portworx MultiCluster Operator is installed on the ACM hub cluster.
For more information, see Install Portworx MultiCluster Operator.

- One or more OpenShift clusters running Portworx Enterprise are imported into ACM as workload clusters.

- You are signed in to the OpenShift web console with `cluster administrator` privileges.

note

Only users with `cluster administrator` privileges can view the information under the Portworx option in the multicluster management view. To give other users access, configure RBAC for them. For more information, see Role-Based Access Control for ACM Disaster Recovery.

## Clusters dashboard​

The Clusters dashboard displays each workload cluster that is imported into ACM, along with its health, platform, and disaster recovery readiness. Use this dashboard to confirm that a cluster is eligible to participate in a DR pair before you configure replication.

### Access the Clusters dashboard​

To access the Clusters dashboard, complete the following steps:

- Sign in to the OpenShift web console.

- Switch to the multicluster management view, and from the left navigation pane, select the Portworx option.

- Select Clusters.
The system displays the Clusters dashboard that lists all workload clusters.

The top of the dashboard displays the following summary cards:

Summary cardDescription

All ClustersDisplays the total number of workload clusters available in the hub cluster.

DR Ready ClustersDisplays the number of clusters that meet the requirements to participate in disaster recovery.

Paired ClustersDisplays the number of clusters that are currently part of a Disaster Recovery Pair.

Clusters Available for PairingDisplays the number of DR-ready clusters that are not yet part of a Disaster Recovery Pair.

### Clusters dashboard attributes​

The following table lists the attributes that are displayed in the Clusters dashboard.

AttributeDescription

Cluster NameDisplays the name of the workload cluster as imported into ACM. Click the name to view the cluster details.

Last HeartbeatDisplays the time elapsed since the hub cluster last received a heartbeat from the workload cluster. The system displays Unknown if no heartbeat has been received.

DR ReadyDisplays whether the cluster is ready to participate in disaster recovery. A value of Yes indicates that the cluster passed the automated preflight checks, and a value of No indicates that it did not.

Portworx installedDisplays whether Portworx Enterprise is installed and running on the workload cluster.

Cluster statusDisplays the current operational health of the cluster, along with the deployed Portworx version in parentheses. For example, Healthy (3.5.2). Other states include Invalid, which indicates that the cluster cannot be used for disaster recovery.

PlatformDisplays the underlying infrastructure platform on which the cluster runs, such as VSphere.

CapacityDisplays the used storage capacity relative to the total capacity of the cluster.

## Disaster Recovery Pairs dashboard​

The Disaster Recovery Pairs dashboard displays each DR pair configured between a source and destination workload cluster. Use this dashboard to verify that a replication channel is healthy before you create or fail over a Protection Group.

### Access the Disaster Recovery Pairs dashboard​

To access the Disaster Recovery Pairs dashboard, complete the following steps:

- Sign in to the OpenShift web console.

- Switch to the multicluster management view, and from the left navigation pane, select the Portworx option.

- Select Disaster Recovery Pairs.
The system displays the Disaster Recovery Pairs dashboard that lists all existing DR pairs.

### Disaster Recovery Pairs dashboard attributes​

The following table lists the attributes that are displayed in the Disaster Recovery Pairs dashboard.

AttributeDescription

Disaster Recovery Pair NameDisplays the name of the DR pair.

Source ClusterDisplays the workload cluster that hosts the protected workloads and acts as the source for replication. Click the name to view the cluster details.

Destination ClusterDisplays the workload cluster that receives replicated data and serves as the failover target. Click the name to view the cluster details.

Disaster Recovery TypeDisplays the type of disaster recovery configured for the pair. ACM-based DR supports the Asynchronous type.

Pair TypeDisplays whether the pair is Unidirectional or Bidirectional.

Pairing StatusDisplays the health of the pairing, such as Ready when the replication channel between the clusters is established and operational, or Not Ready when it is not.

Created atDisplays the date and time when the DR pair was created.

## Protection Groups dashboard​

The Protection Groups dashboard displays each Protection Group and the state of its replication. Use this dashboard to confirm that migrations are running on schedule and to determine whether a Protection Group is ready for failover or failback.

### Access the Protection Groups dashboard​

To access the Protection Groups dashboard, complete the following steps:

- Sign in to the OpenShift web console.

- Switch to the multicluster management view, and from the left navigation pane, select the Portworx option.

- Select Protection Groups.
The system displays the Protection Groups dashboard that lists all existing protection groups.

### Protection Groups dashboard attributes​

The following table lists the attributes that are displayed in the Protection Groups dashboard. To view additional details for a protection group, click the expand arrow at the start of its row.

AttributeDescription

NameDisplays the name of the protection group.

Disaster Recovery PairDisplays the DR pair that the protection group uses to replicate namespaces between the source and destination clusters.

Active siteDisplays the site that currently hosts the active workloads for the protection group, either Primary or DR.

Replication stateDisplays whether replication is currently running for the protection group, such as Active.

Protection StateDisplays the current DR state of the protection group, such as Ready for Failback after the initial reverse synchronization completes. The system displays Unknown when the state cannot be determined.

PlacementDisplays the distribution of protected namespaces across the sites, shown as the number on the primary cluster and the number on the DR cluster. For example, 0 Primary / 2 DR.

Sync StatusDisplays whether migrations are running on schedule and whether the most recent migration completed successfully. The system displays Unknown when the status cannot be determined.

## Disaster Recovery Actions dashboard​

The Disaster Recovery Actions dashboard displays each failover and failback action triggered for your Protection Groups. Use this dashboard to track the progress of a DR action and confirm that it completed successfully.

### Access the Disaster Recovery Actions dashboard​

To access the Disaster Recovery Actions dashboard, complete the following steps:

- Sign in to the OpenShift web console.

- Switch to the multicluster management view, and from the left navigation pane, select the Portworx option.

- Select Disaster Recovery Actions.
The system displays the Disaster Recovery Actions dashboard that lists all failover and failback actions.

### Disaster Recovery Actions dashboard attributes​

The following table lists the attributes that are displayed in the Disaster Recovery Actions dashboard.

AttributeDescription

NameDisplays the name that you assigned to the failover or failback action when you created it.

Protection GroupDisplays the protection group that the action applies to.

Event TypeDisplays whether the action is a Failover or a Failback.

StatusDisplays the current state of the action as it progresses to completion. A status of Successful confirms that the action completed.

StageDisplays the stage that the action is currently executing within its workflow.

Start AtDisplays the date and time when the action started.

Completed AtDisplays the date and time when the action completed.

note

To view the underlying Stork action, sign in to the workload cluster on which the action is running and inspect the `Action` objects in the admin namespace.

In this topic:
