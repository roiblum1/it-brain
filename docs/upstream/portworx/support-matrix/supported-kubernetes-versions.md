# Supported Kubernetes Versions

Source: https://docs.portworx.com/portworx-enterprise/support-matrix/supported-kubernetes-versions (Portworx Enterprise latest)

Supported Kubernetes Versions | Portworx Enterprise Documentation

Portworx by Everpure recommends that you only upgrade to an OpenShift version and Kubernetes version that is listed here. Do not upgrade to a more recent version that is not listed here.

Before you install Portworx on any environment, ensure that you're using a supported environment version:

If your Kubernetes distribution supports multiple Linux distributions and kernel versions, refer to the Supported kernels page to ensure that your kernel version is supported.

Portworx Enterprise version:

3.7.1▼

Portworx Operator version: 26.4.0 or later

Showing 22 supported Kubernetes distributions for Portworx Enterprise 3.7.1

Kubernetes distributionSupported versions

Vanilla Kubernetes

- 1.32 (starting from 1.32.2)

- 1.33

- 1.34

- 1.35

- 1.36

Google Kubernetes Engine (GKE)

- 1.34.11

- 1.35.8

- 1.36.4

Azure Kubernetes Service (AKS)

- 1.34.11

- 1.35.8

- 1.36.4

Amazon Elastic Kubernetes Service (EKS)

- 1.34.11

- 1.35.8

- 1.36.4

IBM Cloud Kubernetes Service (IKS)

- 1.34.10

- 1.35.7

- 1.36.3

OCI Kubernetes Engine (OKE)

- 1.34.2

- 1.35.2

- 1.36.1

KOPS

- 1.34.1

- 1.35.2

- 1.36.0

SUSE Rancher Kubernetes Engine (RKE2)

- 1.32.13

- 1.33.13

- 1.34.11

- 1.35.8

- 1.36.4

Note: Portworx supports SUSE Rancher versions 2.11.x, 2.12.x, 2.13.x, 2.14.x, 2.15.x

Mirantis

- 1.31.7 ( MKE: 3.8.7, MCR: 23.0.17)

- 1.31.13 ( MKE: 3.8.10, MCR: 25.0.14)

- 1.34.9 ( MKE: 3.9.5, MCR: 25.0.14)

Charmed Kubernetes

- Juju version: 3.6.8
Kubernetes version: 1.33.5

- Juju version: 3.6.8
Kubernetes version: 1.34.5

- Juju version: 3.6.8
Kubernetes version: 1.35.9

SUSE Virtualization (Harvester)

- 1.6.0

- 1.6.1

- 1.7.1

- 1.8.1

Red Hat OpenShift

- OpenShift version: 4.18 (verified up to 4.18.56)
 Kubernetes version: 1.31

- OpenShift version: 4.19 (verified up to 4.19.51)
 Kubernetes version: 1.32.13

- OpenShift version: 4.20 (verified up to 4.20.42)
 Kubernetes version: 1.33.13

- OpenShift version: 4.21 (verified up to 4.21.37)
 Kubernetes version: 1.34.9

- OpenShift version: 4.22 (verified up to 4.22.18)
 Kubernetes version: 1.35.8

Note: Supports both bare metal and VM

Red Hat OpenShift on IBM Cloud

- ROKS version: 4.18 (verified up to 4.18.54)
 Kubernetes version: 1.31

- ROKS version: 4.19 (verified up to 4.19.45)
 Kubernetes version: 1.32

- ROKS version: 4.20 (verified up to 4.20.36)
 Kubernetes version: 1.33

- ROKS version: 4.21 (verified up to 4.21.31)
 Kubernetes version: 1.34

- ROKS version: 4.22 (verified up to 4.22.13)
 Kubernetes version: 1.35

Red Hat OpenShift Service on AWS

- ROSA version: 4.19 (verified up to 4.19.45)
 Kubernetes version: 1.32

- ROSA version: 4.20 (verified up to 4.20.38)
 Kubernetes version: 1.33

- ROSA version: 4.21 (verified up to 4.21.32)
 Kubernetes version: 1.34

- ROSA version: 4.22 (verified up to 4.22.13)
 Kubernetes version: 1.35

Azure Red Hat OpenShift

- ARO version: 4.18 (verified up to 4.18.35)
 Kubernetes version: 1.31

- ARO version: 4.19 (verified up to 4.19.45)
 Kubernetes version: 1.32

- ARO version: 4.20 (verified up to 4.20.38)
 Kubernetes version: 1.33

- ARO version: 4.21 (verified up to 4.21.33)
 Kubernetes version: 1.34

VMware vSphere Kubernetes Service (VKS)

- v1.32.10---vmware.1-fips-vkr.2, VKS 3.3.0

- v1.33.6---vmware.1-fips-vkr.2, VKS 3.4.0

- v1.34.2---vmware.2-vkr.2, VKS 3.5.0

- v1.35.2---vmware.1-vkr.3, VKS 3.6.2

- v1.36.1---vmware.4-vkr.5, VKS 3.7.0

VMware Tanzu Kubernetes Grid Integrated Edition (TKGI)

- TKGI version: 1.22.1-build.4
Kubernetes version: 1.31.5

- TKGI version: 1.24.0-build.1
Kubernetes version: 1.33.7

- TKGI version: 1.25.0-build.1
Kubernetes version: 1.34.7

Google Anthos on Bare Metal

- Anthos version: 1.32.900-gke.60
Kubernetes version: v1.32.11-gke.200

- Anthos version: 1.33.500-gke.63
Kubernetes version: v1.33.5-gke.2200

- Anthos version: 1.34.900-gke.135
Kubernetes version: v1.34.7-gke.200

- Anthos version: 1.35.500-gke.142
Kubernetes version: v1.35.8-gke.100

- Anthos version: 1.36.0-gke.532
Kubernetes version: v1.36.0-gke.2800

Google Anthos on VMware

- Anthos version: 1.32.900-gke.60
 vSphere version: 7.0.3 & 8.0.3
 Kubernetes version: v1.32.11-gke.200

- Anthos version: 1.33.500-gke.63
 vSphere version: 7.0.3 & 8.0.3
 Kubernetes version: v1.33.5-gke.2200

- Anthos version: 1.34.900-gke.135
 vSphere version: 7.0.3 & 8.0.3
 Kubernetes version: v1.34.7-gke.200

- Anthos version: 1.35.500-gke.142
 vSphere version: 7.0.3 & 8.0.3
 Kubernetes version: v1.35.8-gke.100

- Anthos version: 1.36.0-gke.532
 vSphere version: 7.0.3 & 8.0.3
 Kubernetes version: v1.36.0-gke.2800

Gardener on Azure

- 1.33.5

- 1.34.6

- 1.35.3

Gardener on Google Cloud Platform

- 1.33.9

- 1.34.5

- 1.35.2

Gardener on AWS

- 1.33.10

- 1.34.6

- 1.35.3
