# storkctl get

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/storkctl-reference/get (Portworx Enterprise latest)

storkctl get | Portworx Enterprise Documentation

Get stork resources

Example: `storkctl get <subcommand> <flags>`

note

The following commands support a set of global flags that can be used across all `storkctl` commands. For details, see the Global Flags section.

## storkctl get applicationclones​

Get applicationclone resources

Aliases: `applicationclone`, `clone`, `clones`

Example: `storkctl get applicationclone <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get applicationregistrations​

Get applicationRegistration resources

Aliases: `applicationregistration`, `appreg`, `appregs`

Example: `storkctl get applicationregistration <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get backuplocation​

Get BackupLocations

Aliases: `bl`

Example: `storkctl get backuplocation <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

`--showSecrets`, `-s``bool`Display the secret information from the backupLocations`false`Optional

## storkctl get clusterdomainsstatus​

Get cluster domain statuses

Aliases: `cds`

Example: `storkctl get clusterdomainsstatus <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get clusterdomainupdate​

Get cluster domain updates

Aliases: `cdu`

Example: `storkctl get clusterdomainupdate <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get clusterpair​

Get cluster pair resources

Aliases: `cp`

Example: `storkctl get clusterpair <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get failback​

Get the status of failback actions

Example: `storkctl get failback <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get failover​

Get the status of failover actions

Example: `storkctl get failover <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get groupsnapshots​

Get group volume snapshots

Aliases: `groupsnapshot`

Example: `storkctl get groupsnapshot <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get migrations​

Get migration resources

Aliases: `migration`

Example: `storkctl get migration <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--admin-cluster-pair``string`Name of the admin cluster pair referenced by the migrations-Optional

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

`--clusterpair`, `-c``string`Name of the cluster pair referenced by the migrations-Optional

## storkctl get migrationschedules​

Get migration schedules

Aliases: `migrationschedule`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--admin-cluster-pair``string`Name of admin clusterpair referenced by the migrationschedules-Optional

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

`--clusterpair`, `-c``string`Name of the cluster pair referenced by the migrationschedules-Optional

## storkctl get schedulepolicy​

Get schedule policies

Aliases: `sp`

Example: `storkctl get schedulepolicy <name> <flags>`

## storkctl get volumesnapshotrestore​

Get snapshot restore status

Aliases: `volumesnapshotrestores`, `snapshotrestore`, `snapshotrestore`, `snaprestore`, `snapsrestores`

Example: `storkctl get volumesnapshotrestore <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

## storkctl get volumesnapshots​

Get volume snapshot resources

Aliases: `volumesnapshot`, `snapshots`, `snapshot`, `snap`

Example: `storkctl get volumesnapshot <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

`--pvc`, `-p``string`Name of the PVC for which to list snapshots-Optional

## storkctl get volumesnapshotschedules​

Get volume snapshot schedules

Aliases: `volumesnapshotschedule`, `snapshotschedule`, `snapshotschedules`

Example: `storkctl get volumesnapshotschedule <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--all-namespaces`, `-A``bool`If present, list the requested object(s) across all namespaces.
Namespace in current context is ignored even if specified with --namespace.`false`Optional

`--pvc`, `-p``string`Name of the PVC for which to list snapshot schedules-Optional

In this topic:
