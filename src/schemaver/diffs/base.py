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
        self.new_schema = new_schema
        self.old_schema = old_schema
        # Use set math to get validation attrs that were added or removed
        new_attrs = set(new_schema.schema)
        old_attrs = set(old_schema.schema)
        if getattr(self, "FIELD_TYPE", None):
            attrs = {option.value for option in self.FIELD_TYPE}
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

    def _format_changed_message(self, attr: str, attr_type: str) -> str:
        # get the old and new values
        old_val = self.old_schema.schema[attr]
        new_val = self.new_schema.schema[attr]
        loc = self.new_schema.context.location
        # prepare the changelog message
        message = f"{attr_type} attribute '{attr}' was modified on '{loc}' "
        message += f"from '{old_val}' to '{new_val}'"
        return message

    def _record_max_and_min_changes(  # noqa: PLR0913 # pylint: disable=R0913
        self,
        attr: str,
        max_fields: set[str],
        min_fields: set[str],
        attr_type: str,
        changelog: Changelog,
    ) -> None:
        """Record changes to max and min validation attributes (e.g. maxLength)."""
        # only proceed if attr is one of the max or min fields
        if attr not in (*max_fields, *min_fields):
            return
        # prepare the changelog message
        message = self._format_changed_message(attr, attr_type)
        # get the old and new values
        old_val = self.old_schema.schema[attr]
        new_val = self.new_schema.schema[attr]
        value_increased = new_val > old_val
        # set the change level
        if attr in max_fields and value_increased:
            # raising a maximum is an ADDITION
            level = ChangeLevel.ADDITION
        elif attr in min_fields and not value_increased:
            # lowering a MIN is an ADDITION
            level = ChangeLevel.ADDITION
        else:
            level = ChangeLevel.REVISION
        change = self._record_change(attr, message, level)
        changelog.add(change)
