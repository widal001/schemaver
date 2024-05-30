"""Test the Release class when a schema adds, removes, or modifies property attributes."""

from copy import deepcopy

import pytest

from schemaver.lookup import ChangeLevel, MetadataField, ValidationField
from schemaver.release import Release

from tests.unit_tests.release.helpers import (
    BASE_SCHEMA,
    BASE_VERSION,
    PROP_ANY,
    PROP_ARRAY,
    PROP_INT,
    PROP_OBJECT,
    PROP_STRING,
    assert_release_level,
)


class TestChangingValidation:
    """Test adding, removing, and modifying validations."""

    VALIDATION_EXAMPLES = (
        (PROP_ANY, ValidationField.TYPE.value, "string"),
        (PROP_ANY, ValidationField.ENUM.value, ["foo", "bar"]),
        (PROP_ANY, ValidationField.FORMAT.value, "email"),
        # array types
        (PROP_ARRAY, ValidationField.ITEMS.value, {"type": "string"}),
        (PROP_ARRAY, ValidationField.MAX_ITEMS.value, 10),
        (PROP_ARRAY, ValidationField.MIN_ITEMS.value, 10),
        (PROP_ARRAY, ValidationField.CONTAINS.value, {"type": "string"}),
        (PROP_ARRAY, ValidationField.UNIQUE_ITEMS.value, True),
        (PROP_ARRAY, ValidationField.MAX_CONTAINS.value, 10),
        (PROP_ARRAY, ValidationField.MIN_CONTAINS.value, 10),
        # object types
        (PROP_OBJECT, ValidationField.PROPS.value, {"type": "string"}),
        (PROP_OBJECT, ValidationField.MAX_PROPS.value, 10),
        (PROP_OBJECT, ValidationField.MIN_PROPS.value, 10),
        (PROP_OBJECT, ValidationField.EXTRA_PROPS.value, False),
        (PROP_OBJECT, ValidationField.DEPENDENT_REQUIRED.value, True),
        (PROP_OBJECT, ValidationField.REQUIRED.value, ["foo"]),
        # numeric types
        (PROP_INT, ValidationField.MULTIPLE_OF.value, 10),
        (PROP_INT, ValidationField.MAX.value, 10),
        (PROP_INT, ValidationField.EXCLUSIVE_MAX.value, 10),
        (PROP_INT, ValidationField.MIN.value, 10),
        (PROP_INT, ValidationField.EXCLUSIVE_MIN.value, 10),
        # string types
        (PROP_STRING, ValidationField.MAX_LENGTH.value, 10),
        (PROP_STRING, ValidationField.MIN_LENGTH.value, 10),
        (PROP_STRING, ValidationField.PATTERN.value, "[A-z]+"),
    )

    @pytest.mark.parametrize(("prop", "attr", "value"), VALIDATION_EXAMPLES)
    def test_adding_new_validations_should_result_in_a_revision(
        self,
        prop: str,
        attr: str,
        value: dict | list | str | int,
    ):
        """
        Should result in a REVISION.

        Adding new validation should result in a revision because some previously
        valid JSON inputs will no longer be valid against the new schema.
        """
        # arrange - add the validation attribute to the new schema
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        new["properties"][prop][attr] = value
        # act
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=ChangeLevel.REVISION)

    @pytest.mark.parametrize(("prop", "attr", "value"), VALIDATION_EXAMPLES)
    def test_removing_existing_validations_should_result_in_an_addition(
        self,
        prop: str,
        attr: str,
        value: dict | list | str | int,
    ):
        """
        Should result in an ADDITION.

        Removing previous validations should result in an addition because all
        previously valid inputs will remain valid and some inputs that weren't
        previously valid will now be valid against the new schema.
        """
        # arrange - add the validation attribute to the old schema
        new = deepcopy(BASE_SCHEMA)
        old = deepcopy(new)
        old["properties"][prop][attr] = value
        # act
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=ChangeLevel.ADDITION)


class TestChangingMetadata:
    """Test adding, removing, and modifying metadata."""

    VALIDATION_EXAMPLES = (
        (PROP_ANY, MetadataField.TITLE.value, "Title"),
        (PROP_ANY, MetadataField.DESCRIPTION.value, "Description"),
        (PROP_ANY, MetadataField.DEFAULT.value, "default value"),
        (PROP_ANY, MetadataField.EXAMPLES.value, ["foo", "bar"]),
        (PROP_ANY, MetadataField.READ_ONLY.value, True),
        (PROP_ANY, MetadataField.WRITE_ONLY.value, True),
        (PROP_ANY, MetadataField.DEPRECATED.value, True),
    )

    @pytest.mark.parametrize(("prop", "attr", "value"), VALIDATION_EXAMPLES)
    def test_adding_new_metadata_should_result_in_a_revision(
        self,
        prop: str,
        attr: str,
        value: dict | list | str | int,
    ):
        """
        Should result in an ADDITION.

        Removing previous metadata should result in an addition because all
        previously valid inputs will remain valid.
        """
        # arrange - add the validation attribute to the new schema
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        new["properties"][prop][attr] = value
        # act
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=ChangeLevel.ADDITION)

    @pytest.mark.parametrize(("prop", "attr", "value"), VALIDATION_EXAMPLES)
    def test_removing_existing_metadata_should_result_in_an_addition(
        self,
        prop: str,
        attr: str,
        value: dict | list | str | int,
    ):
        """
        Should result in an ADDITION.

        Removing previous metadata should result in an addition because all
        previously valid inputs will remain valid.
        """
        # arrange - add the validation attribute to the old schema
        new = deepcopy(BASE_SCHEMA)
        old = deepcopy(new)
        old["properties"][prop][attr] = value
        # act
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=ChangeLevel.ADDITION)

    @pytest.mark.parametrize(
        ("prop", "attr", "old_value", "new_value"),
        [
            (PROP_ANY, MetadataField.TITLE.value, "Title old", "Title new"),
            (PROP_ANY, MetadataField.DESCRIPTION.value, "Old", "New"),
            (PROP_ANY, MetadataField.DEFAULT.value, "Old", "New"),
            (PROP_ANY, MetadataField.EXAMPLES.value, ["foo", "bar"], ["foo"]),
            (PROP_ANY, MetadataField.READ_ONLY.value, False, True),
            (PROP_ANY, MetadataField.WRITE_ONLY.value, False, True),
            (PROP_ANY, MetadataField.DEPRECATED.value, False, True),
        ],
    )
    def test_changing_existing_metadata_should_result_in_an_addition(
        self,
        prop: str,
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
        old = deepcopy(BASE_SCHEMA)
        old["properties"][prop][attr] = old_value
        new = deepcopy(old)
        new["properties"][prop][attr] = new_value
        # act
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=ChangeLevel.ADDITION)
