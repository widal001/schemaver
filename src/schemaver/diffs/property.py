"""Diff the properties between two object instance types."""

from __future__ import annotations

from typing import TYPE_CHECKING

from schemaver.changelog import Changelog, SchemaChange
from schemaver.diffs.base import BaseDiff
from schemaver.lookup import PROP_LOOKUP, DiffType, ObjectField, Required

if TYPE_CHECKING:
    from schemaver.property import Property


class PropertyDiff(BaseDiff):
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
        return changelog
