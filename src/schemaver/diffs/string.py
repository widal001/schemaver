"""Diff the numeric validation attributes between two schemas."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from schemaver.diffs.base import BaseDiff

if TYPE_CHECKING:
    from schemaver.changelog import Changelog


class StringField(Enum):
    """List of validation attributes for strings."""

    # string types
    MAX_LENGTH = "maxLength"
    MIN_LENGTH = "minLength"
    PATTERN = "pattern"


class StringValidationDiff(BaseDiff):
    """Record the numeric validation attributes that were added, removed, or changed."""

    FIELD_TYPE = StringField

    def _record_change_for_existing_attrs(
        self,
        attr: str,
        changelog: Changelog,
    ) -> None:
        """Record change for modifications to existing validation attributes."""
        self._record_max_and_min_changes(
            attr=attr,
            max_fields={StringField.MAX_LENGTH.value},
            min_fields={StringField.MIN_LENGTH.value},
            attr_type="String validation",
            changelog=changelog,
        )
