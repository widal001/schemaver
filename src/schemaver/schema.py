"""Track schema changes for a given schema."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from schemaver.diffs.array import ArrayValidationDiff
from schemaver.diffs.core import CoreField, CoreValidationDiff
from schemaver.diffs.metadata import MetadataDiff
from schemaver.diffs.numeric import NumericValidationDiff
from schemaver.diffs.object import ObjectField, ObjectValidationDiff
from schemaver.diffs.property import ExtraProps, PropertyDiff
from schemaver.diffs.string import StringValidationDiff

if TYPE_CHECKING:
    from schemaver.changelog import Changelog
    from schemaver.diffs.base import BaseDiff


class InstanceType(Enum):
    """The instance type for a schema."""

    ARRAY = "array"
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    OBJECT = "object"
    ANY = None


@dataclass
class SchemaContext:
    """Context about the current schema."""

    location: str = "root"
    curr_depth: int = 0
    is_required: bool = True
    extra_props: ExtraProps = ExtraProps.NOT_ALLOWED


class Schema:
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

    def diff(self, old: Schema, changelog: Changelog) -> Changelog:
        """Record the differences between this schema and an older version."""
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
        """Whether or not additional properties are allowed."""
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
        return ExtraProps.RESTRICTED

    def _log_diff(
        self,
        old: Schema,
        changelog: Changelog,
        diff_cls: type[BaseDiff],
    ) -> Changelog:
        """Use the provided diff class to find and record changes."""
        diff = diff_cls(old_schema=old, new_schema=self)
        diff.populate_changelog(changelog)
        return changelog

    def _diff_object(self, old: Schema, changelog: Changelog) -> Changelog:
        """Log the diff between two different objects."""
        # diff the object's validation attributes
        object_diff = ObjectValidationDiff(old_schema=old, new_schema=self)
        object_diff.populate_changelog(changelog)
        if not object_diff.properties_have_changed:
            return changelog
        # update the context then diff the properties
        for schema in [self, old]:
            schema: Schema  # type: ignore[no-redef]
            schema.context.curr_depth += 1
            schema.context.location += ".properties"
            schema.context.extra_props = self.extra_props
        prop_diff = PropertyDiff(old_schema=old, new_schema=self)
        prop_diff.populate_changelog(changelog)
        # if existing properties were changed
        # recursively diff the sub-schema of each property
        for prop in prop_diff.changed:
            new_sub = self._init_sub_schema(self, prop)
            old_sub = self._init_sub_schema(old, prop)
            new_sub.diff(old=old_sub, changelog=changelog)
        return changelog

    @classmethod
    def _init_sub_schema(cls, parent: Schema, prop: str) -> Schema:
        """Init a new sub-schema from a parent schema."""
        context = SchemaContext(
            location=f"{parent.context.location}.{prop}",
            curr_depth=parent.context.curr_depth + 1,
            is_required=prop in parent.required_props,
            extra_props=parent.extra_props,
        )
        return cls(parent.schema["properties"][prop], context)
