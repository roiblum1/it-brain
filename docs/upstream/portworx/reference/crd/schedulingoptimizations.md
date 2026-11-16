# SchedulingOptimization CRD reference

Source: https://docs.portworx.com/portworx-enterprise/reference/crd/schedulingoptimizations (Portworx Enterprise latest)

SchedulingOptimization CRD reference | Portworx Enterprise Documentation

SchedulingOptimization is a cluster-scoped request asking Stork to re-evaluate whether running workloads are still placed where the scheduler would put them today and to converge them back. The storage driver creates one CR per request (for example after a pool failover moves volume replicas). Stork only updates status; the creator owns deletion..

## SchedulingOptimization​

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

`spec`SchedulingOptimizationSpec holds one named field per optimization kind, each
with its own config block; future kinds are additive named fields. At least
one kind must be enabled for the request to do anything.`object`

`status`SchedulingOptimizationStatus is the status of a scheduling optimization request`object`

### `spec` fields​

FieldDescriptionType

`spec.vmHyperconvergence`VMHyperconvergence requests remediation of KubeVirt VMs that are no
longer running on a node holding a replica of their volumes.`object`

`spec.vmHyperconvergence.coolOffPeriod`CoolOffPeriod overrides the cluster-wide default for the minimum time
between Stork-triggered live migrations of the same VM.`string`

`spec.vmHyperconvergence.enabled`Enabled is the request marker: true means run VM hyperconvergence
remediation. The typical request sets only this field.`boolean`

`spec.vmHyperconvergence.maxParallelMigrations`MaxParallelMigrations overrides the cluster-wide default for the
engine's per-run worker configuration. In practice this sets the
taskmanager's distributor buffer size — a backpressure hint, not
a hard semaphore — plus the workers value the engine reports on
its logs and clamp events. The hard cap on concurrently-running
live migrations comes from KubeVirt's own
MigrationConfiguration.parallelMigrationsPerCluster (default 5),
which queues excess VMIMs on its side.`integer`

### `status` fields​

FieldDescriptionType

`status.finishTimestamp`FinishTimestamp records when the run reached the final stage`string`

`status.lastUpdateTimestamp`LastUpdateTimestamp is bumped on every status write — a liveness signal
for the creator while counters sit still during a long migration`string`

`status.reason`Reason carries a short explanation of the terminal Status whenever
there is something worth stating. Populated on non-clean outcomes
(candidates outstanding, driver failure) and on clean no-op passes
where the run completed successfully without doing any work — an
opt-out CR (no optimization kind enabled, or the kind's Enabled=false)
finalizes as Successful with a reason string; an already-converged
fleet finalizes as Successful with an empty reason.`string`

`status.stage`SchedulingOptimizationStageType is where in the workflow the request is`string`

`status.startTimestamp`StartTimestamp records when the request was promoted and the run started`string`

`status.status`SchedulingOptimizationStatusType is how the request is going`string`

`status.vmHyperconvergence`VMHyperconvergence holds the result of VM hyperconvergence remediation,
mirroring the spec field of the same name`object`

`status.vmHyperconvergence.details`Details lists per-VM outcomes for evaluator-side skips and every
candidate the migration engine ran. Bounded by maxNonHyperconvergedPerRun
in the evaluator. Successful/Skipped/Failed counters are always exact
regardless of Details content.`array`

`status.vmHyperconvergence.details.name`Name of the VirtualMachineInstance`string`

`status.vmHyperconvergence.details.namespace`Namespace of the VirtualMachineInstance`string`

`status.vmHyperconvergence.details.reason`Reason is the skip reason or failure text, set when Status is not
Successful. The format is "<Enum>: <detail>" — the stork enum (e.g.
MigrationRunFailed, MigrationTimedOut, EvaluationError), a colon
separator, and a detail string. For failed migrations the detail
begins with "vmim=<ns>/<name>" and may be followed by KubeVirt's
own failureReason (e.g.
"MigrationRunFailed: vmim=ns/mig-vmi-a: unable to attach volume").
For an EvaluationError skip the detail is the raw evaluator error
(e.g. "EvaluationError: persistentvolumeclaims "foo" not found").
Clients matching on the enum should split on the first ": " rather
than comparing the full string. The detail is capped to keep CR
size bounded.`string`

`status.vmHyperconvergence.details.status`Status is the per-VM outcome`string`

`status.vmHyperconvergence.failed`Failed counts migrations attempted but reported failed by KubeVirt`integer`

`status.vmHyperconvergence.skipped`Skipped counts non-hyperconverged candidates that a filter blocked`integer`

`status.vmHyperconvergence.successful`Successful counts live migrations that completed successfully`integer`

In this topic:
