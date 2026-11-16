# Configure Portworx Pods and Containers

Source: https://docs.portworx.com/portworx-enterprise/how-to-guides/configure-resource-limits (Portworx Enterprise latest)

Configure Portworx Pods and Containers | Portworx Enterprise Documentation

Use the `ComponentK8sConfig` custom resource (CR) to configure CPU and memory limits, tolerations, node affinity, labels, annotations, priority class, and container arguments across Portworx components. This CR simplifies configuration management and improves consistency in large environments.

With `ComponentK8sConfig`, you can:

- Centralize Kubernetes configuration for all Portworx components

- Improve consistency and manageability at scale

- Apply fine-grained controls per component, workload, or container

- Configure per-container arguments for CSI sidecar containers

If you are already using the `StorageCluster` to configure these settings, you can migrate them to `ComponentK8sConfig`. For details, see Migrate from StorageCluster to ComponentK8sConfig.

To learn more about the various fields that you can configure in the ComponentK8sConfig CR, see ComponentK8sConfig CRD reference.

## Prerequisites​

- Ensure that you are running Portworx Operator version 25.3.0 or later.

## Configuration guidelines​

Follow the guidelines below when using `ComponentK8sConfig`:

- Component names are case-sensitive. Use the exact component names as listed in the Mapping of components to workloads table. For example:

- Use `Portworx Telemetry` (not `Portworx telemetry`)

- Use `Stork` (not `stork`)

- Use `Alert Manager` (not `AlertManager`)

- Use `Cert Manager` (not `Cert manager`)

- Avoid reusing container names across blocks for the same workload to prevent unintended overrides.

- Labels and annotations defined at the component level are inherited by all pods, workloads, and services under that component.

- Starting with Portworx Operator version 26.4.0, you can set labels and annotations on operator-managed Kubernetes Services using `ComponentK8sConfig`. Use the `service/<service-name>` format as the workload name when targeting a service (for example, `service/stork-service`).

- Starting with Portworx Operator version 25.5.0, if you delete the `ComponentK8sConfig` custom resource (CR) and revert to using the `StorageCluster` for configuration, the Portworx Operator triggers a restart of both Portworx and KVDB pods. This ensures that the operator re-applies the configuration correctly from the `StorageCluster` resource.

## Migrate from StorageCluster to ComponentK8sConfig​

If you configure Kubernetes settings in your `StorageCluster`, migrate them to `ComponentK8sConfig` for better modularity and long-term maintainability.

To initiate migration:

- Add the following annotation to your `StorageCluster` object:

```

 metadata:

   annotations:

     portworx.io/migrate-configs: "true"

```

-
The Portworx Operator:

-
Creates a `ComponentK8sConfig` CR automatically, if one is not already present.

-
Migrates supported settings from the `StorageCluster` (STC) object to the new CR.

-
Adds a status condition to indicate successful migration:

```

status:

  conditions:

    - type: ConfigMigration

      status: Completed

      message: 'successfully migrated configs to componentK8sConfig CR'

```

important

After a successful migration, configure resource limits, tolerations, and affinity exclusively in `ComponentK8sConfig`. The operator ignores configuration changes in the `StorageCluster`, and `ComponentK8sConfig` is the single source of truth for these configurations.

note

-
After migration, clean up the configurations in the `StorageCluster` object that were migrated to `ComponentK8sConfig`; Portworx Operator gives precedence to the `ComponentK8sConfig` CR and ignores the equivalent settings in the `StorageCluster` CR.

-
If you use GitOps to manage Kubernetes objects, update the Git repository with the new `ComponentK8sConfig` custom resource (CR) created as part of the migration.

It is not mandatory to use the migration feature by using the annotation; you can also perform the migration manually by creating a new `ComponentK8sConfig` CR in your Git repository and applying it to the cluster. Confirm that the configuration is applied successfully. If the new configuration is working as expected, remove the duplicate settings from the `StorageCluster` custom resource.

## Verify your configuration​

Use the following commands to confirm that your configuration was applied:

```

kubectl get componentk8sconfig

kubectl describe componentk8sconfig <componentk8sconfig-name>

```

