# Portworx Autopilot Release Notes

Source: https://docs.portworx.com/portworx-enterprise/autopilot-release-notes (Portworx Enterprise latest)

Portworx Autopilot Release Notes | Portworx Enterprise Documentation

## 1.6.0​

October 29, 2026

### New Features​

-
Azure Monitor support for Autopilot
Configure Autopilot's Prometheus provider to query Azure Monitor Managed Prometheus with credentials supplied through Kubernetes Secrets. For more information, see Configure Autopilot to use Azure Monitor.

-
New Parameters to rebalance without trigger
 Autopilot has added support to set rebalance thresholds independent of the trigger. A rule can now trigger on any condition or schedule while independently controlling how sensitive the actual rebalance is using the parameters `poolProvDeviationPerc`, `poolUsageDeviationPerc`, `poolProvPerc` and `poolUsagePerc`. For more information, see Examples in Autopilot use cases for Rebalance action.

### Improvements​

Issue NumberIssue Description

PWX-36651AutopilotRuleObjects now display a descriptive status message when an action is blocked in the `ActiveActionsPending` state. The message identifies which object is currently being processed by another rule and confirms that Autopilot will retry automatically. Previously, this state was silent and provided no visibility into why the action was waiting.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-58855When `spec.autopilot.providers` was configured with two entries of the same `type`, Autopilot silently registered only the first entry, making the second unreachable. Additionally, an `AutopilotRule` referencing a provider name not in the registry retried in a tight loop (13+ attempts in under 10 seconds). `RuleValidationFailed` events and rule status messages were re-written on every polling tick even when the error had not changed.

User Impact: Duplicate provider configurations were accepted without error, making the misconfiguration invisible. Invalid provider name references generated excessive Kubernetes events and log noise. Rule status timestamps incremented on every tick.

Resolution: Autopilot now rejects startup configurations that define two providers of the same type. Invalid provider name errors are reported at the regular 30-second polling cadence. Status and event writes are gated on the error message actually changing.

Affected Versions: AllMinor

PWX-53278When multiple AutopilotRules targeted the same storage pool, the cooldown period was enforced per rule but not across rules. After one rule completed a pool expansion and entered its cooldown, a second rule could immediately schedule another expansion on the same pool.

User Impact: Storage pools could be expanded multiple times in rapid succession when targeted by more than one rule, potentially over-expanding beyond the intended size.

Resolution: Autopilot now enforces a pool-level cooldown across rules. After one rule acts on a pool, other rules targeting the same pool wait until the cooldown expires before scheduling an action, and then retry. Default cooldown period is 5 minutes. AutopilotRule can override this with `spec.actionsCoolDownPeriod` (in seconds). If a rule sets it, that rule uses its own value or 5-minute default.

Affected Versions: 1.5.0Minor

PWX-53277When the Autopilot pod restarted while a pool expansion was in `ActiveActionsInProgress` state, the ARO skipped the `ActiveActionsTaken` state and transitioned directly to `Normal`, even when Portworx had completed the expansion while Autopilot was down.

User Impact: After a pod restart, the expansion completed by Portworx while Autopilot was down had no entry in the ARO history. If the rule's conditions were still met, Autopilot could expand the pool again on the next evaluation cycle. That later expansion was recorded in the ARO, but the earlier one was missing.

Resolution: Autopilot now persists the operation context in the ARO before triggering an action. After restart, it uses the stored context to verify completion status and records the `ActiveActionsTaken` transition correctly.

Affected Versions: 1.3.3Minor

PWX-53078When two AutopilotRules matched the same PVC, the second rule could silently take ownership of the existing ARO and continue its state machine from where the first rule left off. This caused ARO state histories to show transitions attributed to different rules mixed together on the same object.

User Impact: ARO state histories showed incorrect rule names for transitions, making it difficult to audit which rule was responsible for each action.

Resolution: Each ARO now belongs to exactly one rule for its entire lifecycle. When a second rule matches a PVC that is already owned by another rule, the second rule skips that PVC. Only one ARO is created per volume, and the first rule to create it retains it.
Prefer using selectors for PVC rules, instead of blanket AutopilotRules Use label or namespace selectors, or combine conditions with `OR` in a single rule.

Affected Versions: AllMinor

note

This release also addresses security vulnerabilities.

## 1.5.1​

September 22, 2026

This release addresses security vulnerabilities.

## 1.5.0​

April 22, 2026

### New Features​

- Addition of Datadog as a metrics source
Portworx Enterprise has extended Autopilot's monitoring capabilities to include Datadog as a metrics source, in addition to Prometheus. This enables use of Datadog infrastructure for Autopilot rule evaluation. Every Autopilot rule can use either Prometheus or Datadog as the metrics source.
For more information, see Configure Autopilot to enable Datadog with Portworx Autopilot.
 Refer to one of the examples in Automate storage operations with Autopilot and write Autopilot rules with Datadog.

## 1.4.0​

March 10, 2026

### New Features​

-
Support for Time-Based Action Window to trigger AutopilotRule actions
Portworx now supports defining time-based execution windows during which actions can be triggered. If not specified, actions might trigger immediately when conditions are met.
For more information, see Action Window.

-
Support for Dynamic IO Throttle Limits of IOPS and Bandwidth for Portworx volumes
Portworx now allows automatic adjustment of IOPS and bandwidth limits for your volumes based on their size. This removes the need to manually tune throttle limits every time a volume is created or resized.
For more information, see Dynamic App I/O Control with Autopilot.

## 1.3.18​

October 27, 2025

### Improvements​

Issue NumberIssue Description

PWX-47044Added support for the `dontWaitForCleanVolumes` parameter in pool expansion actions to allow `resize-drive` operations even when volumes have only a single replica on the pool. For more information, see AutopilotRule CRD Reference.

note

This release also addresses security vulnerabilities.

## 1.3.17​

May 21, 2025

This release addresses security vulnerabilities.

## 1.3.16​

December 9, 2024

### Improvements​

Issue NumberIssue Description

PWX-38984Added support for `matchExpressions` along with `matchLabels` in Autopilot rules. You can now select the objects using either `matchLabels`, `matchExpressions`, or both selectors.

PWX-34122Updated the CRD schema to adhere to the strict structural schema validations introduced in Kubernetes 1.23 and later. This allows setting `actionCoolDownPeriod` and `pollInterval` without encountering strict decoding errors.

PWX-38947Autopilot now supports `add-drive` and `resize-drive` options for pool expansion. Additionally, the default resize type is changed to `auto`.

PWX-35367Implemented a dedicated scheduler process for moving FSM states, which would decrease the latency of Autopilot operations.

PWX-39812The following changes has been made to reduce the CPU usage of the Prometheus pod:

- Increased the default value of `pollInterval` from 10 seconds to 60 seconds to reduce the CPU usage of the Prometheus pod when scraping a lot of data due to a large number of volumes.

- Optimization to reduce the number of query calls from Autopilot to Prometheus.

### Fixes​

Issue NumberIssue DescriptionSeverity

PWX-39803If the rebalance action is skipped due to an error during the dry run without checking the audit actions, the cluster might be left in an unbalanced state.

User Impact: Affected overall performance and resource distribution across the cluster.

 Resolution: Added checks to ensure that rebalance is not skipped when audit entries are present in the dry run response.

 Affected Versions: AllMinor

PWX-36918Autopilot assumed the default `.svc.cluster.local` DNS domain for the Kubernetes cluster, causing connection failures using different DNS domains.

User Impact: Connection failures were seen when using a DNS domain other than the default domain.

 Resolution: Autopilot now determines the DNS domain Kubernetes uses for its internal services.

 Affected Versions: AllMajor

PWX-35742Autopilot triggered multiple dry run rebalance operations, even if there is a run in progress.

User Impact: Multiple dry run rebalance operations were triggered continuously.

 Resolution: Added checks to ensure that no other rebalance operation is running before triggering a new one.

 Affected Versions: AllMinor

## 1.3.15​

July 25, 2024

### Notes​

- In order to use Portworx with OpenShift version 4.16, you must use Operator version 24.1.1 and Autopilot version 1.3.15.

## 1.3.14​

March 18, 2024

### Improvements​

Improvement NumberImprovement Description

PWX-36274OpenShift users on version 4.12 or newer, can now configure Autopilot to use OpenShift Prometheus deployment for monitoring.

### Fixes​

The following issues have been fixed:

Issue NumberIssue Description

PWX-36160In certain scenarios, Autopilot would generate duplicate `AutopilotRuleObjects` for Storage pools. The pool expansion and re-balance rules would overlap, generating events on a common `AutopilotRuleObjects`. This overlap prevented any of the rules from proceeding and taking action.

Resolution: Autopilot now does not create duplicate `AutopilotRuleObjects` for storage pools.

PWX-36046Prometheus self-signed CA certificate bundle was inadvertently overriding the container's default CA certificates. As a result, while Autopilot could integrate with SSL-enabled Prometheus instances using self-signed SSL certificates, it would fail to work with those using commercially signed SSL certificates.

Resolution: Autopilot is now compatible with both commercial and self-signed SSL-enabled Prometheus endpoints.

### Known issues (Errata)​

Issue NumberIssue Description

PD-2814When attempting to resize a pool or volume using AutopilotRules, users may encounter errors leading to a failed condition check for a rule and see the `connection reset by peer` error message when in the Kubernetes events by running the command `kubectl get events --field-selector involvedObject.kind=AutopilotRule --all-namespaces`. Autopilot may enter a state where it does not retry the operation after encountering this error.

Workaround: Manually restart the Autopilot pod within your Kubernetes environment. This action forces Autopilot to reconnect to the OCP Prometheus endpoints.

## 1.3.13​

February 08, 2024

### Notes​

- In order to use Portworx with OpenShift version 4.14, you must use Operator version 23.10.3 and Autopilot version 1.3.13. The Upgrade to OpenShift 4.14 or newer with Portworx page details the steps for upgrading OpenShift.

- Enabling monitoring on OpenShift version 4.14 will no longer setup a separate Prometheus instance for metrics and Autopilot.

## 1.3.12​

November 30, 2023

### Improvements​

Improvement NumberImprovement Description

PWX-34605Autopilot now appends the rule name as a suffix to newly created AutopilotRuleObjects. As a result, Autopilot can schedule and execute multiple rules for a pool without overriding them.

PWX-33620The time required to resize PVCs in a cluster with a large number of volumes has been considerably reduced.

## 1.3.11​

September 25, 2023

### Improvements​

Improvement NumberImprovement Description

PWX-33668Autopilot now does not treat an offline Prometheus target as a fatal error. It continues to monitor metrics from other Prometheus targets.

### Fixes​

The following issues have been fixed:

Issue NumberIssue Description

PWX-33620With Autopilot, resizing of PVCs took a long time in a cluster with a large number of PVCs.

User impact: Autopilot's Kubernetes API calls were being throttled adding to the delay required for triggering actions.

Resolution: Added controller-runtime caching to Autopilot to reduce the time taken for volume resizing.

## 1.3.10​

August 16, 2023

### Notes​

- This version addresses security vulnerabilities.

## 1.3.9​

August 7, 2023

### Notes​

- This version addresses security vulnerabilities.

## 1.3.8​

May 31, 2023

### Fixes​

The following issues have been fixed:

Issue NumberIssue Description

PWX-31468Autopilot pods kept restarting when deployed on OpenShift with the `fsGroup securityContext` setting.

User impact: Autopilot pods crashed because it used a filesystem watcher to monitor configuration changes and load applications.

Resolution: Autopilot now uses the `sched-ops` API to monitor configuration changes.

## 1.3.7​

February 22, 2023

### Notes​

- This version addresses security vulnerabilities.

## 1.3.6​

February 16, 2023

### Notes​

- This version addresses security vulnerabilities.

## 1.3.5​

January 26, 2023

### Improvements​

Portworx has upgraded or enhanced functionality in the following areas:

Improvement NumberImprovement Description

PWX-28744Miscellaneous improvements.

## 1.3.3​

September 26, 2022

### Fixes​

The following issues have been fixed:

Issue NumberIssue Description

PWX-26135Parameters in AutopilotRule actions were pruned for Kubernetes versions 1.23 and higher.

User impact: Users on Kubernetes 1.23 or greater saw some parameters, such as 'x-kubernetes-preserve-unknown-fields: true', removed when applying a CRD.

Resolution: Autopilot no longer prunes parameters.

## 1.3.2​

December 14, 2021

### Improvements​

Portworx has upgraded or enhanced functionality in the following areas:

Improvement NumberImprovement Description

PD-1047Autopilot 1.3.2 now supports installations that use PX-Security. Follow the instructions in Autopilot to use Autopilot with PX-Security.

## 1.3.1​

November 22, 2021

### Improvements​

Portworx has upgraded or enhanced functionality in the following areas:

Improvement NumberImprovement Description

PD-1035Autopilot 1.3.1 now supports Kubernetes 1.22 and higher

## 1.3.0​

Sep 02, 2020

### Improvements​

Portworx has upgraded or enhanced functionality in the following areas:

Improvement NumberImprovement Description

AUT-113Added support to rebalance Portworx storage pools. Refer to documentation for more details.

AUT-136Added support to users to require approval before actions are taken for a AutopilotRule. Refer to documentation for more details.

AUT-138Added support for `requiredMatches` in the `AutopilotRule` CRD. This allows users to specify number of conditions that are required to match in the rule. See the Automatically rebalance Portworx storage pools use case on example on how this can be used.

AUT-144Added support for Autopilot to create Github Pull Requests to approvals for its actions. This enables users to integrate GitOps workflows with Autopilot. for more details.

AUT-157Make AutopilotRuleObject namespace scoped. Refer to documentation for usage of AutopilotRuleObjects.

AUT-205Improve support bundle collection

### Fixes​

The following issues have been fixed:

Issue NumberIssue Description

AUT-83Autopilot pool expand should never bring Portworx out of quorum

User impact: In certain situations where 2 or more pools have non-intersection volumes, Autopilot can triggered expand on multiple pools at the same time which can bring the PX cluster out of quorum.

Resolution: Autopilot will now perform expansion on only one pool at a given time. Subsequent pools will have their actions in pending state until the previous one is complete.

AUT-87If an action is declined, Autopilot will now perform exponential backoff before retrying it.

User impact: If an action was declined due to the maxsize being hit in the AutopilotRule for a PVC resize, Autopilot used to aggressively retry flooding logs and events.

Resolution: Autopilot will now perform exponential backoff.

AUT-169Autopilot loses track of volume for rule when PX-Backup backs up and restores to same namespace.

User impact: If a user has a PVC that was restored from a backup or pre-provisioned, Autopilot would not be able to track the metrics of the PVC correctly.

Resolution: Autopilot was incorrect assuming the volume name of a PVC by using the PVC UUID. Instead now, it will use the actual volume name from the PVC spec.

AUT-209Fixed an issue where Autopilot incorrectly determines that conditions are not met for an object.

User impact: There are situations where the prometheus API reports empty metrics when it is initializing and it hasn't scraped its targets. If Autopilot queries prometheus during such times, it will find empty metrics and will be misled to consider the conditions as not being met for that object.

Resolution: Autopilot will no longer accept metrics from Prometheus if a Portworx metrics target is not healthy. The Portworx metrics target will become healthy when Prometheus has initialized completely and has been able to perform a successful scrape.

## 1.2.1​

May 30, 2020

### Improvements​

Portworx has upgraded or enhanced functionality in the following areas:

Improvement Description

The PVC resize action no longer requires a Portworx Autopilot Capacity Management license

## 1.2.0​

March 20, 2020

### Improvements​

Portworx has upgraded or enhanced functionality in the following areas:

Improvement Description

Added support for a new parameter, `scalesize`, under the storage pool expand action that allows you to increase storage pool capacity by a fixed amount. See details on all action parameters here.

Added validation for the AutopilotRule CRD

Added an alert event that occurs when Autopilot detects an action that cannot be performed due to license restrictions. See the list of alerts for more information.

## 1.1.0​

February 19, 2020

### Improvements​

Portworx has upgraded or enhanced functionality in the following areas:

Improvement Description

Added a new CRD, called AutopilotRuleObject, which can be used to check for useful events in objects that autopilot monitors, such as PVCs and StoragePools.

Added basic metrics for monitoring Autopilot and Grafana dashboards to view them. To view Autopilot metrics, follow the steps in the Prometheus and Grafana article.

### Fixes​

The following issues have been fixed:

Issue Description

When an Autopilot pod restarted while expanding a storage pool, it sometimes started expanding another storage pool.

User impact: If multiple pools for a volume started expansion together, the volume could go out of quorum.

Resolution: Autopilot pods now correctly wait for previous storage pool expansions to complete when they're restarted.

Deleting Autopilot rules or PVCs sometimes caused the Autopilot pod to crash

User impact: If Autopilot crashed, it could start expanding another storage pool while one was already in being expanded.

Resolution: The Autopilot pod no longer crashes when rules or PVCs are deleted.

## 1.0.0​

November 18, 2019

Introducing Portworx Autopilot! See the Autopilot section of the documentation for more information

In this topic:
