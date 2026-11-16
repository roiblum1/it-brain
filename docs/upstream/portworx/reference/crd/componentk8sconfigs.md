# ComponentK8sConfig CRD reference

Source: https://docs.portworx.com/portworx-enterprise/reference/crd/componentk8sconfigs (Portworx Enterprise latest)

ComponentK8sConfig CRD reference | Portworx Enterprise Documentation

Schema and configuration details for the ComponentK8sConfig custom resource definition (CRD), which is used by the Portworx Operator to manage Kubernetes-based component configurations.

important

The component names specified in `spec.components.componentNames` are case sensitive. For a list of valid component names with the correct capitalization, refer to the mapping of components to workloads, pods, and containers.

## ComponentK8sConfig​

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

`spec`ComponentK8sConfigSpec defines the desired state of ComponentK8sConfig`object`

`status`ComponentK8sConfigStatus defines the synchronization state of the configuration.`object`

### `spec` fields​

FieldDescriptionType

`spec.globalConfig`GlobalConfig contains settings that apply to all Portworx components. Component-specific settings in `spec.components` override global settings. You can configure labels, annotations, placement rules, and a priority class globally. You can’t configure resource requirements globally; specify them per component.

Note: Supported in Portworx Operator 25.6.0 or later.`object`

`spec.globalConfig.labels`Labels applied to all Portworx component pods.`object`

`spec.globalConfig.annotations`Annotations applied to all Portworx component pods.`object`

`spec.globalConfig.placement`Placement rules (node affinity and tolerations) applied to all Portworx component pods.`object`

`spec.globalConfig.priorityClass``PriorityClass` applied to all Portworx component pods. This helps ensure Portworx pods are scheduled with the specified priority and are less likely to be evicted under resource pressure. For more information, see Pod Priority and Preemption.`string`

`spec.components`Components is the list of Portworx components that are deployed and managed by PX Operator`array`

`spec.components.componentNames`ComponentNames for which the configurations will be applied.`array`

`spec.components.workloadConfigs`WorkloadConfig contains the configuration for the various workloads - deployments, daemonset or pods of a component.`array`

`spec.components.workloadConfigs`.
`annotations`Annotations are the annotations to be applied to the component`object`

`spec.components.workloadConfigs.`
`containerConfigs`ContainerConfig contains container configuration for all or some containers of the component`array`

`spec.components.workloadConfigs.`
`containerConfigs.containerNames`ContainerNames is the list of containers for a workload on which these resource configurations will be applied.`array`

`spec.components.workloadConfigs.`
`containerConfigs.resources`Resources contains resource requirements for all the containers selected by the containerNames`object`

`spec.components.workloadConfigs.`
`containerConfigs.resources.claims`Claims lists the names of resources, defined in spec.resourceClaims,
that are used by this container.

This is an alpha field and requires enabling the
DynamicResourceAllocation feature gate.

This field is immutable. It can only be set for containers.`array`

`spec.components.workloadConfigs.`
`containerConfigs.resources.claims.name`Name must match the name of one entry in pod.spec.resourceClaims of
the Pod where this field is used. It makes that resource available
inside a container.`string`

`spec.components.workloadConfigs.`
`containerConfigs.resources.limits`Limits describes the maximum amount of compute resources allowed.
More info: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/`object`

`spec.components.workloadConfigs.`
`containerConfigs.resources.requests`Requests describes the minimum amount of compute resources required.
If Requests is omitted for a container, it defaults to Limits if that is explicitly specified,
otherwise to an implementation-defined value. Requests cannot exceed Limits.
More info: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/`object`

`spec.components.workloadConfigs.`
`containerConfigs.args`Container arguments to override on all containers selected by `containerNames`. The operator merges each entry into the container's existing args by matching the flag name (the substring before `=`). Matching args are replaced in place; new args are appended.

Available in Operator 26.5.0 or later. Each entry must be a POSIX-style flag: long form `--name` or `--name=value` (name has two or more characters after the double dash), or short form `-x` or `-x=value` (single character after a single dash). Single-dash multi-character flags such as `-kube-api-qps=50` are not supported — pflag-based CSI sidecar containers parse them as combined short flags and fail to start. The Kubernetes API server rejects entries that do not match this format.`array`

`spec.components.workloadConfigs.`
`containerConfigs.env`Environment variables to override on all containers selected by `containerNames`. The operator merges each entry into the container's existing environment variables by matching `name`. A matching variable is replaced in place; a new variable is appended.

Available in Operator 26.5.0 or later. Only components that support environment variable overrides accept this field, and the `ComponentK8sConfig` is rejected with `status.phase` set to `VALIDATION_FAILED` if you set `env` on a container that does not support it. The `CSI` component does not support `env`; use `args` instead.`array`

`spec.components.workloadConfigs.`
`labels`Labels are the labels to be applied to the component`object`

`spec.components.workloadConfigs.`
`placement`Placement contains placement information for each component`object`

