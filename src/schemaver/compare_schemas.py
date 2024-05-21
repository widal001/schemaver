"""Compare two schemas and list the changes."""

from __future__ import annotations

from dataclasses import dataclass

from schemaver.lookup import (
    METADATA_FIELDS,
    PROP_LOOKUP,
    VALIDATION_FIELDS,
    ChangeLevel,
    DiffType,
    ExtraProps,
    Required,
    ValidationField,
)


@dataclass
class Release:
    """Document the schema changes made when releasing a new SchemaVer."""

    new_version: str
    old_version: str
    kind: ChangeLevel
    changelog: Changelog


@dataclass
class SchemaChange:
    """Characterize an individual change made to a JSON schema."""

    kind: ChangeLevel
    description: str
    depth: int = 0
    location: str = "root"


@dataclass
class Changelog:
    """Record and categorize a list of schema changes."""

    changes: list[SchemaChange]

    @property
    def model_changes(self) -> list[SchemaChange]:
        """Get the model-level changes."""
        return self._filter_changes(ChangeLevel.MODEL)

    @property
    def revisions(self) -> list[SchemaChange]:
        """Get the revision-level changes."""
        return self._filter_changes(ChangeLevel.REVISION)

    @property
    def additions(self) -> list[SchemaChange]:
        """Get the addition-level changes."""
        return self._filter_changes(ChangeLevel.ADDITION)

    def _filter_changes(self, level: ChangeLevel) -> list[SchemaChange]:
        """Filter changelog by level."""
        return [change for change in self.changes if change.kind == level]


@dataclass
class SchemaContext:
    """Context about the current schema."""

    field_name: str = "root"
    curr_depth: int = 0
    required_before: bool = True
    required_now: bool = True


class PropsByStatus:
    """Set of props grouped by required status."""

    def __init__(self, props: set[str], required: set[str]) -> None:
        """Initialize the PropsByStatus class."""
        self.required = props & required  # in both props and required sets
        self.optional = props - required  # in props but not in required


class AttributesByType:
    """Set of attributes grouped by type, e.g. validation, metadata."""

    def __init__(self, attrs: set[str]) -> None:
        """Initialize the AttributeByTypes class."""
        self.validation = attrs & VALIDATION_FIELDS
        self.metadata = attrs & METADATA_FIELDS


@dataclass
class ObjectDiff:
    """List the props added, removed, or changed grouped by required status."""

    added: PropsByStatus
    removed: PropsByStatus
    changed: set[str]


@dataclass
class AttributeDiff:
    """List the attributes that were added, removed, or changed."""

    added: AttributesByType
    removed: AttributesByType
    changed: AttributesByType


def compare_schemas(
    new_schema: dict,
    previous_schema: dict,
    old_version: str,
) -> Release:
    """Compare two schemas and create a release with the correct SchemaVer and Changelog."""
    changelog = Changelog(changes=[])
    root_context = SchemaContext()
    changelog = parse_changes_recursively(
        new_schema=new_schema,
        previous_schema=previous_schema,
        context=root_context,
        changelog=changelog,
    )
    if changelog.model_changes:
        release_kind = ChangeLevel.MODEL
    elif changelog.revisions:
        release_kind = ChangeLevel.REVISION
    else:
        release_kind = ChangeLevel.ADDITION

    return Release(
        new_version="2-0-0",
        old_version=old_version,
        kind=release_kind,
        changelog=changelog,
    )


def record_prop_change(  # noqa: PLR0913
    prop: str,
    context: SchemaContext,
    lookup: dict,
    diff: DiffType,
    required: Required,
    extra_props: ExtraProps,
) -> SchemaChange:
    """Categorize and record a change made to an object's property."""
    message = (
        f"{required.value.title()} property '{prop}' was {diff.value} "
        f"with additional properties {extra_props.value}"
    )
    return SchemaChange(
        kind=lookup[diff][required][extra_props],
        depth=context.curr_depth,
        description=message,
        location=context.field_name + f"['properties']['{prop}]",
    )


def parse_changes_recursively(
    new_schema: dict,
    previous_schema: dict,
    context: SchemaContext,
    changelog: Changelog,
) -> Changelog:
    """Recursively work through each element of the schema and parse changes."""
    # create local variables to simplify accessing validation fields
    props_attr = ValidationField.PROPS.value
    required_attr = ValidationField.REQUIRED.value
    extra_props = ValidationField.EXTRA_PROPS.value
    # diff the schema attributes
    attr_diff = diff_schema_attributes(new_schema, previous_schema)
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
    # diff the properties
    if props_changed or required_changed:
        # extra
        required_now = new_schema.get(required_attr, set())
        required_before = previous_schema.get(required_attr, set())
        object_diff = diff_object_properties(
            new_object=new_schema.get(props_attr, {}),
            old_object=previous_schema.get(props_attr, {}),
            new_required=set(required_now),
            old_required=set(required_before),
        )
        # fmt: off
        extra_props_now = (
            ExtraProps.ALLOWED
            if new_schema.get(extra_props, True)
            else ExtraProps.NOT_ALLOWED
        )
        extra_props_before = (
            ExtraProps.ALLOWED
            if previous_schema.get(extra_props, True)
            else ExtraProps.NOT_ALLOWED
        )
        # fmt: on
        # record changes for added props
        for prop in object_diff.added.required:
            change = record_prop_change(
                prop=prop,
                context=context,
                lookup=PROP_LOOKUP,
                diff=DiffType.ADDED,
                required=Required.YES,
                extra_props=extra_props_before,
            )
            changelog.changes.append(change)
        for prop in object_diff.added.optional:
            change = record_prop_change(
                prop=prop,
                context=context,
                lookup=PROP_LOOKUP,
                diff=DiffType.ADDED,
                required=Required.NO,
                extra_props=extra_props_before,
            )
            changelog.changes.append(change)
        # record changes for removed props
        for prop in object_diff.removed.optional:
            change = record_prop_change(
                prop=prop,
                context=context,
                lookup=PROP_LOOKUP,
                diff=DiffType.REMOVED,
                required=Required.NO,
                extra_props=extra_props_now,
            )
            changelog.changes.append(change)
        for prop in object_diff.removed.required:
            change = record_prop_change(
                prop=prop,
                context=context,
                lookup=PROP_LOOKUP,
                diff=DiffType.REMOVED,
                required=Required.YES,
                extra_props=extra_props_now,
            )
            changelog.changes.append(change)
        # recursively parse changes for props that have changed
        for prop in object_diff.changed:
            context = SchemaContext(
                curr_depth=context.curr_depth + 1,
                field_name=context.field_name + f"['properties']['{prop}']",
                required_now=prop in required_now,
                required_before=prop in required_before,
            )
            return parse_changes_recursively(
                new_schema=new_schema["properties"][prop],
                previous_schema=previous_schema["properties"][prop],
                context=context,
                changelog=changelog,
            )
    return changelog


def diff_schema_attributes(
    new_schema: dict,
    old_schema: dict,
) -> AttributeDiff:
    """Determine which attributes were added, removed, or changed between versions."""
    # Use set math to get attrs that were added or removed
    new_attrs = set(new_schema)
    old_attrs = set(old_schema)
    attrs_added = AttributesByType(new_attrs - old_attrs)
    attrs_removed = AttributesByType(old_attrs - new_attrs)
    # get the attributes that were modified
    changed = set()
    for attr in new_attrs & old_attrs:
        if new_schema[attr] != old_schema[attr]:
            changed.add(attr)
    attrs_changed = AttributesByType(changed)
    return AttributeDiff(
        added=attrs_added,
        removed=attrs_removed,
        changed=attrs_changed,
    )


def diff_object_properties(
    new_object: dict,
    old_object: dict,
    new_required: set,
    old_required: set,
) -> ObjectDiff:
    """Determine which properties were added, removed, or changed between versions."""
    # get the props that were added or removed between versions
    new_props = set(new_object)
    old_props = set(old_object)
    added_props = PropsByStatus(
        props=(new_props - old_props),
        required=set(new_required),
    )
    removed_props = PropsByStatus(
        props=(old_props - new_props),
        required=set(old_required),
    )
    # get the props present in both objects but changed in some way
    changed_props = set()
    for prop in new_props & old_props:
        if new_object[prop] != old_object[prop]:
            changed_props.add(prop)
            continue
        was_required = prop in old_required
        now_required = prop in new_required
        if was_required != now_required:
            changed_props.add(prop)
    # return the diff
    return ObjectDiff(
        added=added_props,
        removed=removed_props,
        changed=changed_props,
    )
