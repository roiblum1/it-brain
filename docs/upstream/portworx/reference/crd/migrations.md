# Migration CRD reference

Source: https://docs.portworx.com/portworx-enterprise/reference/crd/migrations (Portworx Enterprise latest)

Migration CRD reference | Portworx Enterprise Documentation

Migration represents migration status.

## Migration​

FieldDescriptionType

`apiVersion`APIVersion defines the versioned schema of this representation of an object.
Servers should convert recognized schemas to the latest internal value, and
may reject unrecognized values.
More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources`string`

`kind`Kind is a string value representing the REST resource this object represents.
Servers may infer this from the endpoint the client submits requests to.
Cannot be updated.
In CamelCase.
More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds`string`

`spec`MigrationSpec is the spec used to migrate apps between clusterpairs`object`

`status`MigrationStatus is the status of a migration operation`object`

### `spec` fields​

FieldDescriptionType

`spec.adminClusterPair`AdminClusterPair is the name of the admin cluster pair used for managing the migration.`string`

`spec.clusterPair`ClusterPair is the name of the cluster pair using which the migration will be performed.`string`

`spec.enforcePrimaryKind`EnforcePrimaryKind controls which workload class this migration covers
(VM-granularity feature; only KubeVirt virtual machines are supported). Tri-state:
 nil → legacy collection (today's behaviour, default for upgraded schedules)
 true → primaries-only: only objects of the kinds enumerated in PrimaryKinds
 are collected as primaries, with their dep closure walked by the
 per-Kind handler. Requires PrimaryKinds to be non-empty.
 false → non-primaries-only: every namespace-wide object EXCEPT the
 registered primary Kinds and their dep closure is collected.
 PrimaryKinds is ignored when EnforcePrimaryKind=false.
See .specify/specs/001-vm-granularity-migration/spec.md FR-002, FR-003, FR-004.`boolean`

`spec.excludeResourceTypes`ExcludeResourceTypes is a list of resource types that should be excluded from the migration.`array`

`spec.excludeSelectors`ExcludeSelectors is a set of label-based selectors used to filter out specific objects from the migration.`object`

`spec.ignoreOwnerReferencesCheck`IgnoreOwnerReferencesCheck specifies whether the migration should ignore checks related to owner references.`boolean`

`spec.includeNetworkPolicyWithCIDR`IncludeNetworkPolicyWithCIDR determines whether network policies with CIDR-based rules should be included in the migration.`boolean`

`spec.includeOptionalResourceTypes`IncludeOptionalResourceTypes is a list of optional Kubernetes resource types that should be included in the migration.`array`

`spec.includeResources`IncludeResources specifies whether Kubernetes resources (such as Deployments, ConfigMaps, etc.) should be included in the migration.`boolean`

`spec.includeVolumes`IncludeVolumes specifies whether underlying volumes should be included in the migration.`boolean`

`spec.namespaceSelectors`NamespaceSelectors is a set of label-based selectors used to filter which namespaces should be migrated.`object`

`spec.namespaces`Namespaces is a list of namespaces that should be migrated to the destination cluster.`array`

`spec.postExecRule`PostExecRule is the name of the rule that should be executed after migration completes.`string`

`spec.preExecRule`PreExecRule is the name of the rule that should be executed before migration starts.`string`

`spec.primaryKinds`PrimaryKinds enumerates the primary Kinds to migrate when
EnforcePrimaryKind=true. Ignored when EnforcePrimaryKind is nil or false.
Each entry's Kind MUST appear in the compiled-in primary-Kind registry
(only kubevirt.io/v1/VirtualMachine is supported).`array`

`spec.primaryKinds.includeNames`IncludeNames narrows the entry to specific instance names within the
schedule's namespaces. When empty, every instance of Kind in scope is
selected (subject to MigrationSpec.Selectors / ExcludeSelectors).
When non-empty, the global Selectors / ExcludeSelectors MUST be empty
(validator-enforced mutex).`array`

`spec.primaryKinds.kind`Kind in canonical "group/version/kind" form (e.g.
"kubevirt.io/v1/VirtualMachine"). Only the registered
primary Kinds are accepted. Currently, only kubevirt.io/v1/VirtualMachine is supported.`string`

`spec.purgeDeletedResources`PurgeDeletedResources specifies whether deleted resources (that existed before but no longer exist) should be removed from the destination cluster.`boolean`

`spec.selectors`Selectors is a set of label-based selectors used to filter the objects that should be included in the migration.`object`

`spec.skipDeletedNamespaces`SkipDeletedNamespaces determines whether namespaces that have been deleted should be skipped during migration.`boolean`

`spec.skipServiceUpdate`SkipServiceUpdate determines whether service updates should be skipped during migration.`boolean`

`spec.startApplications`StartApplications determines whether the migrated applications should be started on the destination cluster after migration.`boolean`

`spec.transformSpecs`TransformSpecs is a list of transformation specifications that should be applied to Kubernetes resources before they are migrated.`array`

### `status` fields​

FieldDescriptionType

`status.resources.status`MigrationStatusType is the status of the migration`string`

`status.stage`MigrationStageType is the stage of the migration`string`

`status.status`MigrationStatusType is the status of the migration`string`

`status.summary`Summary provides a short summary on the migration`object`

`status.summary.elapsedTimeForResourceMigration`ElapsedTimeForResourceMigration provides the total time the
resource migration stage has been running or the total time
taken for the resource migration to complete if the volume migration has finished`string`

`status.summary.elapsedTimeForVolumeMigration`ElapsedTimeForVolumeMigration provides the total time the
volume migration stage has been running or the total time
taken for the volume migration to complete if the volume migration has finished`string`

`status.summary.numOfMigratedResources`NumberOfMigratedResources gives the total count of migrated k8s resources`integer`

`status.summary.numOfMigratedVolumes`NumberOfMigratedVolumes gives the total count of successfully migrated volumes`integer`

`status.summary.totalBytesMigrated`TotalBytesMigrated gives the total amount of bytes migrated across all the volumes`integer`

`status.summary.totalNumberOfResources`TotalNumberOfResources gives the total count of resources`integer`

`status.summary.totalNumberOfVolumes`TotalNumberOfVolumes gives the total count of volumes`integer`

`status.volumes.status`MigrationStatusType is the status of the migration`string`

In this topic:
