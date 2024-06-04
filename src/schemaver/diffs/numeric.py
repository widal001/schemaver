"""Diff the numeric validation attributes between two schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from schemaver.diffs.base import BaseDiff
from schemaver.lookup import ChangeLevel, NumericField

if TYPE_CHECKING:
    from schemaver.changelog import Changelog
    from schemaver.property import Property


MAX_FIELDS = {NumericField.EXCLUSIVE_MAX.value, NumericField.MAX.value}
MIN_FIELDS = {NumericField.EXCLUSIVE_MIN.value, NumericField.MIN.value}


class NumericValidationDiff(BaseDiff):
    """Record the numeric validation attributes that were added, removed, or changed."""

    FIELD_TYPE = NumericField

    added: set[str]
    removed: set[str]
    changed: set[str]

    def __init__(self, new_schema: Property, old_schema: Property) -> None:
        """Initialize the CoreFieldsDiff."""
        super().__init__(new_schema, old_schema)

    def _record_change_for_existing_attrs(
        self,
        attr: str,
        changelog: Changelog,
    ) -> None:
        """Record change for modifications to existing validation attributes."""
        # get the old and new values
        old_val = self.old_schema.schema[attr]
        new_val = self.new_schema.schema[attr]
        # prepare the changelog message
        message = "Validation attribute '{attr}' was modified on '{loc}' "
        message += f"from {old_val} to {new_val}"
        # set the change level
        value_increased = new_val > old_val
        if attr in MAX_FIELDS and value_increased:
            # raising a maximum is an ADDITION
            level = ChangeLevel.ADDITION
        elif attr in MIN_FIELDS and not value_increased:
            # lowering a MIN is an ADDITION
            level = ChangeLevel.ADDITION
        else:
            level = ChangeLevel.REVISION
        change = self._record_change(attr, message, level)
        changelog.add(change)
