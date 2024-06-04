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
    StringValidationDiff,
)
from schemaver.lookup import CoreField, ExtraProps, InstanceType

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
            case InstanceType.NUMBER:
                return self._log_diff(old, changelog, NumericValidationDiff)
            case InstanceType.INTEGER:
                return self._log_diff(old, changelog, NumericValidationDiff)
            case InstanceType.STRING:
                return self._log_diff(old, changelog, StringValidationDiff)
            case InstanceType.ARRAY:
                return self._log_diff(old, changelog, ArrayValidationDiff)
        return changelog

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
