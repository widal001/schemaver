"""Diff the numeric validation attributes between two schemas."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from schemaver.changelog import ChangeLevel
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
        # get the old and new values
        old_val = self.old_schema.schema[attr]
        new_val = self.new_schema.schema[attr]
        # prepare the changelog message
        message = "Validation attribute '{attr}' was modified on '{loc}' "
        message += f"from {old_val} to {new_val}"
        # set the change level
        value_increased = new_val > old_val
        min_field: str = StringField.MAX_LENGTH.value
        max_field: str = StringField.MIN_LENGTH.value
        if attr == min_field and value_increased:
            # raising a MAX is an ADDITION
            level = ChangeLevel.ADDITION
        elif attr == max_field and not value_increased:
            # lowering a MIN is an ADDITION
            level = ChangeLevel.ADDITION
        else:
            # everything else is a REVISION
            level = ChangeLevel.REVISION
        change = self._record_change(attr, message, level)
        changelog.add(change)
