"""Diff the numeric validation attributes between two schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from schemaver.diffs.base import BaseDiff
from schemaver.lookup import ChangeLevel, ObjectField

if TYPE_CHECKING:
    from schemaver.changelog import Changelog
    from schemaver.property import Property


class ObjectValidationDiff(BaseDiff):
    """Record the numeric validation attributes that were added, removed, or changed."""

    FIELD_TYPE = ObjectField

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
        # only proceed if max_props or min_props has changed
        # other differences will be handled by PropertyDiff
        max_field: str = ObjectField.MAX_PROPS.value
        min_field: str = ObjectField.MIN_PROPS.value
        if attr not in (max_field, min_field):
            return
        # get the old and new values
        old_val = self.old_schema.schema[attr]
        new_val = self.new_schema.schema[attr]
        # prepare the changelog message
        message = "Validation attribute '{attr}' was modified on '{loc}' "
        message += f"from {old_val} to {new_val}"
        # set the change level
        value_increased = new_val > old_val
        if attr == max_field and value_increased:
            # raising a maximum is an ADDITION
            level = ChangeLevel.ADDITION
        elif attr == min_field and not value_increased:
            # lowering a MIN is an ADDITION
            level = ChangeLevel.ADDITION
        else:
            level = ChangeLevel.REVISION
        change = self._record_change(attr, message, level)
        changelog.add(change)

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