Check the value of the `status.phase` field. A value of `ACCEPTED` indicates that the operator successfully processed your configuration. For more information, review the `status.reason` field.

## Mapping of components to workloads, pods, and containers​

The table below lists each component, its Kubernetes workload(s), the workload type, the expected pod name pattern created by that workload, and the containers in those pods.

ComponentWorkload nameWorkload typePod name patternContainers in the pod

Cert Manager`cert-manager``Deployment``cert-manager-*``cert-manager-controller`

`cert-manager-cainjector``Deployment``cert-manager-cainjector-*``cert-manager-cainjector`

`cert-manager-webhook``Deployment``cert-manager-webhook-*``cert-manager-webhook`

`service/cert-manager``Service`N/AN/A

`service/cert-manager-cainjector``Service`N/AN/A

`service/cert-manager-webhook``Service`N/AN/A

Portworx Proxy`portworx-proxy``DaemonSet``portworx-proxy-*``portworx-proxy`

`service/portworx-service``Service`N/AN/A

Portworx Plugin`px-plugin``Deployment``px-plugin--``px-plugin`

`px-plugin-proxy``Deployment``px-plugin-proxy--``nginx`

`service/px-plugin``Service`N/AN/A

`service/px-plugin-proxy``Service`N/AN/A

Stork`stork``Deployment``stork--``stork`

`stork-scheduler``Deployment``stork-scheduler--``stork-scheduler`

`service/stork-service``Service`N/AN/A

Autopilot`autopilot``Deployment``autopilot--``autopilot`

`service/autopilot``Service`N/AN/A

Portworx Telemetry`px-telemetry-registration``Deployment``px-telemetry-registration--``registration`, `envoy`

`px-telemetry-metrics-collector``Deployment``px-telemetry-metrics-collector--``collector`, `envoy`

`px-telemetry-phonehome``DaemonSet``px-telemetry-phonehome-*``log-upload-service`, `envoy`

PVC Controller`portworx-pvc-controller``Deployment``portworx-pvc-controller--``portworx-pvc-controller-manager`

Prometheus`px-prometheus-operator``Deployment``px-prometheus-operator--``px-prometheus-operator`

`px-prometheus``Prometheus instance``px-prometheus-*``px-prometheus`

`service/px-prometheus``Service`N/AN/A

CSI`px-csi-ext``Deployment``px-csi-ext--`
`csi-external-provisioner`, `csi-attacher`, `csi-snapshotter`, `csi-resizer`, `csi-snapshot-controller`, `csi-health-monitor-controller`

`service/px-csi-service``Service`N/AN/A

Portworx API`portworx-api``DaemonSet``portworx-api-*``portworx-api`, `csi-node-driver-registrar`

`service/portworx-api``Service`N/AN/A

Storage`storage``Pod``storage``portworx`

`service/portworx-service``Service`N/AN/A

KVDB`portworx-kvdb``Pod``portworx-kvdb``portworx-kvdb`

`service/portworx-kvdb-service``Service`N/AN/A

Alert Manager`portworx``Alertmanager instance``portworx-alertmanager-*``portworx-alertmanager`

`service/alertmanager-portworx``Service`N/AN/A

Integration Operator`px-integration-operator``Deployment``px-integration-operator--``manager`

Portworx Fusion`fusion-controller``Deployment``fusion-controller-*``controller`

`fusion-webhook``Deployment``fusion-webhook-*``webhook`

PxLibsUpdate`px-libs-update``DaemonSet``px-libs-update-*``pxlib-update`

## Basic usage examples​

Based on the components mapping, the following examples demonstrate how to configure Kubernetes settings using `ComponentK8sConfig`.

- Set resource limits

- Apply placement rules and tolerations

- Add labels and annotations

- Configure priority class

- Configure CSI sidecar container arguments

### Set resource limits​

This example limits each `stork` and `autopilot` container to 1 CPU and 256 MiB of memory, with requests set to 500m CPU and 128 MiB of memory:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: stork-autopilot-resources

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - Stork

        - Autopilot

      workloadConfigs:

        - workloadNames:

            - stork

            - autopilot

          containerConfigs:

            - containerNames:

                - stork

                - autopilot

              resources:

                requests:

                  cpu: "500m"

                  memory: "128Mi"

                limits:

                  cpu: "1000m"

                  memory: "256Mi"

