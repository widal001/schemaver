"""Compare two schemas and list the changes."""

from __future__ import annotations

from schemaver.changelog import Changelog
from schemaver.diff import AttributeDiff, PropertyDiff
from schemaver.lookup import (
    ChangeLevel,
    ExtraProps,
    SchemaContext,
    ValidationField,
)
from schemaver.version import Version


class Release:
    """Document the schema changes made when releasing a new SchemaVer."""

    new_version: Version
    old_version: Version
    new_schema: dict
    old_schema: dict
    kind: ChangeLevel
    changes: Changelog

    def __init__(
        self,
        new_schema: dict,
        old_schema: dict,
        old_version: str,
    ) -> None:
        """Compare two schemas and create a release with the correct SchemaVer and Changelog."""
        self.new_schema = new_schema
        self.old_schema = old_schema
        self.changes = _parse_changes_recursively(
            schema_now=new_schema,
            schema_before=old_schema,
            context=SchemaContext(),
            changelog=Changelog(changes=[]),
        )
        self.kind = self.changes.change_level
        self.old_version = Version(old_version)
        self.new_version = self.old_version.bump(self.kind)


def _parse_changes_recursively(
    schema_now: dict,
    schema_before: dict,
    context: SchemaContext,
    changelog: Changelog,
) -> Changelog:
    """Recursively work through each element of the schema and parse changes."""
    # create local variables to simplify accessing validation fields
    props_attr = ValidationField.PROPS.value
    required_attr = ValidationField.REQUIRED.value
    extra_props = ValidationField.EXTRA_PROPS.value
    # get the attributes that were added, removed, or modified
    # populate the changelog with the differences
    attr_diff = AttributeDiff(schema_now, schema_before)
    changelog = attr_diff.populate_changelog(changelog, context)
    # determine if the properties have changed
    props_changed = (
        props_attr in attr_diff.added.validation
        or props_attr in attr_diff.removed.validation
        or props_attr in attr_diff.changed.validation
    )
    required_changed = (
        required_attr in attr_diff.added.validation
        or required_attr in attr_diff.removed.validation
        or required_attr in attr_diff.changed.validation
    )
    # diff the properties if they've changed
    if props_changed or required_changed:
        # get props that were added, removed, or modified
        required_now = schema_now.get(required_attr, set())
        required_before = schema_before.get(required_attr, set())
        prop_diff = PropertyDiff(
            new_object=schema_now.get(props_attr, {}),
            old_object=schema_before.get(props_attr, {}),
            new_required=set(required_now),
            old_required=set(required_before),
        )
        # fmt: off
        # populate the changelog with the differences
        context.extra_props_now = (
            ExtraProps.ALLOWED
            if schema_now.get(extra_props, True)
            else ExtraProps.NOT_ALLOWED
        )
        context.extra_props_before = (
            ExtraProps.ALLOWED
            if schema_before.get(extra_props, True)
            else ExtraProps.NOT_ALLOWED
        )
        # fmt: on
        changelog = prop_diff.populate_changelog(changelog, context)
        # recursively parse changes for props that have changed
        for prop in prop_diff.changed:
            context = SchemaContext(
                curr_depth=context.curr_depth + 1,
                field_name=context.field_name + f"['properties']['{prop}']",
                required_now=prop in required_now,
                required_before=prop in required_before,
            )
            return _parse_changes_recursively(
                schema_now=schema_now["properties"][prop],
                schema_before=schema_before["properties"][prop],
                context=context,
                changelog=changelog,
            )
    return changelog
