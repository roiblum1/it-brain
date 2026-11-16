# StorageCluster

Source: https://docs.portworx.com/portworx-enterprise/reference/crd/storage-cluster (Portworx Enterprise latest)

StorageCluster | Portworx Enterprise Documentation

The Portworx cluster configuration is specified by a Kubernetes CRD (CustomResourceDefinition) called StorageCluster. The StorageCluster object acts as the definition of the Portworx Cluster.

The `StorageCluster` object provides a Kubernetes-native experience. You can manage your Portworx cluster just like any other application running on Kubernetes. That is, if you create or edit the `StorageCluster` object, the operator creates or edits the Portworx cluster in the background.

To generate a `StorageCluster` spec customized for your environment, point your browser to Portworx Central and click "Install and Run" to start the Portworx spec generator. The wizard walks you through all the necessary steps to create a `StorageCluster` spec customized for your environment.

Note that using the Portworx spec generator is the recommended way of generating a `StorageCluster` spec. However, if you want to generate the `StorageCluster` spec manually, you can refer to the StorageCluster Examples and StorageCluster Schema sections.

## StorageCluster Examples​

This section provides a few examples of common Portworx configurations you can use for manually configuring your Portworx cluster. Update the default values in these files to match your environment.

-
Portworx with internal KVDB, configured to use all unused devices on the system.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0

  kvdb:

    internal: true

  storage:

    useAll: true

```

-
Portworx with external ETCD and Stork as default scheduler.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0

  kvdb:

    endpoints:

    - etcd:http://etcd-1.net:2379

    - etcd:http://etcd-2.net:2379

    - etcd:http://etcd-3.net:2379

    authSecret: px-kvdb-auth

  stork:

    enabled: true

    args:

      health-monitor-interval: "100"

      webhook-controller: "true"

```

-
Portworx with Security enabled.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0

  security:

    enabled: true

```

-
Portworx with PX-StoreV2 datastore enabled, but preflight check disabled.

When PX-StoreV2 is enabled, Portworx performs a preflight check in the background to validate the prerequisites. PX-StoreV2 is only enabled if this preflight check passes. However, you can choose to manually bypass the preflight check by setting the annotation `portworx.io/preflight-check: skip`. In such cases, to ensure proper initialization of PX-StoreV2, you must perform the following before applying the STC specification:

- Explicitly specify a metadata drive using the `systemMetadataDeviceSpec` field (for example, `systemMetadataDeviceSpec: size=64`)

- Update the annotation to enable PX-StoreV2 (`portworx.io/misc-args: ' -T px-storev2 '`) if the annotation is not available in the STC specification.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

  annotations:

      portworx.io/misc-args: ' -T px-storev2 '

      portworx.io/preflight-check: skip

spec:

  image: portworx/oci-monitor:3.0

  cloudStorage:

      systemMetadataDeviceSpec: size=64

```

-
Portworx with Security enabled, guest access disabled, a custom self-signed issuer/secret location, and five-day token lifetime.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0

  security:

    enabled: true

    auth:

      guestAccess: 'Disabled'

      selfSigned:

        issuer: 'openstorage.io'

        sharedSecret: 'px-shared-secret'

        tokenLifetime: '5d'

```

-
Portworx with update and delete strategies, and placement rules.

note

From Kubernetes version 1.24 and newer, the label key `node-role.kubernetes.io/master` is replaced by `node-role.kubernetes.io/control-plane`.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0

  updateStrategy:

    type: RollingUpdate

    rollingUpdate:

      maxUnavailable: 20%

  placement:

    nodeAffinity:

      requiredDuringSchedulingIgnoredDuringExecution:

        nodeSelectorTerms:

        - matchExpressions:

          - key: px/enabled

            operator: NotIn

            values:

            - "false"

          - key: node-role.kubernetes.io/control-plane

            operator: DoesNotExist

          - key: node-role.kubernetes.io/worker

            operator: Exists

    tolerations:

    - key: infra/node

      operator: Equal

      value: "true"

      effect: NoExecute

```

-
Portworx with custom image registry, network interfaces, and miscellaneous options.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0

  imagePullPolicy: Always

  imagePullSecret: regsecret

  customImageRegistry: docker.private.io/repo

  network:

    dataInterface: eth1

    mgmtInterface: eth2

  secretsProvider: vault

  runtimeOptions:

    num_io_threads: "10"

  env:

  - name: VAULT_ADDRESS

    value: "http://10.0.0.1:8200"

```

-
Portworx with node-specific overrides. Use different devices or no devices on different set of nodes.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0

  storage:

    devices:

    - /dev/sda

    - /dev/sdb

  nodes:

  - selector:

      labelSelector:

        matchLabels:

          <custom-key>:"<custom-value>"

    storage:

      devices:

      - /dev/nvme1

      - /dev/nvme2

  - selector:

      labelSelector:

        matchLabels:

          <custom-key>:"<custom-value>"

    storage:

      devices: []

```

Replace `<custom-key>:<custom-value>` with the node label you have added to your cluster. For example, if you have labeled your node as `px/storage: "nvme"` to specify that the node uses NVME drives, you may use this key-value pair, where `custom-key` is `px/storage` and `custom-value` is `nvme`.

-
Portworx with pre-provisioned per-node storage and dedicated system metadata devices. Use `selector.nodeName` to apply a specific storage configuration to individual nodes, including `systemMetadataDevice` to designate a dedicated metadata device on each node.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0

  storage:

    devices:

    - /dev/sda

    - /dev/sdb

  nodes:

  - selector:

      nodeName: node1

    storage:

      devices:

      - /dev/nvme1

      - /dev/nvme2

      systemMetadataDevice: /dev/sdc

  - selector:

      nodeName: node2

    storage:

      devices:

      - /dev/nvme1

      - /dev/nvme2

      systemMetadataDevice: /dev/sdc

```

In this example, `node1` and `node2` each use NVMe drives for data storage with a dedicated system metadata device. Any new node that does not match a `nodes` selector automatically uses the default storage configuration from `spec.storage` — in this case, `/dev/sda` and `/dev/sdb`. To bring a new node up as a storageless node instead, set `spec.storage.devices` to an empty list (`devices: []`).

To ensure Portworx selects the correct drives on each node when using label selectors, label your drives ahead of time. See Assign custom labels to device pools for details.

-
Portworx with a cluster domain defined.

```

    apiVersion: core.libopenstorage.org/v1

    kind: StorageCluster

    metadata:

      name: portworx

      namespace: <px-namespace>

    annotations:

      portworx.io/misc-args: "-cluster_domain example-cluster-domain-name”

```

-
Portworx with HTTP/HTTPS proxy configuration for external communications

Portworx supports HTTP and HTTPS proxy configuration for outbound connections. Use the `PX_HTTP_PROXY` and `PX_HTTPS_PROXY` environment variables to specify the proxy server for external communications such as license activation and renewal, cloud object store operations (CloudSnaps to S3, Azure Blob Storage, and Google Cloud Storage), and telemetry data uploads to Pure1.

When the proxy environment variables are configured, all HTTP and HTTPS requests go through the proxy by default. Use the `NO_PROXY` environment variable to specify a comma-separated list of addresses or domains that bypass the proxy and communicate directly. This is essential for internal cluster communication, such as Kubernetes services (`.svc`, `.cluster.local`), loopback addresses (`localhost`, `127.0.0.1`), and pod and service CIDR ranges (for example, `10.0.0.0/8`).

You can include authentication credentials in the proxy URL using the format `http://user:password@<IP:port>`.

Note: Floating license server communication doesn't use the proxy by default. To use a proxy with floating license servers, set the `PX_FORCE_HTTP_PROXY` environment variable to `1`.