```

### Apply placement rules and tolerations​

To pin `px-csi-ext` pods to specific nodes and configure tolerations:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: csi-placement-config

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - CSI

      workloadConfigs:

        - workloadNames:

            - px-csi-ext

          placement:

            nodeAffinity:

              requiredDuringSchedulingIgnoredDuringExecution:

                nodeSelectorTerms:

                  - matchExpressions:

                      - key: px-schedule

                        operator: NotIn

                        values:

                          - "false"

            tolerations:

              - key: px-schedule

                operator: Equal

                value: value

                effect: NoSchedule

```

### Add labels and annotations​

To apply environment-specific metadata to all `prometheus` pods:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: prometheus-metadata

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - Prometheus

      labels:

        portworx.io/env: dev

      annotations:

        portworx.io/env: dev

```

The operator automatically applies these labels and annotations to all pods and workloads in the `prometheus` component.

### Configure priority class​

note

Priority class configuration is supported in Portworx Operator 25.6.0 or later.

Kubernetes Pod Priority and Preemption allows you to assign priority values to pods. Higher-priority pods are scheduled before lower-priority pods and are protected from eviction when resources are constrained.

For Portworx components, assigning a high priority class ensures that:

- Portworx pods are always scheduled, even when nodes are at full capacity

- Portworx pods are less likely to be preempted when the cluster is under resource pressure

- Communication with the Kubernetes API server remains stable

You can configure a priority class for Portworx components in two ways:

- Globally using `spec.globalConfig.priorityClass` to apply the same priority class to all Portworx components

- Per-component using `spec.components.workloadConfigs.priorityClass` to override the global priority class for specific components

#### Apply priority class globally to all components​

This example applies the predefined `system-node-critical` priority class to all Portworx components:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: global-priority-config

  namespace: <portworx>

spec:

  globalConfig:

    priorityClass: system-node-critical

```

#### Apply priority class to specific components​

This example applies the `system-node-critical` priority class only to the Portworx storage component:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: storage-priority-config

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - Storage

      workloadConfigs:

        - workloadNames:

            - storage

          priorityClass: system-node-critical

```

#### Override global priority class for specific components​

This example sets a global priority class for all components, but overrides it for the CSI component:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: mixed-priority-config

  namespace: <portworx>

spec:

  globalConfig:

    priorityClass: system-node-critical

  components:

    - componentNames:

        - CSI

      workloadConfigs:

        - workloadNames:

            - px-csi-ext

          priorityClass: system-cluster-critical

```

In this example, all Portworx components use `system-node-critical` except the CSI component, which uses `system-cluster-critical`.

note

You can also use custom PriorityClass resources with Portworx components. For information on creating custom PriorityClass resources, see the Kubernetes documentation on Pod Priority and Preemption.

### Configure CSI sidecar container arguments​

You can configure command-line arguments for individual CSI sidecar containers to tune throughput and concurrency. This is useful at scale where the default settings may not provide sufficient throughput for high-volume snapshot or provisioning operations.

note

This feature requires Portworx Operator 26.5.0 or later.

The operator merges each argument into the container's existing args by matching the flag name (the substring before `=`). Matching args are replaced in place; new args are appended.

Each argument must use a POSIX-style flag format:

- Long form: `--name` or `--name=value` (name has two or more characters)

- Short form: `-x` or `-x=value` (single character)

Single-dash multi-character flags such as `-kube-api-qps=50` are not supported. CSI sidecar containers use pflag-based argument parsing and interpret single-dash multi-character flags as combined short flags, causing the container to fail to start.

The Kubernetes API server rejects the `ComponentK8sConfig` if an argument does not match this format, for example when a flag and its value are separated by a space instead of `=`.

The following CSI sidecar containers support argument overrides, and accept any valid POSIX-style flag. There is no predefined allowlist restricting which flags you can pass. You must pass flags that are valid for the sidecar image version running in your cluster.

- `csi-external-provisioner`

- `csi-attacher`

- `csi-snapshotter`

- `csi-resizer`

- `csi-snapshot-controller`

- `csi-health-monitor-controller`

This example sets Kubernetes API QoS arguments on the `csi-external-provisioner` and `csi-attacher` containers:

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: csi-args-config

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - CSI

      workloadConfigs:

        - workloadNames:

            - px-csi-ext

          containerConfigs:

            - containerNames:

                - csi-external-provisioner

              args:

                - "--kube-api-qps=50"

                - "--kube-api-burst=100"

                - "--worker-threads=20"

            - containerNames:

                - csi-attacher

              args:

                - "--kube-api-qps=50"

                - "--kube-api-burst=100"

                - "--worker-threads=20"

```

## Advanced usage examples​

Based on the components mapping, the following scenarios illustrate how configurations are applied and merged.

- Different configurations for specific components

- Merging configurations for pods

### Different configurations for specific components​

This configuration defines common resource limits for Stork and Autopilot and different resource configurations for telemetry. This flexibility allows you to handle each component's unique resource requirements.

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: example-component-config

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - Stork

        - Autopilot

      workloadConfigs:

        - workloadNames:

            - stork

            - stork-scheduler

            - autopilot

          containerConfigs:

            - containerNames:

                - stork

                - stork-scheduler

                - autopilot

              resources:

                requests:

                  memory: "128Mi"

                  cpu: "500m"

                limits:

                  memory: "256Mi"

                  cpu: "1000m"

    - componentNames:

        - Portworx Telemetry

      workloadConfigs:

        - workloadNames:

            - px-telemetry-registration

          containerConfigs:

            - containerNames:

                - registration

                - envoy

              resources:

                requests:

                  memory: "128Mi"

                  cpu: "500m"

                limits:

                  memory: "256Mi"

                  cpu: "1000m"

```

### Merging configurations for pods​

#### Overrides when a similar configuration is defined twice​

This example defines resource requests and limits for the same `stork` component twice. The second definition overrides the first.

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: example-component-config

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - Stork

      workloadConfigs:

        - workloadNames:

            - stork

          containerConfigs:

            - containerNames:

                - stork

              resources:

                requests:

                  memory: "128Mi"

                  cpu: "500m"

                limits:

                  memory: "256Mi"

                  cpu: "1000m"

    - componentNames:

        - Stork

      workloadConfigs:

        - workloadNames:

            - stork

          containerConfigs:

            - containerNames:

                - stork

              resources:

                requests:

                  memory: "64Mi"

                  cpu: "150m"

                limits:

                  memory: "128Mi"

                  cpu: "500m"

```

#### Appending and merging configurations​

When you define resource requests and limits specifically for the `csi-attacher` and `csi-external-provisioner` containers within the CSI component, you can also specify pod-level placement configurations, including node affinity and tolerations. As a result, the operator creates CSI pods using the defined placement rules and adds resource limits for the `csi-external-provisioner` and `csi-attacher` containers.

```

apiVersion: core.libopenstorage.org/v1

kind: ComponentK8sConfig

metadata:

  name: example-component-config

  namespace: <portworx>

spec:

  components:

    - componentNames:

        - CSI

      workloadConfigs:

        - workloadNames:

            - px-csi-ext

          containerConfigs:

            - containerNames:

                - csi-attacher

              resources:

                requests:

                  memory: "128Mi"

                  cpu: "500m"

                limits:

                  memory: "256Mi"

                  cpu: "1000m"

    - componentNames:

        - CSI

      workloadConfigs:

        - workloadNames:

            - px-csi-ext

          containerConfigs:

            - containerNames:

                - csi-external-provisioner

              resources:

                requests:

                  memory: "128Mi"

                  cpu: "500m"

                limits:

                  memory: "256Mi"

                  cpu: "1000m"

    - componentNames:

        - CSI

      workloadConfigs:

        - workloadNames:

            - px-csi-ext

          placement:

            nodeAffinity:

              requiredDuringSchedulingIgnoredDuringExecution:

                nodeSelectorTerms:

                  - matchExpressions:

                      - key: px-schedule

                        operator: NotIn

                        values:

                          - "false"

            tolerations:

              - key: px-schedule

                operator: Equal

                value: value

                effect: NoSchedule

```

In this topic:
