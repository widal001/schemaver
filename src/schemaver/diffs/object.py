"""Diff the numeric validation attributes between two schemas."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from schemaver.diffs.base import BaseDiff

if TYPE_CHECKING:
    from schemaver.changelog import Changelog


class ObjectField(Enum):
    """List of validation attributes for objects."""

    # object types
    PROPS = "properties"
    MAX_PROPS = "maxProperties"
    MIN_PROPS = "minProperties"
    EXTRA_PROPS = "additionalProperties"
    DEPENDENT_REQUIRED = "dependentRequired"
    REQUIRED = "required"


class ObjectValidationDiff(BaseDiff):
    """Record the numeric validation attributes that were added, removed, or changed."""

    FIELD_TYPE = ObjectField

    def _record_change_for_existing_attrs(
        self,
        attr: str,
        changelog: Changelog,
    ) -> None:
        """Record change for modifications to existing validation attributes."""
        self._record_max_and_min_changes(
            attr=attr,
            max_fields={ObjectField.MAX_PROPS.value},
            min_fields={ObjectField.MIN_PROPS.value},
            attr_type="Object validation",
            changelog=changelog,
        )

    @property
    def properties_have_changed(self) -> bool:
        """Indicate whether the object's properties have changed."""
        # check if the set of required props have changed
        changed_props = (
            *self.added,
            *self.removed,
            *self.changed,
        )
        required_attr: str = ObjectField.REQUIRED.value
        required_changed = required_attr in changed_props
        # check if any props were added removed or modified
        props_attr: str = ObjectField.PROPS.value
        props_changed = props_attr in changed_props
        return props_changed or required_changed
