"""Manage the shared attributes and methods for recording diffs between schemas."""

from __future__ import annotations

from schemaver.changelog import Changelog, SchemaChange
from schemaver.diffs.base import BaseDiff
from schemaver.lookup import ChangeLevel, CoreField


class CoreValidationDiff(BaseDiff):
    """Record the core validation attributes that were added, removed, or changed."""

    FIELD_TYPE = CoreField

    added: set[str]
    removed: set[str]
    changed: set[str]

    def populate_changelog(self, changelog: Changelog) -> Changelog:
        """Use the AttributeDiff to record changes and add them to the changelog."""
        # record changes for METADATA attributes that were ADDED
        for attr in self.added:
            message = "Validation attribute '{attr}' was added to '{loc}'."
            change = self._record_change(attr, message, ChangeLevel.REVISION)
            changelog.add(change)
        # record changes for METADATA attributes that were REMOVED
        for attr in self.removed:
            message = "Validation attribute '{attr}' was removed from '{loc}'."
            change = self._record_change(attr, message, ChangeLevel.ADDITION)
            changelog.add(change)
        for attr in self.changed:
            self._record_change_for_existing_attrs(attr, changelog)
        return changelog

    def _record_change_for_existing_attrs(
        self,
        attr: str,
        changelog: Changelog,
    ) -> None:
        """Record change for modifications to existing validation attributes."""
        message = "Validation attribute '{attr}' was modified on '{loc}' "
        message += f"from {self.old_schema.schema[attr]} to {self.old_schema.schema[attr]}"
        # fmt: off
        level = (
            ChangeLevel.MODEL
            if attr == CoreField.TYPE.value
            else ChangeLevel.REVISION
        )
        # fmt: on
        change = self._record_change(attr, message, level)
        changelog.add(change)

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
