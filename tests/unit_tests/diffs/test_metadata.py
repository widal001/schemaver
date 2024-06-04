"""Test recording the diff in metadata between schemas."""

import pytest

from schemaver.lookup import MetadataField
from schemaver.changelog import ChangeLevel

from tests.unit_tests.diffs.helpers import (
    assert_changes,
    arrange_add_attribute,
    arrange_change_attribute,
    arrange_remove_attribute,
)

BASE_SCHEMA = {"type": "string"}
EXAMPLES = (
    (MetadataField.TITLE.value, "Title"),
    (MetadataField.DESCRIPTION.value, "Description"),
    (MetadataField.DEFAULT.value, "default value"),
    (MetadataField.EXAMPLES.value, ["foo", "bar"]),
    (MetadataField.READ_ONLY.value, True),
    (MetadataField.WRITE_ONLY.value, True),
    (MetadataField.DEPRECATED.value, True),
)


class TestDiffMetadata:
    """Test adding, removing, and modifying metadata."""

    @pytest.mark.parametrize(("attr", "value"), EXAMPLES)
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
        # arrange
        setup = arrange_add_attribute(BASE_SCHEMA, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        wanted = {
            ChangeLevel.ADDITION: 1,
            ChangeLevel.REVISION: 0,
            ChangeLevel.MODEL: 0,
        }
        assert_changes(got=setup.changelog, wanted=wanted)

    @pytest.mark.parametrize(("attr", "value"), EXAMPLES)
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
        # arrange
        setup = arrange_remove_attribute(BASE_SCHEMA, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        wanted = {
            ChangeLevel.ADDITION: 1,
            ChangeLevel.REVISION: 0,
            ChangeLevel.MODEL: 0,
        }
        assert_changes(got=setup.changelog, wanted=wanted)

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
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=attr,
            old_val=old_value,
            new_val=new_value,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        wanted = {
            ChangeLevel.ADDITION: 1,
            ChangeLevel.REVISION: 0,
            ChangeLevel.MODEL: 0,
        }
        assert_changes(got=setup.changelog, wanted=wanted)
