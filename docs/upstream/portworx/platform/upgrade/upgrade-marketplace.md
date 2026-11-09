# Upgrade Portworx Marketplace Deployment

Source: https://docs.portworx.com/portworx-enterprise/platform/upgrade/upgrade-marketplace (Portworx Enterprise latest)

Upgrade Portworx Marketplace Deployment | Portworx Enterprise Documentation

## Upgrade or reconfigure Portworx using AWS Marketplace​

note

During an upgrade, Portworx pods are deleted and re-created on each node to apply the spec changes. The `spec.updateStrategy` field in the StorageCluster resource controls how nodes are upgraded. By default, the update strategy is RollingUpdate, and the `maxUnavailable` field specifies the maximum number of nodes that can be unavailable at a time. The default value of `maxUnavailable` is 1.

This is expected behavior, and you might see pod deletion events in the Kubernetes audit logs. You don't need to take any action.

When Portworx releases new versions, you can upgrade it through Helm. You can also reconfigure Portworx through Helm by performing upgrade operations, even if there is no new version to upgrade to. Perform the following steps to upgrade or reconfigure Portworx:

-
Upgrade the Helm repository to make sure you have the latest version of the Helm chart by running the following `helm` command:

```

helm repo update

```

-
Upgrade or reconfigure Portworx by running the `upgrade` command and specifying the same options you used when you installed Portworx, or new options if you want to reconfigure Portworx. For example:

```

helm upgrade my-release portworx/portworx --set storage.drives="type=gp2\,size=1000" --set serviceAccount="portworx-aws"

```

## Upgrade Portworx on IBM Cloud via Helm​

Prerequisites:

- You must be logged in to your IBM Cloud account

- You have installed Helm client

Steps to Upgrade:

-
Add the `ibm-px` repository to your local Helm repository:

```

helm repo add ibm-px https://raw.githubusercontent.com/portworx/ibm-helm/master/repo/stable

```

-
Verify that the repository has been successfully added:

```

helm repo list

```

```

NAME    URL

ibm-px  https://raw.githubusercontent.com/portworx/ibm-helm/master/repo/stable

```

-
Download the latest Portworx Helm chart version from the `ibm-px` repository to your local repository:

```

helm repo update

```

```

Hang tight while we grab the latest from your chart repositories......

Successfully got an update from the "ibm-px" chart repository update Complete.

⎈ Happy Helming!⎈

```

-
Run the following command to get the namespace where Portworx is deployed. You will need this in the next step:

```

helm ls

```

```

NAME        NAMESPACE   REVISION    UPDATED                             STATUS      CHART             APP VERSION

portworx    default     1           2023-04-13 03:55:43.649969545 +0000 UTC   deployed    portworx-1.0.44    2.13.0

```

In the above example, the Portworx Helm chart is deployed in the `default` namespace and the current version of Portworx Helm chart running on your IKS or OCP cluster is `portworx-1.0.44`.

-
Save the parameters of the currently running Portworx catalog to the `values.yaml` file using the following command. Replace the `px-namespace` with the namespace obtained in the previous step:

```

helm get values portworx -n <px-namespace> > /tmp/values.yaml

```

-
Find the latest Portworx Versions, then add them to the respective fields in the `/tmp/values.yaml` file:

- `imageVersion`: add the latest Portworx version

- `storkVersion`: add the latest Stork version

-
Apply the edited YAML file to install the latest Portworx Helm chart:

```

helm upgrade portworx -f /tmp/values.yaml ibm-px/portworx

```

```

Release "portworx" has been upgraded. Happy Helming!

NAME: portworx

LAST DEPLOYED: Thu Apr 13 09:48:59 2023

NAMESPACE: default

STATUS: deployed

REVISION: 2

NOTES:

Your Release is named "portworx"

Portworx Pods should be running on each node in your cluster.

```

Once the Portworx Helm chart has been successfully applied, you will see the details of your deployment.

-
Verify that Portworx Helm chart version has been updated. You should see that it has been updated from `portworx-1.0.44` to `portworx-1.0.46`.

```

helm ls

```

```

NAME        NAMESPACE   REVISION    UPDATED                             STATUS      CHART       APP VERSION

portworx    default           2     2023-04-13 09:48:59.58672 +0530 IST       deployed    portworx-1.0.46   2.13.2

```

In this topic:
