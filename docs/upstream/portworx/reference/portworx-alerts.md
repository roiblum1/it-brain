# Portworx Alerts

Source: https://docs.portworx.com/portworx-enterprise/reference/portworx-alerts (Portworx Enterprise latest)

Portworx Alerts | Portworx Enterprise Documentation

Portworx provides a way to monitor your cluster using alerts. It has a predefined set of alerts which are listed below. The alerts are broadly classified into the following types based on the Resource on which it is raised

- Cluster

- Nodes

- Disks

- Volumes

- Pools

Each alert has a severity from one of the following levels:

- INFO

- WARNING

- ALARM

### List of Alerts​

NameResourceTypeSeverityDescriptionMetric

DriveOperationFailureDRIVEALARMTriggered when a driver operation such as add or replace fails.`px_alerts_driveoperationfailure_total`

DriveOperationSuccessDRIVENOTIFYTriggered when a driver operation such as add or replace succeeds.`px_alerts_driveoperationsuccess_total`

DriveStateChangeDRIVEWARNINGTriggered when there is a change in the driver state viz. Free Disk space goes below the recommended level of 10%.`px_alerts_drivestatechange_total`

DriveStateChangeClearDRIVEWARNINGTriggered when the drive’s state gets cleared.`px_alerts_drivestatechangeclear_total`

CloudDriveCreateWarningDRIVEALARMWarning during cloud drive creation`px_alerts_clouddrivecreatewarning_total`

CloudDriveNotFoundDRIVEWARNINGTriggered when a cloud-drive is not found. Decommission the node if drives are not recoverable.`px_alerts_clouddrivenotfound_total`

CloudDriveDeleteFailureDRIVEALARMTriggered when cloud-drive deletion fails and needs to be deleted manually`px_alerts_clouddrivedeletefailure_total`

SvMotionDatastoreWrongPrefixDRIVEALARMFound cloud drive on a datastore with prefix not matching VSPHERE_DATASTORE_PREFIX`px_alerts_svmotiondatastorewrongprefix_total`

SvMotionDatastoreNoPermissionDRIVEALARMPX cannot update new paths since we do not have access permission to the datastore`px_alerts_svmotiondatastorenopermission_total`

SvMotionMonitoringFailureDRIVEALARMPX had a failure in recognizing vSphere Storage vMotion`px_alerts_svmotionmonitoringfailure_total`

SvMotionMonitoringSuccessDRIVENOTIFYSuccessfully updated ConfigMap with new paths after Storage vMotion`px_alerts_svmotionmonitoringsuccess_total`

VolumeOperationFailureAlarmVOLUMEALARMTriggered when a volume operation fails. Volume operations could be resize, cloudsnap, etc. The alert message will give more info about the specific error case.`px_alerts_volumeoperationfailurealarm_total`

VolumeOperationSuccessVOLUMENOTIFYTriggered when a volume operation such as resize succeeds.`px_alerts_volumeoperationsuccess_total`

VolumeStateChangeVOLUMEWARNINGTriggered when there is a change in the state of the volume.`px_alerts_volumestatechange_total`

IOOperationVOLUMEALARMTriggered when an IO operation such as Block Read/Block Write fails.`px_alerts_iooperation_total`

VolumeOperationFailureWarnVOLUMEWARNINGTriggered when a volume operation fails. Volume operations could be resize, cloudsnap, etc. The alert message will give more info about the specific error case.`px_alerts_volumeoperationfailurewarn_total`

VolumeSpaceLowVOLUMEALARMTriggered when the free space available in a volume goes below a threshold.`px_alerts_volumespacelow_total`

ReplAddVersionMismatchVOLUMEWARNINGTriggered when a volume HA update fails with version mismatch.`px_alerts_repladdversionmismatch_total`

CloudsnapOperationUpdateVOLUMENOTIFYTriggered if a cloudsnap schedule is changed successfully.`px_alerts_cloudsnapoperationupdate_total`

CloudsnapOperationFailureVOLUMEALARMTriggered when a cloudsnap operation fails.`px_alerts_cloudsnapoperationfailure_total`

CloudsnapOperationSuccessVOLUMENOTIFYTriggered when a cloudsnap operation succeeds.`px_alerts_cloudsnapoperationsuccess_total`

VolumeCreateSuccessVOLUMENOTIFYTriggered when a volume is successfully created.`px_alerts_volumecreatesuccess_total`

VolumeCreateFailureVOLUMEALARMTriggered when a volume creation fails.`px_alerts_volumecreatefailure_total`

VolumeDeleteSuccessVOLUMENOTIFYTriggered when a volume is successfully deleted.`px_alerts_volumedeletesuccess_total`

VolumeDeleteFailureVOLUMEALARMTriggered when a volume deletion fails.`px_alerts_volumedeletefailure_total`

VolumeMountSuccessVOLUMENOTIFYTriggered when a volume is successfully mounted at the requested path.`px_alerts_volumemountsuccess_total`

VolumeMountFailureVOLUMEALARMTriggered when a volume cannot be mounted at the requested path.`px_alerts_volumemountfailure_total`

VolumeUnmountSuccessVOLUMENOTIFYTriggered when a volume is successfully unmounted.`px_alerts_volumeunmountsuccess_total`

VolumeUnmountFailureVOLUMEALARMTriggered when a volume cannot be unmounted. The alert message provides more info about the specific error case.`px_alerts_volumeunmountfailure_total`

VolumeHAUpdateSuccessVOLUMENOTIFYTriggered when a volume’s replication factor (HA factor) is successfully updated.`px_alerts_volumehaupdatesuccess_total`

VolumeHAUpdateFailureVOLUMEALARMTriggered when an update to volume’s replication factor (HA factor) fails.`px_alerts_volumehaupdatefailure_total`

SnapshotCreateSuccessVOLUMENOTIFYTriggered when a volume is successfully created.`px_alerts_snapshotcreatesuccess_total`

SnapshotCreateFailureVOLUMEALARMTriggered when a volume snapshot creation fails.`px_alerts_snapshotcreatefailure_total`

SnapshotRestoreSuccessVOLUMENOTIFYTriggered when a snapshot is successfully restored on a volume.`px_alerts_snapshotrestoresuccess_total`

SnapshotRestoreFailureVOLUMEALARMTriggered when the operation of restoring a snapshot fails.`px_alerts_snapshotrestorefailure_total`

SnapshotIntervalUpdateFailureVOLUMEALARMTriggered when an update of the snapshot interval for a volume fails.`px_alerts_snapshotintervalupdatefailure_total`

SnapshotIntervalUpdateSuccessVOLUMENOTIFYTriggered when a snapshot interval of a volume is successfully updated.`px_alerts_snapshotintervalupdatesuccess_total`

VolumeExtentDiffSlowVOLUMEWARNINGVolume extent diff is taking too long.`px_alerts_volumeextentdiffslow_total`

VolumeExtentDiffOkVOLUMEWARNINGVolume extent diff is okay.`px_alerts_volumeextentdiffok_total`

SnapshotDeleteSuccessVOLUMENOTIFYTriggered when a snapshot is successfully deleted.`px_alerts_snapshotdeletesuccess_total`

SnapshotDeleteFailureVOLUMEALARMTriggered when a snapshot delete is successfully deleted.`px_alerts_snapshotdeletefailure_total`

VolumeSpaceLowClearedVOLUMENOTIFYTriggered when the free disk space goes above the recommended level of 10%.`px_alerts_volumespacelowcleared_total`

CloudMigrationUpdateVOLUMENOTIFYTriggered if a cloud migration is updated.`px_alerts_cloudmigrationupdate_total`

CloudMigrationSuccessVOLUMENOTIFYTriggered when a cloud migration operation succeeds.`px_alerts_cloudmigrationsuccess_total`

CloudMigrationFailureVOLUMEALARMTriggered when a cloud migration operation fails.`px_alerts_cloudmigrationfailure_total`

CloudsnapOperationWarningVOLUMEWARNINGTriggered when a cloud snap operation encounters a problem.`px_alerts_cloudsnapoperationwarning_total`

IOOperationWarningVOLUMEWARNINGIO operation warning`px_alerts_iooperationwarning_total`

FilesystemCheckSuccessVOLUMENOTIFYFilesystem-Check fixed filesystem errors in volume`px_alerts_filesystemchecksuccess_total`

FilesystemCheckFailedVOLUMEWARNINGFilesystem-Check failed to fix errors in volume`px_alerts_filesystemcheckfailed_total`

FilesystemCheckFoundErrorsVOLUMEWARNINGFilesystem-Check found errors in the filesystem`px_alerts_filesystemcheckfounderrors_total`

VolumeResizeSuccessfulVOLUMENOTIFYVolume resize operation successful`px_alerts_volumeresizesuccessful_total`

VolumeResizeDeferredVOLUMENOTIFYVolume resize operation deferred to next mount`px_alerts_volumeresizedeferred_total`

VolumeResizeFailedVOLUMEALARMVolume resize operation failed`px_alerts_volumeresizefailed_total`

VolumeAttachFailureVOLUMEALARMTriggered when a volume cannot be attached to the requested node.`px_alerts_volumeattachfailure_total`

VolumeDetachFailureVOLUMEALARMTriggered when a volume cannot be detached from a node.`px_alerts_volumedetachfailure_total`

VolumeRemoteDetachVOLUMENOTIFYTriggered when a volume is detached from a remote node to allow attaching.`px_alerts_volumeremotedetach_total`

VolumeCreateWarningVOLUMEWARNINGTriggered when a volume creation encounters a non-critical problem.`px_alerts_volumecreatewarning_total`

CloudMigrationCanceledVOLUMENOTIFYTriggered when a cloud migration operation is canceled.`px_alerts_cloudmigrationcanceled_total`

SharedV4FailoverNotAvailableVOLUMEWARNINGTriggered when service failover is not available for a sharedv4 volume because it is not HA.`px_alerts_sharedv4failovernotavailable_total`

SharedV4FailoverAvailableVOLUMENOTIFYTriggered when service failover is available for a sharedv4 volume.`px_alerts_sharedv4failoveravailable_total`

VolumeNodiscardMntOptsValidationFailedVOLUMENOTIFYvolume discard/nodiscard mount options not configured correctly`px_alerts_volumenodiscardmntoptsvalidationfailed_total`

VolumeIOThrottleWarningVOLUMEWARNINGvolume max_iops/max_bandwidth options not enforced`px_alerts_volumeiothrottlewarning_total`

VolumeUnhealthyReplicasIncreasedVOLUMEWARNINGTriggered when a the number of unhealthy volume replicas increased.`px_alerts_volumeunhealthyreplicasincreased_total`

VolumeUnhealthyReplicasDecreasedVOLUMENOTIFYTriggered when the number of unhealthy volume replicas decreases.`px_alerts_volumeunhealthyreplicasdecreased_total`

VolumeAutoFstrimFailedVOLUMEALARMAuto fstrim failed.`px_alerts_volumeautofstrimfailed_total`

NodiscardInXFSDisabledVOLUMEALARMNodiscard is disabled for volumes formatted with XFS, please refer to Portworx documentation for details`px_alerts_nodiscardinxfsdisabled_total`

AutoFstrimInXFSDisabledVOLUMEALARMAuto fstrim is disabled for volumes formatted with XFS, please refer to Portworx documentation for details`px_alerts_autofstriminxfsdisabled_total`

AutoFstrimInXFSNotAutoEnabledVOLUMEALARMAuto fstrim is not automatically enabled for volumes formatted with XFS, please refer to Portworx documentation for details`px_alerts_autofstriminxfsnotautoenabled_total`

FADAVolumeDeletePartialFailureVOLUMEWARNINGFailed to delete FlashArray Direct Access volume on FlashArray. Volume needs to be manually cleaned up from FlashArray.`px_alerts_fadavolumedeletepartialfailure_total`

VolumeFastpathStatusActiveVOLUMENOTIFYVolume fastpath status transitions to active.`px_alerts_volumefastpathstatusactive_total`

VolumeFastpathStatusInactiveVOLUMENOTIFYVolume fastpath status transitions to inactive.`px_alerts_volumefastpathstatusinactive_total`

VolumeDeviceExistsVOLUMEALARMTriggered when there is a stale device for a volume that requires cleanup`px_alerts_volumedeviceexists_total`

LegacySharedToSharedv4ServiceMigrationStartedVOLUMENOTIFYTriggered when a legacy shared volume is picked up for migration to type sharedv4 service.`px_alerts_legacysharedtosharedv4servicemigrationstarted_total`

LegacySharedToSharedv4ServiceMigrationSuccessVOLUMENOTIFYTriggered when a legacy shared volume has successfully migrated to type sharedv4 service`px_alerts_legacysharedtosharedv4servicemigrationsuccess_total`

LegacySharedToSharedv4ServiceMigrationPendingVOLUMEWARNINGTriggered when a legacy shared volume hasn't migrated to type sharedv4 service for too long`px_alerts_legacysharedtosharedv4servicemigrationpending_total`

VolGroupOperationFailureCLUSTERALARMTriggered when a volume group operation fails.`px_alerts_volgroupoperationfailure_total`

VolGroupOperationSuccessCLUSTERNOTIFYTriggered when a volume group operation succeeds.`px_alerts_volgroupoperationsuccess_total`

