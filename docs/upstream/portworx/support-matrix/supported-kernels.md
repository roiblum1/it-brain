# Supported Kernels

Source: https://docs.portworx.com/portworx-enterprise/support-matrix/supported-kernels (Portworx Enterprise latest)

Supported Kernels | Portworx Enterprise Documentation

Portworx runs as a Docker or OCI container, available on DockerHub. Portworx has a dependency on the kernel module, which must be installed on hosts. Portworx is distributed with pre-built kernel modules for select CentOS and Ubuntu Linux distributions. If your kernel version is not listed in the table below, Portworx will attempt to download a pre-compiled kernel module from mirrors.portworx.com (if available) if it is not packaged with the Portworx container. This process may fail if the host is behind a proxy. If you already have the kernel-headers and kernel-devel packages installed, Portworx will attempt to compile its kernel modules. However, this can fail for kernel versions higher than 5.4. If you don't have these packages, you must install them before restarting Portworx.

Portworx by Everpure recommends that you only upgrade to a kernel version listed on this support page. Do not upgrade to a more recent kernel version that is not listed.

important

Starting from release 3.1.0, Portworx Enterprise will exclusively support kernel versions 4.18 and above.

### End of Support Notification​

- Portworx Enterprise 3.5.0 is the last release that will support Fedora (all versions).

- Starting with Portworx Enterprise 3.5.0, Photon3 is no longer supported, as the distribution has reached end of life (EOL).

- Starting with Portworx Enterprise 3.4.0, support for CentOS 7 and CentOS 8 has ended, as both distributions have reached their end of life (EOL).

## Install kernel headers​

To install the kernel headers and kernel development packages for kernels not listed in the table below, follow the steps for your distribution.

#### CentOS​

```

yum install kernel-headers-`uname -r`

yum install kernel-devel-`uname -r`

```

#### Ubuntu​

```

apt install linux-headers-$(uname -r)

```

warning

A Kernel performance issue on Ubuntu 20.04 with Kernel version 5.15 is causing a drop in the sequential write operations. Avoid using this Ubuntu and Kernel version until the issue is fixed. See the bug description for more information.

## Qualified Distros and Kernel versions​

Portworx Enterprise supports the following Kubernetes distributions and kernels.

note

Portworx by Everpure will accept support requests from customers running in RHEL environments supported by SUSE, via SUSE Multi-Linux Support (MLS).

### 3.7.1.1​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 13Up to 6.12.101+deb13-amd64

Debian 12Up to 6.12.101+deb12-amd64

Debian 11Up to 6.1.0-0.deb11.52-amd64

OEL 8 Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 9.4 Oracle Enterprise Linux (UEK Kernels)Up to 6.12.0-205.92.4.2.el9uek

Photon 5.0Up to 6.12.103-9.ph5

Photon 4.0Up to 5.10.260-2.ph4

RHEL 9.8Up to 5.14.0-687.66.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.154.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.161.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.202.1.el9_2

RHEL 8.10Up to 4.18.0-553.184.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.193.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.157.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.73.2

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.182.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.235.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.37.1

SUSE Linux Micro 6.1Up to 6.4.0-50.1

SUSE Linux Micro 6.0Up to 6.4.0-50.1

Ubuntu 24.04Up to 6.8.0-147-generic, Up to 6.14.0-37-generic, Up to 6.17.0-42-generic, Up to 7.0.0-38-generic

Ubuntu 22.04Up to 5.15.0-194-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar StableUp to 6.12.113-flatcar

Linux DistroKernel Version

CentOS Stream 10Up to 6.12.0-260.el10

CentOS Stream 9Up to 5.14.0-741.el9

Debian 13Up to 6.12.101+deb13-amd64

Debian 12Up to 6.12.101+deb12-amd64

Debian 11Up to 6.1.0-0.deb11.52-amd64

RHEL 10.2Up to 6.12.0-211.74.1.el10_2

RHEL 10.1Up to 6.12.0-124.56.1.el10_1

RHEL 10.0Up to 6.12.0-55.117.1.el10_0

RHEL 9.8Up to 5.14.0-687.66.1.el9_8

RHEL 10.0Up to 6.12.0-55.109.1.el10_0

RHEL 9.8Up to 5.14.0-687.53.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.154.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.161.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.202.1.el9_2

RHEL 8.10Up to 4.18.0-553.184.1.el8_10

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.73.2

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.182.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.235.1

SLES (SUSE Enterprise Linux) SLES16 SP0Up to 6.12.0-160000.38.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.37.1

SUSE Linux Micro 6.1Up to 6.4.0-50.1

SUSE Linux Micro 6.0Up to 6.4.0-50.1

Ubuntu 24.04Up to 6.8.0-147-generic, Up to 6.14.0-37-generic, Up to 6.17.0-42-generic, Up to 7.0.0-38-generic

Ubuntu 22.04Up to 5.15.0-194-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar Stable6.12.113-flatcar

Gardener on AzureUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

Gardener on GCPUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

Gardener on AWSUp to 6.12.74-cloud-amd64 (OS Image: Garden Linux 1877.14), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-190-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-42-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.211.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.158.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.189.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.147.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.136.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.45.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.58.1.el9_8

RHEL 10.0 with Multipath v0.9.9Up to 6.12.0-55.99.1.el10_0

RHEL 10.1 with Multipath v0.9.9Up to 6.12.0-124.56.1.el10_1

RHEL 10.2 with Multipath v0.9.9Up to 6.12.0-211.50.1.el10_2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-190-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-42-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.211.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.158.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.189.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.147.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.136.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.45.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.58.1.el9_8

RHEL 10.0 with Multipath v0.9.9Up to 6.12.0-55.99.1.el10_0

RHEL 10.1 with Multipath v0.9.9Up to 6.12.0-124.56.1.el10_1

RHEL 10.2 with Multipath v0.9.9Up to 6.12.0-211.50.1.el10_2

### 3.7.1​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 13Up to 6.12.101+deb13-amd64

Debian 12Up to 6.12.101+deb12-amd64

Debian 11Up to 6.1.0-0.deb11.52-amd64

OEL 8 Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 9.4 Oracle Enterprise Linux (UEK Kernels)Up to 6.12.0-205.92.4.2.el9uek

Photon 5.0Up to 6.12.103-9.ph5

Photon 4.0Up to 5.10.260-2.ph4

RHEL 9.8Up to 5.14.0-687.61.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.152.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.158.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.199.1.el9_2

RHEL 8.10Up to 4.18.0-553.179.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.193.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.157.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.73.2

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.182.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.235.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.37.1

SUSE Linux Micro 6.1Up to 6.4.0-50.1

SUSE Linux Micro 6.0Up to 6.4.0-50.1

Ubuntu 24.04Up to 6.8.0-147-generic, Up to 6.14.0-37-generic, Up to 6.17.0-42-generic, Up to 7.0.0-42-generic

Ubuntu 22.04Up to 5.15.0-202-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar StableUp to 6.12.102-flatcar

Linux DistroKernel Version

CentOS Stream 10Up to 6.12.0-260.el10

CentOS Stream 9Up to 5.14.0-741.el9

Debian 13Up to 6.12.101+deb13-amd64

Debian 12Up to 6.12.101+deb12-amd64

Debian 11Up to 6.1.0-0.deb11.52-amd64

RHEL 10.2Up to 6.12.0-211.69.1.el10_2

RHEL 10.1Up to 6.12.0-124.56.1.el10_1

RHEL 10.0Up to 6.12.0-55.113.1.el10_0

RHEL 9.8Up to 5.14.0-687.61.1.el9_8

RHEL 10.0Up to 6.12.0-55.109.1.el10_0

RHEL 9.8Up to 5.14.0-687.53.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.152.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.158.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.199.1.el9_2

RHEL 8.10Up to 4.18.0-553.179.1.el8_10

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.73.2

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.182.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.235.1

SLES (SUSE Enterprise Linux) SLES16 SP0Up to 6.12.0-160000.38.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.37.1

SUSE Linux Micro 6.1Up to 6.4.0-50.1

SUSE Linux Micro 6.0Up to 6.4.0-50.1

Ubuntu 24.04Up to 6.8.0-147-generic, Up to 6.14.0-37-generic, Up to 6.17.0-42-generic, Up to 7.0.0-42-generic

Ubuntu 22.04Up to 5.15.0-202-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar Stable6.12.102-flatcar

Gardener on AzureUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

Gardener on GCPUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

Gardener on AWSUp to 6.12.74-cloud-amd64 (OS Image: Garden Linux 1877.14), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-190-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-42-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.211.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.158.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.189.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.147.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.136.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.45.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.58.1.el9_8

RHEL 10.0 with Multipath v0.9.9Up to 6.12.0-55.99.1.el10_0

RHEL 10.1 with Multipath v0.9.9Up to 6.12.0-124.56.1.el10_1

RHEL 10.2 with Multipath v0.9.9Up to 6.12.0-211.50.1.el10_2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-190-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-42-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.211.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.158.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.189.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.147.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.136.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.45.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.58.1.el9_8

RHEL 10.0 with Multipath v0.9.9Up to 6.12.0-55.99.1.el10_0

RHEL 10.1 with Multipath v0.9.9Up to 6.12.0-124.56.1.el10_1

RHEL 10.2 with Multipath v0.9.9Up to 6.12.0-211.50.1.el10_2

### 3.7.0​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 13Up to 6.12.101+deb13-amd64

Debian 12Up to 6.12.101+deb12-amd64

Debian 11Up to 6.1.0-0.deb11.52-amd64

OEL 8 Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 5.15.0-323.211.3.4.el8uek

OEL 9.4 Oracle Enterprise Linux (UEK Kernels)Up to 6.12.0-205.92.4.2.el9uek

Photon 5.0Up to 6.12.103-9.ph5

Photon 4.0Up to 5.10.260-2.ph4

RHEL 9.8Up to 5.14.0-687.54.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.146.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.153.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.194.1.el9_2

RHEL 8.10Up to 4.18.0-553.170.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.193.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.157.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.73.2

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.182.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.235.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.37.1

SUSE Linux Micro 6.1Up to 6.4.0-50.1

SUSE Linux Micro 6.0Up to 6.4.0-50.1

Ubuntu 24.04Up to 6.8.0-142-generic, Up to 6.11.0-29-generic, Up to 6.14.0-37-generic, Up to 6.17.0-42-generic, Up to 7.0.0-34-generic

Ubuntu 22.04Up to 5.15.0-198-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar StableUp to 6.12.102-flatcar

Linux DistroKernel Version

CentOS Stream 10Up to 6.12.0-260.el10

CentOS Stream 9Up to 5.14.0-741.el9

Debian 13Up to 6.12.101+deb13-amd64

Debian 12Up to 6.12.101+deb12-amd64

Debian 11Up to 6.1.0-0.deb11.52-amd64

RHEL 10.2Up to 6.12.0-211.62.1.el10_2

RHEL 10.1Up to 6.12.0-124.56.1.el10_1

RHEL 10.0Up to 6.12.0-55.108.1.el10_0

RHEL 9.8Up to 5.14.0-687.54.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.146.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.153.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.194.1.el9_2

RHEL 8.10Up to 4.18.0-553.170.1.el8_10

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.73.2

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.182.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.235.1

SLES (SUSE Enterprise Linux) SLES16 SP0Up to 6.12.0-160000.38.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.37.1

SUSE Linux Micro 6.1Up to 6.4.0-50.1

SUSE Linux Micro 6.0Up to 6.4.0-50.1

Ubuntu 24.04Up to 6.8.0-142-generic, Up to 6.11.0-29-generic, Up to 6.14.0-37-generic, Up to 6.17.0-42-generic, Up to 7.0.0-34-generic

