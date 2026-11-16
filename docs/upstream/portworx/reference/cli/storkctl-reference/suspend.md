# storkctl suspend

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/storkctl-reference/suspend (Portworx Enterprise latest)

storkctl suspend | Portworx Enterprise Documentation

Suspend schedules

Example: `storkctl suspend <subcommand> <flags>`

note

The following commands support a set of global flags that can be used across all `storkctl` commands. For details, see the Global Flags section.

## storkctl suspend migrationschedules​

Suspend migration schedules

Aliases: `migrationschedule`

Example: `storkctl suspend migrationschedule <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--admin-cluster-pair``string`Referenced admin clusterpair name to suspend related migration schedules-Optional

`--clusterPair`, `-c``string`Referenced clusterpair name to suspend related migration schedules-Optional

## storkctl suspend volumesnapshotschedules​

Suspend snapshot schedules

Aliases: `volumesnapshotschedule`, `snapshotschedule`, `snapshotschedules`

Example: `storkctl suspend volumesnapshotschedule <name> <flags>`

In this topic:
