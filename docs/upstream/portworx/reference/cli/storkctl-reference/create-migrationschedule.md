# Create MigrationSchedule with storkctl

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/storkctl-reference/create-migrationschedule (Portworx Enterprise latest)

Create MigrationSchedule with storkctl | Portworx Enterprise Documentation

This topic explains how to create and delete a MigrationSchedule using the `storkctl` command-line tool.

note

Starting from Stork 25.5.0, you can use the admin ClusterPair to create migration schedules in any namespace instead of creating a local ClusterPair and referencing it in the migration schedule. For more information, see Use the admin ClusterPair for migrations in any namespace.

### How to use the storkctl command?​

To create a MigrationSchedule using `storkctl`, you can use the `create migrationschedules` or `create migrationschedule` command with specific flags to define the schedule details.

note

In the `storkctl create` command, default values will be applied to all optional parameters in case you do not provide input.

Additionally, validations are implemented that will generate relevant error messages in the event of invalid or incorrect inputs to the command. For example:

```

error: unable to retrieve transformation default/my-resource-transformation, err: resourcetransformations.stork.libopenstorage.org "my-resource-transformation" not found

```

### Preview resources before creating migration schedule​

You can preview the resources without creating the MigrationSchedule by using the `--preview` or `--preview-file` flags with the `storkctl create migrationschedule` command.

These flags allow you to verify all resources, including resources that are not bound to a namespace, such as `ClusterRoles` and `ClusterRoleBindings`, before executing a migration.

#### To preview a migration without running it​

Use the `--preview` flag with the usual command and parameters you would use to create the MigrationSchedule. This performs a dry run and displays the resources that would be included in the MigrationSchedule.

Example:

```

storkctl create migrationschedule -n <migrationNamespace> --namespaces <list of namespaces to migrate> --preview

```

#### To save the preview output to a file​

Use the `--preview-file <filename>.yaml` flag to write the list of resources to a file for review.

Example:

```

storkctl create migrationschedule -n <migrationNamespace> --namespaces <list of namespaces to migrate> --previewFile=output.yaml

```

### Create an interval-based migration schedule​

Run the following command to create a migration schedule with specific configurations, including the cluster pair, namespaces to migrate, migration interval, pre-execution rule, resource transformation, and the namespace for migration resources:

```

storkctl create migrationschedule <migrationScheduleName> \

-c <clusterPairName> \

--namespaces <list of namespaces to migrate> \

-i <time-in-minutes> \

--pre-exec-rule <RuleName> \

--transform-spec <ResourceTransformationName> \

-n <migrationNamespace>

```

Example command to create a schedule policy with the specified interval:

```

storkctl create migrationschedule my-migration-schedule \

-c my-cluster-pair \

--namespaces namespace1,namespace2 \

-i 30 \

--pre-exec-rule mysql-pre-rule \

--transform-spec mysql-service-transform \

-n kube-system

```

```

my-migration-schedule created successfully

```

To view the migration schedule, run the `kubectl get migrationschedule my-migration-schedule -oyaml` command. Example migration schedule:

```

apiVersion: stork.libopenstorage.org/v1alpha1

kind: MigrationSchedule

metadata:

 name: my-migration-schedule

 namespace: kube-system

spec:

 autoSuspend: true

 schedulePolicyName: my-migration-schedule

 suspend: false

 template:

   spec:

     adminClusterPair: ""

     clusterPair: my-cluster-pair

     excludeResourceTypes: null

     excludeSelectors: null

     ignoreOwnerReferencesCheck: false

     includeNetworkPolicyWithCIDR: false

     includeOptionalResourceTypes: null

     includeResources: true

     includeVolumes: true

     namespaceSelectors: null

     namespaces:

     - namespace1

     - namespace2

     postExecRule: ""

     preExecRule: mysql-pre-rule

     purgeDeletedResources: false

     selectors: null

     skipDeletedNamespaces: true

     skipServiceUpdate: false

     startApplications: false

     transformSpecs:

     - mysql-service-transform

```

### Create a migration schedule with namespace selectors and annotations flags​

Run the following command to create a migration schedule with specific configurations, including the cluster pair, namespace selectors, schedule policy, authentication annotations, and the namespace for migration resources:

```

storkctl create migrationschedule <migrationScheduleName> \

-c <clusterPairName> \

--namespace-selectors <key1>=<value1> \

--schedule-policy-name <your-schedule-policy> \

--annotations openstorage.io/auth-secret-namespace=<namespace-where -the-kubernetes-secret-holding-the-auth-token-resides>,openstorage.io/auth-secret-name=<kubernetes-secret-name-which-holds-the-auth-token> \

-n <migrationNamespace>

```

Example:

```

storkctl create migrationschedule my-migration-schedule \

-c my-cluster-pair \

--namespace-selectors stage=production,priority=P0 \

--schedule-policy-name default-daily-policy \

--annotations openstorage.io/auth-secret-namespace=auth-namespace,openstorage.io/auth-secret-name=my-auth-secret \

-n my-migration-namespace

```

Example migration schedule:

```

apiVersion: stork.libopenstorage.org/v1alpha1

kind: MigrationSchedule

metadata:

 annotations:

   openstorage.io/auth-secret-name: my-auth-secret

   openstorage.io/auth-secret-namespace: auth-namespace

 name: my-migration-schedule

 namespace: my-migration-namespace

spec:

 autoSuspend: true

 schedulePolicyName: default-daily-policy

 suspend: false

 template:

   spec:

     adminClusterPair: ""

     clusterPair: my-cluster-pair

     excludeResourceTypes: null

     excludeSelectors: null

     ignoreOwnerReferencesCheck: false

     includeNetworkPolicyWithCIDR: false

     includeOptionalResourceTypes: null

     includeResources: true

     includeVolumes: true

      namespaceSelectors:

         priority: P0

         stage: production

     namespaces: null

     postExecRule: ""

     preExecRule: ""

     purgeDeletedResources: false

     selectors: null

     skipDeletedNamespaces: true

     skipServiceUpdate: false

     startApplications: false

     transformSpecs: null

```

### Create a migration schedule with few boolean flags​

Run the following command to create a migration schedule with specific configurations, including the cluster pair, namespaces to migrate, exclusion of certain resources, purging of deleted resources, and the namespace for migration resources:

```

storkctl create migrationschedule <migrationScheduleName> \

-c <clusterPairName> \

--namespaces <list-of-namespaces-to-migrate> \

-- exclude-resources \

-- purge-deleted-resources \

-n <migrationNamespace>

```

Example:

```

storkctl create migrationschedule my-migration-schedule \

-c my-cluster-pair \

--namespaces namespace1 \

--exclude-resources \

--purge-deleted-resources \

-n namespace1

```

Example migration schedule:

```

apiVersion: stork.libopenstorage.org/v1alpha1

kind: MigrationSchedule

metadata:

 name: my-migration-schedule

 namespace: namespace1

spec:

 autoSuspend: true

 schedulePolicyName: default-migration-policy

 suspend: false

 template:

   spec:

     adminClusterPair: ""

     clusterPair: my-cluster-pair

     excludeResourceTypes: null

     excludeSelectors: null

     ignoreOwnerReferencesCheck: false

     includeNetworkPolicyWithCIDR: false

     includeOptionalResourceTypes: null

     includeResources: false

     includeVolumes: true

     namespaceSelectors: null

     namespaces:

     - namespace1

     postExecRule: ""

     preExecRule: ""

     purgeDeletedResources: true

     selectors: null

     skipDeletedNamespaces: true

     skipServiceUpdate: false

     startApplications: false

     transformSpecs: null

```

### Create a migration schedule for specific VMs​

Starting with Stork 26.5.0, you can create a migration schedule that migrates specific KubeVirt VMs and the resources that they depend on. For prerequisites, migration modes, and limitations, see Migrate specific VMs with a migration schedule.

To migrate all VMs in a namespace and their dependencies, run the following command:

```

storkctl create migrationschedule <migrationScheduleName> \

-c <clusterPairName> \

--namespaces <namespace> \

--schedule-policy-name <your-schedule-policy> \

--enforce-primary-kind=true \

--primary-kind=kubevirt.io/v1/VirtualMachine \

-n <migrationNamespace>

```

To migrate only specific VMs, add the `--include-names` flag:

```

storkctl create migrationschedule <migrationScheduleName> \

-c <clusterPairName> \

--namespaces <namespace> \

--schedule-policy-name <your-schedule-policy> \

--enforce-primary-kind=true \

--primary-kind=kubevirt.io/v1/VirtualMachine \

--include-names=<vm-name1>,<vm-name2> \

-n <migrationNamespace>

```

To migrate everything in the namespace except the VMs and their dependencies, set `--enforce-primary-kind=false`:

```

storkctl create migrationschedule <migrationScheduleName> \

-c <clusterPairName> \

--namespaces <namespace> \

--schedule-policy-name <your-schedule-policy> \

--enforce-primary-kind=false \

-n <migrationNamespace>

```

To see the resources that Stork migrates before you create the schedule, add the `--preview` flag to any of these commands. For more information, see Preview resources before creating migration schedule.

To add or remove VMs on an existing schedule, see storkctl update migrationschedule.

### Set up schedule policy for migration schedule​

You have three options to set up the schedule policy for the migration schedule:

- Use existing policy: Employ the `schedule-policy-name` flag to utilize an already existing schedule policy.