Ubuntu 22.04Up to 5.15.0-198-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar Stable6.12.102-flatcar

Gardener on AzureUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

Gardener on GCPUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

Gardener on AWSUp to 6.12.74-cloud-amd64 (OS Image: Garden Linux 1877.14), Up to 6.18.35-cloud-amd64 (OS Image: Garden Linux 2150.5.0)

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-190-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-42-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.211.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.158.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.189.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.147.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.136.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.45.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.17.1.el9_8

RHEL 10.0 with Multipath v0.9.9Up to 6.12.0-55.99.1.el10_0

RHEL 10.1 with Multipath v0.9.9Up to 6.12.0-124.56.1.el10_1

RHEL 10.2 with Multipath v0.9.9Up to 6.12.0-211.50.1.el10_2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-190-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-138-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-42-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.211.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.158.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.189.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.147.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.136.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.45.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.17.1.el9_8

RHEL 10.0 with Multipath v0.9.9Up to 6.12.0-55.99.1.el10_0

RHEL 10.1 with Multipath v0.9.9Up to 6.12.0-124.56.1.el10_1

RHEL 10.2 with Multipath v0.9.9Up to 6.12.0-211.50.1.el10_2

### 3.6.2​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-49-amd64

Debian 11Up to 6.1.0-0.deb11.49-amd64

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-318.199.3.2.el8uek

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

Photon 5.0Up to 6.1.159-9.ph5

Photon 4.0Up to 5.10.255-1.ph4

RHEL 9.8Up to 5.14.0-687.65.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.154.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.161.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.202.1.el9_2

RHEL 8.10Up to 4.18.0-553.184.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.13.1.el8_7

RHEL 8.6Up to 4.18.0-372.192.1.el8_6

Rocky 9.5Up to 5.14.0-503.40.1.el9_5

Rocky 9.4Up to 5.14.0-427.134.1.el9_4

Rocky 8.10Up to 4.18.0-553.134.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.60.1

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.169.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.214.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.35.1

SUSE Linux Micro 6.1Up to 6.4.0-48.1

SUSE Linux Micro 6.0Up to 6.4.0-48.1

Ubuntu 24.04Up to 6.8.0-147-generic, Up to 6.11.0-29-generic, Up to 6.14.0-37-generic, Up to 6.17.0-42-generic, Up to 7.0.0-42-generic

Ubuntu 22.04Up to 5.15.0-202-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar StableUp to 6.12.93-flatcar

Gardener on AzureUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9)

Gardener on GCPUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9)

Gardener on AWSUp to 6.12.74-cloud-amd64 (OS Image: Garden Linux 1877.14)

Linux DistroKernel Version

CentOS Stream 10Up to 6.12.0-233.el10

CentOS Stream 9Up to 5.14.0-710.el9

Debian 12Up to 6.1.0-49-amd64

Debian 11Up to 6.1.0-0.deb11.49-amd64

RHEL 10.2Up to 6.12.0-211.74.1.el10_2

RHEL 10.1Up to 6.12.0-124.56.1.el10_1

RHEL 10.0Up to 6.12.0-55.117.1.el10_0

RHEL 9.8Up to 5.14.0-687.65.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.154.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.161.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.202.1.el9_2

RHEL 8.10Up to 4.18.0-553.184.1.el8_10

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.60.1

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.169.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.214.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.35.1

SUSE Linux Micro 6.1Up to 6.4.0-48.1

SUSE Linux Micro 6.0Up to 6.4.0-48.1

Ubuntu 24.04Up to 6.8.0-147-generic, Up to 6.11.0-29-generic, Up to 6.14.0-37-generic, Up to 6.17.0-42-generic, Up to 7.0.0-42-generic

Ubuntu 22.04Up to 5.15.0-202-generic, Up to 6.8.0-138-generic, Up to 6.8.0-124-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar StableUp to 6.12.93-flatcar

Gardener on AzureUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9)

Gardener on GCPUp to 6.12.60-cloud-amd64 (OS Image: Garden Linux 1877.9)

Gardener on AWSUp to 6.12.74-cloud-amd64 (OS Image: Garden Linux 1877.14)

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-179-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-106-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-35-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-19-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.188.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.137.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.177.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.134.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.123.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.17.1.el9_8

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-179-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-106-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-35-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-19-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.188.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.137.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.177.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.134.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.123.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.17.1.el9_8

### 3.6.1​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-48-amd64

Debian 11Up to 6.1.0-0.deb11.48

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-318.199.3.2.el8uek

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

Photon 5.0Up to 6.1.159-9.ph5

Photon 4.0Up to 5.10.255-1.ph4

Photon 3.0Up to 4.19.325-1.ph3

RHEL 9.8Up to 5.14.0-687.33.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.131.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.141.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.184.1.el9_2

RHEL 8.10Up to 4.18.0-553.150.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.192.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.124.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.45.1

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.163.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.214.1

SUSE Linux Micro 6.2Up to 6.12.0-160000.35.1

SUSE Linux Micro 6.1Up to 6.4.0-150600.21.3

SUSE Linux Micro 6Up to 6.4.0-36.1

Ubuntu 24.04Up to 6.8.0-136-generic, Up to 6.11.0-29-generic, Up to 6.14.0-37-generic, Up to 6.17.0-41-generic

Ubuntu 22.04Up to 5.15.0-186-generic, Up to 6.8.0-136-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

AKS Ubuntu 22.04Up to 5.15.0-1110-azure

AKS Ubuntu 24.04Up to 6.8.0-1052-azure

GKE Ubuntu 24.04Up to 6.8.0-1051-gke

Flatcar StableUp to 6.12.74-flatcar

Linux DistroKernel Version

CentOS Stream 10Up to 6.12.0-213.el10

CentOS Stream 9Up to 5.14.0-687.el9

Debian 12Up to 6.1.0-48-amd64

Debian 11Up to 6.1.0-0.deb11.48-amd64

RHEL 10.2Up to 6.12.0-211.42.1.el10_2

RHEL 10.1Up to 6.12.0-124.56.1.el10_1

RHEL 10.0Up to 6.12.0-55.94.1.el10_0

RHEL 9.8Up to 5.14.0-687.33.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.131.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.141.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.184.1.el9_2

RHEL 8.10Up to 4.18.0-553.150.1.el8_10

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.45.1

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.163.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.214.1

SUSE Linux Micro 6.1Up to 6.4.0-150600.21.3

SUSE Linux Micro 6Up to 6.4.0-36.1

Ubuntu 24.04Up to 6.8.0-136-generic, Up to 6.11.0-29-generic, Up to 6.14.0-37-generic, Up to 6.17.0-41-generic

Ubuntu 22.04Up to 5.15.0-186-generic, Up to 6.8.0-136-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

AKS Ubuntu 22.04Up to 5.15.0-1110-azure

AKS Ubuntu 24.04Up to 6.8.0-1052-azure

GKE Ubuntu 24.04Up to 6.8.0-1051-gke

Flatcar StableUp to 6.12.74-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-179-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-106-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-35-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-19-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.188.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.137.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.177.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.134.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.123.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.17.1.el9_8

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-179-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-106-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-35-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-19-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.188.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.137.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.177.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.134.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.123.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.17.1.el9_8

### 3.6.0​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-45-amd64

Debian 11Up to 5.10.0-39-amd64

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-318.199.3.2.el8uek

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

Photon 5.0Up to 6.1.159-9.ph5

Photon 4.0Up to 5.10.252-2.ph4

Photon 3.0Up to 4.19.325-1.ph3

RHEL 9.8Up to 5.14.0-687.5.3.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.116.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.130.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.172.1.el9_2

RHEL 8.10Up to 4.18.0-553.132.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.193.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.105.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.28.1

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.136.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.194.1

SUSE Linux Micro 6.1Up to 6.4.0-150600.21.3

SUSE Linux Micro 6Up to 6.4.0-36.1

Ubuntu 24.04Up to 6.8.0-117-generic, Up to 6.11.0-29-generic, Up to 6.14.0-37-generic

Ubuntu 22.04Up to 5.15.0-181-generic, Up to 6.8.0-117-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar StableUp to 6.12.74-flatcar

Linux DistroKernel Version

CentOS Stream 10Up to 6.12.0-213.el10

CentOS Stream 9Up to 5.14.0-687.el9

Debian 12Up to 6.1.0-45-amd64

Debian 11Up to 5.10.0-39-amd64

RHEL 10.0Up to 6.12.0-55.77.1.el10_0

RHEL 9.8Up to 5.14.0-687.5.3.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.116.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.130.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.170.1.el9_2

RHEL 8.10Up to 4.18.0-553.132.1.el8_10

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP7Up to 6.4.0-150700.53.31.1

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.81.3

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.136.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.194.1

SUSE Linux Micro 6.1Up to 6.4.0-150600.21.3

SUSE Linux Micro 6Up to 6.4.0-36.1

Ubuntu 24.04Up to 6.8.0-117-generic, Up to 6.11.0-29-generic, Up to 6.14.0-33-generic

Ubuntu 22.04Up to 5.15.0-181-generic, Up to 6.8.0-117-generic

Ubuntu 20.04Up to 5.4.0-216-generic, Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.68-92.122.amzn2023.x86_64

Flatcar StableUp to 6.12.74-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-181-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-106-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-35-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-19-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.193.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.132.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.172.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.130.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.116.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.5.3.el9_8

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-181-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-106-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-35-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.17.0-19-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.193.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 8.10 with Multipath v0.8.4Up to 4.18.0-553.132.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.172.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.130.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.116.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.5.3.el9_8

### 3.5.2​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-41-amd64

Debian 11Up to 5.10.0-37-amd64

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-315.196.5.1.el8uek

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

Photon 4.0Up to 5.10.246-6.ph4

Photon 3.0Up to 4.19.325-1.ph3

RHEL 9.8Up to 5.14.0-687.54.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.154.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.161.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.199.1.el9_2

RHEL 8.10Up to 4.18.0-553.184.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.193.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.89.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.73.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.130.3

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.184.1

SUSE Linux Micro 6.1Up to 6.4.0-36-default

SUSE Linux Micro 6Up to 6.4.0-36-default

Ubuntu 24.04Up to 6.8.0-146-generic, Up to 6.11.0-29-generic, Up to 6.14.0-33-generic

Ubuntu 22.04Up to 5.15.0-198-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.53-69.119.amzn2023.x86_64

Flatcar StableUp to 6.12.58-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-41-amd64

Debian 11Up to 5.10.0-37-amd64

RHEL 10.2Up to 6.12.0-211.74.1.el10_2

RHEL 10.1Up to 6.12.0-124.56.1.el10_1

RHEL 10.0Up to 6.12.0-55.117.1.el10_0

RHEL 9.8Up to 5.14.0-687.54.1.el9_8

RHEL 9.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.6Up to 5.14.0-570.154.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.161.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.199.1.el9_2

RHEL 8.10Up to 4.18.0-553.184.1.el8_10

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.73.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.127.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.184.1

SUSE Linux Micro 6.1Up to 6.4.0-36-default

SUSE Linux Micro 6Up to 6.4.0-36-default

Ubuntu 24.04Up to 6.8.0-146-generic, Up to 6.11.0-29-generic, Up to 6.14.0-33-generic

Ubuntu 22.04Up to 5.15.0-198-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.55-74.119.amzn2023.x86_64

Flatcar StableUp to 6.12.58-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-90-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-101-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-29-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-33-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.193.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-553.92.1.el8_10

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.177.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.125.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.122.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.15.1.el9_8

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-90-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-101-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-29-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-33-generic

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.177.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.125.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.122.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.55.1.el9_7

RHEL 9.8 with Multipath v0.8.7Up to 5.14.0-687.15.1.el9_8

### 3.5.1​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-41-amd64

Debian 11Up to 5.10.0-37-amd64

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-315.196.5.1.el8uek

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

Photon 4.0Up to 5.10.246-6.ph4

Photon 3.0Up to 4.19.325-1.ph3

RHEL 9.7Up to 5.14.0-611.16.1.el9_7

RHEL 9.6Up to 5.14.0-570.73.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.103.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.122.1.el9_2

RHEL 8.10Up to 4.18.0-553.109.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.173.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.89.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.73.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.127.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.184.1

SUSE Linux Micro 6.1Up to 6.4.0-36-default

SUSE Linux Micro 6Up to 6.4.0-36-default

Ubuntu 24.04Up to 6.8.0-90-generic, Up to 6.11.0-29-generic, Up to 6.14.0-33-generic

Ubuntu 22.04Up to 5.15.0-143-generic, Up to 6.8.0-90-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.53-69.119.amzn2023.x86_64

Flatcar StableUp to 6.12.58-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-41-amd64

Debian 11Up to 5.10.0-37-amd64

RHEL 10.0Up to 6.12.0-55.34.1.el10_0

RHEL 9.7Up to 5.14.0-611.16.1.el9_7

RHEL 9.6Up to 5.14.0-570.73.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.103.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.122.1.el9_2

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.73.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.127.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.184.1

SUSE Linux Micro 6.1Up to 6.4.0-36-default

SUSE Linux Micro 6Up to 6.4.0-36-default

Ubuntu 24.04Up to 6.8.0-90-generic, Up to 6.11.0-29-generic, Up to 6.14.0-33-generic

Ubuntu 22.04Up to 5.15.0-143-generic, Up to 6.8.0-90-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.55-74.119.amzn2023.x86_64

Flatcar StableUp to 6.12.58-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-90-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-29-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-33-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.168.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.148.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.102.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.64.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.16.1.el9_7

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-90-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-29-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-33-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.166.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.148.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.102.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.64.1.el9_6

RHEL 9.7 with Multipath v0.8.7Up to 5.14.0-611.16.1.el9_7

### 3.5.0​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-41-amd64

Debian 11Up to 5.10.0-36-amd64

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-313.189.5.3.el8uek

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

Photon 4.0Up to 5.10.246-6.ph4

Photon 3.0Up to 4.19.325-1.ph3

RHEL 9.6Up to 5.14.0-570.66.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.104.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.148.1.el9_2

RHEL 8.10Up to 4.18.0-553.89.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.168.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.81.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.73.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.124.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.179.1

SUSE Linux Micro 6.1Up to 6.4.0-35-default

SUSE Linux Micro 6Up to 6.4.0-35-default

Ubuntu 24.04Up to 6.8.0-90-generic, Up to 6.11.0-29-generic, Up to 6.14.0-35-generic

Ubuntu 22.04Up to 5.15.0-143-generic, Up to 6.8.0-88-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.53-69.119.amzn2023.x86_64

Flatcar StableUp to 6.6.110-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-41-amd64

Debian 11Up to 5.10.0-36-amd64

RHEL 10.0Up to 6.12.0-55.34.1.el10_0

RHEL 9.6Up to 5.14.0-570.66.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.104.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.148.1.el9_2

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.73.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.124.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.179.1

SUSE Linux Micro 6.1Up to 6.4.0-35-default

SUSE Linux Micro 6Up to 6.4.0-35-default

Ubuntu 24.04Up to 6.8.0-90-generic, Up to 6.11.0-29-generic, Up to 6.14.0-35-generic

Ubuntu 22.04Up to 5.15.0-143-generic, Up to 6.8.0-88-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.976.amzn2.x86_64

Amazon Linux 2023Up to 6.12.55-74.119.amzn2023.x86_64

Flatcar StableUp to 6.6.110-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-88-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-90-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-29-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-33-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.168.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.148.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.104.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.64.1.el9_6

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-88-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-90-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-29-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-33-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.166.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.148.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.104.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.64.1.el9_6

### 3.4.2​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-41-amd64

Debian 11Up to 5.10.0-36-amd64

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-311.185.9.el8uek

Photon 4.0Up to 5.10.246-5.ph4

Photon 3.0Up to 4.19.324-1.ph3

Photon 5.0Up to 6.1.148-1.ph5

RHEL 9.6Up to 5.14.0-570.138.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.148.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.189.1.el9_2

RHEL 8.10Up to 4.18.0-553.159.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.193.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.81.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.73.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.124.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.179.1

SUSE Linux Micro 6.1Up to 6.4.0-35-default

SUSE Linux Micro 6Up to 6.4.0-35-default

Ubuntu 24.04Up to 6.8.0-117-generic, Up to 6.11.0-29-generic, Up to 6.14.0-33-generic, Up to 6.17.0-42-generic

Ubuntu 22.04Up to 5.15.0-187-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.978.amzn2.x86_64

Amazon Linux 2023Up to 6.12.55-74.119.amzn2023.x86_64

Flatcar StableUp to 6.6.110-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-41-amd64

Debian 11Up to 5.10.0-36-amd64

RHEL 9.6Up to 5.14.0-570.138.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.148.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.189.1.el9_2

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

RHEL 8.10Up to 4.18.0-553.159.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.73.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.124.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.179.1

SUSE Linux Micro 6.1Up to 6.4.0-35-default

SUSE Linux Micro 6Up to 6.4.0-35-default

Ubuntu 24.04Up to 6.8.0-117-generic, Up to 6.11.0-29-generic, Up to 6.14.0-33-generic, Up to 6.17.0-42-generic

Ubuntu 22.04Up to 5.15.0-187-generic, Up to 6.8.0-138-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.245-241.978.amzn2.x86_64

Amazon Linux 2023Up to 6.12.55-74.119.amzn2023.x86_64

Flatcar StableUp to 6.6.110-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-88-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-101-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-29-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-33-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.193.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.177.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.129.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.114.1.el9_6

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-88-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-101-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-29-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.14.0-33-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.193.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.24.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.177.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.129.1.el9_4

RHEL 9.5 with Multipath v0.8.7Up to 5.14.0-503.14.1.el9_5

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.114.1.el9_6

### 3.4.1​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-39-amd64

Debian 11Up to 5.10.0-35-amd64

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-311.185.9.el8uek

Photon 4.0Up to 5.10.244-2.ph4

Photon 3.0Up to 4.19.324-1.ph3

RHEL 9.6Up to 5.14.0-570.62.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.97.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.124.1.el9_2

RHEL 8.10Up to 4.18.0-553.83.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.168.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.76.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.70.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.116.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.176.1

SUSE Linux Micro 6.1Up to 6.4.0-34-default

SUSE Linux Micro 6Up to 6.4.0-34-default

Ubuntu 24.04Up to 6.8.0-85-generic, Up to 6.14.0-33-generic

Ubuntu 22.04Up to 5.15.0-143-generic, Up to 6.8.0-85-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.242-239.961.amzn2

Amazon Linux 2023Up to 6.12.40-64.114.amzn2023

Flatcar StableUp to 6.6.106-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-39-amd64

Debian 11Up to 5.10.0-35-amd64

RHEL 9.6Up to 5.14.0-570.62.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.97.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.124.1.el9_2

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.70.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.116.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.176.1

SUSE Linux Micro 6.1Up to 6.4.0-34-default

SUSE Linux Micro 6Up to 6.4.0-34-default

Ubuntu 24.04Up to 6.14.0-33-generic

Ubuntu 22.04Up to 6.8.0-85-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.242-239.961.amzn2

Amazon Linux 2023Up to 6.12.40-64.114.amzn2023

Flatcar StableUp to 6.6.106-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-60

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-24

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.46.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.118.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.97.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.62.1.el9_6

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-60

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-24

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.46.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.118.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.97.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.62.1.el9_6

### 3.4.0​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-38-amd64

Debian 11Up to 5.10.0-35-amd64

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-311.185.9.el8uek

Photon 4.0Up to 5.10.240-2.ph4

Photon 3.0Up to 4.19.324-1.ph3

RHEL 9.6Up to 5.14.0-570.51.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.91.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.124.1.el9_2

RHEL 8.10Up to 4.18.0-553.79.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.104.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.162.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.69.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.60.5

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.116.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.173.1

SUSE Linux Micro 6.1Up to 6.4.0-31-1

SUSE Linux Micro 6Up to 6.4.0-31-1

Ubuntu 24.04Up to 6.11.0-29-generic, Up to 6.8.0-85-generic, Up to 6.14.0-28-generic

Ubuntu 22.04Up to 5.15.0-141-generic, Up to 6.8.0-85-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.240-238.959.amzn2

Amazon Linux 2023Up to 6.12.40-63.114.amzn2023

Flatcar StableUp to 6.6.100-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-38-amd64

Debian 11Up to 5.10.0-35-amd64

RHEL 8.10Up to 4.18.0-553.79.1.el8_10

RHEL 9.6Up to 5.14.0-570.51.1.el9_6

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.91.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.124.1.el9_2

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.60.5

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.116.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.173.1

SUSE Linux Micro 6.1Up to 6.4.0-31-1

SUSE Linux Micro 6Up to 6.4.0-31-1

Ubuntu 24.04Up to 6.11.0-29-generic, Up to 6.8.0-79-generic, Up to 6.14.0-28-generic

Ubuntu 22.04Up to 5.15.0-141-generic, Up to 6.8.0-85-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.240-238.959.amzn2

Amazon Linux 2023Up to 6.12.40-63.114.amzn2023

Flatcar StableUp to 6.6.100-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-60

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-24

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.46.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.118.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.81.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.32.1.el9_6

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-60

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-24

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.46.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.118.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.81.1.el9_4

RHEL 9.6 with Multipath v0.8.7Up to 5.14.0-570.32.1.el9_6

### 3.3.1​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-37-amd64

Debian 11Up to 5.10.0-35-amd64

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-309.180.4.el8uek

Photon 4.0Up to 5.10.238-2.ph4

Photon 3.0Up to 4.19.324-1.ph3

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.116.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.148.1.el9_2

RHEL 8.10Up to 4.18.0-553.117.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.97.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.183.1.el8_6

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.54.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.53.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.110.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.164.1

SUSE Linux Micro 6.1Up to 6.4.0-28-default

SUSE Linux Micro 6Up to 6.4.0-28-default

SUSE Linux Micro 5.5Up to 5.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-107-generic Up to 6.11.0-29-generic

Ubuntu 22.04Up to 6.8.0-107-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.236-228.935.amzn2

Amazon Linux 2023Up to 6.1.134-152.225.amzn2023

Flatcar StableUp to 6.6.94-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-37-amd64

Debian 11Up to 5.10.0-35-amd64

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.116.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.148.1.el9_2

RHEL 8.10Up to 4.18.0-553.117.1.el8_10

Rocky 9.5Up to 5.14.0-503.14.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.53.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.110.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.164.1

SUSE Linux Micro 6.1Up to 6.4.0-28-default

SUSE Linux Micro 6Up to 6.4.0-28-default

SUSE Linux Micro 5.5Up to 5.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-107-generic, Up to 6.11.0-28-generic

Ubuntu 22.04Up to 6.8.0-107-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.235-227.919.amzn2

Amazon Linux 2023Up to 6.1.132-147.221.amzn2023

Flatcar StableUp to 6.6.94-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-60

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-101-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-24

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.148.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.113.1.el9_4

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.183.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-60

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-101-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-24

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.148.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.113.1.el9_4

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.183.1.el8_6

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

### 3.3.0​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-37-amd64

Debian 11Up to 5.10.0-35-amd64

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-309.180.4.el8uek

Photon 4.0Up to 5.10.238-2.ph4

Photon 3.0Up to 4.19.324-1.ph3

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.72.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.118.1.el9_2

RHEL 8.10Up to 4.18.0-553.109.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.97.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.147.1.el8_6

Rocky 9.5Up to 5.14.0-503.40.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.56.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.50.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.103.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.164.1

SUSE Linux Micro 6.1Up to 6.4.0-28-default

SUSE Linux Micro 6Up to 6.4.0-29-default

SUSE Linux Micro 5.5Up to 5.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-62-generic

Ubuntu 22.04Up to 6.8.0-60-generic

Ubuntu 22.04Up to 5.15.0-141-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.236-228.935.amzn2

Amazon Linux 2023Up to 6.1.134-152.225.amzn2023

Flatcar StableUp to 6.6.88-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-37-amd64

Debian 11Up to 5.10.0-35-amd64

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.70.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.118.1.el9_2

Rocky 9.5Up to 5.14.0-503.40.1.el9_5

Rocky 9.4Up to 5.14.0-427.72.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.50.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.103.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.164.1

SUSE Linux Micro 6.1Up to 6.4.0-28-default

SUSE Linux Micro 6Up to 6.4.0-29-default

SUSE Linux Micro 5.5Up to 5.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-62-generic

Ubuntu 22.04Up to 6.8.0-60-generic

Ubuntu 22.04Up to 5.15.0-141-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.235-227.919.amzn2

Amazon Linux 2023Up to 6.1.132-147.221.amzn2023

Flatcar StableUp to 6.6.88-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-60

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-24

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.118.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.68.2.el9_4

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.9.4Up to 5.15.0-139

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116

Ubuntu 22.04 with Multipath v0.9.4Up to 6.8.0-60

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-49

Ubuntu 24.04 with Multipath v0.9.4Up to 6.11.0-24

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.118.1.el9_2

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.24.1.el9_3

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.68.2.el9_4

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

### 3.2.3​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Debian 12Up to 6.1.0-33-amd64

Debian 11Up to 5.10.0-32-amd64

Debian 10Up to 4.19.0-27-amd64

Fedora 38Up to 6.8.9-100.fc38

Fedora 37Up to 6.5.12-100.fc37

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

OEL 8 Oracle Enterprise Linux (UEK Kernels)Up to 5.15.0-307.178.5.el8uek

Photon 4.0Up to 5.10.236-2.ph4

Photon 3.0Up to 4.19.325-1.ph3

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.97.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.115.1.el9_2

RHEL 8.10Up to 4.18.0-553.83.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.95.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.168.1.el8_6

Rocky 9.5Up to 5.14.0-503.40.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.51.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.47.2

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.88.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.161.1

SUSE Linux Micro 6.1Up to 6.4.0-25.1

SUSE Linux Micro 6Up to 6.4.0-26.1

SUSE Linux Micro 5.5Up to 5.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-60-generic

Ubuntu 22.04Up to 6.8.0-87-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.235-227.919.amzn2

Amazon Linux 2023Up to 6.1.134-152.225.amzn2023

Flatcar StableUp to 6.6.83-flatcar

Linux DistroKernel Version

Debian 12Up to 6.1.0-33-amd64

Debian 11Up to 5.10.0-34-amd64

Fedora 38Up to 6.8.9-100.fc38

Fedora 37Up to 6.5.12-100.fc37

RHEL 9.5Up to 5.14.0-503.40.1.el9_5

RHEL 9.4Up to 5.14.0-427.97.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.115.1.el9_2

RHEL 8.10Up to 4.18.0-553.83.1.el8_10

Rocky 9.5Up to 5.14.0-503.40.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.47.2

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.88.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.161.1

SUSE Linux Micro 6.1Up to 6.4.0-25.1

SUSE Linux Micro 6Up to 6.4.0-26.1

SUSE Linux Micro 5.5Up to 5.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-59-generic

Ubuntu 22.04Up to 6.8.0-87-generic

Ubuntu 20.04Up to 5.15.0-139-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.235-227.919.amzn2

Amazon Linux 2023Up to 6.1.134-152.225.amzn2023

Flatcar StableUp to 6.6.83-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 20.04 with Multipath v0.8.3Up to 5.4.0-144-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with Multipath v0.9.4 (compiled)Up to 6.5.0-27-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-40-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.97.1.el9_4.x86_64

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 20.04 with Multipath v0.8.3Up to 5.4.0-144-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with Multipath v0.9.4 (compiled)Up to 6.5.0-27-generic

RHEL9.2 with Multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL9.4 with Multipath v0.8.7Up to 5.14.0-427.50.1.el9_4.x86_64

### 3.2.2​

#### Supported Distros and Kernels​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Fedora 38Up to 6.8.9-100.fc38

Fedora 37Up to 6.5.12-100.fc37

Photon 4.0Up to 5.10.230-1.ph4

Photon 3.0Up to 4.19.325-1.ph3

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

RHEL 9.5Up to 5.14.0-503.26.1.el9_5

RHEL 9.4Up to 5.14.0-427.50.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.104.1.el9_2

RHEL 8.10Up to 4.18.0-553.47.1.el8_10

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.89.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.137.1.el8_6

Rocky 9.5Up to 5.14.0-503.26.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.40.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.38.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.88.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.150.1

SUSE Linux Micro 6.1Up to 6.4.0-24.1

SUSE Linux Micro 6Up to 6.4.0-24.1

SUSE Linux Micro 5.5Up to 5.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-55-generic

Ubuntu 22.04Up to 6.8.0-52-generic

Ubuntu 20.04Up to 5.15.0-131-generic

Debian 12Up to 6.1.0-31-amd64

Debian 11Up to 5.10.0-32-amd64
Note: Support for Debian 11 with kernel version 5.10.0-34-amd64 for PXStoreV1 has been removed due to a known issue, and we recommend using Debian 12 with kernel version `6.1.0-31-amd64`.

Debian 10Up to 4.19.0-27-amd64

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.234-225.895.amzn2.x86_64

Amazon Linux 2023Up to 6.1.128-136.201.amzn2023.x86_64

Flatcar StableUp to 6.6.83-flatcar

Linux DistroKernel Version

Fedora 38Up to 6.8.9-100.fc38

Fedora 37Up to 6.5.12-100.fc37

RHEL 9.5Up to 5.14.0-503.26.1.el9_5

RHEL 9.4Up to 5.14.0-427.50.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.104.1.el9_2

Rocky 9.5Up to 5.14.0-503.26.1.el9_5

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.38.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.88.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.150.1

SUSE Linux Micro 6.1Up to 6.4.0-24.1

SUSE Linux Micro 6Up to 6.4.0-24.1

SUSE Linux Micro 5.5Up to 5.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-53-generic

Ubuntu 22.04Up to 6.8.0-52-generic

Ubuntu 20.04Up to 5.15.0-131-generic

Debian 12Up to 6.1.0-31-amd64

Debian 11Up to 5.10.0-34-amd64

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.234-225.895.amzn2.x86_64

Amazon Linux 2023Up to 6.1.128-136.201.amzn2023.x86_64

Ubuntu 22.04.5 LTS (GKE 1.31.5-gke.10680005)5.15.0-1072-gke

Ubuntu 22.04.5 LTS (GKE 1.30.9-gke.1046000)5.15.0-1072-gke

Ubuntu 22.04.5 LTS (GKE 1.31.4-gke.1372000)5.15.0-1072-gke

Ubuntu 22.04.5 LTS (AKS 1.31, 9.9.9.0-14c1dce)5.15.0-1079-azure

Ubuntu 22.04.5 LTS (AKS 1.30.3, 9.9.9.0-fd8b305)5.15.0-1079-azure

#### Supported Distros and Kernel versions for SUSE Rancher​

Linux DistroKernel Version

SUSE Linux Micro 5.55.14.21-150500.55.88

SUSE Linux Micro 6.06.4.0-21

SUSE Linux Micro 6.16.4.0-19, 6.4.0-21

Ubuntu 22.04 LTS6.5.0-15

Ubuntu 24.04 LTS6.8.0-40, 6.8.0-48

RHEL 9.45.14.0-427.50.1.el9_4

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

- PX-StoreV1

- PX-StoreV2

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 20.04 with Multipath v0.8.3Up to 5.4.0-144-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with Multipath v0.9.4 (compiled)Up to 6.5.0-27-generic

Ubuntu 24.04 with Multipath v0.9.4Up to 6.8.0-40-generic

Ubuntu 24.04 with Multipath v0.9.46.8.0-48-generic

Ubuntu 24.04 with Multipath v0.9.46.8.0-49-generic

RHEL 8.6 with Multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with Multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with Multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with Multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with Multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Linux DistroKernel Version

Ubuntu 20.04 with Multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 20.04 with Multipath v0.8.3Up to 5.4.0-144-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 5.15.0-116-generic

Ubuntu 22.04 with Multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with Multipath v0.9.4 (compiled)Up to 6.5.0-27-generic

RHEL9.2 with Multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL9.4 with Multipath v0.8.7Up to 5.14.0-427.50.1.el9_4.x86_64

### 3.2.1.2​

#### Supported Distros and Kernels​

Linux DistroKernel Version

Fedora 38Up to 6.8.9-100.fc38

Fedora 37Up to 6.5.12-100.fc37

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

Photon 4.05.10.230-1.ph4

Photon 3.04.19.325-1.ph3

RHEL 9.5Up to 5.14.0-503.22.1.el9_5

RHEL 9.4Up to 5.14.0-427.50.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.100.1.el9_2

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEL 8.8Up to 4.18.0-477.86.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.134.1.el8_6

RHEL 8.10Up to 4.18.0-553.el8_10

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.33.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.30.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.88.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.147.1

SUSE Linux Micro 6.16.4.0-19.1

SUSE Linux Micro 6.06.4.0-21.1

SUSE Linux Enterprise Micro 5.55.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-52-generic

Ubuntu 22.04Up to 6.8.0-51-generic

Ubuntu 20.04Up to 5.15.0-130-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.230-223.885.amzn2.x86_64

Amazon Linux 2023Up to 6.1.119-129.201.amzn2023.x86_64

FlatCar StableUp to 6.6.74-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux DistroKernel Version

Fedora 38Up to 6.8.9-100.fc38

Fedora 37Up to 6.5.12-100.fc37

RHEL 9.5Up to 5.14.0-503.22.1.el9_5

RHEL 9.4Up to 5.14.0-427.50.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.97.1.el9_2

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.30.1

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.88.1

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.147.1

SUSE Linux Micro 6.16.4.0-19.1

SUSE Linux Micro 6.06.4.0-21.1

SUSE Linux Enterprise Micro 5.55.14.21-150500.55.88.1

Ubuntu 24.04Up to 6.8.0-51-generic

Ubuntu 22.04Up to 6.8.0-51-generic

Ubuntu 20.04Up to 5.15.0-130-generic

Cloud DistroKernel Version

Amazon Linux 2Up to 5.10.230-223.885.amzn2.x86_64

Amazon Linux 2023Up to 6.1.119-129.201.amzn2023.x86_64

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux kernels

Distribution NameKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

Ubuntu 24.04 with multipath v0.9.4Up to 6.8.0-40-generic

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade for PX-StoreV2​

Linux kernels

Distribution NameKernel Version

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

Ubuntu 24.04 with multipath v0.9.4Up to 6.8.0-40-generic

### 3.2.1.1​

#### Supported Distros and Kernels​

Linux DistroKernel Version

OEL 8.9 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9

OEL 8.8 Oracle Enterprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8

Photon 4.05.10.230-1.ph4

Photon 3.04.19.324-1.ph3

RHEL 9.4Up to 5.14.0-427.42.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.97.1.el9_2

RHEL 8.9Up to 4.18.0-513.24.1.el8_9

RHEl 8.8Up to 4.18.0-477.83.1.el8_8

RHEl 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.129.1.el8_6

RHEL 8.10Up to 4.18.0-553.el8_10

Rocky 9.4Up to 5.14.0-427.22.1.el9_4

Rocky 8.10Up to 4.18.0-553.33.1.el8_10

SLES (SUSE Enterprise Linux) SLES15 SP6Up to 6.4.0-150600.23.25-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

Ubuntu 24.04Up to 6.8.0-51-generic

Ubuntu 22.04Up to 6.8.0-50-generic

Ubuntu 20.04Up to 5.15.0-130-generic

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux DistroKernel Version

RHEL 9.4Up to 5.14.0-427.42.1.el9_4

RHEL 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.97.1.el9_2

Ubuntu 24.04Up to 6.8.0-50-generic

Ubuntu 22.04Up to 6.8.0-50-generic

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux kernels

Distribution NameKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

Ubuntu 24.04 with multipath v0.9.4Up to 6.8.0-40-generic

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade for PX-StoreV2​

Linux kernels

Distribution NameKernel Version

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

Ubuntu 24.04 with multipath v0.9.4Up to 6.8.0-40-generic

### 3.2.1​

#### Supported Distros and Kernel versions​

Linux kernels

Distribution NameKernel Version

Oracle 8.9Up to 4.18.0-513.24.1.el8_9

Oracle 8.8Up to 4.18.0-477.27.1.el8_8

Oracle 8.0Up to 5.15.0-302.167.6.el8uek

Photon 5.0Up to 6.1.81-5.ph5

Photon 4.0Up to 5.10.229-2.ph4

Photon 3.0Up to 4.19.323-1.ph3

Rhel 9.4Up to 5.14.0-427.42.1.el9_4

Rhel 9.3Up to 5.14.0-362.24.1.el9_3

Rhel 9.2Up to 5.14.0-284.92.1.el9_2

Rhel 8.10Up to 4.18.0-553.27.1.el8_10

Rhel 8.9Up to 4.18.0-513.24.1.el8_9

Rhel 8.8Up to 4.18.0-477.75.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.129.1.el8_6

Rocky 9.4Up to 5.14.0-427.42.1.el9_4

Rocky 8.10Up to 4.18.0-553.27.1.el8_10

Ubuntu 24.04Up to 6.8.0-49-generic

Ubuntu 22.04Up to 6.8.0-49-generic

Ubuntu 20.04 LTSUp to 5.15.0-126-generic

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

Cloud distros

Distribution NameKernel Version

Amazon Linux 2Up to 5.15.145-95.161.amzn2.x86_64

Amazon Linux 2023Up to 6.1.115-126.197.amzn2023.x86_64

FlatCar StableUp to 6.6.60-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux kernels

Distribution NameKernel Version

Rhel 9.4Up to 5.14.0-427.42.1.el9_4

Rhel 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.90.1.el9_2

Rocky 9.4Up to 5.14.0-427.42.1.el9_4

Ubuntu 24.04Up to 6.8.0-48-generic

Ubuntu 22.04Up to Up to 6.8.0-48-generic

Cloud distros

Distribution NameKernel Version

Amazon Linux 2Up to 5.10.228-219.884.amzn2.x86_64

Amazon Linux 2023Up to 6.1.115-126.197.amzn2023.x86_64

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux kernels

Distribution NameKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

Ubuntu 24.04 with multipath v0.9.4Up to 6.8.0-40-generic

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade for PX-StoreV2​

Linux kernels

Distribution NameKernel Version

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

Ubuntu 24.04 with multipath v0.9.4Up to 6.8.0-40-generic

### 3.2.0​

#### Supported Distros and Kernel versions​

Linux kernels

Distribution NameKernel Version

Oracle 8.9Up to 4.18.0-513.24.1.el8_9

Oracle 8.8Up to 4.18.0-477.27.1.el8_8

Oracle 8Up to 5.15.0-301.163.5.2.el8uek

Rhel 9.4Up to 5.14.0-427.40.1.el9_4

Rhel 9.3Up to 5.14.0-362.24.1.el9_3

Rhel 9.2Up to 5.14.0-284.88.1.el9_2

Rhel 8.10Up to 4.18.0-553.22.1.el8_10

Rhel 8.9Up to 4.18.0-513.24.1.el8_9

Rhel 8.8Up to 4.18.0-477.75.1.el8_8

RHEL 8.7Up to 4.18.0-425.19.2.el8_7

RHEL 8.6Up to 4.18.0-372.123.1.el8_6

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

Rocky 9.4Up to 5.14.0-427.40.1.el9_4

Rocky 8.10Up to 4.18.0-553.22.1.el8_10

Ubuntu 22.04Up to 6.8.0-47-generic

Ubuntu 20.04 LTSUp to 5.15.0-124-generic

Ubuntu 18.04Up to 5.4.0-150-generic

Cloud distros

Distribution NameKernel Version

Amazon Linux 2Up to 5.15.145-95.161.amzn2.x86_64

FlatCar StableUp to 6.6.53-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux kernels

Distribution NameKernel Version

Rhel 9.4Up to 5.14.0-427.37.1.el9_4

Rhel 9.3Up to 5.14.0-362.24.1.el9_3

RHEL 9.2Up to 5.14.0-284.86.1.el9_2

Rocky 9.4Up to 5.14.0-427.40.1.el9_4

Ubuntu 22.04Up to Up to 6.8.0-47-generic

Ubuntu 20.04Up to 5.15.0-124-generic

Ubuntu 18.04Up to 5.4.0-150-generic

Cloud distros

Distribution NameKernel Version

Amazon Linux 2Up to 5.10.205-195.804.amzn2.x86_64

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux kernels

Distribution NameKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu 22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

Ubuntu 24.04 with multipath v0.9.4Up to 6.8.0-40-generic

### 3.1.8​

#### Supported Distros and Kernel versions​

Linux DistroKernel Version

Debian 10Up to 4.19.0-27-amd64

Debian 11Up to 5.10.0-32-amd64

Debian 12Up to 6.1.0-23-amd64

OEL 8.x Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-205.149.5.1.el8uek.x86_64

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-477.27.0.1.el8_8.x86_64

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9.x86_64

Fedora 37Up to 6.0.7-301.fc37.x86_64

Fedora 38Up to 6.2.9-300.fc38.x86_64

RHEL 8.6Up to 4.18.0-372.158.1.el8_6.x86_64

RHEL 8.7Up to 4.18.0-425.19.2.el8_7.x86_64

RHEL 8.8Up to 4.18.0-477.58.1.el8_8.x86_64

RHEL 8.9Up to 4.18.0-513.24.1.el8_9.x86_64

RHEL 8.10Up to 4.18.0-553.72.1.el8_10.x86_64

RHEL 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

RHEL 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

RHEL 9.4Up to 5.14.0-427.85.1.el9_4.x86_64

Rocky Linux 8.10Up to 4.18.0-553.8.1.el8_10.x86_64

Rocky Linux 9.4Up to 5.14.0-427.22.1.el9_4.x86_64

Ubuntu 18.04 LTSUp to 5.4.0-150-generic

Ubuntu 20.04 LTSUp to 5.15.0-101-generic

Ubuntu 22.04 LTSUp to 6.8.0-78-generic

Photon 3Up to 4.19.311-1.ph3

Photon 4Up to 5.10.222-2.ph4

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

FlatCar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux DistroKernel Version

Rhel 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

Rhel 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

Ubuntu 18.04Up to 5.4.0-150-generic

Ubuntu 20.04Up to 5.15.0-101-generic

Ubuntu 22.04Up to 6.5.0-28-generic

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

Flatcar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux DistroKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu-22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

### 3.1.7​

#### Supported Distros and Kernel versions​

Linux DistroKernel Version

Debian 10Up to 4.19.0-27-amd64

Debian 11Up to 5.10.0-32-amd64

Debian 12Up to 6.1.0-23-amd64

OEL 8.x Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-205.149.5.1.el8uek.x86_64

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-477.27.0.1.el8_8.x86_64

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9.x86_64

Fedora 37Up to 6.0.7-301.fc37.x86_64

Fedora 38Up to 6.2.9-300.fc38.x86_64

RHEL 8.6Up to 4.18.0-372.158.1.el8_6.x86_64

RHEL 8.7Up to 4.18.0-425.19.2.el8_7.x86_64

RHEL 8.8Up to 4.18.0-477.58.1.el8_8.x86_64

RHEL 8.9Up to 4.18.0-513.24.1.el8_9.x86_64

RHEL 8.10Up to 4.18.0-553.72.1.el8_10.x86_64

RHEL 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

RHEL 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

RHEL 9.4Up to 5.14.0-427.85.1.el9_4.x86_64

Rocky Linux 8.10Up to 4.18.0-553.8.1.el8_10.x86_64

Rocky Linux 9.4Up to 5.14.0-427.22.1.el9_4.x86_64

Ubuntu 18.04 LTSUp to 5.4.0-150-generic

Ubuntu 20.04 LTSUp to 5.15.0-101-generic

Ubuntu 22.04 LTSUp to 6.8.0-78-generic

Photon 3Up to 4.19.311-1.ph3

Photon 4Up to 5.10.222-2.ph4

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

FlatCar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux DistroKernel Version

Rhel 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

Rhel 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

Ubuntu 18.04Up to 5.4.0-150-generic

Ubuntu 20.04Up to 5.15.0-101-generic

Ubuntu 22.04Up to 6.5.0-28-generic

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

Flatcar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux DistroKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu-22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

### 3.1.6​

#### Supported Distros and Kernel versions​

Linux DistroKernel Version

Debian 10Up to 4.19.0-27-amd64

Debian 11Up to 5.10.0-32-amd64

Debian 12Up to 6.1.0-23-amd64

OEL 8.x Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-205.149.5.1.el8uek.x86_64

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-477.27.0.1.el8_8.x86_64

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9.x86_64

Fedora 37Up to 6.0.7-301.fc37.x86_64

Fedora 38Up to 6.2.9-300.fc38.x86_64

RHEL 8.6Up to 4.18.0-372.158.1.el8_6.x86_64

RHEL 8.7Up to 4.18.0-425.19.2.el8_7.x86_64

RHEL 8.8Up to 4.18.0-477.58.1.el8_8.x86_64

RHEL 8.9Up to 4.18.0-513.24.1.el8_9.x86_64

RHEL 8.10Up to 4.18.0-553.72.1.el8_10.x86_64

RHEL 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

RHEL 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

RHEL 9.4Up to 5.14.0-427.85.1.el9_4.x86_64

Rocky Linux 8.10Up to 4.18.0-553.8.1.el8_10.x86_64

Rocky Linux 9.4Up to 5.14.0-427.22.1.el9_4.x86_64

Ubuntu 18.04 LTSUp to 5.4.0-150-generic

Ubuntu 20.04 LTSUp to 5.15.0-101-generic

Ubuntu 22.04 LTSUp to 6.8.0-78-generic

Photon 3Up to 4.19.311-1.ph3

Photon 4Up to 5.10.222-2.ph4

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

FlatCar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux DistroKernel Version

Rhel 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

Rhel 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

Ubuntu 18.04Up to 5.4.0-150-generic

Ubuntu 20.04Up to 5.15.0-101-generic

Ubuntu 22.04Up to 6.5.0-28-generic

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

Flatcar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux DistroKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu-22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

### 3.1.5​

#### Supported Distros and Kernel versions​

Linux DistroKernel Version

Debian 10Up to 4.19.0-27-amd64

Debian 11Up to 5.10.0-32-amd64

Debian 12Up to 6.1.0-23-amd64

OEL 8.x Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-205.149.5.1.el8uek.x86_64

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-477.27.0.1.el8_8.x86_64

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9.x86_64

Fedora 37Up to 6.0.7-301.fc37.x86_64

Fedora 38Up to 6.2.9-300.fc38.x86_64

RHEL 8.6Up to 4.18.0-372.158.1.el8_6.x86_64

RHEL 8.7Up to 4.18.0-425.19.2.el8_7.x86_64

RHEL 8.8Up to 4.18.0-477.58.1.el8_8.x86_64

RHEL 8.9Up to 4.18.0-513.24.1.el8_9.x86_64

RHEL 8.10Up to 4.18.0-553.72.1.el8_10.x86_64

RHEL 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

RHEL 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

RHEL 9.4Up to 5.14.0-427.85.1.el9_4.x86_64

Rocky Linux 8.10Up to 4.18.0-553.8.1.el8_10.x86_64

Rocky Linux 9.4Up to 5.14.0-427.22.1.el9_4.x86_64

Ubuntu 18.04 LTSUp to 5.4.0-150-generic

Ubuntu 20.04 LTSUp to 5.15.0-101-generic

Ubuntu 22.04 LTSUp to 6.8.0-78-generic

Photon 3Up to 4.19.311-1.ph3

Photon 4Up to 5.10.222-2.ph4

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

FlatCar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux DistroKernel Version

Rhel 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

Rhel 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

Ubuntu 18.04Up to 5.4.0-150-generic

Ubuntu 20.04Up to 5.15.0-101-generic

Ubuntu 22.04Up to 6.5.0-28-generic

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

Flatcar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux DistroKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu-22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

### 3.1.4​

#### Supported Distros and Kernel versions​

Linux DistroKernel Version

Debian 10Up to 4.19.0-27-amd64

Debian 11Up to 5.10.0-32-amd64

Debian 12Up to 6.1.0-23-amd64

OEL 8.x Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-205.149.5.1.el8uek.x86_64

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-477.27.0.1.el8_8.x86_64

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9.x86_64

Fedora 37Up to 6.0.7-301.fc37.x86_64

Fedora 38Up to 6.2.9-300.fc38.x86_64

RHEL 8.6Up to 4.18.0-372.109.1.el8_6.x86_64

RHEL 8.7Up to 4.18.0-425.19.2.el8_7.x86_64

RHEL 8.8Up to 4.18.0-477.58.1.el8_8.x86_64

RHEL 8.9Up to 4.18.0-513.24.1.el8_9.x86_64

RHEL 8.10Up to 4.18.0-553.8.1.el8_10.x86_64

RHEL 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

RHEL 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

RHEL 9.4Up to 5.14.0-427.26.1.el9_4.x86_64

Rocky Linux 8.10Up to 4.18.0-553.8.1.el8_10.x86_64

Rocky Linux 9.4Up to 5.14.0-427.22.1.el9_4.x86_64

Ubuntu 18.04 LTSUp to 5.4.0-150-generic

Ubuntu 20.04 LTSUp to 5.15.0-101-generic

Ubuntu 22.04 LTSUp to 6.5.0-28-generic

Photon 3Up to 4.19.311-1.ph3

Photon 4Up to 5.10.222-2.ph4

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

FlatCar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux DistroKernel Version

Rhel 9.2Up to 5.14.0-284.73.1.el9_2.x86_64

Rhel 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

Ubuntu 18.04Up to 5.4.0-150-generic

Ubuntu 20.04Up to 5.15.0-101-generic

Ubuntu 22.04Up to 6.5.0-28-generic

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.220-209.869.amzn2.x86_64

Flatcar StableUp to 6.6.43-flatcar

#### Supported Distros and Kernel versions for Pure FlashArray and FlashBlade​

Linux DistroKernel Version

RHEL 8.6 with default multipath v0.8.4Up to 4.18.0-372.46.1.el8_6.x86_64

RHEL 8.9 with default multipath v0.8.4Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2 with default multipath v0.8.7Up to 5.14.0-284.32.1.el9_2.x86_64

RHEL 9.3 with default multipath v0.8.7Up to 5.14.0-362.18.1.el9_3.x86_64

RHEL 9.4 with default multipath v0.8.7Up to 5.14.0-427.13.1.el9_4.x86_64

Ubuntu 18.04 with default multipath v0.7.4Up to 5.4.0-150-generic

Ubuntu 20.04 with default multipath v0.8.3Up to 5.15.0-67-generic

Ubuntu-22.04 with default multipath v0.8.8Up to 6.5.0-35-generic

Ubuntu 22.04 with multipath v0.9.4Up to 6.5.0-27-generic

### 3.1.2​

#### Supported Distros and Kernel versions​

Linux DistroKernel Version

Debian 10Up to 4.19.0-26-amd64

Debian 11Up to 5.10.0-28-amd64

Debian 12Up to 6.1.0-18-amd64

OEL 8.x Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-205.149.5.1.el8uek.x86_64

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8.x86_64

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-513.24.1.el8_9.x86_64

Fedora 36Up to 6.2.15-100.fc36.x86_64

Fedora 37Up to 6.5.12-100.fc37.x86_64

Fedora 38Up to 6.2.9-300.fc38.x86_64

RHEL 8.6Up to 4.18.0-372.103.1.el8_6.x86_64

RHEL 8.7Up to 4.18.0-425.19.2.el8_7.x86_64

RHEL 8.8Up to 4.18.0-477.55.1.el8_8.x86_64

RHEL 8.9Up to 4.18.0-513.24.1.el8_9.x86_64

RHEL 8.10Up to 4.18.0-553.5.1.el8_10.x86_64

RHEL 9.2Up to 5.14.0-284.66.1.el9_2.x86_64

RHEL 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

RHEL 9.4Up to 5.14.0-427.18.1.el9_4.x86_64

Rocky Linux 8.10Up to 4.18.0-553.8.1.el8_10.x86_64

Rocky Linux 9.4Up to 5.14.0-427.22.1.el9_4.x86_64

Ubuntu 18.04 LTSUp to 5.4.0-150-generic

Ubuntu 20.04 LTSUp to 5.15.0-101-generic

Ubuntu 22.04 LTSUp to 6.5.0-28-generic

Photon 3Up to 4.19.311-1.ph3

Photon 4Up to 5.10.214-3.ph4

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.59-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.217-205.860.amzn2.x86_64

FlatCar StableUp to 6.1.90-flatcar

note

Using Ubuntu 22.04 with Multipath 0.8.8 can cause high CPU usage and make your system unresponsive. To maintain stability, avoid upgrading to Ubuntu 22.04 if you use Multipath 0.8.8.

#### Supported Distros and Kernel versions for PX-StoreV2​

Linux DistroKernel Version

Fedora 36Up to 6.2.15-100.fc36.x86_64

Fedora 37Up to 6.5.12-100.fc37.x86_64

Rhel 9.2Up to 5.14.0-284.66.1.el9_2.x86_64

Rhel 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

Ubuntu 18.04Up to 5.4.0-150-generic

Ubuntu 20.04Up to 5.15.0-101-generic

Ubuntu 22.04Up to 6.5.0-28-generic

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.217-205.860.amzn2.x86_64

Flatcar StableUp to 6.1.90-flatcar

### 3.1.1​

#### Supported Distros and Kernel versions​

Linux DistroKernel Version

Debian 10Up to 4.19.0-26-amd64

Debian 11Up to 5.10.0-28-amd64

Debian 12Up to 6.1.0-18-amd64

OEL 8.x Oracle Enteprise Linux (UEK Kernels)Up to 5.15.0-204.147.6.2.el8uek.x86_64

OEL 8.8 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-477.27.1.el8_8.x86_64

OEL 8.9 Oracle Enteprise Linux (RHCK Kernels)Up to 4.18.0-513.18.1.el8_9.x86_64

Fedora 36Up to 6.2.15-100.fc36.x86_64

Fedora 37Up to 6.5.12-100.fc37.x86_64

Fedora 38Up to 6.7.9-100.fc38.x86_64

RHEL 8.6Up to 4.18.0-372.95.1.el8_6.x86_64

RHEL 8.7Up to 4.18.0-425.19.2.el8_7.x86_64

RHEL 8.8Up to 4.18.0-477.27.1.el8_8.x86_64

RHEL 8.9Up to 4.18.0-513.18.1.el8_9.x86_64

RHEL 9.2Up to 5.14.0-284.54.1.el9_2.x86_64

RHEL 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

Rocky Linux 8.8Up to 4.18.0-513.18.1.el8_9.x86_64

Rocky Linux 9.2Up to 5.14.0-362.24.1.el9_3.x86_64

Ubuntu 18.04 LTSUp to 5.4.0-150-generic

Ubuntu 20.04 LTSUp to 5.15.0-101-generic

Ubuntu 22.04 LTSUp to 6.5.0-26-generic

Photon 3Up to 4.19.307-3.ph3

Photon 4Up to 5.10.212-3.ph4

SLES (SUSE Enterprise Linux) SLES15 SP4Up to 5.14.21-150400.24.108-default

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150400.24.46-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.210-201.852.amzn2.x86_64

Flatcar StableUp to 6.1.81-flatcar

note

Using Ubuntu 22.04 with Multipath 0.8.8 can cause high CPU usage and make your system unresponsive. To maintain stability, avoid upgrading to Ubuntu 22.04 if you use Multipath 0.8.8.

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.210-201.852.amzn2.x86_64

Flatcar StableUp to 6.1.81-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

note

Linux kernel version 4.20 or newer is the minimum required version, 5.0 or newer is recommended.

Linux DistroKernel Version

Fedora 36Up to 6.2.15-100.fc36.x86_64

Fedora 37Up to 6.5.12-100.fc37.x86_64

Rhel 9.2Up to 5.14.0-284.54.1.el9_2.x86_64

Rhel 9.3Up to 5.14.0-362.24.1.el9_3.x86_64

Ubuntu 18.04Up to 5.4.0-150-generic

Ubuntu 20.04Up to 5.15.0-101-generic

Ubuntu 22.04Up to 6.5.0-26-generic

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.210-201.852.amzn2.x86_64

Flatcar StableUp to 6.1.81-flatcar

### 3.1.0​

#### Supported Distros and Kernel versions​

Linux DistroKernel Version

Centos 7.9Up to 7.9 3.10.0-1160.108.1.el7

Debian 10Up to 4.19.0-25-cloud-amd64

Debian 11Up to 5.10.0-27-amd64

Debian 12Up to 6.1.0-17-amd64

OEL 7.9 (Oracle Enteprise Linux)Up to 3.10.0-1160.105.1.0.1.el7.x86_64

Fedora 36Up to 6.2.15-100.fc36.x86_64

Fedora 37Up to 6.5.12-100.fc37.x86_64

RHEL 7.9Up to 3.10.0-1160.99.1.el7.x86_64

RHEL 8.6Up to 4.18.0-372.87.1.el8_6.x86_64

RHEL 8.7Up to 4.18.0-425.19.2.el8_7.x86_64

RHEL 8.8Up to 4.18.0-513.11.1.el8_9.x86_64

RHEL 8.9Up to 4.18.0-513.11.1.el8_9.x86_64

RHEL 9.2Up to 5.14.0-284.48.1.el9_2.x86_64

RHEL 9.3Up to 5.14.0-362.13.1.el9_3.x86_64

Rocky Linux 8.8Up to 4.18.0-477.27.1.el8_8.x86_64

Rocky Linux 9.2Up to 5.14.0-362.13.1.el9_3.x86_64

Ubuntu 18.04 LTSUp to 5.4.0-150-generic

Ubuntu 20.04 LTSUp to 5.15.0-91-generic

Ubuntu 22.04 LTSUp to 6.5.0-14-generic

Photon 3Up to 4.19.247-6.ph3

Photon 4Up to 5.10.118-3.ph4

SLES (SUSE Enterprise Linux) SLES15 SP5Up to 5.14.21-150500.55.39-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.205-195.804.amzn2.x86_64

Flatcar StableUp to 6.1.73-flatcar

#### Supported Distros and Kernel versions for PX-StoreV2​

note

Linux kernel version 4.20 or newer is the minimum required version, 5.0 or newer is recommended.

Linux DistroKernel Version

Fedora 36Up to 6.2.15-100.fc36.x86_64

Fedora 37Up to 6.5.12-100.fc37.x86_64

Rhel 9.2Up to 5.14.0-284.48.1.el9_2.x86_64

Rhel 9.3Up to 5.14.0-362.8.1.el9_3.x86_64

Ubuntu 18.04Up to 5.4.0-150-generic

Ubuntu 20.04Up to 5.15.0-92-generic

Ubuntu 22.04Up to 6.5.0-15-generic

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.205-195.804.amzn2.x86_64

Flatcar StableUp to 6.1.73-flatcar

### 3.0.4​

Linux DistroKernel Version

CentOS 7Up to 3.10.0-1160.95.1.el7.x86_64

Ubuntu 20.04.2 LTSUp to 5.4.0-144-generic

Ubuntu 22.04.2 LTSUp to 5.19.0-45-generic

Fedora 36Up to kernel-6.2.15-300.fc38.x86_64

RHEL 7.9 (Ootpa)Up to 3.10.0-1160.99.1.el7.x86_64

RHEL 8.8 (Ootpa)Up to 4.18.0-477.27.1.el8_8.x86_64

RHEL 9.2 (Plow)5.14.0-284.30.1.el9_2.x86_64 and 5.14.0-284.32.1.el9_2.x86_64

Rocky Linux 8.8 (Green Obsidian)Up to 4.18.0-477.27.1.el8_8.x86_64

Rocky Linux 9.2 (Blue Onyx)Up to 5.14.0-284.18.1.el9_2.x86_64

Debian 10Up to 4.19.0-25-cloud-amd64

Debian 11Up to 5.10.0-25-amd64

OEL 7.9Up to 3.10.0-1160.99.1.0.1.el7.x86_64

Photon 3.0Up to 4.19.269-3.ph3

Photon 4.0Up to 5.10.118-3.ph4

SLES15 SP45.14.21-150400.24.33-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.162-141.675.amzn2.x86_64

FlatCar StableUp to 5.15.129-flatcar

### 3.0.2​

Linux DistroKernel Version

CentOS 7Up to 3.10.0-1160.95.1.el7.x86_64

Ubuntu 20.04.2 LTSUp to 5.4.0-144-generic

Ubuntu 22.04.2 LTSUp to 5.19.0-45-generic

Fedora 36Up to 5.17.5-300.fc36.x86_64

RHEL 7.9 (Ootpa)Up to 3.10.0-1160.99.1.el7.x86_64

RHEL 8.8 (Ootpa)Up to 4.18.0-477.27.1.el8_8.x86_64

RHEL 9.2 (Plow)5.14.0-284.30.1.el9_2.x86_64 and 5.14.0-284.32.1.el9_2.x86_64

Rocky Linux 8.8 (Green Obsidian)Up to 4.18.0-477.27.1.el8_8.x86_64

Rocky Linux 9.2 (Blue Onyx)Up to 5.14.0-284.18.1.el9_2.x86_64

Debian 10Up to 4.19.0-25-cloud-amd64

Debian 11Up to 5.10.0-25-amd64

OEL 7.9Up to 3.10.0-1160.99.1.0.1.el7.x86_64

Photon 3.0Up to 4.19.269-3.ph3

Photon 4.0Up to 5.10.118-3.ph4

SLES15 SP45.14.21-150400.24.33-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.162-141.675.amzn2.x86_64

FlatCar StableUp to 5.15.129-flatcar

### 3.0.0​

Linux DistroKernel Version

CentOS 7.9-vanillaUp to 3.10.0-1160.92.1.el7.x86_64

CentOS 8.5-vanillaUp to 4.18.0-348.7.1.el8_5.x86_64

Ubuntu 18.04 LTSUp to 4.15.0-175-generic

Ubuntu 20.04 LTSUp to 5.15.0-1017-generic

Ubuntu 22.04.2 LTSUp to 5.19.0-45-generic

Fedora 28Up to 5.0.16-100.fc28.x86_64

Fedora 33Up to 5.14.18-100.fc33.x86_64

Fedora 34Up to 5.17.12-100.fc34.x86_64

RHEL 7Up to 4.20.13-1.el7.elrepo.x86_64

RHEL 8.8 (Ootpa)Up to 4.18.0-477.15.1.el8_8.x86_64

RHEL 9.2 (Plow)(Single Kernel) 5.14.0-284.13.1.el9_2.x86_64

Debian 9Up to 4.9.0-13-amd64

Debian 10Up to 4.19.0-24-cloud-amd64

Debian 11Up to 5.10.0-23-amd64

OEL 7.9Up to 3.10.0-1160.92.1.0.1.el7.x86_64

Photon 3.0Up to 4.19.247-6.ph3

Photon 4.0Up to 5.10.118-3.ph4

SLES15 SP45.14.21-150400.24.33-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.162-141.675.amzn2.x86_64

FlatCar AlphaUp to 5.15.89-flatcar

FlatCar BetaUp to 5.15.111-flatcar

FlatCar StableUp to 5.15.113-flatcar

### 2.13.0​

Linux DistroKernel Version

CentOS 7.8-vanillaUp to 3.10.0-1160.83.1.el7.x86_64

CentOS 7.9Up to 5.16.14-1.el7.elrepo.x86_64

CentOS 8.2-vanillaUp to 4.18.0-348.7.1.el8_5.x86_64

Ubuntu 18.04.5 LTSUp to 5.4.0-1040-gcp

Ubuntu 20.04.05 LTSUp to 5.15.0-1017-generic

Ubuntu 20.10Up to 5.13.0-1028-gcp

Ubuntu 21.04Up to 5.11.0-1007-gcp

Ubuntu 22.04.1 LTSUp to 5.15.0-60-generic

Fedora 27Up to 4.18.19-100.fc27.x86_64

Fedora 28Up to 5.0.16-100.fc28.x86_64

Fedora 33Up to 5.14.18-100.fc33.x86_64

Fedora 34Up to 5.17.12-100.fc34.x86_64

RHEL 7.6Up to 4.20.13-1.el7.elrepo.x86_64

RHEL 7.9Up to 3.10.0-1160.71.1.el7.x86_64

RHEL 8.4Up to 4.18.0-305.25.1.el8_4.x86_64

RHEL 8.5 (Ootpa)Up to 4.18.0-348.20.1.el8_5.x86_64

RHEL 8.6 (Ootpa)Up to 4.18.0-305.25.1.el8_4.x86_64

RHEL 8.7 (Ootpa)Up to 4.18.0-425.10.1.el8_7.x86_64

Debian 9Up to 4.9.0-13-amd64

Debian 10Up to 4.19.0-23-cloud-amd64

Debian 11Up to 5.10.0-21-amd64

OEL 7.9Up to 3.10.0-1160.59.1.el7.x86_64

Photon 3.0Up to 4.19.269-3.ph3

Photon 4.0Up to 5.10.118-3.ph4

SLES15 SP45.14.21-150400.24.33-default

Cloud DistroKernel Version

Amazon Linux v2Up to 5.10.162-141.675.amzn2.x86_64

FlatCar AlphaUp to 5.15.89-flatcar

FlatCar BetaUp to 5.15.63-flatcar

FlatCar StableUp to 5.15.63-flatcar

### 2.12.2​

Linux DistroKernel Version

CentOS 7.8-vanillaUp to 3.10.0-1127.el7.x86_64

CentOS 7.9Up to 5.16.14-1.el7.elrepo.x86_64

CentOS 8.2-vanillaUp to 4.18.0-193.el8.x86_64

Ubuntu 18.04.5 LTSUp to 5.4.0-1040-gcp

Ubuntu 20.04.05 LTSUp to 5.15.0-1017-generic

Ubuntu 20.10Up to 5.13.0-1028-gcp

Ubuntu 21.04Up to 5.11.0-1007-gcp

Ubuntu 22.04.1 LTSUp to 5.15.0-46-generic

Fedora 27Up to 4.18.19-100.fc27.x86_64

Fedora 28Up to 5.0.16-100.fc28.x86_64

Fedora 33Up to 5.14.18-100.fc33.x86_64

Fedora 34Up to 5.17.12-100.fc34.x86_64

RHEL 7.6Up to 4.20.13-1.el7.elrepo.x86_64

RHEL 7.9Up to 3.10.0-1127.el7.x86_64

RHEL 8.4Up to 4.18.0-305.25.1.el8_4.x86_64

RHEL 8.5 (Ootpa)Up to 4.18.0-425.3.1.el8.x86_64

RHEL 8.6 (Ootpa)Up to 4.18.0-425.3.1.el8.x86_64

RHEL 8.7 (Ootpa)Up to 4.18.0-425.13.1.el8_7.x86_64

Debian 9Up to 4.9.0-13-amd64

Debian 10Up to 4.19.0-20-cloud-amd64

OEL 7.9Up to 3.10.0-1160.59.1.el7.x86_64

Photon 3.0Up to 4.19.247-6.ph3

Photon 4.0Up to 5.10.118-3.ph4

Cloud DistroKernel Version

Amazon Linux v24.14.232-177.418.amzn2.x86_64

FlatCar AlphaUp to 5.15.63-flatcar

FlatCar BetaUp to 5.15.63-flatcar

FlatCar StableUp to 5.15.63-flatcar

### 2.12​

Linux DistroKernel Version

CentOS 7.8-vanillaUp to 3.10.0-1127.el7.x86_64

CentOS 7.9Up to 5.16.14-1.el7.elrepo.x86_64

CentOS 8.2-vanillaUp to 4.18.0-193.el8.x86_64

Ubuntu 18.04.5 LTSUp to 5.4.0-1040-gcp

Ubuntu 20.04.05 LTSUp to 5.15.0-1017-generic

Ubuntu 20.10Up to 5.13.0-1028-gcp

Ubuntu 21.04Up to 5.11.0-1007-gcp

Ubuntu 22.04.1 LTSUp to 5.15.0-46-generic

Fedora 27Up to 4.18.19-100.fc27.x86_64

Fedora 28Up to 5.0.16-100.fc28.x86_64

Fedora 33Up to 5.14.18-100.fc33.x86_64

Fedora 34Up to 5.17.12-100.fc34.x86_64

RHEL 7.6Up to 4.20.13-1.el7.elrepo.x86_64

RHEL 7.9Up to 3.10.0-1127.el7.x86_64

RHEL 8.4Up to 4.18.0-305.25.1.el8_4.x86_64

RHEL 8.5 (Ootpa)Up to 4.18.0-425.3.1.el8.x86_64

RHEL 8.6 (Ootpa)Up to 4.18.0-425.3.1.el8.x86_64

Debian 9Up to 4.9.0-13-amd64

Debian 10Up to 4.19.0-20-cloud-amd64

OEL 7.9Up to 3.10.0-1160.59.1.el7.x86_64

Photon 3.0Up to 4.19.247-6.ph3

Photon 4.0Up to 5.10.118-3.ph4

Cloud DistroKernel Version

Amazon Linux v24.14.232-177.418.amzn2.x86_64

FlatCar AlphaUp to 5.15.63-flatcar

FlatCar BetaUp to 5.15.63-flatcar

FlatCar StableUp to 5.15.63-flatcar

### 2.11​

Linux DistroKernel Version

CentOS 7.8-vanilla3.10.0-1127.el7.x86_64

CentOS 8.2-vanilla4.18.0-193.el8.x86_64

Ubuntu 18.04.5 LTS5.4.0-1040-gcp

Ubuntu 20.04.02 LTS5.4.0-73-generic

Ubuntu 20.105.13.0-1028-gcp

Ubuntu 21.045.11.0-1007-gcp

Fedora 27Up to 4.18.19-100.fc27.x86_64

Fedora 28Up to 5.0.16-100.fc28.x86_64

Fedora 33Up to 5.14.18-100.fc33.x86_64

FlatCar Alpha5.10.93-flatcar

FlatCar Beta5.10.93-flatcar

FlatCar Stable5.10.107-flatcar

RHEL 7.64.20.13-1.el7.elrepo.x86_64

RHEL 7.9Up to 3.10.0-1127.el7.x86_64

RHEL 8.4Up to 4.18.0-305.25.1.el8_4.x86_64

RHEL 8.5 (Ootpa)Up to 4.18.0-372.16.1.el8_6.x86_64

Debian 9Up to 4.9.0-13-amd64

Debian 10Up to 4.19.0-20-cloud-amd64

OEL 7.9Up to 3.10.0-1160.59.1.el7.x86_64

Cloud DistroKernel Version

Amazon Linux v24.14.232-177.418.amzn2.x86_64

Photon 3.04.19.132-6.ph3

Photon 4.05.10.4-16.ph4

### 2.10​

Linux DistroKernel Version

CentOS 7.55.4.12-1.el7.elrepo.x86_64

CentOS 7.8-vanilla3.10.0-1127.el7.x86_64

CentOS 8.2-vanilla4.18.0-240.22.1.el8_3.x86_64

Ubuntu 18.04.5 LTS5.4.0-1040-gcp

Ubuntu 20.04.02 LTS5.4.0-73-generic

Ubuntu 20.105.13.0-1019-gcp

Ubuntu 21.045.11.0-1007-gcp

Fedora 27Up to 4.13.9-300.fc27.x86_64

Fedora 28Up to 4.16.3-301.fc28.x86_64

FlatCar Alpha5.10.93-flatcar

FlatCar Beta5.10.93-flatcar

FlatCar Stable5.10.107-flatcar

RHEL 7.64.20.13-1.el7.elrepo.x86_64

RHEL 7.8Up to 3.10.0-1160.25.1.el7.x86_64

RHEL 8.4 BETA4.18.0-293.el8.x86_64

Debian 9Up to 4.9.0-15-amd64

Debian 10Up to 4.19.0-16-cloud-amd64

OEL 7.9Up to 3.10.0-1160.59.1.el7.x86_64

Cloud DistroKernel Version

Amazon Linux v24.14.225-169.362.amzn2.x86_64

Photon 3.04.19.132-6.ph3

Photon 4.05.10.4-16.ph4

### 2.9​

Linux DistroKernel Version

CentOS 7.55.4.12-1.el7.elrepo.x86_64

CentOS 7.8-vanilla3.10.0-1127.el7.x86_64

CentOS 8.2-vanilla4.18.0-240.22.1.el8_3.x86_64

Ubuntu 18.04.5 LTS5.4.0-1040-gcp

Ubuntu 20.04.02 LTS5.4.0-73-generic

Ubuntu 20.105.8.0-1031-gcp

Ubuntu 21.045.11.0-1007-gcp

Fedora 27Up to 4.13.9-300.fc27.x86_64

Fedora 28Up to 4.16.3-301.fc28.x86_64

FlatCar Alpha5.10.46-flatcar

FlatCar Beta5.10.46-flatcar

FlatCar Stable5.10.75-flatcar

RHEL 7.64.20.13-1.el7.elrepo.x86_64

RHEL 7.8Up to 3.10.0-1160.25.1.el7.x86_64

RHEL 8.4 BETA4.18.0-293.el8.x86_64

Debian 9Up to 4.9.0-15-amd64

Debian 10Up to 4.19.0-16-cloud-amd64

Cloud DistroKernel Version

Amazon Linux v24.14.225-169.362.amzn2.x86_64

Photon 3.04.19.132-6.ph3

Photon 4.05.10.4-16.ph4

### 2.8​

Linux DistroKernel Version

CentOS 7.55.4.12-1.el7.elrepo.x86_64

CentOS 7.8-vanilla3.10.0-1127.el7.x86_64

CentOS 8.2-vanilla4.18.0-240.22.1.el8_3.x86_64

Ubuntu 16.04.7 LTS4.4.0-116-generic

Ubuntu 18.04.5 LTS5.4.0-1040-gcp

Ubuntu 20.04.02 LTS5.4.0-73-generic

Ubuntu 20.105.8.0-1031-gcp

Fedora 27Up to 4.13.9-300.fc27.x86_64

Fedora 28Up to 4.16.3-301.fc28.x86_64

FlatCar Alpha5.10.32-flatcar

FlatCar Beta5.10.32-flatcar

FlatCar Stable5.10.32-flatcar

RHEL 7.63.10.0-1160.25.1.el7.x86_64

RHEL 7.8Up to 3.10.0-1160.25.1.el7.x86_64

RHEL 8.4 BETA4.18.0-293.el8.x86_64

Debian 9Up to 4.9.0-15-amd64

Debian 10Up to 4.19.0-16-cloud-amd64

Cloud DistroKernel Version

Amazon Linux v24.14.225-169.362.amzn2.x86_64

Photon 3.04.19.132-6.ph3

Photon 4.05.10.4-16.ph4

### 2.7​

Linux DistroKernel Version

CentOS 7.55.4.12-1.el7.elrepo.x86_64

CentOS 7.65.7.7-1.el7.elrepo.x86_64, 5.7.12-1.el7.elrepo.x86_64

CentOS 7.8-vanilla3.10.0-1127.el7.x86_64

CentOS 8.2-vanilla4.18.0-193.el8.x86_64

Ubuntu 16.044.15.0-142-generic, 4.15.0-144-generic

Ubuntu 18.04.5 LTS4.15.0-135-generic, 5.4.0-1040-gcp, 5.4.0-1036-azure, 5.3.0-1039-gke, IBM Cloud: 4.15.0-142

Ubuntu 20.04 LTS5.4.0-72-generic

Ubuntu 20.105.8.0-1028-gcp

Fedora 27Up to 4.13.9-300.fc27.x86_64

Fedora 28Up to 5.0.16-100.fc28.x86_64

FlatCar Alpha5.10.25-flatcar

FlatCar Beta5.10.25-flatcar

FlatCar Stable5.10.25-flatcar

RHEL 7.8Up to 3.10.0-1160.24.1.el7.x86_64, IBM Cloud: 3.10.0-1160.24.1.el7

RHEL 8.24.18.0-193.29.1.el8_2.x86_64, 4.18.0-193.el8_2.x86_64

RHEL 8.3 (Ootpa)4.18.0-240.1.1.el8_3.x86_64, 4.18.0-240.15.1.el8_3.x86_64

RHEL 8.4 BETA4.18.0-293.el8.x86_64

Debian 9Up to 4.9.0-14-amd64

Debian 10Up to 4.19.0-16-cloud-amd64

Cloud DistroKernel Version

Amazon Linux v24.14.219-164.354.amzn2.x86_64

### 2.6​

Linux DistroKernel Version

CentOS 7.55.4.12-1.el7.elrepo.x86_64

CentOS 7.8-vanilla3.10.0-1127.el7.x86_64

CentOS 8.2-vanilla4.18.0-240.10.1.el8_3.x86_64

Ubuntu 16.04Up to 4.4.0-116-generic

Ubuntu 20045.4.0-42-generic

Fedora 27Up to 4.13.9-300.fc27.x86_64

Fedora 28Up to 5.0.16-100.fc28.x86_64

RHEL 7.5Up to 3.10.0-1127.el7.x86_64

RHEL 7.6Up to 3.10.0-1127.el7.x86_64

RHEL 7.8Up to 3.10.0-1127.el7.x86_64

RHEL 8.24.18.0-240.10.1.el8_3.x86_64

Debian 9Up to 4.9.0-12-amd64

FlatCar Stable5.4.77-flatcar

FlatCar Beta5.8.18-flatcar

Cloud DistroKernel Version

CoreOS Alpha4.9.123-coreos

CoreOS Beta 2411.1.0 (Rhyolite)4.9.123-coreos

CoreOS Stable 2345.3.0 (Rhyolite)4.9.123-coreos

Amazon Linux v24.14.186-146.268.amzn2.x86_64

### 2.5.3​

Linux DistroKernel Version

Ubuntu 16.04Up to 4.4.0-116-generic #140-Ubuntu

Fedora 27Up to 4.18.18-100.fc27.x86_64

Fedora 28Up to 4.18.10-200.fc28.x86_64

RHEL 7.5Up to 3.10.0-1127.el7.x86_64

RHEL 7.8Up to 3.10.0-1127.el7.x86_64

Debian 9Up to 4.9.0-12-amd64 #1 SMP Debian 4.9.210-1

Cloud DistroKernel Version

CoreOS AlphaUp to 4.19.106-coreos

CoreOS Beta 2411.1.0 (Rhyolite)Up to 4.19.106-coreos

CoreOS Stable 2345.3.0 (Rhyolite)Up to 4.19.106-coreos

RHEL 8.1 (Ootpa)Up to 4.18.0-80.4.2.el8_0.x86_64

Ubuntu19.04Up to 5.0.0-1017-gcp

Ubuntu18.04.4 LTSUp to 5.0.0-1033-gcp

Amazon Linux v2Up to 4.14.77-81.59.amzn2.x86_64

### 2.0.0​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-957.el7.x86_64

UbuntuUp to 4.19.5-041905-generic

### 1.7.2​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-957.el7.x86_64

### 1.7.1.1​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.14.4.el7.x86_64

UbuntuUp to 4.19.1-041901-generic

### 1.7.1​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.14.4.el7.x86_64

UbuntuUp to 4.19.0-041900-generic

### 1.7.0​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.14.4.el7.x86_64

UbuntuUp to 4.19.0-041900-generic

### 1.6.1.4 and 1.6.1.3​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.14.4.el7.x86_64

UbuntuUp to 4.19.0-041900-generic

### 1.6.1.2​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.14.4.el7.x86_64

UbuntuUp to 4.18.16-041816-generic

### 1.6.1.1​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.14.4.el7.x86_64

UbuntuUp to 4.18.12-041812-generic

### 1.6.1​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.14.4.el7.x86_64

UbuntuUp to 4.18.11-041811-generic

### 1.6.0​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.11.6.el7.x86_64

UbuntuUp to 4.18.8-041808-generic

### 1.5.1​

Linux DistroKernel Version

CentOS/RHELUp to 3.10.0-862.11.6.el7.x86_64

UbuntuUp to 4.18.7-041807-generic

In this topic:
