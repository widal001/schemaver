"""Create helper functions for the diffs testing sub-package."""

from copy import deepcopy
from dataclasses import dataclass

from schemaver.changelog import Changelog, ChangeLevel
from schemaver.property import Property


def assert_changes(got: Changelog, wanted: dict[ChangeLevel, int]):
    """Assert that the changelog contains the correct number of changes."""
    # assert we got the total number of changes we wanted
    assert len(got) == sum(wanted.values())
    for level, count in wanted.items():
        assert len(got.filter(level)) == count


@dataclass
class TestSetup:
    """The elements needed to set up a test."""

    old_schema: Property
    new_schema: Property
    changelog: Changelog


def arrange_add_attribute(
    base: dict,
    attr: str,
    value: str | int | list | dict,
) -> TestSetup:
    """Add an attribute to the new schema."""
    # arrange - add validation to the new schema
    old: dict = deepcopy(base)
    new: dict = deepcopy(old)
    new[attr] = value
    # arrange - create properties and changelog
    return TestSetup(
        changelog=Changelog(),
        old_schema=Property(old),
        new_schema=Property(new),
    )


def arrange_remove_attribute(
    base: dict,
    attr: str,
    value: str | int | list | dict,
) -> TestSetup:
    """Remove an attribute from the old schema."""
    # arrange - add validation to the new schema
    new: dict = deepcopy(base)
    old: dict = deepcopy(new)
    old[attr] = value
    # arrange - create properties and changelog
    return TestSetup(
        changelog=Changelog(),
        old_schema=Property(old),
        new_schema=Property(new),
    )


def arrange_change_attribute(
    base: dict,
    attr: str,
    old_val: str | int | list | dict,
    new_val: str | int | list | dict,
) -> TestSetup:
    """Change the value of an attribute in the old schema."""
    # arrange - add validation to the new schema
    old: dict = deepcopy(base)
    new: dict = deepcopy(old)
    old[attr] = old_val
    new[attr] = new_val
    # arrange - create properties and changelog
    return TestSetup(
        changelog=Changelog(),
        old_schema=Property(old),
        new_schema=Property(new),
    )