VolGroupStateChangeCLUSTERWARNINGTriggered when a volume group’s state changes.`px_alerts_volgroupstatechange_total`

ContainerOperationFailureCLUSTERALARMContainer operation failed`px_alerts_containeroperationfailure_total`

ContainerOperationSuccessCLUSTERALARMContainer operation succeeded`px_alerts_containeroperationsuccess_total`

ContainerStateChangeCLUSTERALARMContainer state changed`px_alerts_containerstatechange_total`

LicenseExpiringCLUSTERWARNINGWarning triggers 7 days before the installed Portworx Enterprise or Trial license will expire (e.g. “PX-Enterprise license will expire in 6 days, 12:00”). It will also keep triggering after the license has expired (e.g. “Trial license expired 4 days, 06:22 ago”).`px_alerts_licenseexpiring_total`

ClusterPairSuccessCLUSTERNOTIFYTriggered when a cluster pair operation succeeds.`px_alerts_clusterpairsuccess_total`

ClusterPairFailureCLUSTERALARMTriggered when a cluster pair operation fails.`px_alerts_clusterpairfailure_total`

ClusterDomainAddedCLUSTERNOTIFYTriggered when a cluster domain is added.`px_alerts_clusterdomainadded_total`

ClusterDomainRemovedCLUSTERNOTIFYTriggered when a cluster domain is removed.`px_alerts_clusterdomainremoved_total`

ClusterDomainActivatedCLUSTERNOTIFYTriggered when a cluster domain is activated.`px_alerts_clusterdomainactivated_total`

ClusterDomainDeactivatedCLUSTERNOTIFYTriggered when a cluster domain is deactivated.`px_alerts_clusterdomaindeactivated_total`

MeteringAgentWarningCLUSTERWARNINGTriggered when the metering agent encounters a non-critical problem.`px_alerts_meteringagentwarning_total`

MeteringAgentCriticalCLUSTERALARMTriggered when the metering agent encounters a critical problem.`px_alerts_meteringagentcritical_total`

ClusterLicenseUpdatedCLUSTERNOTIFYTriggered when a license is updated for a cluster.`px_alerts_clusterlicenseupdated_total`

LicenseExpiredCLUSTERALARMTriggered when the cluster license expires.`px_alerts_licenseexpired_total`

LicenseLeaseExpiringCLUSTERWARNINGTriggered when the license lease is about to expire since the last lease refresh failed.`px_alerts_licenseleaseexpiring_total`

LicenseLeaseExpiredCLUSTERALARMTriggered when the license lease has expired since the last lease refresh failed.`px_alerts_licenseleaseexpired_total`

RebalanceJobFinishedCLUSTERALARMRebalance job finished execution`px_alerts_rebalancejobfinished_total`

RebalanceJobStartedCLUSTERALARMRebalance job started execution`px_alerts_rebalancejobstarted_total`

RebalanceJobPausedCLUSTERALARMRebalance job paused execution`px_alerts_rebalancejobpaused_total`

RebalanceJobCancelledCLUSTERALARMRebalance job cancelled`px_alerts_rebalancejobcancelled_total`

LicenseNodesOverAllocatedCLUSTERALARMToo many nodes in cluster`px_alerts_licensenodesoverallocated_total`

AutoFstrimDisabledInClusterCLUSTERNOTIFYAuto fstrim is disabled in this cluster`px_alerts_autofstrimdisabledincluster_total`

LicenseExpansionStartedCLUSTERNOTIFYTriggered when the cluster license is expanded.`px_alerts_licenseexpansionstarted_total`

LicenseExpansionEndedCLUSTERNOTIFYTriggered when the cluster license expansion is ended.`px_alerts_licenseexpansionended_total`

BaseAgentRegistrationFailedCLUSTERALARMBase agent failed to register`px_alerts_baseagentregistrationfailed_total`

ScheduledJobSubmissionFailureCLUSTERALARMTriggered when scheduler failed to submit the jobs at the scheduled time`px_alerts_scheduledjobsubmissionfailure_total`

NodeIDInClusterManagerWithoutSpecCLUSTERWARNINGTriggered when a node's entry is found in cluster database but does not have a storage spec associated with it`px_alerts_nodeidinclustermanagerwithoutspec_total`

DefragScheduleCreatedCLUSTERNOTIFYA new defrag schedule is created`px_alerts_defragschedulecreated_total`

DefragScheduleDeletedCLUSTERNOTIFYA defrag schedule is deleted`px_alerts_defragscheduledeleted_total`

DefragScheduleStartedCLUSTERNOTIFYTriggered when a defrag schedule starts a run`px_alerts_defragschedulestarted_total`

DefragScheduleFinishedCLUSTERNOTIFYTriggered when a defrag schedule finishes a run`px_alerts_defragschedulefinished_total`

DefragScheduleJobSubmissionFailureCLUSTERWARNINGTriggered when a defrag schedule failed to submit defrag job.`px_alerts_defragschedulejobsubmissionfailure_total`

NodeStartFailureNODEALARMTriggered when a node in the Portworx cluster fails to start.`px_alerts_nodestartfailure_total`

NodeStartSuccessNODENOTIFYTriggered when a node in the Portworx cluster successfully initializes.`px_alerts_nodestartsuccess_total`

NodeStateChangeNODEALARMNode state changed (i.e. it went down, came online etc.)`px_alerts_nodestatechange_total`

NodeJournalHighUsageNODEALARMTriggered when a node’s timestamp journal usage is not within limits.`px_alerts_nodejournalhighusage_total`

PXInitFailureNODEALARMTriggered when Portworx fails to initialize on a node.`px_alerts_pxinitfailure_total`

PXInitSuccessNODENOTIFYTriggered when Portworx successfully initializes on a node.`px_alerts_pxinitsuccess_total`

PXStateChangeNODEWARNINGTriggered when the Portworx daemon shuts down in error.`px_alerts_pxstatechange_total`

StorageVolumeMountDegradedNODEALARMTriggered when Portworx storage enters degraded mode on a node.`px_alerts_storagevolumemountdegraded_total`

ClusterManagerFailureNODEALARMTriggered when Cluster manager on a Portworx node fails to start. The alert message will give more info about the specific error case.`px_alerts_clustermanagerfailure_total`

KernelDriverFailureNODEALARMTriggered when an incorrect Portworx kernel module is detected. Indicates that Portworx is started with an incorrect version of the kernel module.`px_alerts_kerneldriverfailure_total`

NodeDecommissionSuccessNODENOTIFYTriggered when a node is successfully decommissioned from Portworx cluster.`px_alerts_nodedecommissionsuccess_total`

NodeDecommissionFailureNODEALARMTriggered when a node could not be decommissioned from Portworx cluster.`px_alerts_nodedecommissionfailure_total`

NodeDecommissionPendingNODEWARNINGTriggered when a node decommission is kept in pending state as it has data which is not replicated on other nodes.`px_alerts_nodedecommissionpending_total`

NodeInitFailureNODEALARMTriggered when Portworx fails to initialize on a node.`px_alerts_nodeinitfailure_total`

NodeScanCompletionNODENOTIFYTriggered when node media scan completes without error.`px_alerts_nodescancompletion_total`

CloudsnapScheduleFailureNODEALARMTriggered if a cloudsnap schedule fails to configure.`px_alerts_cloudsnapschedulefailure_total`

NodeMarkedDownNODEWARNINGTriggered when a Portworx node marks another node down as it is unable to connect to it.`px_alerts_nodemarkeddown_total`

PXReadyNODENOTIFYTriggered when Portworx is ready on a node.`px_alerts_pxready_total`

StorageFailureNODEALARMTriggered when the provided storage drives could not be mounted by Portworx.`px_alerts_storagefailure_total`

ObjectstoreFailureNODEALARMTriggered when an object store error is detected.`px_alerts_objectstorefailure_total`

ObjectstoreSuccessNODENOTIFYTriggered upon a successful object store operation.`px_alerts_objectstoresuccess_total`

ObjectstoreStateChangeNODENOTIFYTriggered in response to a state change.`px_alerts_objectstorestatechange_total`

SharedV4SetupFailureNODEWARNINGTriggered when the creation of a sharedv4 volume fails.`px_alerts_sharedv4setupfailure_total`

NodeTimestampFailureNODEALARMNode timestamp journal failure`px_alerts_nodetimestampfailure_total`

NodeJournalFailureNODEALARMNode journal failure`px_alerts_nodejournalfailure_total`

StoragePoolFailureNODEALARMStorage Pool handling encountered an issue`px_alerts_storagepoolfailure_total`

NodeDriverFailureNODEALARMNode Kernel Driver Failure`px_alerts_nodedriverfailure_total`

StoragelessToStorageNodeTransitionFailureNODEALARMTriggered when a node fails to transition from a storageless type to a storage type.`px_alerts_storagelesstostoragenodetransitionfailure_total`

StoragelessToStorageNodeTransitionSuccessNODENOTIFYTriggered when a node transitions from a storageless type to a storage type successfully.`px_alerts_storagelesstostoragenodetransitionsuccess_total`

SecretsAuthFailedNODEWARNINGSecrets setup has failed`px_alerts_secretsauthfailed_total`

LicenseServerDownNODEWARNINGTriggered when a node is unable to reach the license server.`px_alerts_licenseserverdown_total`

FloatingLicenseSetupErrorNODEALARMTriggered when a node fails to setup a floating license.`px_alerts_floatinglicensesetuperror_total`

NFSServerUnhealthyNODEWARNINGTriggered when the NFS server on this node is unhealthy.`px_alerts_nfsserverunhealthy_total`

FileSystemDependencyNODEALARMTriggered during Portworx installation if there’s a filesystem dependency failure.`px_alerts_filesystemdependency_total`

RebootRequiredNODEALARMTriggered when a node requires a reboot.`px_alerts_rebootrequired_total`

TempFileSystemInitializationNODEALARMTriggered during Portworx installation if a node fails to initialize a temporary filesystem.`px_alerts_tempfilesysteminitialization_total`

UnsupportedKernelNODEALARMTriggered during a Portworx installation if the node contains a kernel that is not supported by Portworx.`px_alerts_unsupportedkernel_total`

InvalidDeviceNODEALARMTriggered during Portworx installation if an invalid device is provided to Portworx as a storage device.`px_alerts_invaliddevice_total`

NfsDependencyInstallFailureNODEALARMTriggered during Portworx installation if Portworx cannot install the NFS service.`px_alerts_nfsdependencyinstallfailure_total`

NfsDependencyNotEnabledNODEALARMTriggered during Portworx installation if Portworx cannot enable the NFS service.`px_alerts_nfsdependencynotenabled_total`

LicenseCheckFailedNODEALARMTriggered if a node fails a license check.`px_alerts_licensecheckfailed_total`

PortworxStoppedOnNodeNODEWARNINGTriggered if Portworx is stopped on a node.`px_alerts_portworxstoppedonnode_total`

KvdbConnectionFailedNODEALARMTriggered if Portworx fails to connect to the KVDB.`px_alerts_kvdbconnectionfailed_total`

InternalKvdbSetupFailedNODEALARMTriggered if Portworx fails to setup Internal KVDB on a node.`px_alerts_internalkvdbsetupfailed_total`

PortworxMonitorImagePullFailedNODEALARMTriggered if Portworx fails to pull Portworx images during installation.`px_alerts_portworxmonitorimagepullfailed_total`

PortworxMonitorPrePostExecutionFailedNODEALARMTriggered if Portworx fails to execute pre or post installation tasks.`px_alerts_portworxmonitorprepostexecutionfailed_total`

PortworxMonitorMountValidationFailedNODEALARMTriggered if Portworx fails to validate mounts provided to Portworx container during installation.`px_alerts_portworxmonitormountvalidationfailed_total`

PortworxMonitorSchedulerInitializationFailedNODEALARMTriggered if Portworx fails to initialize connection with scheduler during installation.`px_alerts_portworxmonitorschedulerinitializationfailed_total`

PortworxMonitorServiceControlsInitializationFailedNODEALARMTriggered if Portworx fails to initialize the service controls during installation.`px_alerts_portworxmonitorservicecontrolsinitializationfailed_total`

PortworxMonitorInstallFailedNODEALARMTriggered if Portworx installation fails.`px_alerts_portworxmonitorinstallfailed_total`

MissingInputArgumentNODEALARMTriggered if there’s a missing input install argument.`px_alerts_missinginputargument_total`

PortworxMonitorImagePullInProgressNODENOTIFYTriggered when Portworx is pulling and extracting images during installation or upgrade.`px_alerts_portworxmonitorimagepullinprogress_total`

InvalidArgumentNODEALARMInvalid input argument`px_alerts_invalidargument_total`

PXHostDependencyFailureNODEALARMHost does not meet dependencies for applied px configuration`px_alerts_pxhostdependencyfailure_total`

KvdbConnectionWarningNODEWARNINGkvdb endpoint is not accessible`px_alerts_kvdbconnectionwarning_total`

CallHomeFailureNODEALARMCall home failure`px_alerts_callhomefailure_total`

CloudsnapSettingWarningNODEWARNINGCloudsnap setting Warning`px_alerts_cloudsnapsettingwarning_total`

Sharedv4ServerHighLoadWarnNODEWARNINGSharedV4 server high load detected`px_alerts_sharedv4serverhighloadwarn_total`

