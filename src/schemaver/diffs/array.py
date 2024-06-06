"""Diff the numeric validation attributes between two schemas."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from schemaver.diffs.base import BaseDiff

if TYPE_CHECKING:
    from schemaver.changelog import Changelog


class ArrayField(Enum):
    """List of validations attributes for arrays."""

    # array types
    ITEMS = "items"
    MAX_ITEMS = "maxItems"
    MIN_ITEMS = "minItems"
    CONTAINS = "contains"
    UNIQUE_ITEMS = "uniqueItems"
    MAX_CONTAINS = "maxContains"
    MIN_CONTAINS = "minContains"


MAX_FIELDS = {ArrayField.MAX_CONTAINS.value, ArrayField.MAX_ITEMS.value}
MIN_FIELDS = {ArrayField.MIN_CONTAINS.value, ArrayField.MIN_ITEMS.value}


class ArrayValidationDiff(BaseDiff):
    """Record the numeric validation attributes that were added, removed, or changed."""

    FIELD_TYPE = ArrayField

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
            attr_type="Array validation",
            changelog=changelog,
        )