```

apiVersion: core.libopenstorage.org/v1

kind: StorageCluster

metadata:

  name: portworx

  namespace: <px-namespace>

spec:

  image: portworx/oci-monitor:3.0.0

  env:

    - name: PX_HTTP_PROXY

      value: "http://<IP:port>"

    - name: PX_HTTPS_PROXY

      value: "http://<IP:port>"

    - name: NO_PROXY

      value: "localhost,.svc,.cluster.local"

```

## StorageCluster Schema​

This section explains the fields used to configure the `StorageCluster` object.

FieldDescriptionTypeDefault

spec.
imageSpecifies the Portworx monitor image.`string`None

spec.
imagePullPolicySpecifies the image pull policy for all images deployed by the operator. It can take one of the following values: `Always` or `IfNotPresent`.`string``Always`

spec.
imagePullSecretIf Portworx pulls images from a secure repository, you can use this field to specify the secret name. Note that the secret should be in the same namespace as the `StorageCluster` object.`string`None

spec.
customImageRegistryThe custom container registry server Portworx uses to fetch the Docker images. You can include the repository as well (example: `myregistry.net:5443` or `myregistry.com/myrepository`).
 Operator 26.3.0 and later: When set to `registry.portworx.io` (bare hostname, with or without a trailing `/`), the operator automatically appends `/portworx` and persists the value as `registry.portworx.io/portworx`. All component images are then pulled from `registry.portworx.io/portworx/<image>:<tag>`. Setting `registry.portworx.io/<path>` with a path other than `/portworx` emits a warning Kubernetes event because only the `/portworx` namespace is currently mirrored in that registry; the value is not modified.`string`None

spec.
secretsProviderThe name of the secrets provider Portworx uses to store your credentials. To use features like cloud snapshots or volume encryption, you must configure a secret store provider. Refer to the Secret store management page for more details.`string`k8s

spec.
runtimeOptionsA collection of key-value pairs that override the runtime options. Note: When runtime options are specified as part of the `misc-args` annotation using `rt_opts`, the key-value pairs in `RuntimeOptions` are ignored, and a warning is raised in the `StorageCluster`.`map[string]string`None

spec.
securityAn object for specifying PX-Security configurations. Refer to the Operator Security page for more details.`object`None

spec.
featureGatesA collection of key-value pairs specifying which Portworx features should be enabled or disabled. 1`map[string]string`None

spec.
env[]A list of Kubernetes-like environment variables. Similar to how environment variables are provided in Kubernetes, you can directly provide values to Portworx or import them from a source like a `Secret`, `ConfigMap`, etc.
 Portworx Operator 26.4.0 and later (requires Portworx Enterprise 3.7.0 or later): When `spec.env` changes, the operator validates each variable name against the Portworx-supported list. If a variable is not recognized, the operator emits a Kubernetes `Warning` event with reason `FailedValidation` on the StorageCluster. Reconciliation continues regardless of the outcome.`[]object`None

spec.
metadata.
annotationsA map of components and custom annotations. 2map[string]map[string]stringNone

spec.
metadata.
labelsA map of components and custom labels. This allows users to specify custom labels for components managed by the Portworx operator. Labels can be applied to specific components (e.g., `deployment/autopilot`) or globally to all components of a type (e.g., `deployment/*`). 3map[string]map[string]stringNone

spec.
resources.
requests.
cpuSpecifies the CPU that the Portworx container requests; for example: `"4000m"`.
Note: This applies only to the Portworx `oci-monitor` pod and does not control the CPU limits for the `px-runc` container. To configure resource limits for the `px-runc` container at the runtime level, use the `portworx.io/misc-args` annotation. See the Annotations section for details.`string`None

spec.
resources.
requests.
memorySpecifies the memory that the Portworx container requests; for example: `"4Gi"`.
Note: This applies only to the Portworx `oci-monitor` pod and does not control the memory limits for the `px-runc` container. To configure resource limits for the `px-runc` container at the runtime level, use the `portworx.io/misc-args` annotation. See the Annotations section for details.`string`None

### KVDB configuration​

This section explains the fields used to configure Portworx with a KVDB. Note that if you don't specify the endpoints, the operator starts Portworx with the internal KVDB.

FieldDescriptionTypeDefault

spec.
kvdb.
internalSpecifies if Portworx starts with the internal KVDB.`boolean``true`

spec.
kvdb.endpoints[]
A list of endpoints for your external key-value database like etcd. This field takes precedence over the `spec.kvdb.internal` field. That is, if you specify the endpoints, Portworx ignores the `spec.kvdb.internal` field and uses the external KVDB.`[]string`None

spec.
kvdb.
authSecretIndicates the name of the secret Portworx uses to authenticate against your KVDB. The secret must be placed in the same namespace as the `StorageCluster` object. The secret should provide the following information:
 - `username` (optional)
 - `password` (optional)
 - `kvdb-ca.crt` (the CA certificate)
 - `kvdb.key` (certificate key)
 - `kvdb.crt` (etcd certificate)
 - `acl-token` (optional)
For example, create a directory called etcd-secrets, copy the files into it and create a secret with `kubectl -n kube-system create secret generic px-kvdb-auth --from-file=etcd-secrets/``string`None

### Storage configuration​

This section provides details about the fields used to configure the storage for your Portworx cluster. If you don't specify a device, the operator sets the `spec.storage.useAll` field to `true`.

important

The fields under `spec.storage.*` are immutable after initial provisioning. This means updating these fields later, including during an upgrade, does not re-provision or migrate existing nodes. To apply updated settings, provision new storage nodes after making the change or contact Portworx Support.

note

If a cluster contains an AWS node, the Portworx Operator treats the cluster as an Amazon EKS cluster and uses Amazon Elastic Block Store (EBS) `gp3` volumes as the default storage. Because on-premises nodes cannot attach EBS volumes, always configure `spec.storage` or `spec.cloudStorage` explicitly on an Amazon EKS cluster with hybrid nodes. Otherwise, Portworx Enterprise fails to start. For more information, see Installation on an Amazon EKS Cluster with Hybrid Nodes.

FieldDescriptionTypeDefault

spec.
storage.
useAllIf set to `true`, Portworx uses all available, unformatted, and unpartitioned devices. 4`boolean``true`

spec.
storage.
useAllWithPartitionsIf set to `true`, Portworx uses all the available and unformatted devices. 4`boolean``false`

spec.
storage.
forceUseDisksIf set to `true`, Portworx uses a device even if there's a file system on it. Note that Portworx may wipe the drive before using it.`boolean``false`

spec.
storage.
devices[]Specifies the list of devices Portworx should use.`[]string`None

spec.
storage.
cacheDevices[]Specifies the list of cache devices Portworx should use.`[]string`None

spec.
storage.
journalDeviceSpecifies the device Portworx uses for journaling.`string`None

spec.
storage.
systemMetadataDeviceIndicates the device Portworx uses to store metadata. For better performance, specify a system metadata device when using Portworx with the internal KVDB. For PX-StoreV2, you must create a system metadata device, where the internal KVDB resides.
Note: You must allocate a minimum of 64 GB for the system metadata device. However, for larger clusters or high-ingress environments, Portworx by Everpure recommends increasing the minimum size to 256 GB to support longer degraded volume tolerance.
The system metadata device stores data needed to keep replicated volumes in sync during outages. The usage grows with the number of degraded volumes and the write I/O rate. For example, 64 GB typically supports about 1 hour of degraded volume operation, whereas 256 GB might support up to 4 hours. Increase the size based on your cluster scale and availability requirements.`string`None

spec.
storage.
kvdbDeviceSpecifies the device Portworx uses to store internal KVDB data.`string`None

### Cloud storage configuration​

This section explains the fields used to configure Portworx with cloud storage. Once the cloud storage is configured, Portworx manages the cloud disks automatically based on the provided specs.

important

- The `spec.storage` fields take precedence over the fields presented in this section. Make sure the `spec.storage` fields are empty when configuring Portworx with cloud storage.

- The fields under `spec.cloudStorage.*` are immutable after initial provisioning. This means updating these fields later, including during an upgrade, does not re-provision or migrate existing nodes. To apply updated settings, provision new storage nodes after making the change or contact Portworx Support.

FieldDescriptionTypeDefault

spec.
cloudStorage.
providerSpecifies the cloud provider name, such as: pure, azure, aws, gce, vsphere.`string`None

spec.
cloudStorage.
deviceSpecs[]A list of specifications for cloud storage devices. Portworx creates a cloud disk for each device specification. In a FlashArray Cloud Drive deployment, you can set the `storage_backend` field in a device specification to select the FlashArray on which Portworx provisions the storage pool. For more information, see Select the KDS for storage pools.`[]string`None

spec.
cloudStorage.
journalDeviceSpecSpecifies the cloud device Portworx uses for journaling.`string`None

spec.
cloudStorage.
systemMetadataDeviceSpecIndicates the cloud device Portworx uses for metadata. For performance, specify a system metadata device when using Portworx with the internal KVDB.
In PX-StoreV2 environments, specifying `spec.cloudStorage.systemMetadataDeviceSpec` is mandatory.`string`None

spec.
cloudStorage.
kvdbDeviceSpecSpecifies the cloud device Portworx uses for an internal KVDB.
If you specify `spec.cloudStorage.systemMetadataDeviceSpec`, Portworx ignores `kvdbDeviceSpec`. The internal KVDB uses the drives provisioned by `systemMetadataDeviceSpec` instead of separate KVDB drives.`string`None

spec.
cloudStorage.
maxStorageNodesPerZoneDeprecated Cannot be specified for a new install. Cannot be updated for an existing install. Can only be removed.`uint32`None

spec.
cloudStorage.
maxStorageNodesDeprecated Cannot be specified for a new install. Cannot be updated for an existing install. Can only be removed.`uint32`None

spec.
cloudStorage.
initialStorageNodesSpecifies the number of storage nodes to be created during the initial installation. For more information, see Manage storage nodes in a cluster.`uint32`None

### Cluster Diagnostics configuration​

This section describes the fields used to configure `spec.clusterDiags`. Once clusterDiags is enabled, you can use the `PortworxDiag` custom resource to collect cluster-level diagnostics. For more information about collecting diagnostics using `PortworxDiag`, see Collect diagnostics using `PortworxDiag` custom resource.

FieldDescriptionTypeDefault

spec.
clusterDiags.
enabledSpecifies whether clusterDiags is enabled or disabled. When enabled, the Portworx Operator creates a `PortworxDiag` CR every 4 hours to collect pod-level diagnostics. Starting with Operator 26.3.0, `clusterDiags` is enabled by default on new and upgraded clusters. Setting this field to `false` disables clusterDiags and persists across upgrades.`boolean`true

spec.
clusterDiags.
imageSpecifies the Docker image for the clusterDiags container. For example, `portworx/cluster-diags:3.3.0`.`string`None

### Network configuration​

This section describes the fields used to configure the network settings. If these fields are not specified, Portworx auto-detects the network interfaces.

FieldDescriptionTypeDefault

spec.
network.
dataInterfaceSpecifies the network interface Portworx uses for data traffic.`string`None

spec.
network.
mgmtInterfaceIndicates the network interface Portworx uses for control plane traffic.`string`None

### Volume configuration​

This section describes the fields used to configure custom volume mounts for Portworx pods.

FieldDescriptionTypeDefault

spec.
volumes[].
nameUnique name for the volume.`string`None

spec.
volumes[].
mountPathPath within the Portworx container at which the volume should be mounted. Must not contain the ':' character.`string`None

spec.
volumes[].
mountPropagationDetermines how mounts are propagated from the host to container and the other way around.`string`None

spec.
volumes[].
readOnlyVolume is mounted read-only if true, read-write otherwise.`boolean`false

spec.
volumes[].
[secret|configMap|hostPath]Specifies the location and type of the mounted volume. This is similar to the VolumeSource schema of a Kubernetes pod volume.`object`None

### Placement rules​

You can use the placement rules to specify where Portworx should be deployed. By default, the operator deploys Portworx on all worker nodes.

FieldDescriptionTypeDefault

spec.
placement.
nodeAffinityUse this field to restrict Portworx on certain nodes. It works similarly to the Kubernetes node affinity feature.`object`None

spec.
placement.
tolerations[]Specifies a list of tolerations that will be applied to Portworx pods so that they can run on nodes with matching taints.
Note: When you modify this field, all Portworx Deployments, DaemonSets, and pods restart to apply the new tolerations, except for KVDB pods. KVDB pods apply the updated tolerations when they restart. This does not affect cluster operations. You can use the ComponentK8sConfig CRD to apply tolerations.`[]object`None

For Operator 1.8 and higher, if you have topology labels `topology.kubernetes.io/region` or `topology.kubernetes.io/zone` specified on worker nodes, Operator would deploy Stork, Stork scheduler, CSI and PVC controller pods with `topologySpreadConstraints` to distribute pod replicas across Kubernetes failure domains.

### Taint-based scheduling​

This section describes the field used to enable taint-based scheduling on Portworx nodes.

FieldDescriptionTypeDefault

spec.
taintBasedScheduling.
enabledEnables taint-based scheduling for Portworx nodes. When set to `true`, and Stork is enabled, the Operator taints Portworx storage and storageless nodes and adds matching tolerations to Portworx system pods, such as Portworx, Stork, and CSI. Stork adds matching tolerations to application pods that use Portworx volumes. This blocks workloads that lack matching tolerations from being scheduled on Portworx nodes. For more information, see Taint-based scheduling with Stork.

Note: This field is supported starting with Operator version 25.5.1 and Stork version 25.6.0 or later.`boolean``false`

### Update strategy​

This section provides details on how to specify an update strategy.

FieldDescriptionTypeDefault

spec.
updateStrategy.
typeIndicates the update strategy. Currently, Portworx supports the following update strategies: `RollingUpdate` and `OnDelete`.`object``RollingUpdate`

spec.
updateStrategy.
rollingUpdate.
maxUnavailableSimilarly to how Kubernetes rolling update strategies work, this field specifies how many nodes can be down at any given time. Note that you can specify this as a number or percentage.

Note: Portworx by Everpure recommends keeping the `maxUnavailable` value as 1. Changing this value could potentially lead to volume and Portworx quorum loss during the upgrade process.`int` or `string``1`

spec.
updateStrategy.
rollingUpdate.
minReadySecondsDuring rolling updates, the system waits for all pods to be ready for at least `minReadySeconds` before updating the next batch of pods, where the size of the pod batch is specified through the `spec.updateStrategy.rollingUpdate.maxUnavailable` flag.`string``1`

spec.
updateStrategy.
rollingUpdate.
disruption.allowEnables the smart upgrade if you set the value to `false`. The smart upgrade feature enables a streamlined, resilient upgrade process for Portworx nodes, allowing them to be upgraded in parallel while maintaining volume quorum and without application disruption.`boolean``true`

spec.
autoUpdateComponentsIndicates the update strategy for the component images (such as Stork, Autopilot, Prometheus, and so on). Portworx supports the following auto update strategies for the component images:

- `None`: Updates the component images only when the Portworx image changes in `StorageCluster.spec.image`.

- `Once`: Updates the component images once even if the Portworx image does not change. This is useful when the component images on the manifest server change due to bug fixes.

- `Always`: Regularly checks for updates on the manifest server, and updates the component images if required.

`string`None

### Delete/Uninstall strategy​

This section provides details on how to specify an uninstall strategy for your Portworx cluster.

FieldDescriptionTypeDefault

spec.
deleteStrategy.
typeIndicates what happens when the Portworx `StorageCluster` object is deleted. Set this field only at the time you uninstall Portworx; do not set it during installation. By default, there is no delete strategy. With Operator 26.5.0 or later, deletion of a `StorageCluster` is blocked until you set a delete strategy, and the Operator emits a `DeleteStrategyPreset` warning event if a delete strategy is set on a running `StorageCluster`. With earlier Operator versions, no delete strategy means only the Kubernetes components deployed by the operator are removed, and the Portworx `systemd` service continues to run. Portworx supports the following delete strategies:

-  `Uninstall` - Removes all Portworx components from the system and leaves the devices and KVDB intact.

-  `UninstallAndWipe` - Removes all Portworx components from the system and wipes the devices and metadata from KVDB.

- `UninstallAndDelete` – Removes all Portworx components from the system, wipes the devices, deletes metadata from KVDB, and removes the cloud drive.

- Supported on vSphere, AWS, GKE, and Azure with Operator version 25.5.0 or later and Portworx version 3.5.0 or later.

- Supported on Oracle Cloud Infrastructure, IBM Cloud, and FlashArray cloud drives. with Operator version 26.3.0 or later and Portworx version 3.6.2 or later.

`string`None

spec.
deleteStrategy.
ignoreVolumesIndicates whether to ignore volumes when deleting the storage cluster. If set to `true`, the cluster is deleted even if Portworx volumes are present. If set to `false`, the deletion is blocked if Portworx volumes exist.`boolean``false`

important

Set `deleteStrategy` only at the time you uninstall Portworx. Do not set it during installation, and do not keep it in a GitOps manifest or a copied StorageCluster template. If it is set, an accidental `kubectl delete storagecluster` starts an uninstall and, with `UninstallAndWipe` or `UninstallAndDelete`, permanently deletes data.

#### Delete strategy guardrails​

With Operator 26.5.0 or later:

- Deletion is blocked if `deleteStrategy` is not set. The `StorageCluster` remains in the `Terminating` state and Portworx is not uninstalled. Set `deleteStrategy`, and the Operator resumes the uninstall automatically.

- A warning event is emitted if `deleteStrategy` is set on a running `StorageCluster`. The Operator emits a `Warning` event with the reason `DeleteStrategyPreset`. The message states the configured strategy type. For `UninstallAndWipe` and `UninstallAndDelete`, it also states that data is permanently erased on uninstall. The Operator repeats the event every 5 minutes until you remove the field, and immediately if you change the strategy type.

To check for the warning:

```

kubectl describe storagecluster <storagecluster-name> -n <px-namespace>

```

To remove a `deleteStrategy` if you do not intend to uninstall Portworx:

```

kubectl patch storagecluster <storagecluster-name> -n <px-namespace> \

  --type=merge \

  -p '{"spec":{"deleteStrategy":null}}'

```

If you manage the `StorageCluster` through GitOps or Helm, also remove `deleteStrategy` from the source manifest or values file. Otherwise, it is applied again.

To uninstall Portworx, set `deleteStrategy` and then delete the `StorageCluster`. For the full procedure, see Uninstall Portworx using the Operator.

### Pure Platform configuration​

This section provides details on how to configure Portworx by Everpure platform integrations, including Fusion and Integration Operator.

note

Pure Platform configuration requires Portworx Operator 26.1.0 or later and Portworx Enterprise 3.6.0 or later.

FieldDescriptionTypeDefault

spec.
purePlatform.
integrationOperator.
imageSpecifies the Docker image for the Portworx Integration Operator. The integration operator is deployed on OCP clusters when Fusion is enabled or Dynamic plugin is enabled.`string`None

spec.
purePlatform.
fusion.
enabledEnables or disables Pure Storage Fusion integration for the storage cluster. When enabled, the Fusion Controller acts as a bridge between Pure Fusion and Kubernetes.`boolean``false`

spec.
purePlatform.
fusion.
imageSpecifies the Docker image for the Fusion controller.`string`None

spec.
purePlatform.
fusion.
fusionAuthSecretSpecifies the name of the Kubernetes secret containing LDAP credentials for Fusion authentication. The secret should contain keys: `endpoint`, `username`, `password` (for LDAP auth) or `token` (for legacy auth).`string``pure-fusion-cred`

spec.
purePlatform.
fusion.
tokenRotationIntervalSpecifies the rotation interval for API tokens generated from LDAP credentials. Format: duration string (e.g., `24h`, `12h`, `1h`). Set to `0` to disable automatic token rotation. Minimum value: `1h`.`string``24h`

### Monitoring configuration​

This section provides details on how to enable monitoring for Portworx.

FieldDescriptionTypeDefault

spec.
monitoring.
prometheus.
enabledEnables or disables a Prometheus cluster.`boolean``false`

spec.
monitoring.
prometheus.
exportMetricsExpose the Portworx metrics to an external or operator deployed Prometheus.`boolean``false`

spec.
monitoring.
prometheus.
alertManager.
enabledEnables or disables Prometheus Alertmanager`boolean`None

spec.
monitoring.
prometheus.
remoteWriteEndpointSpecifies the remote write endpoint for Prometheus.`string`None

spec.
monitoring.
telemetry.
enabledEnable telemetry and metrics collector`boolean``false`

spec.
monitoring.
telemetry.
hostNetworkHostNetwork if set, will use host's network for telemetry pods`boolean``false`

spec.
monitoring.
telemetry.
metricsCollector.
enabledEnables or disables the `px-telemetry-metrics-collector` deployment. When disabled, diagnostics upload continues, but real-time metrics forwarding to Pure1 stops. For more information, see Customize metrics collector.

Note: Supported with Portworx Operator 25.5.2 or later.`boolean``true`

spec.
monitoring.
telemetry.
metricsCollector.
imageSpecifies the image for the real-time metrics container in the `px-telemetry-metrics-collector` deployment. For more information, see Customize metrics collector.
Note: Supported with Portworx Operator 25.5.2 or later.`string`None

spec.
monitoring.
telemetry.
resourcesResources define resource requests and limits for telemetry pods, although requests and limits shouldn't be necessary. If needed, set a limit of 500m of CPU and 500Mi of memory.`object`None

spec.
monitoring.
telemetry.
resources.
claimsClaims list the names of resources, defined in spec.resourceClaims, that are used by this container. This is an alpha feature and requires the DynamicResourceAllocation feature gate to be enabled. This field is immutable. It can only be set for containers.`array`None

spec.
monitoring.
telemetry.
resources.
claims.
nameName must match the name of one entry in pod.spec.resourceClaims of the Pod where this field is used. It makes that resource available inside a container.`string`None

spec.
monitoring.
telemetry.
resources.
limitsLimits describe the maximum amount of compute resources allowed. For more information, see Resource Management for Pods and Containers.`object`None

spec.
monitoring.
telemetry.
resources.
requestsRequests describe the minimum amount of compute resources required. If Requests is omitted for a container, it defaults to Limits if explicitly specified, otherwise to an implementation-defined value. Requests cannot exceed Limits. For more information, see Resource Management for Pods and Containers.`object`None

spec.
monitoring.
prometheus.
resourcesProvides the ability to configure Prometheus resource usage such as memory and CPU usage.`object`Default limits: CPU 1, memory 800M, and ephemeral storage 5G

spec.
monitoring.
prometheus.
replicasSpecifies the number of Prometheus replicas that will be deployed.`int`1

spec.
monitoring.
prometheus.
retentionSpecifies the time period for which Prometheus retains historical metrics.`string``24h`

spec.
monitoring.
prometheus.
retentionSizeSpecifies the maximum amount of disk space that Prometheus can use to store historical metrics.`string`None

spec.
monitoring.
prometheus.
storageSpecifies the storage type that Prometheus will use for storing data. If you set the storage type to PVCs, do not set the `runAsGroup` or `fsGroup` option for the `spec.monitoring.prometheus.securityContext` flag.`object`None

spec.
monitoring.
prometheus.
volumesSpecifies additional volumes to the output Prometheus StatefulSet. These specified volumes will be appended to other volumes generated as a result of the `spec.monitoring.prometheus.storage` spec.`object`None

spec.
monitoring.
prometheus.
volumeMountsSpecifies additional VolumeMounts on the output Prometheus StatefulSet definition. These specified VolumeMounts will be appended to other VolumeMounts in the Prometheus container generated as a result of `spec.monitoring.prometheus.storage` spec.`object`None

spec.
monitoring.
prometheus.
securityContext.
runAsNonRootFlag that indicates that the container must run as a non-root user.`boolean`None

spec.
monitoring.
grafana.
enabledEnables or disables a Grafana instance with Portworx dashboards.`boolean`false

### Filesystem Dependencies Update Configuration​

This section provides details on how to configure automated deployment and management of the `pxfslibs` update DaemonSet through the Portworx Operator. This feature is supported only in air-gapped environments.

note

The following fields are supported with Portworx Operator 25.6.0 or later.

FieldDescriptionTypeDefault

spec.
pxfslibsUpdate.
enabledEnables or disables the `pxfslibs` update DaemonSet deployment. When enabled, the Operator automatically deploys the DaemonSet for updating filesystem dependencies.`boolean``false`

spec.
pxfslibsUpdate.
imageSpecifies the image used for the `pxfslibs` update DaemonSet.`string``None`

spec.
pxfslibsUpdate.
autoDeleteDetermines whether the DaemonSet is automatically deleted after successful execution. If set to `true`, the Operator deletes the DaemonSet after completion.`boolean``false`

spec.
pxfslibsUpdate.
onDemandTriggerTriggers an on-demand update of the `pxfslibs` DaemonSet. Specify a timestamp string (for example, `"27 Oct 2025 9:35 PM"`). The Operator converts this to UTC ISO format for scheduling. Each time you update this field with a new timestamp, the Operator triggers a new update. Use this when you manually push updated pxfslib images to your internal registry.`string``None`

spec.
pxfslibsUpdate.
scheduleSpecifies a cron expression for scheduling recurring updates of the `pxfslibs` DaemonSet. For example, `"0 3 * * 0"` schedules updates every Sunday at 3:00 AM. Use this if you have an automation in place to update the pxfslib container image in your internal registry.`string``None`

For more information about updating filesystem dependencies, see Update Portworx file system dependencies.

### Stork configuration​

This section describes the fields used to manage the Stork deployment through the Portworx operator.

FieldDescriptionTypeDefault

spec.
stork.
enabledEnables or disables Stork at any given time.`boolean``true`

spec.
stork.
restrictDataProtectionRBACControls RBAC permissions for Stork data protection workflows. When set to `true`, Stork runs with minimal permissions for scheduling and monitoring only. When set to `false` or omitted (the default), Stork receives full data protection permissions if the operator ClusterRole resource has sufficient permissions. Use this setting for storage-only deployments that don’t require data protection features, such as backups or disaster recovery.

Supported in Portworx Operator 26.1.0 or later and Portworx Enterprise 3.4.0 or later. For more information, see Restrict RBAC for Stork and Operator.`boolean``false`

spec.
stork.
imageSpecifies the Stork image.`string`None

spec.
stork.
lockImageEnables locking Stork to the given image. When set to false, the Portworx Operator will overwrite the Stork image to a recommended image for the given Portworx version.`boolean``false`

spec.
stork.
argsA collection of key-value pairs that override the default Stork arguments or add new arguments.`map[string]string`None

spec.
stork.
args.admin-namespaceSets up a cluster's admin namespace for migration.
Refer to admin namespace for more information.`string``kube-system`

spec.
stork.
args.log-levelSets the Stork logging level. Valid values: `trace`, `debug`, `info`, `warn`, `error`, `fatal`, `panic`.`string``info`

spec.
stork.
args.verboseDeprecated: Use `scheduler.verboseLogLevel` instead.
Set to `true` to enable verbose logging for the stork-scheduler container (`--v=5`). When both `args.verbose` and `scheduler.verboseLogLevel` are set, `scheduler.verboseLogLevel` takes precedence.`boolean``false`

spec.
stork.
args.enable-fsgroup-optimizationEnables Stork to set `fsGroupChangePolicy` to `OnRootMismatch` for pods that use `ReadWriteMany` or `ReadOnlyMany` volumes and have `fsGroup` configured. This optimization occurs only when `enable-fsgroup-optimization` is also set to `true`. It helps improve pod startup time by avoiding recursive ownership changes.`boolean``false`

spec.
stork.
args.webhook-controllerSet to `true` to make Stork the default scheduler for workloads using Portworx volumes.`boolean``false`

spec.
stork.
args.retain-external-schedulersSet this argument to `true` to prevent Stork from replacing external schedulers, ensuring that only the default scheduler is replaced by Stork.`boolean``false`

spec.stork.args.snapshotdata-gc-intervalPeriod in which the garbage collection job should run.`string`24h

spec.stork.args.snapshotdata-gc-batch-sizeSpecifies the batch size of snapshot data to be deleted at one time. Deletion occurs in batches.`int`50

spec.stork.args.snapshotdata-gc-min-ageMinimum age of snapshot data to qualify for garbage collection. In this default case, even if a snapshot data is stale and doesn't have a corresponding volume snapshot in the cluster, it won't be deleted if created within 24 hours.`string`24h

spec.stork.args.snapshotdata-gc-start-timeStart time window of the garbage collection job, specified in 24-hour time format.`string`00:00

spec.stork.args.snapshotdata-gc-end-timeEnd time window of the garbage collection job, specified in 24-hour time format.`string`00:00

spec.stork.args.disable-pod-cachingOption to disable caching of pod data. Set the value to true to disable caching. By default, pod caching is enabled. Disabling it helps reduce memory consumption, especially when the cluster is scaled to accommodate a large number of pods.`boolean`false

spec.stork.args.enable-driver-cacheEnable driver cache for node health monitoring.`boolean`true

spec.stork.args.node-down-detection-timeoutTimeout in seconds to verify node offline status before proceeding with pod cleanup. Only honored when driver cache is enabled (default: 60)`int`60

spec.stork.args.pod-delete-batch-sizeNumber of pods to delete in each batch when cleaning up pods from offline nodes.`int`5

spec.stork.args.pod-batch-delete-intervalThe interval in seconds between pod delete batches when cleaning up pods from offline nodes.`int`30

spec.stork.args.enable-attach-cap-filterEnables Stork to filter out nodes that have reached the Portworx per-node limit of 1024 volume attachments when scheduling pods. Requires `enable-volume-cache` to be `true`. When set to `false`, Stork skips this check. Supported in Stork 26.5.0 or later.`boolean``true`

spec.stork.args.enable-attach-cap-penaltyEnables Stork to lower the score of candidate nodes that are projected to exceed the `attach-cap-penalty-threshold-percent` of the per-node volume attachment limit when prioritizing nodes. Requires `enable-volume-cache` to be `true`. When set to `false`, Stork applies no penalty. `attach-cap-penalty-threshold-percent` and `attach-cap-penalty-factor` flags apply only when this flag is `true`. Supported in Stork 26.5.0 or later.`boolean``true`

spec.stork.args.attach-cap-penalty-threshold-percentPercentage of the per-node volume attachment limit above which Stork applies the score penalty. Valid values are greater than `0` and up to `100`. Stork ignores values outside this range and uses the default. Applies only when `enable-attach-cap-penalty` is `true`. Supported in Stork 26.5.0 or later.`float``95`

spec.stork.args.attach-cap-penalty-factorMultiplier that Stork applies to the locality score of a node that exceeds the attach limit threshold. Valid values are from `0` to `1`. For example, `0.5` halves the score and `0` sets it to zero. Stork ignores values outside this range and uses the default. Applies only when `enable-attach-cap-penalty` is `true`. Supported in Stork 26.5.0 or later.`float``0.5`

spec.stork.args.disable-pod-failoverSet to `true` to keep application pods that use Portworx volumes running on the same node while Portworx is being upgraded on that node. By default, Stork deletes such pods during the upgrade so that they are scheduled to a different node. Supported in Stork 26.5.0 or later.`boolean``false`

spec.stork.args.early-migration-resources-collectionEnable early resource collection during migration to improve performance.`boolean`true

spec.stork.args.log-file-buffer-size-mibMaximum size in MiB of the in-memory log buffer for hourly log files when file writes fail. Set to `0` to disable buffering. This parameter is used when Stork log telemetry is enabled.`int`50

spec.stork.args.log-file-max-backupsMaximum number of hourly log files to retain. Stork writes one file per hour. To keep N days of logs, set this value to N × 24. Both this limit and the `log-file-max-age` parameter work independently. Whichever limit is reached first removes the older files.`int`168

spec.stork.args.log-file-max-ageMaximum number of days to retain compressed log files. To retain N days of logs, also set `log-file-max-backups` to N × 24. Both limits work independently. Whichever limit is reached first removes the older files.`int`7

spec.stork.args.normalize-stork-scoresEnables or disables Stork's hyperconvergence normalization scoring. Set to `false` to disable the Stork normalization scoring. The `replica-score`, `rack-score`, `zone-score`, `region-score`, and `remote-score` flags apply only when this flag is `true`. The default values of these scoring flags are recommended for normalization. If edited, ensure values of the flags maintain the order: `replica-score` > `rack-score` > `zone-score` > `region-score`.
Supported with Stork 26.4.2 or later, Portworx Operator 26.4.0 or later, and Portworx Enterprise 3.6.2 or later. For more information, see Enable Stork normalization and tune hyperconvergence scoring.`boolean``true`

spec.stork.args.replica-scoreScore assigned to the node holding most of the pod's data. Increasing it gives more weightage to the node holding the pod's data. Applies only when `normalize-stork-scores` is `true`.`int``4`

spec.stork.args.rack-scoreScore assigned to nodes belonging to the same rack as the pod's data node. Applies only when `normalize-stork-scores` is `true`.`int``3`

spec.stork.args.zone-scoreScore assigned to nodes in the same zone as the pod's data node. Applies only when `normalize-stork-scores` is `true`.`int``2`

spec.stork.args.region-scoreScore assigned to nodes in the same region as the pod's data node. Applies only when `normalize-stork-scores` is `true`.`int``1`

spec.stork.args.remote-scoreScore assigned to nodes that don't hold any of the pod's data. Applies only when `normalize-stork-scores` is `true`.`int``0`

spec.stork.args.enable-scheduling-optimizationEnables the scheduling optimization controller for KubeVirt virtual machine (VM) hyperconvergence remediation after pool failover. `scheduling-optimization-max-parallel-migrations`, `scheduling-optimization-cool-off`, and `scheduling-optimization-migration-timeout` flags apply only when this flag is `true`.`boolean``true`

spec.stork.args.scheduling-optimization-max-parallel-migrationsSpecifies the maximum concurrent live migrations that the scheduling optimization engine runs per active request. You can override this value per request in the `SchedulingOptimization` specification. Applies only when `enable-scheduling-optimization` is `true`.`int``5`

spec.stork.args.scheduling-optimization-cool-offSpecifies the minimum interval between Stork-triggered live migrations of the same VM. You can override this value per request in the `SchedulingOptimization` specification. Applies only when `enable-scheduling-optimization` is `true`.`string``1h`

spec.stork.args.scheduling-optimization-migration-timeoutSpecifies the per-VM timeout for waiting on a live migration to complete before the worker gives up its slot. Applies only when `enable-scheduling-optimization` is `true`.`string``30m`

spec.
stork.
scheduler.
verboseLogLevelSets the verbosity level for the stork-scheduler container by adding `--v=N` to its command. Takes precedence over `args.verbose` when both are set. Supported in Portworx Operator 26.4.0 or later.`int`Not set

spec.
stork.
scheduler.
kubeSchedulerClientQPSSteady-state limit on Kubernetes API server calls per second for the stork-scheduler. Valid range: 1–10000. Supported in Portworx Operator 26.4.0 or later.`int``50`

spec.
stork.
scheduler.
kubeSchedulerClientBurstMaximum number of API calls the stork-scheduler can fire in a burst before the QPS limit takes effect. Valid range: 1–10000. Supported in Portworx Operator 26.4.0 or later.`int``100`

spec.stork.scheduler.
kubeSchedulerExtenderWeightControls how much influence Stork's normalization score has on final node selection relative to the built-in Kubernetes scoring plugins. Increase this value to make hyperconvergence stronger. Must be `1` or greater.

Introduced in Portworx Operator 26.4.0; earlier Operator versions hardcode the value to `5`. For more information, see Enable Stork normalization and tune hyperconvergence scoring.`int``1`

spec.
stork.
scheduler.
kubeSchedulerNodeCacheEnabledOverrides the stork extender's `nodeCacheCapable` flag in the generated `stork-config` ConfigMap. When enabled, the kube-scheduler passes candidate nodes to the extender by name only and reuses its cached node info for scoring, which avoids a Kubernetes scheduler issue where extender-gated pods get identical scores from in-tree resource-scoring plugins. Requires Stork 26.4.2 or later; setting this to `true` against an older Stork version is ignored with a warning. An explicit `false` is always honored. When unset, the operator enables this automatically for Stork 26.4.2 or later and leaves it disabled otherwise. Supported in Portworx Operator 26.4.0 or later.`boolean`Not set

spec.
stork.
env[]A list of Kubernetes-like environment variables passed to Stork.`[]object`None

spec.
stork.
volumes[]A list of volumes passed to Stork pods. The schema is similar to the top-level volumes.`[]object`None

spec.
stork.
resourcesSpecifies CPU and memory resource requirements for Stork and Stork Scheduler pods.`object`None

spec.stork.resources.requestsRequested resources for Stork pods.`object`None

spec.stork.resources.requests.cpuCPU request for Stork pods. For example, `"1"` or `"500m"`.`string`None

spec.stork.resources.requests.memoryMemory request for Stork pods. For example, `"3Gi"` or `"512Mi"`.`string`None

spec.stork.resources.limitsResource limits for Stork pods.`object`None

spec.stork.resources.limits.cpuCPU limit for Stork pods. For example, `"1"` or `"500m"`.`string`None

spec.stork.resources.limits.memoryMemory limit for Stork pods. For example, `"3Gi"` or `"512Mi"`.`string`None

### CSI configuration​

This section provides details on how to configure CSI for the StorageCluster.

FieldDescriptionTypeDefault

spec.
csi.
enabledFlag indicating whether CSI needs to be installed for the storage cluster.`boolean`true

spec.
csi.
installSnapshotControllerFlag indicating whether CSI Snapshot Controller needs to be installed for the storage cluster. Starting with Operator 26.5.0, setting this to `false` also stops the Operator from reconciling the `volumesnapshots`, `volumesnapshotcontents`, and `volumesnapshotclasses` CRDs. Use this setting when another component, such as the GKE add-on manager, manages these CRDs.`boolean`true

spec.
csi.
volumeSnapshotClassCSIVolumeSnapshotClassSpec defines configuration for creating a default CSI VolumeSnapshotClass. Note: Supported with Portworx Operator 25.3.1 or later.`object`—

spec.
csi.
volumeSnapshotClass.
createCreate indicates whether a default CSI VolumeSnapshotClass should be created. Default value is true.`boolean``true`

spec.
csi.
seLinuxMountEnables or disables setting the `seLinuxMount` field in the `CSIDriver` object. Set to `false` to disable SELinux relabeling on CSI volumes.`boolean`true

spec.csi.kubeVirtStorageClassesControls creation of default StorageClasses for OpenShift Virtualization (KubeVirt). If running on OpenShift and a `HyperConverged` CR is present, these StorageClasses are created by default.`object`All fields default to `true` on OpenShift

spec.csi.kubeVirtStorageClasses.pxRwxBlockKubevirtCreates the `px-rwx-block-kubevirt` StorageClass (RWX block). 5`boolean``true`

spec.csi.kubeVirtStorageClasses.pxRwxFileKubevirtCreates the `px-rwx-file-kubevirt` StorageClass (shared RWX file). 5`boolean``true`

spec.csi.kubeVirtStorageClasses.pxCdiScratchCreates the `px-cdi-scratch` StorageClass used for CDI scratch space. 5`boolean``true`

### Autopilot configuration​

This section provides details on how to deploy and manage Autopilot.

FieldDescriptionTypeDefault

spec.
autopilot.
enabledEnables or disables Autopilot at any given time.`boolean``false`

spec.
autopilot.
imageSpecifies the Autopilot image.`string`None

spec.
autopilot.
lockImageEnables locking Autopilot to the given image. When set to false, the Portworx Operator will overwrite the Autopilot image to a recommended image for given Portworx version.`boolean``false`

spec.
autopilot.
providers[]List of data providers for Autopilot.`[]object`None

spec.
autopilot.
providers[].
nameUnique name of the data provider. For Datadog, set provider name as `datadog` and for Prometheus set as `default`.`string`None

spec.
autopilot.
providers[].
typeType of the data provider. Currently `prometheus` and `datadog` is supported.`string``prometheus`

spec.
autopilot.
providers[].
paramsMap of key-value parameters for the provider.`map[string]string`None

spec.
autopilot.
providers[].
params.urlURL for the metrics provider where Autopilot scrapes volume and pool metrics. The default is the URL for Prometheus shipped with Portworx.`string``http://px-prometheus:9090`

spec.
autopilot.
providers[].
params.ignore_unhealthy_targetsDetermines whether to ignore unhealthy scraping targets and proceed with Autopilot actions. If set to `false`, Autopilot won't proceed if there are unhealthy targets.`boolean``true`

spec.
autopilot.
argsA collection of key-value pairs that overrides the default Autopilot arguments or adds new arguments.`map[string]string`None

spec.
autopilot.
args.log-levelDetermines the level of logs printed in the Autopilot pod log. Can be set to `trace` or `debug` for troubleshooting.`string``info`

spec.
autopilot.
args.min_poll_intervalFrequency in seconds at which Autopilot checks conditions for all rules and proceeds with state changes.`int``5`

spec.
autopilot.
env[]A list of Kubernetes-like environment variables passed to Autopilot.`[]object`None

spec.
autopilot.
volumes[]A list of volumes passed to Autopilot pods. The schema is similar to the top-level volumes.`[]object`None

spec.
autopilot.
resources.
limits.
memoryMaximum memory size that can be claimed by Autopilot.`string`None

### OpenShift dynamic plugin configuration​

This section describes how to configure the Portworx OpenShift Dynamic Plugin. For more information on how to enable the plugin, see Enable Portworx OpenShift Dynamic Plugin.

note

- The following fields are supported in Portworx Operator 25.6.0 and later.

- Starting with Portworx Operator 25.6.0, the Portworx Plugin components (`px-plugin` and `px-plugin-proxy`) are deployed only when the OpenShift Console plugin is enabled. In earlier versions, these components were always deployed, even when the plugin was disabled. You can configure resource limits, tolerations, and other settings for these components using the `ComponentK8sConfig` CR.

FieldDescriptionTypeDefault

spec.
ocpDynamicPlugin.
pluginImageSpecifies the image for the Portworx Plugin deployment. Use this field to override the default plugin image with a custom image.`string`None

spec.
ocpDynamicPlugin.
proxyImageSpecifies the image for the Portworx Plugin Proxy deployment. Use this field to override the default proxy image with a custom image.`string`None

### Node specific configuration​

This section provides details on how to override certain cluster-level configuration for individual or group of nodes.

FieldDescriptionTypeDefault

spec.
nodes[]A list of node specific configurations.`[]object`None

spec.
nodes[].
selectorSelector for the node(s) to which the configuration in this section will be applied.`object`None

spec.
nodes[].
selector.
.nodeNameName of the node to which this configuration will be applied. Node name takes precedence over `selector.labelSelector`.`string`None

spec.
nodes[].
selector.
.labelSelectorKubernetes style label selector for nodes to which this configuration will be applied.`object`None

spec.
nodes[].
networkSpecify network configuration for the selected nodes, similar to the one specified at cluster level. If this network configuration is empty, then cluster level values are used.`object`None

spec.
nodes[].
storageSpecify storage configuration for the selected nodes, similar to the one specified at cluster-level. If some of the config is left empty, the cluster-level storage values are passed to the nodes. If you don't want to use a cluster-level value and set the field to empty, then explicitly set an empty value for it so no value is passed to the nodes. For instance, set `spec.nodes[0].storage.kvdbDevice: ""`, to prevent using the KVDB device for the selected nodes.`object`None

spec.
nodes[].
envSpecify extra environment variables for the selected nodes. Cluster level environment variables are combined with these and sent to the selected nodes. If same variable is present at cluster level, then the node level variable takes precedence.`[]object`None

spec.
nodes[].
runtimeOptionsSpecify runtime options for the selected nodes. If specified, cluster-level options are ignored and only these runtime options are passed to the nodes. Note: When runtime options are specified as part of the `misc-args` annotation using `rt_opts`, the key-value pairs in `RuntimeOptions` are ignored, and a warning is raised in the `StorageCluster`.`map[string]string`None

spec.
nodes[].
miscArgsString of command-line arguments passed to the Portworx container. This field overrides or adds to miscellaneous arguments specified in cluster-level annotations (`portworx.io/misc-args`).`string`None

### Security Configuration​

FieldDescriptionTypeDefault

spec.
security.
enabledEnables or disables Security at any given time.`boolean``false`

spec.
security.
auth.
guestAccessDetermines how the guest role will be updated in your cluster. The options are Enabled, Disabled, or Managed. Managed will cause the operator to ignore updating the system.guest role. Enabled and Disabled will allow or disable guest role access, respectively.`string`Enabled

spec.
security.
auth.
selfSigned.
tokenLifetimeThe length operator-generated tokens will be alive until being refreshed.`string`24h

spec.
security.
auth.
selfSigned.
issuerThe issuer name to be used when configuring PX-Security. This field maps to the `PORTWORX_AUTH_JWT_ISSUER` environment variable in the Portworx Daemonset.`string`operator.portworx.io

spec.
security.
auth.
selfSigned.
sharedSecretThe Kubernetes secret name for retrieving and storing your shared secret. This field can be used to add a pre-existing shared secret or for customizing which secret name the operator will use for its auto-generated shared secret key. This field maps to the `PORTWORX_AUTH_JWT_SHAREDSECRET` environment variable in the Portworx Daemonset.`string`px-shared-secret

### StorageCluster Annotations​

AnnotationDescription

`portworx.io/misc-args`Arguments that you specify in this annotation are passed to the Portworx container verbatim. Note that you cannot use `=` to specify the value of an argument.
Some of the arguments that you can specify in the annotation are listed below:

- `-cluster_domain` - Specifies the cluster domain.

- `--tracefile-diskusage` - Enables tracing disk usage and logs the statistics.

- `-kvdb_cluster_size` - Specifies the size of the KVDB cluster.

- `--memory` - Specifies the memory in bytes that the Portworx service can consume.

- `--cpus` - Specifies the number of CPUs that Portworx service can use.

- `-T px-storev2` - Enables PX-StoreV2 datastore. For more information about PX-StoreV2, see PX-StoreV2.

- `-rt_opts small_conf=1` - Enables small configuration mode for Two-Node with Arbiter (TNA) setups. This is automatically set when generating StorageCluster specification for a TNA setup using Portworx Central.

Note: CPU and memory limits set under the `spec.resources` field apply only to the Kubernetes pod (OCI monitor), not to the `px-runc` container within the pod. To set resource limits for `px-runc`, use the appropriate annotation instead.

Example usage:
 `portworx.io/misc-args: "-cluster_domain datacenter1 --tracefile-diskusage 5 -kvdb_cluster_size 5 --memory 8589934592 --cpus 2"`

`portworx.io/service-type`Annotation to configure type of services created by operator. For example:
`portworx.io/service-type: "LoadBalancer"` to specify `LoadBalancer` type for all services.
 For Operator 1.8.1 and higher, the value can be a list of service names and corresponding type configurations split in `;`, service not specified will use its default type. For example:
`portworx.io/service-type: "portworx-service:LoadBalancer;portworx-api:ClusterIP;portworx-kvdb-service:LoadBalancer"`

`portworx.io/portworx-proxy`Portworx proxy is needed to allow Kubernetes to communicate with Portworx when using the in-tree driver. The proxy is automatically enabled if you run Portworx in a namespace other than kube-system and not using the default 9001 start port. You can set the annotation to `false` to disable the proxy. For example:
`portworx.io/portworx-proxy: "false"`

`portworx.io/disable-storage-class`When applied to a StorageCluster object and set to true, this annotation instructs the Portworx Operator to disable and remove the default storage classes created during Portworx setup. For example: portworx.io/disable-storage-class: "true"

`portworx.io/health-check`An annotation created by the Operator to save the state of the health checks. If the health checks pass, the Operator writes a value of `passed`. If the health checks fail, the Operator writes a value of `failed` and reruns the checks periodically. You can control the health checks manually by setting the value to `skip` to bypass the health checks, or removing the annotation to instruct the Operator to rerun the checks immediately.

`portworx.io/disable-non-disruptive-upgrade`Annotation to enable smart upgrade feature for Portworx upgrades. To enable the smart upgrade, set the `portworx.io/disable-non-disruptive-upgrade` annotation to `false`.

`portworx.io/storage-pdb-min-available`Annotation to configure the minimum number of nodes that must be available at a time during the platform upgrade. By default, Operator uses the following values if the annotation is not present in the StorageCluster:

- When smart upgrade is enabled, default value is `quorum`.

- When smart upgrade is disabled, default value is `number of nodes-1`.

`portworx.io/migrate-v1-to-v2`Triggers an automated migration from PX-StoreV1 (btrfs) to PX-StoreV2 (dm-thin). Specify a timestamp value (for example, `"2 Jan 2006 3:04 PM"`) to determine when the migration starts. If the timestamp is in the past or present, the migration starts immediately. If the timestamp is in the future, the migration waits until the specified time. The Operator runs preflight checks, enables mixed mode temporarily, and converts nodes one at a time from PX-StoreV1 to PX-StoreV2. During migration, the Operator adds `-rt_opts allow_mixed_mode=1 -T PX-StoreV2` to the `portworx.io/misc-args` annotation and uses the configured system metadata device. Requires Portworx Operator 25.6.0 or later and Portworx Enterprise 3.3.0 or later. To skip specific nodes, add the `portworx.io/skip-pxStorev2-migration=true` label to those nodes. For more information, see Migrate Portworx Datastore from PX-StoreV1 to PX-StoreV2.

`portworx.io/node-drain-timeout`Specifies the timeout for draining volume attachments from a node during PX-StoreV1 to PX-StoreV2 migration. Supported formats include `5s` (seconds), `5m` (minutes), and `5h` (hours). Example: `portworx.io/node-drain-timeout: "5m"`. If not specified, the Operator waits indefinitely. If the timeout expires, the migration pauses and requires manual intervention.

`portworx.io/modify-nodedrain-job-state`Controls the state of node drain jobs during PX-StoreV1 to PX-StoreV2 migration. Supported values: `pause=<job-id>`, `resume=<job-id>`, `cancel=<job-id>`. Example: `portworx.io/modify-nodedrain-job-state: "pause=node-1-drain"`. Use this annotation to pause, resume, or cancel a node drain job.

## Footnotes​

-
As an example, here's how you can enable the `CSI` feature.

For Operator 1.8 and higher:

```

spec:

  csi:

    enabled: true

    installSnapshotController: false

```

For Operator 1.7 and earlier:

```

spec:

  featureGates:

    CSI: "true"

```

You can also use `CSI: "True"` or `CSI: "1"`. ↩

-
The following example configures custom annotations. Change `<custom-domain/custom-key>: <custom-val>` to whatever `key: val` pairs you wish to provide.

```

spec:

  metadata:

    annotations:

      pod/storage:

        <custom-domain/custom-key>: <custom-val>

      service/portworx-api:

        <custom-domain/custom-key>: <custom-val>

      service/portworx-service:

        <custom-domain/custom-key>: <custom-val>

      service/portworx-kvdb-service:

        <custom-domain/custom-key>: <custom-val>

```

Note that `StorageCluster.spec.metadata.annotations` is different from `StorageCluster.metadata.annotations`. Currently, custom annotations are supported on following types of components:

TypeComponents

Podstorage pods

Serviceportworx-api
 portworx-service
 portworx-kvdb-service

 ↩

-
Portworx supports adding custom labels to all components it manages. This feature allows users to specify custom labels in the `StorageCluster` spec under `.spec.metadata.labels`. These labels are automatically propagated to the respective components managed by the operator.

Change `<custom-label-key>: <custom-val>` to whatever `key: val` pairs you wish to provide.

To add custom labels, include them in the `StorageCluster` spec as shown below:

```

spec:

  metadata:

    labels:

      deployment/autopilot:

        <custom-label-key>: <custom-val>

      daemonset/portworx-api:

        <custom-label-key>: <custom-val>

      service/portworx-api:

        <custom-label-key>: <custom-val>

```

Note that `StorageCluster.spec.metadata.labels` is different from `StorageCluster.metadata.labels`.

Global Labels

You can also specify global labels for all components of a specific type.

note

Global labels are overwritten if component-specific labels are provided.

Example:

```

spec:

  metadata:

    labels:

      deployment/*:

        <custom-label-key1>: <custom-val1>

      daemonset/*:

        <custom-label-key2>: <custom-val2>

```

In this example:

- All components of type `deployment` will have the label `<custom-label-key1>: <custom-val1>`.

- All components of type `daemonset` will have the label `<custom-label-key2>: <custom-val2>`.

Custom labelling is supported for the following components managed by Operator:

- `deployment/autopilot`

- `deployment/px-csi-ext`

- `deployment/px-plugin`

- `deployment/px-plugin-proxy`

- `daemonset/portworx-api`

- `service/portworx-api`

- `daemonset/portworx-proxy`

- `deployment/portworx-pvc-controller`

- `daemonset/px-telemetry-phonehome`

- `deployment/px-telemetry-registration`

- `deployment/px-metrics-collector`

- `pod/storage`

- `pod/portworx-kvdb`

- `deployment/stork`

- `deployment/stork-scheduler`

- `deployment/px-prometheus-operator`

- `prometheus/px-prometheus`

- `alertmanager/portworx`

The following label keys are reserved by the Portworx Operator and are ignored when specified as custom labels:

- `name`

- `tier`

- `component`

- `app`

- `role`

- `k8s-app`

- `operator.libopenstorage.org/managed-by`

- `operator.libopenstorage.org/driver`

- `operator.libopenstorage.org/name`

- `operator.libopenstorage.org/node-name`

- `storage`

- `operator.libopenstorage.org/controller-revision-hash`

- `kvdb`

 ↩

-
Note that Portworx ignores this field if you specify the storage devices using the `spec.storage.devices` field. ↩ ↩2

-
If you manually delete any of the default KubeVirt `StorageClasses`, the Operator does not automatically re-create them. To trigger re-creation, manually restart the `px-operator` pod. ↩ ↩2 ↩3

In this topic:
