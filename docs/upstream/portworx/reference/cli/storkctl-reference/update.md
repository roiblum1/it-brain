# storkctl update

Source: https://docs.portworx.com/portworx-enterprise/reference/cli/storkctl-reference/update (Portworx Enterprise latest)

storkctl update | Portworx Enterprise Documentation

Update stork resources

Example: `storkctl update <resource> <flags>`

note

The following commands support a set of global flags that can be used across all `storkctl` commands. For details, see the Global Flags section.

## storkctl update migrationschedules​

Update a running MigrationSchedule by adding/removing primary names

Aliases: `migrationschedule`

Example: `storkctl update migrationschedule <name> --primary-kind=kubevirt.io/v1/VirtualMachine --add-names=vm-newhire`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--add-names``stringSlice`Names to append to the matched entry's IncludeNames. Idempotent.`[]`Optional

`--dry-run``bool`Print the resulting primaryKinds block to stdout without applying.`false`Optional

`--primary-kind``string`Canonical group/version/kind whose PrimaryKindEntry to mutate. Required.-Optional

`--remove-names``stringSlice`Names to remove from the matched entry's IncludeNames. Idempotent.`[]`Optional

## storkctl update volumesnapshotschedules​

Update snapshot schedules

Aliases: `volumesnapshotschedule`, `snapshotschedule`, `snapshotschedules`

Example: `storkctl update volumesnapshotschedule <name> <flags>`

###  Flags

FlagInput typeDescriptionDefaultRequired

`--new-pvc-name``string`Specify the PVC name to be updated in the volumesnapshotschedule-Yes

## storkctl update migrationschedule​

Starting with Stork 26.5.0, you can add or remove VMs on an existing migration schedule that migrates specific VMs, without rewriting the whole schedule.

Aliases: `migrationschedules`, `migrationschedule`

Example: `storkctl update migrationschedule <name> <flags>`

This command works only on migration schedules that have `enforcePrimaryKind` set to `true`. The operation is idempotent. Adding a name that is already present, or removing a name that is not present, has no effect.

To add or remove a VM, run one of the following commands:

```

# Add a VM to the schedule

storkctl update migrationschedule <name> \

--primary-kind=kubevirt.io/v1/VirtualMachine \

--add-names=<vm-name> \

-n <migrationNamespace>

# Remove a VM from the schedule

storkctl update migrationschedule <name> \

--primary-kind=kubevirt.io/v1/VirtualMachine \

--remove-names=<vm-name> \

-n <migrationNamespace>

```

###  Flags

FlagInput typeDescriptionDefaultRequired

`--primary-kind``string`Specify the kind of the primary resource to update, in `group/version/Kind` format. Currently, the only supported value is `kubevirt.io/v1/VirtualMachine`.-Yes

`--add-names``strings`Specify a comma-separated list of object names to add to `includeNames` for the specified primary kind.-No

`--remove-names``strings`Specify a comma-separated list of object names to remove from `includeNames` for the specified primary kind.-No

`--dry-run``boolean`Print the resulting `primaryKinds` block without applying the change.`false`No

In this topic:
