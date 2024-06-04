"""Track schema changes for a given property."""

from __future__ import annotations

from typing import TYPE_CHECKING

from schemaver.diff import AttributeDiff
from schemaver.lookup import (
    CoreField,
    InstanceType,
    SchemaContext,
)

if TYPE_CHECKING:
    from schemaver.changelog import Changelog


class Property:
    """Track schema changes common to all instance types."""

    kind: InstanceType
    schema: dict

    def __init__(
        self,
        schema: dict,
        context: SchemaContext | None = None,
    ) -> None:
        """Initialize the base property."""
        self.kind = InstanceType(schema.get(CoreField.TYPE.value))
        self.schema = schema
        self.context = context or SchemaContext()

    def diff(self, old: Property, changelog: Changelog) -> None:
        """Record the differences between this property and an older version."""
        attr_diff = AttributeDiff(
            old_schema=old.schema,
            new_schema=self.schema,
            prop_type=self.kind,
        )
        attr_diff.populate_changelog(changelog, self.context)
