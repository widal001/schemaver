"""Manage shared methods for diffing two schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from schemaver.changelog import ChangeLevel, Changelog, SchemaChange

if TYPE_CHECKING:
    from enum import Enum

    from schemaver.property import Property


class BaseDiff:
    """Record attributes that were added, removed, or changed."""

    # must be set as a class constant
    FIELD_TYPE: type[Enum]

    # set during init
    added: set[str]
    removed: set[str]
    changed: set[str]

    def __init__(self, new_schema: Property, old_schema: Property) -> None:
        """Initialize the CoreFieldsDiff."""
        # save new and old schemas for later access
        attrs = {option.value for option in self.FIELD_TYPE}
        self.new_schema = new_schema
        self.old_schema = old_schema
        # Use set math to get validation attrs that were added or removed
        new_attrs = set(new_schema.schema) & attrs
        old_attrs = set(old_schema.schema) & attrs
        self.added = new_attrs - old_attrs
        self.removed = old_attrs - new_attrs
        # get the validation attributes that were modified
        changed = set()
        for attr in new_attrs & old_attrs:
            if self.new_schema.schema[attr] != self.old_schema.schema[attr]:
                changed.add(attr)
        self.changed = changed

    def populate_changelog(self, changelog: Changelog) -> Changelog:
        """Use the AttributeDiff to record changes and add them to the changelog."""
        # record changes for attributes that were ADDED
        for attr in self.added:
            message = "Validation attribute '{attr}' was added to '{loc}'."
            change = self._record_change(attr, message, ChangeLevel.REVISION)
            changelog.add(change)
        # record changes for attributes that were REMOVED
        for attr in self.removed:
            message = "Validation attribute '{attr}' was removed from '{loc}'."
            change = self._record_change(attr, message, ChangeLevel.ADDITION)
            changelog.add(change)
        # record changes for the attributes that were MODIFIED
        for attr in self.changed:
            self._record_change_for_existing_attrs(attr, changelog)
        return changelog

    def _record_change_for_existing_attrs(
        self,
        attr: str,
        changelog: Changelog,
    ) -> None:
        """Record change for modifications to existing validation attributes."""
        raise NotImplementedError

    def _record_change(
        self,
        attr: str,
        message: str,
        level: ChangeLevel,
    ) -> SchemaChange:
        """Categorize and record a change made to a property's attribute."""
        context = self.new_schema.context
        return SchemaChange(
            level=level,
            description=message.format(attr=attr, loc=context.location),
            attribute=attr,
            location=context.location,
            depth=context.curr_depth,
        )
