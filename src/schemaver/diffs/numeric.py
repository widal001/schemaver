"""Diff the numeric validation attributes between two schemas."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from schemaver.diffs.base import BaseDiff

if TYPE_CHECKING:
    from schemaver.changelog import Changelog


class NumericField(Enum):
    """List of validation attributes for integers and numbers."""

    # numeric types
    MAX = "maximum"
    MIN = "minimum"
    EXCLUSIVE_MAX = "exclusiveMaximum"
    EXCLUSIVE_MIN = "exclusiveMinimum"
    MULTIPLE_OF = "multipleOf"


MAX_FIELDS = {NumericField.EXCLUSIVE_MAX.value, NumericField.MAX.value}
MIN_FIELDS = {NumericField.EXCLUSIVE_MIN.value, NumericField.MIN.value}


class NumericValidationDiff(BaseDiff):
    """Record the numeric validation attributes that were added, removed, or changed."""

    FIELD_TYPE = NumericField

    def _record_change_for_existing_attrs(
        self,
        attr: str,
        changelog: Changelog,
    ) -> None:
        """Record change for modifications to existing validation attributes."""
        self._record_max_and_min_changes(
            attr=attr,
            max_fields=MAX_FIELDS,
            min_fields=MIN_FIELDS,
            attr_type="Numeric validation",
            changelog=changelog,
        )
