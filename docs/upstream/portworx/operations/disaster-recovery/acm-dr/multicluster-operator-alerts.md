# MultiCluster Operator Alerts and Metrics

Source: https://docs.portworx.com/portworx-enterprise/operations/disaster-recovery/acm-dr/multicluster-operator-alerts (Portworx Enterprise latest)

MultiCluster Operator Alerts and Metrics | Portworx Enterprise Documentation

The Portworx MultiCluster Operator on the ACM hub cluster exposes Prometheus metrics and alerts for ACM disaster recovery (DR). The alerts integrate with OpenShift monitoring and notify you when DR readiness degrades, a DR pair becomes unhealthy, a protection group stays in a bad state, or a DR action fails. The alerts are installed by default with the Operator deployment.

This page lists the metrics, the alerts, and the settings that control them. The alerts appear on the Alerting page of the OpenShift web console.

## Prerequisites​

Set `enableUserWorkload: true` field in the cluster monitoring ConfigMap. For more information, refer Enabling monitoring for user-defined projects.

## Metrics​

All metrics are gauges. They are scraped from port `9090` every 30 seconds.

MetricLabelsDescription

`px_dr_pair_ready``drpair`, `source_cluster`, `dest_cluster`, `namespace`Indicates whether the DR pair is healthy. `1` means healthy and `0` means not healthy.

`px_dr_protection_group_protection_status``protection_group`, `drpair`, `namespace`, `status`Current protection state of a ProtectionGroup, such as `Healthy`, `Failed`, `Suspended`, or `Failed Over`. Only the current state is present.

`px_dr_protection_group_migration_status``protection_group`, `drpair`, `namespace`, `status`Result of the last finished migration: `Successful`, `PartialSuccess`, `Failed`, or `Purged`.

`px_dr_protection_group_sync_status``protection_group`, `drpair`, `namespace`, `status`Indicates whether the spoke cluster is still reporting in: `Fresh`, or `Stale` if there has been no update for 10 or more minutes.

`px_dr_action_status``action`, `type`, `status`, `drpair`, `protection_group`, `namespace`Outcome of a Failover or Failback action: `Successful`, `Failed`, `RollbackSuccessful`, or `RollbackFailed`. Present only after the action has finished.

## Alerts​

All alerts have `critical` severity.

AlertForDescription

`PortworxDisasterRecoveryPairNotReady`15mA DR pair has been not ready or non-compliant.

`PortworxDisasterRecoveryUnhealthyProtectionState`15mA ProtectionGroup has been in a `Failed` or `Unknown` protection state.

`PortworxDisasterRecoveryUnhealthyMigrationState`15mThe last migration of a ProtectionGroup failed.

`PortworxDisasterRecoveryClusterCommunicationLost`15mThe hub cluster has lost contact with the spoke cluster.

`PortworxDisasterRecoveryActionFailed`2mA Failover or Failback action failed.

## Configure alerts​

Portworx allows you to turn the alerts on or off that is created in the ACM hub with MultiCluster Operator. In the namespace where MultiCluster Operator is installed, update the `px-multi-cluster-operator-config` ConfigMap with the following field:

```

ALERTING_ENABLED: true

```

## Customize alerts​

You can change the settings of specific alerts using `ALERT_OVERRIDES` without modifying the Operator. By default, the Operator uses the values listed in the Alerts table. If `ALERT_OVERRIDES` is empty or absent, the Operator uses these defaults.

To customize an alert, add the `ALERT_OVERRIDES` field to the `px-multi-cluster-operator-config` ConfigMap in the namespace where the Operator is installed. Use the alert name as the key, and then set one or both of the following fields:

FieldDescription

`for`The duration that the alert condition must hold before the alert fires. Use the Prometheus duration format, for example `5m`, `1h30m`, `7d`, or `2w`. Supported units are `ms`, `s`, `m`, `h`, `d`, `w`, and `y`.

`severity`The severity of the alert. Valid values are `info`, `warning`, and `critical`.

The alert names must match the names in the Alerts table.

The following example changes the `for` duration and severity of the `PortworxDisasterRecoveryPairNotReady` alert, and changes only the severity of the `PortworxDisasterRecoveryUnhealthyProtectionState` alert:

```

ALERT_OVERRIDES: |

  PortworxDisasterRecoveryPairNotReady:

    for: 10m

    severity: warning

  PortworxDisasterRecoveryUnhealthyProtectionState:

    severity: critical

```

If `ALERT_OVERRIDES` contains an invalid value, the Operator logs an error and continues to use the last valid set of rules.

In this topic:
