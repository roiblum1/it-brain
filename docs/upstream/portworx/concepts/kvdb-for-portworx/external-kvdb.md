# External KVDB for Portworx on Kubernetes

Source: https://docs.portworx.com/portworx-enterprise/concepts/kvdb-for-portworx/external-kvdb (Portworx Enterprise latest)

External KVDB for Portworx on Kubernetes | Portworx Enterprise Documentation

Portworx can use an external key-value database (KVDB) to store cluster metadata and configuration data. Portworx supports etcd as the only external KVDB. etcd is a highly available, distributed key-value store that you deploy and manage independently of Portworx. Use an external KVDB only when required by your deployment.

## Prerequisites​

Before configuring Portworx to use an external KVDB, ensure that your etcd cluster meets the following requirements:

-
A three node etcd cluster with etcd version 3.3 or later.

-
A minimum of 8 GB of memory dedicated to each etcd node.

-
KVDB drive requirements:

- If IOPS are independent of disk size, Portworx recommends a minimum size of 32 GB or a minimum of 450 IOPs.

- If IOPS are dependent on disk size, Portworx recommends a size of 150 GB.

note

If you use cloud-based storage, size the drive according to your cloud provider’s specifications to meet the minimum IOPS requirements.

-
The recommended hardware requirements.

-
Round-trip time (RTT) between etcd members must not exceed 125 ms. Portworx recommends an RTT of 100 ms or less for optimal performance.

## Best practices for maintaining an etcd cluster​

Follow these best practices to keep your etcd cluster healthy and performant when used with Portworx.

#### Configure Compaction​

etcd stores a complete history of its keyspace, and regular compaction is necessary to avoid performance issues and running out of storage space. Regular compaction helps manage the memory usage of the etcd process.

You can configure the compaction period using the `etcd` tool with the `--auto-compaction-retention` option.

Portworx recommends that you retain the history for the last 3 hours. To achieve this, set `--auto-compaction-retention` to `3`. For information on how to set the compaction period, see the etcd documentation.

#### Configure Space Quota​

A space quota, or setting a database size limit in etcd, is crucial for maintaining a stable cluster. Without a space quota, etcd can experience performance issues when the keyspace grows excessively and the available storage space is consumed, resulting in unpredictable cluster behavior.

Portworx recommends that you set the space quota to a maximum value of 8 GiB. To achieve this, use the `etcd` tool to set the `--quota-backend-bytes` to `$((8*1024*1024*1024))`.

For more information on how to set the space quota, see the etcd documentation.

#### Take Regular Snapshots​

You can recover your etcd cluster in the event of a disaster by taking a snapshot of its keyspace. Run the following command as part of a cron job (either on the etcd nodes or on a separate node) to store periodic etcd snapshots:

```

ETCDCTL_API=3 etcdctl --endpoints="<comma-separated-etcd-url>" snapshot save </path/to/snapshot-file> --command-timeout=60s

```

The above command stores etcd snapshots to the specified file. If any etcd operation takes longer than 60 seconds, it times out and is canceled.

For more information on how to setup a recovery mechanism, see the etcd documentation.

## Secure your etcd communication​

You can configure and secure etcd communication in your environment by storing SSL certificates as Kubernetes secrets. Portworx supports two secret formats for etcd certificates: an Opaque secret with Portworx-specific key names, or a standard `kubernetes.io/tls` secret compatible with cert-manager and other certificate management tools. These certificates are automatically available to new nodes joining the cluster. Choose the option that matches how your certificates are managed: use an Opaque secret if you manage certificate files manually, or a `kubernetes.io/tls` secret if certificates are issued by cert-manager or a similar automated tool.

note

The secret's `type` must match the key names you use. A `kubernetes.io/tls` secret is read using only the `ca.crt`, `tls.crt`, and `tls.key` keys; an `Opaque` secret is read using only the `kvdb-ca.crt`, `kvdb.crt`, and `kvdb.key` keys. If you name the keys from one format but leave the secret's type as the other, Portworx skips certificate-based authentication for the external KVDB.

### Use an Opaque secret​

Follow these steps to create the `px-kvdb-auth` secret using Portworx-specific key names:

-
Copy all your etcd certificates and key into a directory `/kvdb-secrets` to create a Kubernetes secret from it. Ensure that the file names match the default names given below:

```

ls -1 kvdb-secrets/

```

```

kvdb-ca.crt

kvdb.crt

kvdb.key

```

-
Create the secret named `px-kvdb-auth` from the above files:

- Kubernetes

- OpenShift

```

kubectl -n <px-namespace> create secret generic px-kvdb-auth \

--from-file=kvdb-secrets/

```

```

secret/px-kvdb-auth created

```

```

oc -n <px-namespace> create secret generic px-kvdb-auth \

--from-file=kvdb-secrets/

```

```

secret/px-kvdb-auth created

```

-
Verify that the secret has three keys: `kvdb-ca.crt`, `kvdb.crt`, and `kvdb.key`, corresponding to the filenames in the `kvdb-secrets` folder. These keys are used by Portworx to reference the certificates:

- Kubernetes

- OpenShift

```

kubectl -n <px-namespace> describe secret px-kvdb-auth

```

```

Name:         px-kvdb-auth

Namespace:    <px-namespace>

Labels:       <none>

Annotations:  <none>

Type:  Opaque

Data

====

kvdb-ca.crt:      1679 bytes

kvdb.crt:  1680 bytes

kvdb.key:  414  bytes

```

```

oc -n <px-namespace> describe secret px-kvdb-auth

```

```

Name:         px-kvdb-auth

Namespace:    <px-namespace>

Labels:       <none>

Annotations:  <none>

Type:  Opaque

Data

====

kvdb-ca.crt:      1679 bytes

kvdb.crt:  1680 bytes

kvdb.key:  414  bytes

```

-
(Optional) After you update the `px-kvdb-auth` secret with new etcd certificates, Portworx pods typically pick up the new certificates during the next reconciliation. In some cases, however, a running Portworx pod may continue to use the previous certificates because of Kubernetes secret-cache propagation delays, projected-volume mount timing, or a pod that was scheduled just before the secret update.

If this occurs, restart the Portworx service on the affected node to ensure it uses the updated certificates:

```

kubectl label node <node_name> px/service=restart

```

Run this command only on nodes still using the previous certificates. You do not need to restart all nodes or perform this step if Portworx has already applied the updated certificates.

### Use a kubernetes.io/tls secret​

If you manage etcd certificates with cert-manager or another tool that produces `kubernetes.io/tls` secrets, you can use those secrets directly with Portworx. Portworx detects the secret type and reads the `ca.crt`, `tls.crt`, and `tls.key` keys automatically.

note

Support for `kubernetes.io/tls` secrets requires Portworx Operator version 26.3.0 or later.

-
Copy your etcd certificates and key into a directory `/kvdb-secrets` using the standard TLS key names:

```

ls -1 kvdb-secrets/

```

```

ca.crt

tls.crt

tls.key

```

-
Create the secret named `px-kvdb-auth` with type `kubernetes.io/tls`:

- Kubernetes

- OpenShift

```

kubectl -n <px-namespace> create secret generic px-kvdb-auth \

  --type=kubernetes.io/tls \

  --from-file=ca.crt=kvdb-secrets/ca.crt \

  --from-file=tls.crt=kvdb-secrets/tls.crt \

  --from-file=tls.key=kvdb-secrets/tls.key

```

```

secret/px-kvdb-auth created

```

```

oc -n <px-namespace> create secret generic px-kvdb-auth \

  --type=kubernetes.io/tls \

  --from-file=ca.crt=kvdb-secrets/ca.crt \

  --from-file=tls.crt=kvdb-secrets/tls.crt \

  --from-file=tls.key=kvdb-secrets/tls.key

```

```

secret/px-kvdb-auth created

```

-
Verify that the secret has type `kubernetes.io/tls` and three keys: `ca.crt`, `tls.crt`, and `tls.key`:

- Kubernetes

- OpenShift

```

kubectl -n <px-namespace> describe secret px-kvdb-auth

```

```

Name:         px-kvdb-auth

Namespace:    <px-namespace>

Labels:       <none>

Annotations:  <none>

Type:  kubernetes.io/tls

Data

====

ca.crt:   1679 bytes

tls.crt:  1680 bytes

tls.key:  414  bytes

```

```

oc -n <px-namespace> describe secret px-kvdb-auth

```

```

Name:         px-kvdb-auth

Namespace:    <px-namespace>

Labels:       <none>

Annotations:  <none>

Type:  kubernetes.io/tls

Data

====

ca.crt:   1679 bytes

tls.crt:  1680 bytes

tls.key:  414  bytes

```

-
(Optional) After you update the `px-kvdb-auth` secret with new etcd certificates, Portworx pods typically pick up the new certificates during the next reconciliation. In some cases, however, a running Portworx pod may continue to use the previous certificates because of Kubernetes secret-cache propagation delays, projected-volume mount timing, or a pod that was scheduled just before the secret update.

If this occurs, restart the Portworx service on the affected node to ensure it uses the updated certificates:

```

kubectl label node <node_name> px/service=restart

```

Run this command only on nodes still using the previous certificates. You do not need to restart all nodes or perform this step if Portworx has already applied the updated certificates.

### Reference keys for etcd integration with Portworx​

To enhance the security of your Portworx cluster and seamlessly integrate it with an etcd cluster, follow these steps to reference the keys created to secure the etcd cluster:

- Log in to Portworx Central to generate a Portworx spec.

- Click the Customize button at the bottom of the page.

- Select Your etcd details on the Basic window to input your etcd cluster endpoints, and choose the Certificate Auth option to secure your external etcd cluster.

- Follow the wizard to generate the Portworx spec.

#### Verifying external etcd endpoints in the Portworx spec​

After generating the spec, confirm that the `kvdb` section of the StorageCluster resource includes your etcd endpoints and authentication secret:

```

spec:

  kvdb:

    endpoints:

      - etcd:https://<your-etcd-endpoint1>:2379

      - etcd:https://<your-etcd-endpoint2>:2379

      - etcd:https://<your-etcd-endpoint3>:2379

    authSecret: px-kvdb-auth

```

When you install Portworx using the generated spec, it uses your specified cluster as an external KVDB, ensuring secure communication. For more information on how to generate a spec for your environment, see Install Portworx Enterprise.

In this topic:
