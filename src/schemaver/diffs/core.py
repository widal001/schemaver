"""Manage the shared attributes and methods for recording diffs between schemas."""

from __future__ import annotations

from enum import Enum

from schemaver.changelog import ChangeLevel, Changelog
from schemaver.diffs.base import BaseDiff


class CoreField(Enum):
    """List of validation attributes supported by all instance types."""

    # all instance types
    TYPE = "type"
    ENUM = "enum"
    FORMAT = "format"


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
        # get the old and new values
        message = self._format_changed_message(attr, "Core validation")
        # fmt: off
        level = (
            ChangeLevel.MODEL
            if attr == CoreField.TYPE.value
            else ChangeLevel.REVISION
        )
        # fmt: on
        change = self._record_change(attr, message, level)
        changelog.add(change)
