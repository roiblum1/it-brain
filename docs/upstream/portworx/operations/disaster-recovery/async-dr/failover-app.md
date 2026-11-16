# Failover an application

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/async-dr/failover-app (Portworx Enterprise latest)

Failover an application | Portworx Enterprise Documentation

In the event of a disaster, when one of your Kubernetes clusters becomes inaccessible, you have the option to failover the applications running on it to an operational Kubernetes cluster.

The following considerations are used in the examples on this page. Update them to the appropriate values for your environment:

- Source Cluster is the Kubernetes cluster which is down and where your applications were originally running.

- Destination Cluster is the Kubernetes cluster where the applications will be failed over.

- The Zookeeper application is being failed over to the destination cluster.

Follow the instructions on this page to perform a failover of your applications to the destination cluster. These instructions apply to both scenarios, whether it is a controlled failover or a disaster recovery.

important

- Portworx supports failover operations at the namespace level. You can failover a set of VMs or applications using label-based or name-based selection within a namespace. Starting from Stork 26.4.0, you can also select specific resources by name or exclude specific resources by name. See:

- Perform failover for specific resources by name (Stork 26.4.0 and later)

- Perform failover with selectors

- Failover from a PX-Security enabled Portworx cluster to a non-secured Portworx cluster is not supported. Asynchronous DR is supported between two Portworx clusters that both have PX-Security enabled, between two non-secured Portworx clusters, and from a non-secured Portworx cluster to a Portworx cluster that has PX-Security enabled.

## Prerequisites​

-
You must ensure that Stork version 24.2.0 or newer is installed on both the source and destination clusters.

note

If you are using a Stork version prior to 24.2.0, then you can follow this procedure to perform a failover.

-
For operators deployed from the OpenShift OperatorHub:

-
Ensure that the operator is deployed on both the source and the destination clusters in the application namespace.

-
Ensure that the migration schedule is created with the `--exclude-resource-types` flag to exclude operator-related resources, as shown in the following example:

```

storkctl create migrationschedule -c cluster-pair -n zookeeper migration-schedule --exclude-resource-types ClusterServiceVersion,operatorconditions,OperatorGroup,InstallPlan,Subscription --exclude-selectors olm.managed=true

```

-
Ensure that the operator and applications are in scaled down state on the source cluster. Stork will leverage `spec.replicas` from most of the standard Kubernetes controllers such as Deployments, StatefulSets, and so on. However, for applications managed by an Operator, an `ApplicationRegistration` CR needs to be created which provides Stork with the necessary information required to perform a scale down of the application. For more information, see the Application Registration document.

## Perform failover​

- Disaster recovery

- Controlled failover

In the event of a disaster, you can migrate an application or workload from the source cluster to destination cluster by running the `storkctl perform failover` command.

If your source cluster is accessible and you want to migrate an application or workload from the source cluster to destination cluster, you can perform a controlled failover by running the `storkctl perform failover` command.

note

By default, Portworx scales down the resources and suspends the migration schedule in the source cluster, ensuring data consistency. If you just want the apps to come up on the destination cluster and do not need data consistency between the source and destination clusters, you can use the `--skip-source-operations` flag to skip source cluster operations.

 Are your clusters paired in a unidirectional manner? (Click to expand for more details)

For Disaster Recovery: If yes, you must use the `--skip-source-operations` flag to skip the source cluster operations.

For Controlled Failover: If yes, you must create a reverse ClusterPair in the destination-to-source direction with the same name as the ClusterPair in the source-to-destination direction to ensure data consistency between the clusters.

You can use the following flags to include or exclude specific namespaces or resources during the failover operation, giving you greater control over what is being restored.

-
Namespace filters

- `--include-namespaces` - Include only a specific subset of namespaces for the migration.

- `--exclude-namespaces` - Exclude specific namespaces from the migration.

-
Resource filters

- `--selectors` - Activate/deactivate only resources with the specified labels.

- `--exclude-selectors` - Exclude resources with the specified labels from activation/deactivation.

- `--resource-types` - Filter resources by type. Format: `KIND` or `GROUP/VERSION/KIND` (e.g., `apps/v1/Deployment`). Could be specified multiple times.

- `--include-objects` - Include specific objects by name. Format: `KIND/NAMESPACE/NAME` or `GROUP/VERSION/KIND/NAMESPACE/NAME`. Mutually exclusive with `--selectors`, `--exclude-selectors`, `--resource-types`, and `--exclude-objects`.

- `--exclude-objects` - Exclude specific objects by name. Format: `KIND/NAMESPACE/NAME` or `GROUP/VERSION/KIND/NAMESPACE/NAME`. Mutually exclusive with `--selectors`, `--exclude-selectors`, `--resource-types`, and `--include-objects`.

-
Operation flags

- `--skip-last-mile-migration` - Use this flag if you want to skip the last-mile migration before workloads are activated or for failover on migration schedules which are already suspended.

### Perform failover for all apps in the migrated namespaces​

To start the failover operation for all applications in the migrated namespaces, run the following command in the destination cluster:

```

storkctl perform failover -m <migration-schedule> -n <migration-schedule-namespace>

```

If the last migration status is in the `PartialSuccess` state, you'll be prompted to proceed with the failover operation. To bypass this prompt, use the `--force` flag.

Example:

```

storkctl perform failover -m migration-schedule -n zookeeper

```

```

Started failover for MigrationSchedule zookeeper/migration-schedule

To check failover status use the command : `storkctl get failover failover-migration-schedule-2024-05-20-140139 -n zookeeper`

```

### Perform failover with namespace filtering​

You can use namespace filters to include or exclude specific namespaces during the failover operation.

- `--include-namespaces` - Include only a specific subset of namespaces for the migration.

- `--exclude-namespaces` - Exclude specific namespaces from the migration.

Examples:

```

# Perform failover for only specific namespaces

storkctl perform failover -m migration-schedule -n zookeeper --include-namespaces=app-ns1,app-ns2

```

```

# Perform failover for all namespaces except specific ones

storkctl perform failover -m migration-schedule -n zookeeper --exclude-namespaces=test-ns

```

note

You cannot use `--include-namespaces` and `--exclude-namespaces` together, or you'll get an error.

### Perform failover for specific resource types​

You can use the `--resource-types` flag to filter resources by type during the failover operation. The format is `KIND` or `GROUP/VERSION/KIND` (e.g., `apps/v1/Deployment`). This flag can be specified multiple times.

Examples:

```

# Perform failover for only StatefulSet resources

storkctl perform failover -m migration-schedule -n zookeeper --resource-types=StatefulSet

```

```

# Perform failover for Deployment and CronJob resources

storkctl perform failover -m migration-schedule -n zookeeper --resource-types Deployment --resource-types batch/v1/CronJob

```

### Perform failover with selectors​

You can use selector flags to activate or deactivate only specific resources based on their labels during the failover operation.

- `--selectors` - Activate/deactivate only resources with the specified labels.

- `--exclude-selectors` - Exclude resources with the specified labels from activation/deactivation.

Examples:

```

# Perform failover for only the resources with the label app=busybox

storkctl perform failover -m migration-schedule -n zookeeper --selectors=app=busybox

```

```

# Perform failover for all resources except the ones with the label app=busybox

storkctl perform failover -m migration-schedule -n zookeeper --exclude-selectors=app=busybox

```

note

You cannot use `--selectors` and `--exclude-selectors` together, or you'll get an error.

```

error: can provide only one of --selectors or --exclude-selectors values at once

```

### Perform failover for specific resources by name​

You can fail over or exclude specific Kubernetes resources by name using the `--include-objects` or `--exclude-objects` flags. These flags can be specified multiple times for multiple resources.

The format for `--include-objects` and `--exclude-objects` is one of:

- `KIND/NAMESPACE/NAME` (e.g., `VirtualMachine/app-ns/my-vm`)

- `GROUP/VERSION/KIND/NAMESPACE/NAME` (e.g., `apps/v1/Deployment/app-ns/payments-api`)

note

- The `NAMESPACE` in the object path is the namespace where the resource lives, which may differ from the MigrationSchedule namespace specified with `-n`.

- `--include-objects` and `--exclude-objects` are mutually exclusive with each other and with `--selectors`, `--exclude-selectors`, and `--resource-types`.

- Both flags can be combined with `--include-namespaces` and `--exclude-namespaces`.

Include specific resources:

```

# Fail over a specific KubeVirt VM by name

storkctl perform failover -m migration-schedule -n <namespace> \

  --include-objects VirtualMachine/app-ns/my-vm

```

```

# Fail over multiple resources by name

storkctl perform failover -m migration-schedule -n <namespace> \

  --include-objects VirtualMachine/app-ns/vm-payments \

  --include-objects VirtualMachine/app-ns/vm-billing

```

```

# Fail over a Deployment by name with full group/version syntax

storkctl perform failover -m migration-schedule -n <namespace> \

  --include-objects apps/v1/Deployment/app-ns/payments-api

```

Exclude specific resources:

```

# Fail over all resources except a specific VM

storkctl perform failover -m migration-schedule -n <namespace> \

  --exclude-objects VirtualMachine/app-ns/my-vm

```

### Perform additional selective failovers​

If a selective failover has been performed and you want to initiate another failover for the remaining applications or VMs, you must use a new `MigrationSchedule` instead of reusing the one referenced in the earlier failover.

-
Delete the `MigrationSchedule` that was referenced by the first failover from both source and destination clusters.

-
Create a new `MigrationSchedule` on the source cluster.

-
Use `--exclude-selectors` to exclude applications/VMs (and their volumes) that are already failed over.

-
Optionally, you can use `--selectors` to migrate only a specific subset of remaining resources.

- Perform the additional failover by referencing the newly created `MigrationSchedule`.

Why a new MigrationSchedule is required

-
Prevents conflicts with resources that are already failed over and activated on the destination cluster.

-
Ensures isolation so that ongoing and last-mile migration only applies to the remaining (non-failed-over) applications/VMs and their volumes.

-
Allows consecutive failovers to proceed smoothly without impacting workloads that have already been failed over.

Using a fresh `MigrationSchedule` isolates the migration scope to the remaining workloads, providing better control and preventing unintended interference with already migrated resources.

## Check failover status​

Run the following command to check the status of the failover operation. You can refer to the above section to get the value of `failover-action-name`.

```

storkctl get failover <failover-action-name> -n <migration-schedule-namespace>

```

Example:

```

storkctl get failover failover-migration-schedule-2024-05-20-140139 -n zookeeper

```

```

NAME                                    CREATED               STAGE       STATUS       MORE INFO

failover-migration-schedule-2024-05-20-140139       20 May 24 14:02 UTC   Completed   Successful   Scaled up Apps in : 1/1 namespaces

```

If the status is failed, you can use the following command to get more information about the failure:

- Kubernetes

- OpenShift

```

kubectl describe actions <failover-action-name> -n <migration-schedule-namespace>

```

```

oc describe actions <failover-action-name> -n <migration-schedule-namespace>

```

## Verify volumes and Kubernetes resources are migrated​

To verify the volumes and Kubernetes resources that are migrated to the destination cluster, run the following command:

- Kubernetes

- OpenShift

```

kubectl get all -n <migration-schedule-namespace>

```

Example:

```

kubectl get all -n zookeeper

```

```

NAME                     READY   STATUS    RESTARTS   AGE

pod/zk-544ffcc474-6gx64   1/1     Running   0          18h

NAME                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE

service/zk-service   ClusterIP   10.233.22.60   <none>        3306/TCP   18h

NAME                 READY   UP-TO-DATE   AVAILABLE   AGE

deployment.apps/zk   1/1     1            1           18h

NAME                            DESIRED   CURRENT   READY   AGE

replicaset.apps/zk-544ffcc474   1         1         1       18h

```

```

oc get all -n <migration-schedule-namespace>

```

Example:

```

oc get all -n zookeeper

```

```

NAME                     READY   STATUS    RESTARTS   AGE

pod/zk-544ffcc474-6gx64   1/1     Running   0          18h

NAME                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE

service/zk-service   ClusterIP   10.233.22.60   <none>        3306/TCP   18h

NAME                 READY   UP-TO-DATE   AVAILABLE   AGE

deployment.apps/zk   1/1     1            1           18h

NAME                            DESIRED   CURRENT   READY   AGE

replicaset.apps/zk-544ffcc474   1         1         1       18h

```

In this topic:
