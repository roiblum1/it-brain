# Rapid Migration of VMs from VMware to OpenShift Virtualization using XCOPY

Source: https://docs.portworx.com/portworx-enterprise/provision-storage/kubevirt-vms/rapid-vm-migration (Portworx Enterprise latest)

Rapid Migration of VMs from VMware to OpenShift Virtualization using XCOPY | Portworx Enterprise Documentation

This topic explains how to rapidly migrate VMware virtual machines to OpenShift Virtualization by using the storage copy offload feature of Migration Toolkit for Virtualization (MTV, formerly Forklift) with Portworx as the storage platform.

Traditional migrations transfer VM data over the network through the migration controller, which can be slow and resource-intensive for large disks. The storage copy offload feature instead delegates the data copy to the underlying storage array using the SCSI XCOPY command, allowing FlashArray to clone LUNs directly without transferring data through the host or network. This approach reduces migration time and minimizes network usage.

## Overview​

The migration workflow consists of the following phases:

- User creates a migration plan by selecting the target VMs and then executes the migration.

- MTV offloads the data copy from the VM disk to a temporary FADA volume to the FlashArray. The FlashArray performs the XCOPY operation directly between the LUNs.

- A post-migration hook copies the FADA data into Portworx-backed volumes on the same FlashArray.

- The migrated VM starts on OpenShift Virtualization by using the Portworx-backed target PVCs.

The migration workflow uses a custom image that runs as a post-migration hook in MTV. This hook performs the following tasks:

-
Identifies migrated VM disks

-
Creates corresponding Portworx volumes
If the Portworx `StorageClass` uses `volumeBindingMode: WaitForFirstConsumer`, the hook first determines the node on which the VM will run. For more information, see Use a WaitForFirstConsumer StorageClass for hyperconvergence.

-
Initiates data conversion

-
Rebinds VM PVCs to Portworx volumes

-
Restarts VMs after conversion

## Prerequisites​

Before you begin, ensure that your cluster meets the following prerequisites:

- Meet all prerequisites for migrating VMs using the storage copy offload feature.
For more information, see the Prerequisites section in OpenShift documentation.

- OpenShift Virtualization is installed.
For information on how to install OpenShift Virtualization, see OpenShift documentation.

- Migration Toolkit for Virtualization (MTV) version 2.10 or later is installed.
For information on how to install MTV, see OpenShift documentation.

- Portworx Enterprise version 3.5.1 or later is installed.

- FlashArray runs Purity 6.3 or later.

- Network connectivity exists between VMware, FlashArray, and the OpenShift cluster.

- SSH connectivity is enabled from the FlashArray to the VMware ESXi hosts.
The vSphere XCOPY populator uses SSH during migration planning, and the plan fails validation if SSH connectivity is not configured.

- The source datastore is a VMFS or vVol datastore.

- A target namespace for migrated VMs (for example, migrated-vms) is created.

## Limitations​

Consider the following limitations before you begin the migration process:

- This feature is supported only on PX-StoreV2 deployments.

- The source VMware datastore and the target Portworx storage must reside on the same FlashArray and within the same FlashArray realm. Migration between different FlashArrays is not supported.

- Only cold (offline) migrations are supported, and the VM state is preserved.

- A single migration plan is validated for the following scale:

- Up to 25 VMs per plan

- Up to 100 disks across all VMs in a plan

- Data disks up to 35 TB

- Only Fibre Channel (FC) and iSCSI storage protocols are supported. NVMe/TCP is not supported.

- If the cluster uses Kube Datastore dynamic pools, pause pool failover before you migrate VMs. A pool move during the `XCOPY` copy causes the copy to fail. For more information, see Rapid VM Migration limitations on Kube Datastore.

- If the cluster has more than one FlashArray, set `kube_datastore_affinity` in the `StorageClass` that you use as `PXD_STORAGE_CLASS`, so that Portworx creates the volumes on the same FlashArray as the source datastore. For more information, see Rapid VM Migration limitations on Kube Datastore.

## Best practices and recommendations​

Review the following best practices and recommendations to plan a successful migration.

### Increase virt-v2v pod resources for VMs with large disks​

When you migrate a VM that has large disks, increase the memory resources of the `virt-v2v` pod on the `ForkliftController`. For example, to migrate a VM with 20 TB disks, run the following command:

```

oc patch ForkliftController -n openshift-mtv forklift-controller --type=merge \

-p '{"spec": {"virt_v2v_memsize": "64000", "virt_v2v_container_limits_memory": "64Gi", "virt_v2v_container_requests_memory": "16Gi"}}'

```

### Keep all FlashArray objects in the same FlashArray Pod or outside a Pod​

FlashArray does not support cross-Pod XCOPY. When you use FlashArray Pods, ensure that the VMware datastore, the intermediate FADA volume, and the FlashArray cloud drives that Portworx uses reside in the same FlashArray Pod. Alternatively, ensure that all of these objects reside outside a FlashArray Pod.

To pin the intermediate FADA volume to a Pod, specify the `pure_fa_pod_name: "<fa-pod-name>"` parameter in the FADA `StorageClass`.

### Create a separate migration plan for VMs with more than 15 disks or at least one disk that is larger than 5TB​

If a VM has more than 15 disks or at least one disk that is larger than 5TB, Portworx by Everpure recommends that you create a separate MTV migration plan for that VM instead of including it in a larger shared plan.

### Use a WaitForFirstConsumer StorageClass for hyperconvergence​

A VM is hyperconverged when it runs on the same node as the storage pools that contain its disks. To place migrated VMs in this configuration, specify a Portworx `StorageClass` that uses `volumeBindingMode: WaitForFirstConsumer` (WFFC) as the `PXD_STORAGE_CLASS` value in the storage secret. For more information, see Step 3: Create the storage secret.

Rapid VM Migration supports both `Immediate` and WFFC destination StorageClasses. With `Immediate` binding, Kubernetes provisions the volumes before a node is selected for the VM, so the volumes might not reside on the node where the VM runs.

To use `WaitForFirstConsumer` (WFFC) with initial hyperconvergence, ensure that:

- Portworx Enterprise 3.7.2 or later is installed.

- The post-migration hook image is version `v1.1.0` or later.

The following table describes WFFC migration behavior for different Portworx Enterprise and hook image versions:

Portworx Enterprise versionHook image versionBehavior

3.7.2 or later`v1.1.0` or laterWFFC migration is supported, and Portworx enforces initial hyperconvergence.

Earlier than 3.7.2`v1.1.0` or laterWFFC migration is supported, but Portworx does not enforce initial hyperconvergence.

Any versionEarlier than `v1.1.0`WFFC migration is not supported.

When the `StorageClass` uses WFFC, the post-migration hook does the following before it converts the FADA volumes:

- Creates an intermediate VM instance that reflects the CPU and memory requests, node affinity rules, and anti-affinity rules of the source VM.

- Waits for the Kubernetes scheduler to select a node for the intermediate VM instance.

- Records the selected node on the destination PVCs.

Portworx then places the volumes on the node where the VM is expected to run. Kubernetes node selectors, taints, tolerations, and node affinity rules that you configured for the VM are honored during volume and VM placement.

For VMs with multiple disks, the migration supports disks that use a combination of `Immediate` and WFFC StorageClasses. Only the disks that use a WFFC `StorageClass` receive initial hyperconvergence. To hyperconverge all disks of a VM, use a WFFC `StorageClass` for each disk.

For more information about hyperconvergence on Kube Datastore, see Run KubeVirt VMs on Kube Datastore.

## Procedure​

### Step 1: Enable the `feature_copy_offload` setting​

In MTV Operator, set the value of `feature_copy_offload` to `true` in `forklift-controller`:

```

oc patch forkliftcontrollers.forklift.konveyor.io forklift-controller --type merge -p '{"spec": {"feature_copy_offload": "true"}}' -n openshift-mtv

```

### Step 2: Configure RBAC and ConfigMap in your OpenShift Cluster​

A cluster administrator must create the following resources before the migration runs:

- A `ServiceAccount` named `fa-pxd-converter` in the `openshift-mtv` namespace

- A `ClusterRole` that can manage PVCs, PVs, pods, jobs, `StorageClass` objects, secrets, `StorageMap` objects, and KubeVirt VM resources

- A `ClusterRoleBinding` for the `fa-pxd-converter` ServiceAccount

- An OpenShift `SecurityContextConstraints` object that allows privileged execution for the `fa-pxd-converter` ServiceAccount

- A `ConfigMap` named `fa-pxd-hook-config` in the `openshift-mtv` namespace that configures the post-migration hook

The `fa-pxd-hook-config` ConfigMap contains the following keys:

KeyDescriptionRequiredDefault

CONVERTER_IMAGESpecifies the container image that the privileged data-copy pods run. Set this key to `docker.io/portworx/fa-pxd-converter:v1.1.0`.Yes-

FA_API_VERSIONSpecifies the FlashArray REST API version that the hook uses.No2.9

XCOPY_JOBSSpecifies the total number of XCOPY jobs that the hook creates.No512

XCOPY_CONCURRENCYSpecifies the maximum number of XCOPY jobs that run at the same time.No8

POKE_WORKERSSpecifies the total number of poke jobs that the hook creates.No512

POKE_CONCURRENCYSpecifies the maximum number of poke jobs that run at the same time.No10

STATS_INTERVALSpecifies the interval, in seconds, at which the hook reports progress statistics.No60

VERIFY_AFTER_COPYSpecifies whether to compare the FADA and Portworx volumes before rebinding the PVCs. Set to `true` to enable verification.Nofalse

CONVERTER_POD_MAX_RETRIESSpecifies the `backoffLimit` of the conversion job, which is the number of times the job retries when a converter pod fails, is OOMKilled, or loses its node.No2

DEVICE_ATTACH_TIMEOUT_MINUTESSpecifies how long, in minutes, the hook waits for the source volume device path to appear on the XCOPY node.No10

To create the RBAC resources and ConfigMap, do the following:

-
Create a YAML file, for example `migration-rbac.yaml`, based on the information provided in the template file.

important

This template uses `migrated-vms` as the target migration namespace. Replace it with your target namespace where applicable.

-
Apply the YAML file.

```

oc apply -f migration-rbac.yaml

```

### Step 3: Create the storage secret​

-
Identify the Portworx (`pxd`) `StorageClass` that backs the migrated volumes. You must specify this `StorageClass` as the `PXD_STORAGE_CLASS` value when you create the secret.

```

oc get storageclass

```

If your cluster does not have a suitable Portworx `StorageClass`, create one before you continue.

To place migrated VMs on the same node as their storage, select a `StorageClass` that uses `WaitForFirstConsumer` binding. For more information, see Use a WaitForFirstConsumer StorageClass for hyperconvergence.

-
Create a Kubernetes secret in the `openshift-mtv` namespace with the Pure FlashArray management endpoint, user credentials, and the `PURE_CLUSTER_PREFIX` value. Create the secret once, with all the fields:

```

oc create secret generic <your-storage-map-secret> \

-n openshift-mtv \

--from-literal=STORAGE_HOSTNAME="<flasharray-mgmt>" \

--from-literal=STORAGE_TOKEN="<flasharray-api-token>" \

--from-literal=STORAGE_SKIP_SSL_VERIFICATION="false" \

--from-literal=PURE_CLUSTER_PREFIX="px_<8chars>" \

--from-literal=PXD_STORAGE_CLASS="<your-px-storage-class>"

```

Replace `<your-storage-map-secret>` with the name of your secret.

note

Portworx supports `STORAGE_TOKEN` based authentication for Pure FlashArray, which replaces the need for username and password credentials.

The following table describes the parameters in the Pure FlashArray storage secret.

KeyDescriptionRequiredDefault

STORAGE_HOSTNAMESpecifies the IP address or URL of the FlashArray management endpoint. Do not include a protocol prefix such as `https://`.Yes-

STORAGE_TOKENSpecifies the FlashArray API token used for authenticationYes-

STORAGE_USERNAMESpecifies the FlashArray user name. Not required when you use `STORAGE_TOKEN`.No-

STORAGE_PASSWORDSpecifies the password for the FlashArray user. Not required when you use `STORAGE_TOKEN`.No-

STORAGE_SKIP_SSL_VERIFICATIONSpecifies whether to skip SSL verification. Set to true to disable SSL verificationNofalse

PURE_CLUSTER_PREFIXSpecifies the cluster prefix. The value is set in the StorageCluster resource.
To retrieve it, run the following command:
`printf "px_%.8s" $(oc get storagecluster -A -o=jsonpath='{.items[?(@.spec.cloudStorage.provider=="pure")].status.clusterUid}')`.

Set `PURE_CLUSTER_PREFIX` to the FlashArray volume-name prefix that precedes the Portworx volume ID. The hook builds the FlashArray volume name as `<PURE_CLUSTER_PREFIX>-<px-volume-id>`.

For example:
• Without a FlashArray Pod, `PURE_CLUSTER_PREFIX: "px_4c1a2b3d"` produces the volume name `px_4c1a2b3d-<px-volume-id>`.
• With a FlashArray Pod, `PURE_CLUSTER_PREFIX: "performance-pod::px_4c1a2b3d"` produces the volume name `performance-pod::px_4c1a2b3d-<px-volume-id>`.Yes-

PXD_STORAGE_CLASSSpecifies the Portworx (`pxd`) `StorageClass` that backs the migrated volumes. Specify it only in this secret, not in the storage map.Yes-

-
Verify that the secret is created successfully:

```

oc get secret <your-storage-map-secret> -n openshift-mtv

```

```

NAME                        TYPE     DATA   AGE

<your-storage-map-secret>   Opaque   5      10s

```

### Step 4: Create an ownerless storage map​

Create an ownerless storage map by using the OpenShift console. For more information, see OpenShift documentation.

important

In the Offload options (optional) section, complete the following steps:

- Select vSphere XCOPY from Offload plugin dropdown menu.

- Select `<your-storage-map-secret>` from the Storage secret dropdown menu. This secret is created in Step 3.

- Select Pure Storage FlashArray from the Storage product dropdown menu.

When you configure the storage map, map the source VMware datastore to a FADA (FlashArray Direct Access) `StorageClass`. Do not map it to the Portworx (`pxd`) `StorageClass`. The Portworx `StorageClass` is specified separately in the storage secret as `PXD_STORAGE_CLASS` in Step 3.

The following example shows a FADA `StorageClass` that you can reference in the storage map:

```

kind: StorageClass

apiVersion: storage.k8s.io/v1

metadata:

  name: sc-portworx-fa-direct-access

provisioner: pxd.portworx.com

parameters:

  backend: "pure_block"

  pure_fa_pod_name: "<fa-pod-name>"

allowVolumeExpansion: true

```

If your cluster uses a FlashArray Pod, you must specify the Pod name in the `pure_fa_pod_name` parameter. If you do not use a FlashArray Pod, omit this parameter.

### Step 5: Create migration plan with post-migration hook​

Create a migration plan by using the OpenShift console.
For more information, see OpenShift documentation.

To convert FADA volumes into Portworx-backed volumes, enable the post-migration hook when you create the migration plan. To do this, perform the following steps on the Hooks (optional) page in the OpenShift console:

- Select the Enable post migration hook checkbox.

- In the Hook runner image field, enter `docker.io/portworx/fa-pxd-hook:v1.1.0`.

- In the Service account field, enter `fa-pxd-converter`.

note

-
For MTV 2.11 and later, set the Service account directly in the OpenShift console while enabling the hook.

-
For MTV versions earlier than 2.11, set the Service account after creating the migration plan but before starting the migration:

```

oc -n openshift-mtv patch hook <plan-name>-post-hook \

-p '{"spec":{"serviceAccount":"fa-pxd-converter"}}' \

--type merge

```

Replace `<plan-name>` with the name of your migration plan.

important

Ensure that the conversion image that you specified in the `CONVERTER_IMAGE` key in Step 2 is accessible from your OpenShift cluster, and that the image pull secrets are configured, if required.

### Step 6: Run and monitor the migration​

Start the migration from MTV and monitor its progress until the hook workflow completes.

When the migration completes, the Migration status column on the Migration plans page displays Complete.

The post-migration hook converts the FADA volumes, rebinds the VM PVCs, and restarts the VMs automatically.

If you set the VM target power state to Retain source VM power state, Portworx Enterprise preserves the source VM power state.

### Step 7: Verify the migration​

After the migration completes, verify that the resources are correctly created and configured:

-
Verify that the VM is running.
To do this, navigate to Virtualization > VirtualMachines > `<vm-name>`. The VM is running if the status is Running on the Overview tab of the VirtualMachine details page.
Alternatively, you can run the following command:

```

oc get vm,vmi -n <namespace>

```

```

NAME        AGE   STATUS   IP            NODE

<vm-name>   10m   Running  10.130.0.10   <node-name>

```

-
Verify that the PVCs are bound and use the Portworx `StorageClass`:

```

oc get pvc -n <namespace>

```

```

NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE

<pvc-name>      Bound    pvc-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx   10Gi       RWO            portworx-sc    10m

```

## Troubleshooting​

Use the following guidance to identify and resolve common issues that may occur during or after migration.

IssueSymptomResolution

VM does not restartThe VM does not start after migration.Run the `oc patch vm <vm-name> -n <namespace> --type merge -p '{"spec":{"running":true}}'` command. Replace `<vm-name>` with the name of the VM that did not restart and `<namespace>` with the namespace where the VM is deployed.

Permission errors during migrationErrors occur when creating or updating resources.Verify the RBAC configuration in Configure RBAC and ConfigMap in your OpenShift Cluster. Ensure that the correct ServiceAccount is configured in the migration hook.

The post-migration hook fails, but the VM is migrated with FADA PVCs.NARun only the post-migration hook instead of the entire migration plan by updating the required placeholder values in the manifest and applying it.

The post-migration hook fails.The error shown in the OpenShift console might not reveal the actual cause of the failure.Check the logs of the hook pod in the `openshift-mtv` namespace.

To find the hook pod, run `oc get pods -n openshift-mtv | grep <forklift-plan-name>`.

To view its logs, run `oc logs -n openshift-mtv <hook-pod-name>`.

Slow migrationMigration takes longer than expected.Validate FlashArray integration and confirm storage mapping configuration.

Storage not using Portworx volumesVM disks are not backed by Portworx volumes.Verify the StorageClass configuration and confirm that the post-migration hook is completed successfully.

In this topic:
