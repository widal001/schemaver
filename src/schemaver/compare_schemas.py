"""Compare two schemas and list the changes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pprint import pprint

from deepdiff.diff import DeepDiff


class ChangeType(Enum):
    """
    Characterize a change using the SchemaVer hierarchy.

    This hierarchy is modeled after the Major.Minor.Patch hierarchy in SemVer.
    Additional information about each change type be found at:
    https://docs.snowplow.io/docs/pipeline-components-and-applications/iglu/common-architecture/schemaver/
    """

    MODEL = "model"
    REVISION = "revision"
    ADDITION = "addition"
    NONE = "no-change"


class PropDiffType(Enum):
    """What happened to a prop between schemas."""

    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"


class RequiredStatus(Enum):
    """How has the prop's required status changed."""

    ALWAYS_REQUIRED = 1
    ALWAYS_OPTIONAL = 2
    NEWLY_REQUIRED = 3
    NEWLY_OPTIONAL = 4
    WAS_REQUIRED = 5
    WAS_OPTIONAL = 6


class ExtraPropsAllowed(Enum):
    """Does the object support additional props."""

    ALWAYS = 1
    NEVER = 2
    NO_TO_YES = 3
    YES_TO_NO = 4


@dataclass
class Release:
    """Document the schema changes made when releasing a new SchemaVer."""

    new_version: str
    old_version: str
    change_level: ChangeType
    changes: ChangeLog


@dataclass
class ChangeLog:
    """List individual updates made between schema versions."""

    model: list[SchemaChange]
    revision: list[SchemaChange]
    addition: list[SchemaChange]


@dataclass
class SchemaChange:
    """Characterize an individual change made to a JSON schema."""

    kind: ChangeType
    description: str
    location: str = ""


@dataclass
class SchemaContext:
    """Context about the current schema."""

    field_name: str = "root"
    curr_depth: int = 0
    is_required: bool = False
    was_required: bool = False
    additional_props: bool = True


@dataclass
class PropsByStatus:
    """Set of props grouped by required status."""

    required: set[str]
    optional: set[str]


@dataclass
class ObjectDiff:
    """List the props added, removed, or changed grouped by required status."""

    added: PropsByStatus
    removed: PropsByStatus
    changed: set[str]


@dataclass
class MetadataDiff:
    """List the differences in key metadata attributes between schemas."""

    prop_type: bool | None = None
    required_status: bool | None = None
    additional_props: bool | None = None
    other_metadata: set[str] | None = None


def compare_schemas(
    new_schema: dict,
    old_schema: dict,
    old_version: str,
) -> Release:
    """Compare two schemas and create a release with the correct SchemaVer and Changelog."""
    changelog = ChangeLog(
        model=[],
        revision=[],
        addition=[],
    )
    root_context = SchemaContext()
    diff = DeepDiff(old_schema, new_schema)
    pprint(diff)  # noqa: T203
    changelog = parse_schema_recursively(
        new_schema=new_schema,
        old_schema=old_schema,
        context=root_context,
        changelog=changelog,
    )
    return Release(
        new_version="2-0-0",
        old_version=old_version,
        change_level=ChangeType.MODEL,
        changes=changelog,
    )


def parse_schema_recursively(
    new_schema: dict,
    old_schema: dict,
    context: SchemaContext,
    changelog: ChangeLog,
) -> ChangeLog:
    """Parse the schema."""
    new_type = new_schema.get("type")
    old_type = old_schema.get("type")
    if (not new_type) or (not old_type):
        raise ValueError
    if new_type != old_type:
        msg = f"Type was changed from {old_type} to {new_type}"
        change = SchemaChange(
            kind=ChangeType.MODEL,
            description=msg,
            location=context.field_name,
        )
        changelog.model.append(change)
        return changelog
    return changelog


def diff_property_metadata(
    new_prop: dict,
    old_prop: dict,
) -> MetadataDiff:
    """Determine which metadata elements were changed between versions."""
    diff = MetadataDiff()
    # check if types have changed
    new_type = new_prop.pop("type", None)
    old_type = old_prop.pop("type", None)
    diff.prop_type = new_type == old_type
    # check if required status has changed
    return diff


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
    added = new_props - old_props
    removed = old_props - new_props
    added_props = PropsByStatus(
        required=(new_required | added),  # union
        optional=(added - new_required),  # difference
    )
    removed_props = PropsByStatus(
        required=(old_required | removed),  # union
        optional=(removed - old_required),  # difference
    )
    # get the props that were shared by both schemas but changed in some way
    changed_props = set()
    for prop in new_props.union(old_props):
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
