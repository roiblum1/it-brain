# Helm Chart compatibility matrix

Source: https://docs.portworx.com/portworx-enterprise/support-matrix/portworx-helm-chart (Portworx Enterprise latest)

Helm Chart compatibility matrix | Portworx Enterprise Documentation

This topic provides the compatibility matrix for the Portworx Helm chart. For more information, see the Portworx Helm chart GitHub repository. For configurable parameter details, see Portworx Helm Chart Parameters.

## Portworx Helm chart compatibility matrix​

The following table lists the Helm version compatibility with Portworx Enterprise and Operator. Ensuring compatibility between these components is crucial for the successful installation and operation of Portworx on Kubernetes clusters.

important

- Portworx Enterprise supports Helm version 3.x (3.18.0 or later).

Helm chart versionPXE versionOperator version

10.2.03.7.226.5.0

10.1.03.7.126.4.0

10.0.03.7.026.3.2

9.2.03.6.226.3.0

9.1.03.6.126.2.0

9.0.03.6.026.1.0

8.2.13.5.225.6.1

8.2.03.5.225.6.0

8.1.03.5.225.5.2

8.0.13.5.125.5.1

8.0.03.5.025.5.0

7.0.53.4.225.5.0

7.0.33.4.125.4.0

7.0.23.4.0.125.3.1

6.1.13.3.1.325.3.1

5.2.23.2.425.2.2

4.1.13.1.925.2.2

## Unsupported Helm versions​

Older Helm versions use `bitnami/kubectl` images and are not supported. They fail with an `ImagePullBackOff` error.

Helm chart versionPXE versionOperator versionSupport status

6.1.03.3.1.325.3.0Not supported

6.0.53.3.1.325.2.2Not supported

6.0.43.3.1.225.2.2Not supported

6.0.33.3.1.125.2.2Not supported

6.0.23.3.125.2.2Not supported

6.0.13.3.0.125.2.1Not supported

5.2.13.2.325.2.1Not supported

5.1.63.2.324.2.4Not supported

5.1.53.2.2.224.2.4Not supported

5.1.43.2.2.124.2.3Not supported

5.1.33.2.224.2.3Not supported

5.1.23.2.1.224.2.2Not supported

5.1.13.2.1.124.2.1Not supported

5.1.03.2.124.2.0Not supported

5.0.03.2.024.1.3Not supported

4.1.03.1.724.2.0Not supported

4.0.03.1.424.1.1Not supported

note

To upgrade from an unsupported version, follow the supported upgrade path.

For example, if you're using Helm 4.0.0 with PX 3.1.x and want to upgrade to PX 3.4:

- Upgrade to PX 3.2 with Helm 5.2.2

- Then, upgrade to PX 3.3.x with Helm 6.1.1

- Finally, upgrade to PX 3.4 with Helm 7.0.2

In this topic:
