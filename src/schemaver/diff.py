"""Identify and categorize the differences between schemas."""

from schemaver.changelog import Changelog, SchemaChange
from schemaver.lookup import (
    METADATA_FIELDS,
    PROP_LOOKUP,
    VALIDATION_FIELDS,
    ChangeLevel,
    DiffType,
    Required,
    SchemaContext,
)

# ##############################
# Property diff
# ##############################


class PropsByStatus:
    """Set of props grouped by required status."""

    def __init__(self, props: set[str], required: set[str]) -> None:
        """Initialize the PropsByStatus class."""
        self.required = props & required  # in both props and required sets
        self.optional = props - required  # in props but not in required


class PropertyDiff:
    """List the props added, removed, or changed grouped by required status."""

    added: PropsByStatus
    removed: PropsByStatus
    changed: set[str]

    def __init__(
        self,
        new_object: dict,
        old_object: dict,
        new_required: set,
        old_required: set,
    ) -> None:
        """Initialize the PropertyDiff."""
        # get the props that were added or removed between versions
        new_props = set(new_object)
        old_props = set(old_object)
        self.added = PropsByStatus(
            props=(new_props - old_props),
            required=set(new_required),
        )
        self.removed = PropsByStatus(
            props=(old_props - new_props),
            required=set(old_required),
        )
        # get the props present in both objects but changed in some way
        self.changed = set()
        for prop in new_props & old_props:
            if new_object[prop] != old_object[prop]:
                self.changed.add(prop)
                continue
            was_required = prop in old_required
            now_required = prop in new_required
            if was_required != now_required:
                self.changed.add(prop)

    def populate_changelog(
        self,
        changelog: Changelog,
        context: SchemaContext,
    ) -> Changelog:
        """Use the PropertyDiff to record changes and add them to the changelog."""

        def record_change(
            prop: str,
            diff: DiffType,
            required: Required,
        ) -> None:
            """Categorize and record a change made to an object's property."""
            # set the value for extra props
            if diff == DiffType.ADDED:
                extra_props = context.extra_props_before
            else:
                extra_props = context.extra_props_now
            # set the message
            message = (
                f"{required.value.title()} property '{prop}' was {diff.value} "
                f"with additional properties {extra_props.value}"
            )
            change = SchemaChange(
                kind=PROP_LOOKUP[diff][required][extra_props],
                depth=context.curr_depth,
                description=message,
                attribute=prop,
                location=context.field_name + f"['properties']['{prop}']",
            )
            changelog.add(change)

        # record changes for REQUIRED props that were ADDED
        for prop in self.added.required:
            record_change(prop, DiffType.ADDED, Required.YES)
        # record changes for OPTIONAL props that were ADDED
        for prop in self.added.optional:
            record_change(prop, DiffType.ADDED, Required.NO)
        # record changes for REQUIRED props that were REMOVED
        for prop in self.removed.required:
            record_change(prop, DiffType.REMOVED, Required.YES)
        # record changes for OPTIONAL props that were REMOVED
        for prop in self.removed.optional:
            record_change(prop, DiffType.REMOVED, Required.NO)
        return changelog


# ##############################
# Attribute diff
# ##############################


class AttributesByType:
    """Set of attributes grouped by type, e.g. validation, metadata."""

    def __init__(self, attrs: set[str]) -> None:
        """Initialize the AttributeByTypes class."""
        self.validation = attrs & VALIDATION_FIELDS
        self.metadata = attrs & METADATA_FIELDS


class AttributeDiff:
    """List the attributes that were added, removed, or changed."""

    added: AttributesByType
    removed: AttributesByType
    changed: AttributesByType

    def __init__(
        self,
        new_schema: dict,
        old_schema: dict,
    ) -> None:
        """Initialize the AttributeDiff."""
        # Use set math to get attrs that were added or removed
        new_attrs = set(new_schema)
        old_attrs = set(old_schema)
        self.added = AttributesByType(new_attrs - old_attrs)
        self.removed = AttributesByType(old_attrs - new_attrs)
        # get the attributes that were modified
        changed = set()
        for attr in new_attrs & old_attrs:
            if new_schema[attr] != old_schema[attr]:
                changed.add(attr)
        self.changed = AttributesByType(changed)

    def populate_changelog(
        self,
        changelog: Changelog,
        context: SchemaContext,
    ) -> Changelog:
        """Use the AttributeDiff to record changes and add them to the changelog."""

        def record_change(
            attr: str,
            message: str,
            kind: ChangeLevel,
        ) -> None:
            """Categorize and record a change made to a property's attribute."""
            change = SchemaChange(
                kind=kind,
                description=message,
                attribute=attr,
                location=context.field_name + f"['{attr}']",
                depth=context.curr_depth,
            )
            changelog.add(change)

        # record changes for METADATA attributes that were ADDED
        for attr in self.added.metadata:
            message = f"Metadata attribute '{attr}' was added."
            record_change(attr, message, kind=ChangeLevel.ADDITION)
        # record changes for METADATA attributes that were REMOVED
        for attr in self.removed.metadata:
            message = f"Metadata attribute '{attr}' was removed."
            record_change(attr, message, kind=ChangeLevel.ADDITION)
        # record changes for METADATA attributes that were MODIFIED
        for attr in self.changed.metadata:
            message = f"Metadata attribute '{attr}' was modified."
            record_change(attr, message, kind=ChangeLevel.ADDITION)
        # record changes for VALIDATION attributes that were ADDED
        for attr in self.added.validation:
            message = f"Validation attribute '{attr}' was added."
            record_change(attr, message, kind=ChangeLevel.REVISION)
        # record changes for VALIDATION attributes that were REMOVED
        for attr in self.removed.validation:
            message = f"Validation attribute '{attr}' was removed."
            record_change(attr, message, kind=ChangeLevel.ADDITION)
        return changelog
