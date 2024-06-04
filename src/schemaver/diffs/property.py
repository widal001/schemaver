"""Diff the properties between two object instance types."""

from schemaver.changelog import Changelog, SchemaChange
from schemaver.lookup import PROP_LOOKUP, DiffType, Required, SchemaContext


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
