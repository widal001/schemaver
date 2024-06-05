"""Diff the metadata attributes between two schemas."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from schemaver.changelog import ChangeLevel
from schemaver.diffs.base import BaseDiff

if TYPE_CHECKING:
    from schemaver.changelog import Changelog


class MetadataField(Enum):
    """List of supported metadata attributes."""

    TITLE = "title"
    DESCRIPTION = "description"
    DEFAULT = "default"
    DEPRECATED = "deprecated"
    READ_ONLY = "readOnly"
    WRITE_ONLY = "writeOnly"
    EXAMPLES = "examples"


class MetadataDiff(BaseDiff):
    """Record the metadata attributes that were added, removed, or changed."""

    FIELD_TYPE = MetadataField

    def populate_changelog(self, changelog: Changelog) -> Changelog:
        """Use the AttributeDiff to record changes and add them to the changelog."""
        # record changes for METADATA attributes that were ADDED
        level = ChangeLevel.ADDITION
        for attr in self.added:
            message = "Metadata attribute '{attr}' was added to '{loc}'."
            change = self._record_change(attr, message, level)
            changelog.add(change)
        # record changes for METADATA attributes that were REMOVED
        for attr in self.removed:
            message = "Metadata attribute '{attr}' was removed from '{loc}'."
            change = self._record_change(attr, message, level)
            changelog.add(change)
        # record changes for METADATA attributes that were MODIFIED
        for attr in self.changed:
            self._record_change_for_existing_attrs(attr, changelog)
        return changelog

    def _record_change_for_existing_attrs(
        self,
        attr: str,
        changelog: Changelog,
    ) -> None:
        message = "Metadata attribute '{attr}' was modified on '{loc}' "
        message += f"from {self.old_schema.schema[attr]} to {self.new_schema.schema[attr]}"
        change = self._record_change(attr, message, ChangeLevel.ADDITION)
        changelog.add(change)