- Create new interval policy: Utilize the `interval` flag to generate a new interval schedule policy with the specified time interval.

- Default Policy: If neither of the above flags is specified, the system will default to using `default-migration-policy`, which is a schedule policy with a 30-minute interval.

note

You can only provide either the `schedule-policy-name` or the `interval` flag; using both is not allowed.

### Create migrationschedule command flags​

You can include one or more of the following flags when using the `storkctl create migrationschedule` command based on your specific requirements:

FieldDescriptionTypeDefault valueOptional

`-h`, `--help`Help for migration schedules

`--admin-cluster-pair`Specify the name of the admin ClusterPair used to migrate cluster-scoped resources, if the ClusterPair is present in a non-admin namespace.stringYes

`--annotations`Add required annotations to the resource in comma-separated key value pairs. key1=value1,key2=value2,...map [string] stringYes

`-c`, `--cluster-pair`Specify the name of the ClusterPair in the same namespace to be used for the migration.stringNo

`--disable-auto-suspend`Prevent automatic suspension of DR migration schedules on the source cluster in case of a disaster.booleanfalseYes

`--disable-skip-deleted-namespaces`If present, Stork will fail the migration when it encounters a namespace that is deleted but specified in the namespaces field. By default, Stork ignores deleted namespaces during migration.booleanfalseYes

`--enforce-primary-kind`Controls how primary kinds, such as KubeVirt VMs, are selected for migration. Set to `true` to migrate only the primary kinds that you specify with `--primary-kind` and their dependencies. Set to `false` to migrate all resources in the namespace except the primary kinds and their dependencies. If you do not set this flag, Stork migrates every resource in the namespace. Available from Stork 26.5.0.booleanNot setYes

`--exclude-resource-types`Comma-separated list of the specific resource types which need to be excluded from migration, ex: Deployment,PersistentVolumeClaim.stringsYes

`--exclude-resources`If present, Kubernetes resources will not be migrated.booleanfalseYes

`--exclude-selectors`Resources with the provided labels will be excluded from the migration. All the labels provided in this option will be OR'ed.map [string] stringYes

`--exclude-volumes`If present, the underlying Portworx volumes will not be migrated. This is the only allowed and default behavior in Sync-DR use-cases or when storage options are not provided in the cluster pair.booleanTrue for Sync-DR and False for Async-DR use cases.Yes

`--ignore-owner-references-check`If set, resources with ownerReferences will also be migrated, even if the corresponding owners are getting migrated.booleanfalseYes

`--include-names`Specify a comma-separated list of primary kind object names to migrate. If you omit this flag, Stork migrates all objects of the primary kind in the namespace. Requires `--enforce-primary-kind=true`. You cannot combine this flag with `--selectors` or `--exclude-selectors`. Available from Stork 26.5.0.stringsYes

`--include-jobs`Set this flag to ensure that K8s Job resources are migrated. By default, the Job resources are not migrated.booleanfalseYes

`--include-network-policy-with-cidr`If set, the underlying network policies will be migrated even if a fixed CIDR is present on them.booleanfalseYes

`-i`, `--interval`Specify the time interval, in minutes, at which Stork should trigger migrations.int30Yes

`--namespace-selectors`Resources in the namespaces with the specified namespace labels will be migrated. All the labels provided in this option will be OR'ed.map [string] stringYes

`--namespaces`Specify the comma-separated list of namespaces to be included in the migration.stringsYes (From Stork version 23.5.0)

`--post-exec-rule`Specify the name of the rule to be executed after every migration is triggered.stringYes

`--pre-exec-rule`Specify the name of the rule to be executed before every migration is triggered.stringYes

`--primary-kind`Specify the kind of the primary resource to migrate, in `group/version/Kind` format. Currently, the only supported value is `kubevirt.io/v1/VirtualMachine`. Required when `--enforce-primary-kind=true`, and valid only with that setting. Available from Stork 26.5.0.stringYes

`--purge-deleted-resources`Set this flag to automatically delete Kubernetes resources in the target cluster when they are removed from the source cluster.booleanfalseYes

`-s`, `--schedule-policy-name`Name of the schedule policy to use. If you want to create a new interval policy, use the `--interval` flag instead.stringdefault-migration-policyYes

`--selectors`Only resources with the provided labels will be migrated. All the labels provided in this option will be OR'ed.map [string] stringYes

`--skip-service-update`If set, service objects will be skipped during migration.booleanfalseYes

`-a`, `--start-applications`If present, the applications will be scaled up on the target cluster after a successful migration.booleanfalseYes

`--suspend`Flag to denote whether schedule should be suspended on creation.booleanfalseYes

`--transform-spec`Specify the ResourceTransformation spec to be applied during migration.stringYes

In this topic:
