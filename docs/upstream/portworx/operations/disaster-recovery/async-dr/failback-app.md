# Failback an application

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/async-dr/failback-app (Portworx Enterprise latest)

Failback an application | Portworx Enterprise Documentation

Failback is the process of moving the application and its data back to the source cluster after the source cluster is restored and operational again.

important

- Before failing back your applications, you must have a `MigrationSchedule` in place on the destination cluster, and the latest migration must have succeeded. This ensures that the most up-to-date application state is available on the original source cluster during failback.

- Portworx supports failback operations at the namespace level. You can failback a set of VMs or applications using label-based or name-based selection within a namespace. Starting from Stork 26.4.0, you can also select or exclude specific resources by name. See:

- Perform failback for specific resources by name (Stork 26.4.0 and later)

- Failback from a PX-Security enabled Portworx cluster to a non-secured Portworx cluster is not supported. Asynchronous DR is supported between two Portworx clusters that both have PX-Security enabled, between two non-secured Portworx clusters, and from a non-secured Portworx cluster to a Portworx cluster that has PX-Security enabled.

The following considerations are used in the examples on this page. Update them to the appropriate values based on your environment:

- Source Cluster is the Kubernetes cluster which is down and where your applications were originally running.

- Destination Cluster is the Kubernetes cluster where the applications will be failed over.

- The Zookeeper application is being failed over to the destination cluster.

## Prerequisites​

-
Ensure that the source and destination clusters have Stork version 24.2.0 or later installed.

note

If you are using a Stork version prior to 24.2.0, follow this procedure to perform a failback.

-
For operators deployed from the OpenShift OperatorHub, ensure that the operator and applications are in a scaled-down state on the destination cluster. Stork leverages `spec.replicas` from most of the standard Kubernetes controllers such as Deployments, and StatefulSets. However, for applications managed by an Operator, an `ApplicationRegistration` CR needs to be created which provides Stork with the necessary information required to perform a scale down of the application. For more information, see Application Registration.

-
For forklifted VMs, if you are performing failback of a VM that was forklifted (migrated from vSphere to OpenShift using the Migration Toolkit for Virtualization or the Forklift operator), you must follow additional steps before starting the reverse migration. For more information, see Reverse migration issues with forklifted VMs.

## Create a reverse ClusterPair​

note

Skip this section if you have created a bidirectional ClusterPair, and proceed to the next section.

If you initially paired your clusters in a unidirectional manner (from source to destination), you must create a reverse `ClusterPair` to establish pairing from the destination cluster back to the source cluster. The reverse `ClusterPair` enables communication from the destination cluster to the source cluster, allowing failback from the destination to the source cluster.

Run the following command from your destination cluster to create a reverse ClusterPair:

```

storkctl create clusterpair reverse-migration-cluster-pair \

--namespace <migrationnamespace> \

--src-kube-file <destination-kubeconfig-file> \

--dest-kube-file <source-kubeconfig-file> \

--use-existing-objectstorelocation \

--unidirectional

```

important

Ensure to provide the destination kubeconfig file with `src-kube-file` and the source kubeconfig file with `dest-kube-file` as mentioned in the above command.

## Reverse sync your clusters​

If the destination cluster is running applications for some time, the application state on the destination cluster may differ from the source cluster. This can happen due to the creation of new resources or changes in data within stateful applications on the destination cluster.

Since both clusters are accessible, follow the instructions to configure a reverse `MigrationSchedule`:

-
Create a schedule policy on your destination cluster using the instructions in the Create a schedule policy section.

-
Create a migration schedule on your destination cluster using the `storkctl create migrationschedule` command. For more information on how to use the command, see Create MigrationSchedule with storkctl.

note

For operators deployed from the OpenShift OperatorHub, create a migration schedule with the `--exclude-resource-types` flag to exclude operator-related resources, as shown in the following example:

```

storkctl create migrationschedule -c cluster-pair -n zookeeper reverse-migration-schedule --exclude-resource-types ClusterServiceVersion,operatorconditions,OperatorGroup,InstallPlan,Subscription --exclude-selectors olm.managed=true

```

## Perform failback​

You can perform a failback using the `storkctl perform failback` command.

Use the following flags to include or exclude specific namespaces or resources during the failback operation. This gives you greater control over what is being restored.

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

- `--skip-last-mile-migration` - Use this flag if you want to skip the last-mile migration before workloads are activated.

note

You cannot use `--include-namespaces` and `--exclude-namespaces` together, nor can you use `--selectors` and `--exclude-selectors` together, or you'll get an error.

```

storkctl perform failover --selectors=app=busybox --exclude-selectors=app=px-mongo-mongodb

```

```

error: can provide only one of --selectors or --exclude-selectors values at once

```

To start the failback operation, run the following command in the destination cluster:

```

storkctl perform failback -m <reverse-migration-schedule> -n <reverse-migration-schedule-namespace>

```

If the last migration status is in the `PartialSuccess` state, you'll be prompted to proceed with the failback operation. To bypass this prompt, use the `--force` flag.

Example:

```

storkctl perform failback -m reverse-migration-schedule -n zookeeper

```

```

Started failback for MigrationSchedule zookeeper/reverse-migration-schedule

To check failback status use the command : `storkctl get failback failback-reverse-migration-schedule-2024-05-21-115006 -n zookeeper`

```

Examples with filtering:

Namespace filtering:

```

# Perform failback for only specific namespaces

storkctl perform failback -m reverse-migration-schedule -n zookeeper --include-namespaces=app-ns1,app-ns2

```

```

# Perform failback for all namespaces except specific ones

storkctl perform failback -m reverse-migration-schedule -n zookeeper --exclude-namespaces=test-ns

```

Resource filtering:

```

# Perform failback for only the resources with the label app=busybox

storkctl perform failback -m reverse-migration-schedule -n zookeeper --selectors=app=busybox

```

```

# Perform failback for all resources except the ones with the label app=busybox

storkctl perform failback -m reverse-migration-schedule -n zookeeper --exclude-selectors=app=busybox

```

```

# Perform failback for only StatefulSet resources

storkctl perform failback -m reverse-migration-schedule -n zookeeper --resource-types=StatefulSet

```

```

# Perform failback for only Deployment and CronJob resources

storkctl perform failback -m reverse-migration-schedule -n zookeeper --resource-types Deployment --resource-types batch/v1/CronJob

```

### Perform failback for specific resources by name​

You can fail back or exclude specific Kubernetes resources by name using the `--include-objects` or `--exclude-objects` flags. These flags can be specified multiple times for multiple resources.

The format for `--include-objects` and `--exclude-objects` is one of:

- `KIND/NAMESPACE/NAME` (e.g., `VirtualMachine/app-ns/my-vm`)

- `GROUP/VERSION/KIND/NAMESPACE/NAME` (e.g., `apps/v1/Deployment/app-ns/payments-api`)

note

- The `NAMESPACE` in the object path is the namespace where the resource lives, which may differ from the MigrationSchedule namespace specified with `-n`.

- `--include-objects` and `--exclude-objects` are mutually exclusive with each other and with `--selectors`, `--exclude-selectors`, and `--resource-types`.

- Both flags can be combined with `--include-namespaces` and `--exclude-namespaces`.

Include specific resources:

```

# Fail back a specific KubeVirt VM by name

storkctl perform failback -m reverse-migration-schedule -n <namespace> \

  --include-objects VirtualMachine/app-ns/my-vm

```

```

# Fail back multiple resources by name

storkctl perform failback -m reverse-migration-schedule -n <namespace> \

  --include-objects VirtualMachine/app-ns/vm-payments \

  --include-objects VirtualMachine/app-ns/vm-billing

```

```

# Fail back a Deployment by name with full group/version syntax

storkctl perform failback -m reverse-migration-schedule -n <namespace> \

  --include-objects apps/v1/Deployment/app-ns/payments-api

```

Exclude specific resources:

```

# Fail back all resources except a specific VM

storkctl perform failback -m reverse-migration-schedule -n <namespace> \

  --exclude-objects VirtualMachine/app-ns/my-vm

```

## Check failback status​

Run the following command to check the status of the failback operation. You can get the `failback-action-name` from the output of the `storkctl perform failback` command.

```

storkctl get failback <failback-action-name> -n <reverse-migration-schedule-namespace>

```

Example:

```

storkctl get failback failback-reverse-migration-schedule-2024-05-21-115006 -n zookeeper

```

```

NAME                                 CREATED               STAGE       STATUS       MORE INFO

failback-reverse-migration-schedule-2024-05-21-115006   21 May 24 11:50 UTC   Completed   Successful   Scaled up Apps in : 1/1 namespaces

```

If the status is failed, you can use the following command to get more information about the failure:

- Kubernetes

- OpenShift

```

kubectl describe actions <failback-action-name> -n <reverse-migration-schedule-namespace>

```

```

oc describe actions <failback-action-name> -n <reverse-migration-schedule-namespace>

```

## Verify volumes and Kubernetes resources are migrated​

To verify the volumes and Kubernetes resources that are migrated to the source cluster, run the following command:

- Kubernetes

- OpenShift

```

kubectl get all -n <reverse-migration-schedule-namespace>

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

oc get all -n <reverse-migration-schedule-namespace>

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