NodeAttachmentsCordonedNODENOTIFYVolume attachments are disabled on this node`px_alerts_nodeattachmentscordoned_total`

NodeAttachmentsUncordonedNODENOTIFYVolume attachments are re-enabled on this node`px_alerts_nodeattachmentsuncordoned_total`

DrainAttachmentsJobStartedNODENOTIFYDrainAttachments job started execution`px_alerts_drainattachmentsjobstarted_total`

DrainAttachmentsJobFinishedNODENOTIFYDrainAttachments job finished execution`px_alerts_drainattachmentsjobfinished_total`

DrainAttachmentsJobCancelledNODEALARMDrainAttachments job cancelled`px_alerts_drainattachmentsjobcancelled_total`

CloudDriveTransferJobStartedNODENOTIFYCloudDriveTransfer job started execution`px_alerts_clouddrivetransferjobstarted_total`

CloudDriveTransferJobInProgressNODENOTIFYCloudDriveTransfer job in progress`px_alerts_clouddrivetransferjobinprogress_total`

CloudDriveTransferJobFinishedNODENOTIFYCloudDriveTransfer job finished execution`px_alerts_clouddrivetransferjobfinished_total`

CloudDriveTransferJobCancelledNODEALARMCloudDriveTransfer job cancelled`px_alerts_clouddrivetransferjobcancelled_total`

DrainAttachmentsOperationWarningNODEWARNINGDrainAttachments operation warning`px_alerts_drainattachmentsoperationwarning_total`

NodeUnsecuredNODEALARMTriggered when an unsecure Portworx node tries to join a secured cluster. Indicates that the Portworx node is not configured correctly with the appropriate authentication security settings.`px_alerts_nodeunsecured_total`

DiagCollectJobStartedNODENOTIFYDiagCollect job started execution`px_alerts_diagcollectjobstarted_total`

DiagCollectJobInProgressNODENOTIFYDiagCollect job in progress`px_alerts_diagcollectjobinprogress_total`

DiagCollectJobFinishedNODENOTIFYDiagCollect job finished execution`px_alerts_diagcollectjobfinished_total`

DiagCollectJobCancelledNODEALARMDiagCollect job cancelled`px_alerts_diagcollectjobcancelled_total`

DiagCollectJobFailedNODEALARMDiagCollect job failed`px_alerts_diagcollectjobfailed_total`

FileSystemModuleDependencyNODEALARMTriggered during Portworx installation if there is a filesystem module dependency failure.`px_alerts_filesystemmoduledependency_total`

RelaxedReclaimMaxReachedNODEWARNINGRelaxedReclaim maximum pending limit reached causing inline delete of the volume/snapshot`px_alerts_relaxedreclaimmaxreached_total`

VolumeIOThrottleNotSupportedNODENOTIFYVolume IO Throttling feature not supported in this node due to kernel limitation`px_alerts_volumeiothrottlenotsupported_total`

UnsupportedOperatingSystemNODEWARNINGUbuntu 16.04 will not be supported after the Portworx 2.10 release.`px_alerts_unsupportedoperatingsystem_total`

CCMstatusFailedNODENOTIFYCCM status check failed`px_alerts_ccmstatusfailed_total`

CCMuploadFailedNODENOTIFYUpload to CCM failed`px_alerts_ccmuploadfailed_total`

PXNodePrerequisiteMissingNODEALARMTriggered when Portworx is missing a prerequisite to start`px_alerts_pxnodeprerequisitemissing_total`

MissingRequestsNODEWARNINGMissing requests on peer`px_alerts_missingrequests_total`

ROVolPodBounceNODENOTIFYTriggered when read-write (rw) volume mounts turn read-only (ro) due to errors. Application pods using them will be bounced.`px_alerts_rovolpodbounce_total`

StorageReadyNODENOTIFYTriggered when storage is ready on this node.`px_alerts_storageready_total`

KvdbEndpointsChangedNODENOTIFYTriggered when this node starts using a different set of kvdb endpoints.`px_alerts_kvdbendpointschanged_total`

KvdbMemberReplaceStartedNODENOTIFYTriggered when this node starts replacing another node as an internal kvdb member.`px_alerts_kvdbmemberreplacestarted_total`

KvdbBootstrapEntryAddedNODENOTIFYTriggered when this node adds an entry (usually for this node) to the internal KVDB bootstrap database.`px_alerts_kvdbbootstrapentryadded_total`

KvdbBootstrapEntryRemovedNODENOTIFYTriggered when this node removes an entry (for this or another node) from the internal KVDB bootstrap database.`px_alerts_kvdbbootstrapentryremoved_total`

KvdbMemberAddedNODENOTIFYTriggered when this node adds itself as a member to the internal KVDB cluster.`px_alerts_kvdbmemberadded_total`

KvdbMemberRemovedNODENOTIFYTriggered when this node removes itself or another node from the internal KVDB cluster.`px_alerts_kvdbmemberremoved_total`

UncordonPoolNODENOTIFYPool in Cordon state has been reset to Up`px_alerts_uncordonpool_total`

KubeVirtLiveMigrationStartedNODENOTIFYTriggered when Portworx starts live-migration for a KubeVirt VM.`px_alerts_kubevirtlivemigrationstarted_total`

KubeVirtLiveMigrationStartFailureNODEALARMTriggered when Portworx fails to start live-migration for a KubeVirt VM.`px_alerts_kubevirtlivemigrationstartfailure_total`

KubeVirtLiveMigrationSuccessNODENOTIFYTriggered when Portworx initiated live-migration of a KubeVirt VM finishes successfully.`px_alerts_kubevirtlivemigrationsuccess_total`

KubeVirtLiveMigrationFailureNODEALARMTriggered when Portworx initiated live-migration of a KubeVirt VM has failed.`px_alerts_kubevirtlivemigrationfailure_total`

VolumeCollocateVPSAddFailureNODEALARMTriggered when a placement strategy could not be added during KubeVirt volume creation. Volumes of the same VM may not get collocated.`px_alerts_volumecollocatevpsaddfailure_total`

VolumeCollocateAddingVPSNODENOTIFYTriggered when a placement strategy is added during KubeVirt volume creation in order to collocate volumes of the same VM.`px_alerts_volumecollocateaddingvps_total`

VolumeCollocateJobStalledNODEALARMTriggered when the background job is not able to collocate volumes of a KubeVirt VM. Manual action may be needed.`px_alerts_volumecollocatejobstalled_total`

VolumeCollocateJobAddingVPSNODENOTIFYTriggered when the background job is adding a placement strategy to a KubeVirt volume for collocating it with other volumes of the same VM.`px_alerts_volumecollocatejobaddingvps_total`

VolumeCollocateJobFailedToAddVPSNODEALARMTriggered when the background job could not add a placement strategy to a KubeVirt volume. Volumes of the same VM may not get collocated.`px_alerts_volumecollocatejobfailedtoaddvps_total`

DefragScheduleStartedOnNodeNODENOTIFYTriggered when a defrag schedule starts execution on a node.`px_alerts_defragschedulestartedonnode_total`

DefragScheduleFinishedOnNodeNODENOTIFYTriggered when a defrag schedule finishes execution on a node.`px_alerts_defragschedulefinishedonnode_total`

ArrayLoginFailedNODEALARMTriggered when to login to FlashArray fails`px_alerts_arrayloginfailed_total`

MountpointCleanupFailedNODEALARMTriggered when mountpoint cleaner fails`px_alerts_mountpointcleanupfailed_total`

NodeStartCannotProceedNODEWARNINGTriggered when Portworx startup on a node cannot proceed because a dependency has not been met`px_alerts_nodestartcannotproceed_total`

PoolExpandInProgressPOOLNOTIFYTriggered when a pool expand operation starts.`px_alerts_poolexpandinprogress_total`

PoolExpandSuccessfulPOOLNOTIFYTriggered when a pool expand operation succeeds.`px_alerts_poolexpandsuccessful_total`

PoolExpandFailedPOOLALARMTriggered when a pool expand operation fails.`px_alerts_poolexpandfailed_total`

AutoCordonPoolStartedPOOLNOTIFYAutoCordonPool background task has started`px_alerts_autocordonpoolstarted_total`

AutoCordonPoolSuccessPOOLNOTIFYAutoCordonPool background task has completed`px_alerts_autocordonpoolsuccess_total`

AutoCordonPoolFailedPOOLWARNINGAutoCordonPool background task has failed`px_alerts_autocordonpoolfailed_total`

AutopilotActionFailedAUTOPILOTRULEOBJECTWARNINGTriggered when an Autopilot action for a rule object fails. Alerts on failures in the last 1 hour.`autopilot_action_failed_total{state="failed"}`

AutopilotPrometheusAuthTokenRefreshFailedCLUSTERWARNINGTriggers when Prometheus authentication token refresh failures exceed 2 over 15 minutes.`autopilot_prom_auth_token_refresh_failures_total`

In this topic:
