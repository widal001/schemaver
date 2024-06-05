"""Identify and categorize the differences between schemas."""

from schemaver.changelog import Changelog, SchemaChange
from schemaver.lookup import (
    CORE_FIELDS,
    METADATA_FIELDS,
    PROP_LOOKUP,
    VALIDATION_CHANGE_LOOKUP,
    VALIDATION_FIELDS,
    ArrayField,
    ChangeDirection,
    ChangeLevel,
    DiffType,
    InstanceType,
    NumericField,
    ObjectField,
    Required,
    SchemaContext,
    StringField,
    ValidationType,
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
            # set the value and the message for additional properties
            location = context.location + ".properties"
            if diff == DiffType.ADDED:
                extra_props = context.extra_props_before
                message = (
                    f"{required.value.title()} property '{prop}' was "
                    f"{diff.value} to '{location}' and additional properties "
                    f"were {extra_props.value} in the previous schema."
                )
            else:
                extra_props = context.extra_props_now
                message = (
                    f"{required.value.title()} property '{prop}' was "
                    f"{diff.value} from '{location}' and additional properties "
                    f"are {extra_props.value} in the current schema."
                )
            # set the message
            change = SchemaChange(
                level=PROP_LOOKUP[diff][required][extra_props],
                depth=context.curr_depth,
                description=message,
                attribute=prop,
                location=location,
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

    def __init__(self, attrs: set[str], kind: InstanceType) -> None:
        """Initialize the AttributeByTypes class."""
        validation_fields = VALIDATION_FIELDS[kind] | CORE_FIELDS
        self.validation = attrs & validation_fields
        self.metadata = attrs & METADATA_FIELDS


class AttributeDiff:
    """List the attributes that were added, removed, or changed."""

    new_schema: dict
    old_schema: dict
    added: AttributesByType
    removed: AttributesByType
    changed: AttributesByType

    def __init__(
        self,
        new_schema: dict,
        old_schema: dict,
        prop_type: InstanceType,
    ) -> None:
        """Initialize the AttributeDiff."""
        # save new and old schemas for later access
        self.new_schema = new_schema
        self.old_schema = old_schema
        # Use set math to get attrs that were added or removed
        new_attrs = set(new_schema)
        old_attrs = set(old_schema)
        self.added = AttributesByType(new_attrs - old_attrs, prop_type)
        self.removed = AttributesByType(old_attrs - new_attrs, prop_type)
        # get the attributes that were modified
        changed = set()
        for attr in new_attrs & old_attrs:
            if new_schema[attr] != old_schema[attr]:
                changed.add(attr)
        self.changed = AttributesByType(changed, prop_type)
        self._prop_type = prop_type

    def populate_changelog(
        self,
        changelog: Changelog,
        context: SchemaContext,
    ) -> Changelog:
        """Use the AttributeDiff to record changes and add them to the changelog."""

        def record_change(
            attr: str,
            message: str,
            level: ChangeLevel,
        ) -> None:
            """Categorize and record a change made to a property's attribute."""
            change = SchemaChange(
                level=level,
                description=message.format(attr=attr, loc=context.location),
                attribute=attr,
                location=context.location,
                depth=context.curr_depth,
            )
            changelog.add(change)

        # record changes for METADATA attributes that were ADDED
        for attr in self.added.metadata:
            message = "Metadata attribute '{attr}' was added to '{loc}'."
            record_change(attr, message, level=ChangeLevel.ADDITION)
        # record changes for METADATA attributes that were REMOVED
        for attr in self.removed.metadata:
            message = "Metadata attribute '{attr}' was removed from '{loc}'."
            record_change(attr, message, level=ChangeLevel.ADDITION)
        # record changes for METADATA attributes that were MODIFIED
        for attr in self.changed.metadata:
            message = (
                "Metadata attribute '{attr}' was modified on '{loc}' "
                f"from {self.old_schema[attr]} to {self.new_schema[attr]}"
            )
            record_change(attr, message, level=ChangeLevel.ADDITION)
        # record changes for VALIDATION attributes that were ADDED
        for attr in self.added.validation:
            message = "Validation attribute '{attr}' was added to '{loc}'."
            record_change(attr, message, level=ChangeLevel.REVISION)
        # record changes for VALIDATION attributes that were REMOVED
        for attr in self.removed.validation:
            message = "Validation attribute '{attr}' was removed from '{loc}'."
            record_change(attr, message, level=ChangeLevel.ADDITION)
        for attr in self.changed.validation:
            self._record_validation_change(attr, context, changelog)
        return changelog

    def _record_validation_change(
        self,
        attr: str,
        context: SchemaContext,
        changelog: Changelog,
    ) -> None:
        """Record a change when the schema."""
        old_val = self.old_schema[attr]
        new_val = self.new_schema[attr]
        message = (
            f"Metadata attribute '{attr}' was modified on '{context.location}' "
            f"from {old_val} to {new_val}"
        )
        # Get the attribute type (i.e. MAX, MIN, OTHER)
        match self._prop_type:
            case InstanceType.ARRAY:
                attr_type = ArrayField(attr).kind
            case InstanceType.OBJECT:
                attr_type = ObjectField(attr).kind
            case InstanceType.INTEGER:
                attr_type = NumericField(attr).kind
            case InstanceType.NUMBER:
                attr_type = NumericField(attr).kind
            case InstanceType.STRING:
                attr_type = StringField(attr).kind
            case _:
                attr_type = ValidationType.OTHER
        if attr_type == ValidationType.OTHER:
            return
        # fmt: off
        change_dir = (
            ChangeDirection.UP
            if new_val > old_val
            else ChangeDirection.DOWN
        )
        # fmt: on
        level = VALIDATION_CHANGE_LOOKUP[attr_type][change_dir]
        change = SchemaChange(
            level=level,
            description=message,
            attribute=attr,
            location=context.location,
            depth=context.curr_depth,
        )
        changelog.add(change)
