"""Track schema changes for a given property."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from schemaver.diffs import (
    ArrayValidationDiff,
    BaseDiff,
    CoreValidationDiff,
    MetadataDiff,
    NumericValidationDiff,
    ObjectValidationDiff,
    PropertyDiff,
    StringValidationDiff,
)
from schemaver.lookup import CoreField, ExtraProps, InstanceType, ObjectField

if TYPE_CHECKING:
    from schemaver.changelog import Changelog


@dataclass
class SchemaContext:
    """Context about the current schema."""

    location: str = "root"
    curr_depth: int = 0
    is_required: bool = True
    extra_props: ExtraProps = ExtraProps.NOT_ALLOWED


class Property:
    """Track schema changes common to all instance types."""

    kind: InstanceType
    schema: dict
    context: SchemaContext

    def __init__(
        self,
        schema: dict,
        context: SchemaContext | None = None,
    ) -> None:
        """Initialize the base property."""
        self.kind = InstanceType(schema.get(CoreField.TYPE.value))
        self.schema = schema
        self.context = context or SchemaContext()

    def diff(self, old: Property, changelog: Changelog) -> Changelog:
        """Record the differences between this property and an older version."""
        # Diff the metadata
        metadata_diff = MetadataDiff(old_schema=old, new_schema=self)
        metadata_diff.populate_changelog(changelog)
        # Diff the core validation fields (i.e. type, enum, format)
        self._log_diff(old, changelog, CoreValidationDiff)
        # If the types don't match, stop diffing
        if self.kind != old.kind:
            return changelog
        # Otherwise proceed with type-specific diffing
        match self.kind:
            case InstanceType.NUMBER | InstanceType.INTEGER:
                return self._log_diff(old, changelog, NumericValidationDiff)
            case InstanceType.STRING:
                return self._log_diff(old, changelog, StringValidationDiff)
            case InstanceType.ARRAY:
                return self._log_diff(old, changelog, ArrayValidationDiff)
            case InstanceType.OBJECT:
                return self._diff_object(old, changelog)
        return changelog

    @property
    def required_props(self) -> set[str]:
        """The set of required properties for this schema."""
        # if the instance type is not an object, return an empty set
        # even if there is a 'required' attribute present
        if self.kind != InstanceType.OBJECT:
            return set()
        # otherwise return the value of 'required', or an empty set
        return set(self.schema.get(ObjectField.REQUIRED.value, []))

    @property
    def extra_props(self) -> ExtraProps:
        """The set of required properties for this schema."""
        # if the instance type is not an object
        # return the value of extra_props from the current context
        if self.kind != InstanceType.OBJECT:
            return self.context.extra_props
        # if 'additionalProps' is unset or True, extra props are allowed
        extra_props = self.schema.get(ObjectField.EXTRA_PROPS.value, True)
        if extra_props is True:
            return ExtraProps.ALLOWED
        # if 'additionalProps' is false, extra props are banned
        if extra_props is False:
            return ExtraProps.NOT_ALLOWED
        # if 'additionalProps' is a non-boolean value, extra props are restricted
        return ExtraProps.VALIDATED

    def _log_diff(
        self,
        old: Property,
        changelog: Changelog,
        diff_cls: type[BaseDiff],
    ) -> Changelog:
        """Use the provided diff class to find and record changes."""
        diff = diff_cls(old_schema=old, new_schema=self)
        diff.populate_changelog(changelog)
        return changelog

    def _diff_object(self, old: Property, changelog: Changelog) -> Changelog:
        """Log the diff between two different objects."""
        # diff the object's validation attributes
        object_diff = ObjectValidationDiff(old_schema=old, new_schema=self)
        object_diff.populate_changelog(changelog)
        if not object_diff.properties_have_changed:
            return changelog
        # update the context then diff the properties
        for schema in [self, old]:
            schema: Property  # type: ignore[no-redef]
            schema.context.curr_depth += 1
            schema.context.location += ".properties"
            schema.context.extra_props = self.extra_props
        prop_diff = PropertyDiff(old_schema=old, new_schema=self)
        prop_diff.populate_changelog(changelog)
        return changelog