`spec.components.workloadConfigs.`
`placement.nodeAffinity`NodeAffinity is used to restrict Portworx on certain nodes. It works similarly to the Kubernetes node affinity feature.`object`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution`The scheduler will prefer to schedule pods to nodes that satisfy
the affinity expressions specified by this field, but it may choose
a node that violates one or more of the expressions. The node that is
most preferred is the one with the greatest sum of weights, i.e.
for each node that meets all of the scheduling requirements (resource
request, requiredDuringScheduling affinity expressions, etc.),
compute a sum by iterating through the elements of this field and adding
"weight" to the sum if the node matches the corresponding matchExpressions; the
node(s) with the highest sum are the most preferred.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference`A node selector term, associated with the corresponding weight.`object`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference.matchExpressions`A list of node selector requirements by node's labels.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference.matchExpressions.key`The label key that the selector applies to.`string`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference.matchExpressions.operator`Represents a key's relationship to a set of values.
Valid operators are In, NotIn, Exists, DoesNotExist. Gt, and Lt.`string`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference.matchExpressions.values`An array of string values. If the operator is In or NotIn,
the values array must be non-empty. If the operator is Exists or DoesNotExist,
the values array must be empty. If the operator is Gt or Lt, the values
array must have a single element, which will be interpreted as an integer.
This array is replaced during a strategic merge patch.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference.matchFields`A list of node selector requirements by node's fields.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference.matchFields.key`The label key that the selector applies to.`string`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference.matchFields.operator`Represents a key's relationship to a set of values.
Valid operators are In, NotIn, Exists, DoesNotExist. Gt, and Lt.`string`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`preference.matchFields.values`An array of string values. If the operator is In or NotIn,
the values array must be non-empty. If the operator is Exists or DoesNotExist,
the values array must be empty. If the operator is Gt or Lt, the values
array must have a single element, which will be interpreted as an integer.
This array is replaced during a strategic merge patch.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`preferredDuringSchedulingIgnoredDuringExecution.`
`weight`Weight associated with matching the corresponding nodeSelectorTerm, in the range 1-100.`integer`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution`If the affinity requirements specified by this field are not met at
scheduling time, the pod will not be scheduled onto the node.
If the affinity requirements specified by this field cease to be met
at some point during pod execution (e.g. due to an update), the system
may or may not try to eventually evict the pod from its node.`object`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms`Required. A list of node selector terms. The terms are ORed.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms.matchExpressions`A list of node selector requirements by node's labels.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms.matchExpressions.key`The label key that the selector applies to.`string`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms.matchExpressions.operator`Represents a key's relationship to a set of values.
Valid operators are In, NotIn, Exists, DoesNotExist. Gt, and Lt.`string`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms.matchExpressions.values`An array of string values. If the operator is In or NotIn,
the values array must be non-empty. If the operator is Exists or DoesNotExist,
the values array must be empty. If the operator is Gt or Lt, the values
array must have a single element, which will be interpreted as an integer.
This array is replaced during a strategic merge patch.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms.matchFields`A list of node selector requirements by node's fields.`array`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms.matchFields.key`The label key that the selector applies to.`string`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms.matchFields.operator`Represents a key's relationship to a set of values.
Valid operators are In, NotIn, Exists, DoesNotExist. Gt, and Lt.`string`

`spec.components.workloadConfigs.`
`placement.nodeAffinity.`
`requiredDuringSchedulingIgnoredDuringExecution.`
`nodeSelectorTerms.matchFields.values`An array of string values. If the operator is In or NotIn,
the values array must be non-empty. If the operator is Exists or DoesNotExist,
the values array must be empty. If the operator is Gt or Lt, the values
array must have a single element, which will be interpreted as an integer.
This array is replaced during a strategic merge patch.`array`

`spec.components.workloadConfigs.`
`placement.tolerations`Tolerations specifies a list of tolerations that will be applied to Portworx pods so that they can run on nodes with matching taints.`array`

`spec.components.workloadConfigs.`
`placement.tolerations.effect`Effect indicates the taint effect to match. Empty means match all taint effects.
When specified, allowed values are NoSchedule, PreferNoSchedule and NoExecute.`string`

`spec.components.workloadConfigs.`
`placement.tolerations.key`Key is the taint key that the toleration applies to. Empty means match all taint keys.
If the key is empty, operator must be Exists; this combination means to match all values and all keys.`string`

`spec.components.workloadConfigs.`
`placement.tolerations.operator`Operator represents a key's relationship to the value.
Valid operators are Exists and Equal. Defaults to Equal.
Exists is equivalent to wildcard for value, so that a pod can
tolerate all taints of a particular category.`string`

`spec.components.workloadConfigs.`
`placement.tolerations.tolerationSeconds`TolerationSeconds represents the period of time the toleration (which must be
of effect NoExecute, otherwise this field is ignored) tolerates the taint. By default,
it is not set, which means tolerate the taint forever (do not evict). Zero and
negative values will be treated as 0 (evict immediately) by the system.`integer`

`spec.components.workloadConfigs.`
`placement.tolerations.value`Value is the taint value the toleration matches to.
If the operator is Exists, the value should be empty, otherwise just a regular string.`string`

`spec.components.workloadConfigs.`
`priorityClass``PriorityClass` applied to the component workload pods. This setting overrides `spec.globalConfig.priorityClass`. For more information, see Pod Priority and Preemption.

Note: Supported in Portworx Operator 25.6.0 or later.`string`

`spec.components.workloadConfigs.`
`workloadNames`WorkloadNames is the list of workloads - deployment/daemonset/pod of a component for which the configurations will be applied.`array`

### `status` fields​

FieldDescriptionType

`status.phase`Phase of the ComponentK8sConfig is a simple, high-level summary of where the ComponentK8sConfig is in its lifecycle. The condition array contains more detailed information about the state of the cluster.`string`

`status.reason`Reason is CamelCase messages split with commas indicating details about why the ComponentK8sConfig is in this state.`string`
