# storkctl delete

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/storkctl-reference/delete (Portworx Enterprise latest)

storkctl delete | Portworx Enterprise Documentation

Delete stork resources

Example: `storkctl delete <resource> <flags>`

note

The following commands support a set of global flags that can be used across all `storkctl` commands. For details, see the Global Flags section.

## storkctl delete applicationclones​

Delete applicationclone resources

Aliases: `applicationclone`, `clone`, `clones`

Example: `storkctl delete applicationclone <name>`

## storkctl delete groupsnapshots​

Delete group volume snapshots

Aliases: `groupsnapshot`

Example: `storkctl delete groupsnapshot <name>`

## storkctl delete migrations​

Delete migration resources

Aliases: `migration`

Example: `storkctl delete migration <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--admin-cluster-pair``string`Name of admin clusterpair referenced by the migrations-Optional

`--clusterPair`, `-c``string`Name of the ClusterPair referenced by the migrations-Optional

## storkctl delete migrationschedules​

Delete migration schedules

Aliases: `migrationschedule`

Example: `storkctl delete migrationschedule <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--admin-cluster-pair``string`Name of the Admin ClusterPair referenced by the migrationschedules-Optional

`--clusterPair`, `-c``string`Name of the ClusterPair referenced by the migrationschedules-Optional

## storkctl delete schedulepolicy​

Delete schedule policies

Aliases: `sp`

Example: `storkctl delete schedulepolicy <name>`

## storkctl delete volumesnapshotrestore​

Delete Volume snapshot restore

Aliases: `volumesnapshotrestores`, `snapshotrestore`, `snapshotrestore`, `snaprestore`, `snapsrestores`

Example: `storkctl delete volumesnapshotrestore <name>`

## storkctl delete volumesnapshots​

Delete volume snapshot resources

Aliases: `volumesnapshot`, `snapshots`, `snapshot`, `snap`

Example: `storkctl delete volumesnapshot <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--pvc`, `-p``string`Name of the PVC for which to delete ALL snapshots-Optional

## storkctl delete volumesnapshotschedules​

Delete snapshot schedules

Aliases: `volumesnapshotschedule`, `snapshotschedule`, `snapshotschedules`

Example: `storkctl delete volumesnapshotschedule <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--pvc`, `-p``string`Name of the PVC for which to delete snapshot schedules-Optional

In this topic:
