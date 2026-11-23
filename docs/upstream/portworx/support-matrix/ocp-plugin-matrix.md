# OpenShift Dynamic Plugin Support Policy

Source: https://docs.portworx.com/portworx-enterprise/support-matrix/ocp-plugin-matrix (Portworx Enterprise latest)

OpenShift Dynamic Plugin Support Policy | Portworx Enterprise Documentation

This topic describes the supported version combinations for the OpenShift Dynamic Plugin. Support is based on validated interoperability between OpenShift, Portworx Enterprise, and the Portworx Operator.

For information on how to enable the OpenShift Dynamic Plugin, see Enable Portworx OpenShift Dynamic Plugin.

## Supported Versions and Combinations​

The following table lists the supported version combinations for the OpenShift Dynamic Plugin. Deployments outside these combinations are not supported for production use.

note

Deployments outside the supported combinations may install successfully but are not supported and may result in reduced or non-functional behavior.

Dynamic PluginPortworx EnterpriseOperatorOpenShift Container PlatformSupport Status

2.4.03.5 or later26.3.2 or later4.18 or laterSupported

2.3.03.5 or later26.2.0 or later4.18 or laterSupported

2.2.03.4 or later25.6.0 or later4.16 or laterSupported

2.1.03.4 or later25.3.1 or later4.16 or laterSupported

2.0.03.3 or earlier25.3.1 or later4.12 or laterSupported

## Cache-Based UI Support​

Cache-based UI functionality enables the OpenShift Dynamic Plugin to retrieve data through a cache-agent service instead of calling Portworx APIs or Kubernetes APIs directly for each request. The cache-agent serves UI data through `/cache/` endpoints to improve performance and reduce backend load.

The following table lists the supported version combinations for the Cache-based UI functionality. Deployments outside these combinations are not supported for production use.

Cache AgentDynamic PluginPortworx EnterpriseOperatorOpenShift Container PlatformSupport Status

1.2.02.4.03.5 or later26.3.2 or later4.18 or laterSupported

1.1.02.3.03.5 or later26.2.0 or later4.18 or laterSupported

1.0.02.2.03.4 or later25.6.0 or later4.16 or laterSupported

## Supported Upgrade Paths​

To enable Dynamic Plugin 2.2.0 in a supported configuration, follow the applicable upgrade path below.

-
If your cluster is running OpenShift version 4.12 through 4.15 and Portworx Enterprise version 3.3 or earlier, upgrade the OpenShift version to 4.16 or later, Portworx Enterprise version to 3.4 or later, and Portworx Operator to version 25.6 or later before upgrading the Dynamic Plugin version to 2.2.0.

-
If your cluster is running OpenShift version 4.16 or later and Portworx Enterprise version 3.3 or earlier, upgrade Portworx Enterprise version to 3.4 or later, and Portworx Operator to version 25.6 or later before enabling Dynamic Plugin version 2.2.0.

In this topic:
