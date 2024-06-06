"""Diff the properties between two object instance types."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from schemaver.changelog import ChangeLevel, Changelog, SchemaChange
from schemaver.diffs.object import ObjectField

if TYPE_CHECKING:
    from schemaver.property import Property


class Required(Enum):
    """Indicate whether a property is required or optional."""

    YES = "required"
    NO = "optional"


class DiffType(Enum):
    """Indicate whether an attribute was added, removed, or modified."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


class ExtraProps(Enum):
    """Indicate whether additionalProps is allowed or not."""

    ALLOWED = "allowed"
    NOT_ALLOWED = "not allowed"
    VALIDATED = "validated"


# Uses the following inputs to determine the appropriate change level
# - Diff type (i.e. property was ADDED vs REMOVED)
# - Required status (i.e. property was/is REQUIRED vs OPTIONAL)
# - Additional props (i.e. additional properties were/are ALLOWED vs BANNED)
PROP_LOOKUP: dict[
    DiffType,
    dict[Required, dict[ExtraProps, ChangeLevel]],
] = {
    # When a property is added to an object
    DiffType.ADDED: {
        # Newly added prop is required
        Required.YES: {
            # additionalProps were previously allowed
            ExtraProps.ALLOWED: ChangeLevel.REVISION,
            # additionalProps were previously banned
            ExtraProps.NOT_ALLOWED: ChangeLevel.MODEL,
        },
        # Newly added prop is optional
        Required.NO: {
            # additionalProps were previously allowed
            ExtraProps.ALLOWED: ChangeLevel.REVISION,
            # additionalProps were previously banned
            ExtraProps.NOT_ALLOWED: ChangeLevel.ADDITION,
        },
    },
    # When a property was removed from an object
    DiffType.REMOVED: {
        # Removed prop was required
        Required.YES: {
            # additionalProps are currently allowed
            ExtraProps.ALLOWED: ChangeLevel.ADDITION,
            # additional props are currently banned
            ExtraProps.NOT_ALLOWED: ChangeLevel.MODEL,
        },
        # Removed prop was optional
        Required.NO: {
            # additionalProps are currently allowed
            ExtraProps.ALLOWED: ChangeLevel.ADDITION,
            # additionalProps are currently banned
            ExtraProps.NOT_ALLOWED: ChangeLevel.REVISION,
        },
    },
}


class PropertyDiff:
    """List the props added, removed, or changed grouped by required status."""

    new_schema: Property
    old_schema: Property
    added: set[str]
    removed: set[str]
    changed: set[str]

    def __init__(self, new_schema: Property, old_schema: Property) -> None:
        """Initialize the PropertyDiff."""
        # save new and old schemas for later access
        self.new_schema = new_schema
        self.old_schema = old_schema
        # get the dictionary of new and old props
        props: str = ObjectField.PROPS.value
        new_obj = new_schema.schema.get(props, {})
        old_obj = old_schema.schema.get(props, {})
        # Use set math to get props that were added or removed
        new_props = set(new_obj)
        old_props = set(old_obj)
        self.added = new_props - old_props
        self.removed = old_props - new_props
        # get the validation attributes that were modified
        self.changed = set()
        for prop in new_props & old_props:
            if new_obj[prop] != old_obj[prop]:
                self.changed.add(prop)
                continue
            was_required = prop in old_schema.required_props
            now_required = prop in new_schema.required_props
            if was_required != now_required:
                self.changed.add(prop)

    def populate_changelog(
        self,
        changelog: Changelog,
    ) -> Changelog:
        """Use the PropertyDiff to record changes and add them to the changelog."""

        def record_change(
            prop: str,
            diff: DiffType,
            required: Required,
        ) -> None:
            """Categorize and record a change made to an object's property."""
            # set the value and the message for added properties
            location = self.new_schema.context.location
            if diff == DiffType.ADDED:
                extra_props = self.old_schema.context.extra_props
                message = (
                    f"{required.value.title()} property '{prop}' was "
                    f"{diff.value} to '{location}' and additional properties "
                    f"were {extra_props.value} in the previous schema."
                )
            # set the value and the message for removed properties
            else:
                extra_props = self.new_schema.context.extra_props
                message = (
                    f"{required.value.title()} property '{prop}' was "
                    f"{diff.value} from '{location}' and additional properties "
                    f"are {extra_props.value} in the current schema."
                )
            # return the change
            change = SchemaChange(
                level=PROP_LOOKUP[diff][required][extra_props],
                depth=self.new_schema.context.curr_depth,
                description=message,
                attribute=prop,
                location=location,
            )
            changelog.add(change)

        # get current and former required props
        required_now = self.new_schema.required_props
        required_before = self.old_schema.required_props

        # record changes for REQUIRED props that were ADDED
        for prop in self.added & required_now:
            record_change(prop, DiffType.ADDED, Required.YES)
        # record changes for OPTIONAL props that were ADDED
        for prop in self.added - required_now:
            record_change(prop, DiffType.ADDED, Required.NO)
        # record changes for REQUIRED props that were REMOVED
        for prop in self.removed & required_before:
            record_change(prop, DiffType.REMOVED, Required.YES)
        # record changes for OPTIONAL props that were REMOVED
        for prop in self.removed - required_before:
            record_change(prop, DiffType.REMOVED, Required.NO)
        # record properties that went from optional to required, or vice versa
        self._record_changes_to_required_status(changelog)
        return changelog

    def _record_changes_to_required_status(
        self,
        changelog: Changelog,
    ) -> None:
        """Log when properties were changed from required to optional."""

        def record_change(message: str, level: ChangeLevel) -> None:
            """Add a change to the changelog."""
            change = SchemaChange(
                level=level,
                description=message,
                attribute=prop,
                depth=context.curr_depth,
                location=context.location,
            )
            changelog.add(change)

        # get current and former required props
        context = self.new_schema.context
        required_now = self.changed & self.new_schema.required_props
        required_before = self.changed & self.old_schema.required_props
        # record REQUIRED to OPTIONAL changes as an ADDITION
        for prop in required_before - required_now:
            message = f"Property {prop} at {context.location}"
            message += "was changed from required to optional."
            record_change(message=message, level=ChangeLevel.ADDITION)
        # record OPTIONAL to REQUIRED changes as a REVISION
        for prop in required_now - required_before:
            message = f"Property {prop} at {context.location}"
            message += "was changed from optional to required."
            record_change(message=message, level=ChangeLevel.REVISION)
