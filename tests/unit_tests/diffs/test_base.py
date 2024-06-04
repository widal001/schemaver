"""Testing the Property class with an unspecified instance type."""

from copy import deepcopy
from typing import Any

import pytest

from schemaver.lookup import MetadataField
from schemaver.changelog import Changelog, ChangeLevel
from schemaver.property import Property

BASE_SCHEMA = {"type": "string"}


def assert_changes(got: Changelog, wanted: dict[ChangeLevel, int]):
    """Assert that the changelog contains the correct number of changes."""
    # assert we got the total number of changes we wanted
    assert len(got) == sum(wanted.values())
    for level, count in wanted.items():
        assert len(got.filter(level)) == count


class TestChangingMetadata:
    """Test adding, removing, and modifying metadata."""

    VALIDATION_EXAMPLES = (
        (MetadataField.TITLE.value, "Title"),
        (MetadataField.DESCRIPTION.value, "Description"),
        (MetadataField.DEFAULT.value, "default value"),
        (MetadataField.EXAMPLES.value, ["foo", "bar"]),
        (MetadataField.READ_ONLY.value, True),
        (MetadataField.WRITE_ONLY.value, True),
        (MetadataField.DEPRECATED.value, True),
    )

    @pytest.mark.parametrize(("attr", "value"), VALIDATION_EXAMPLES)
    def test_adding_new_metadata_should_result_in_a_revision(
        self,
        attr: str,
        value: dict | list | str | int,
    ):
        """
        Should result in an ADDITION.

        Removing previous metadata should result in an addition because all
        previously valid inputs will remain valid.
        """
        # arrange - add the validation attribute to the new schema
        old: dict[str, Any] = deepcopy(BASE_SCHEMA)
        new: dict[str, Any] = deepcopy(old)
        new[attr] = value
        # arrange - create properties and changelog
        changelog = Changelog()
        old_prop = Property(old)
        new_prop = Property(new)
        # act
        new_prop.diff(old_prop, changelog)
        # assert
        wanted = {
            ChangeLevel.ADDITION: 1,
            ChangeLevel.REVISION: 0,
            ChangeLevel.MODEL: 0,
        }
        assert_changes(got=changelog, wanted=wanted)

    @pytest.mark.parametrize(("attr", "value"), VALIDATION_EXAMPLES)
    def test_removing_existing_metadata_should_result_in_an_addition(
        self,
        attr: str,
        value: dict | list | str | int,
    ):
        """
        Should result in an ADDITION.

        Removing previous metadata should result in an addition because all
        previously valid inputs will remain valid.
        """
        # arrange - add the validation attribute to the old schema
        new: dict[str, Any] = deepcopy(BASE_SCHEMA)
        old: dict[str, Any] = deepcopy(new)
        old[attr] = value
        # arrange - create properties and changelog
        changelog = Changelog()
        old_prop = Property(old)
        new_prop = Property(new)
        # act
        new_prop.diff(old_prop, changelog)
        # assert
        wanted = {
            ChangeLevel.ADDITION: 1,
            ChangeLevel.REVISION: 0,
            ChangeLevel.MODEL: 0,
        }
        assert_changes(got=changelog, wanted=wanted)

    @pytest.mark.parametrize(
        ("attr", "old_value", "new_value"),
        [
            (MetadataField.TITLE.value, "Title old", "Title new"),
            (MetadataField.DESCRIPTION.value, "Old", "New"),
            (MetadataField.DEFAULT.value, "Old", "New"),
            (MetadataField.EXAMPLES.value, ["foo", "bar"], ["foo"]),
            (MetadataField.READ_ONLY.value, False, True),
            (MetadataField.WRITE_ONLY.value, False, True),
            (MetadataField.DEPRECATED.value, False, True),
        ],
    )
    def test_changing_existing_metadata_should_result_in_an_addition(
        self,
        attr: str,
        old_value: dict | list | str | int,
        new_value: dict | list | str | int,
    ):
        """
        Should result in an ADDITION.

        Changing previous validations should result in an addition because all
        previously valid inputs will remain valid and some inputs that weren't
        previously valid will now be valid against the new schema.
        """
        # arrange
        old: dict[str, Any] = deepcopy(BASE_SCHEMA)
        old[attr] = old_value
        new: dict[str, Any] = deepcopy(old)
        new[attr] = new_value
        # arrange - create properties and changelog
        changelog = Changelog()
        old_prop = Property(old)
        new_prop = Property(new)
        # act
        new_prop.diff(old_prop, changelog)
        # assert
        wanted = {
            ChangeLevel.ADDITION: 1,
            ChangeLevel.REVISION: 0,
            ChangeLevel.MODEL: 0,
        }
        assert_changes(got=changelog, wanted=wanted)
