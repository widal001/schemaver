"""Test the code in the compare_schemas module."""

from copy import deepcopy

import pytest

from schemaver.compare_schemas import ChangeLevel, Release, compare_schemas
from schemaver.lookup import MetadataField, ValidationField

# default props
PROP_INT = "productId"
PROP_STRING = "productName"
PROP_ENUM = "productType"
PROP_ARRAY = "tags"
PROP_OBJECT = "nestedObject"
PROP_ANY = "anyField"
# base version and schema
BASE_VERSION = "1-0-0"
BASE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/product.schema.json",
    "title": "Product",
    "description": "A product in the catalog",
    "type": "object",
    "properties": {
        PROP_INT: {"type": "integer"},
        PROP_STRING: {"type": "string"},
        PROP_ENUM: {"type": "string", "enum": ["foo", "bar"]},
        PROP_ARRAY: {"type": "array"},
        PROP_OBJECT: {"type": "object"},
        PROP_ANY: {},
    },
    "required": [PROP_INT, PROP_STRING],
    "additionalProperties": False,
}


def assert_release_kind(got: Release, wanted: ChangeLevel):
    """Confirm the release matches expectations."""
    assert got.kind == wanted
    assert len(getattr(got.changelog, wanted.value)) > 0
    for level in ChangeLevel:
        if level not in (wanted, ChangeLevel.NONE):
            assert not getattr(got.changelog, level.value)


class TestAddingProp:
    """Test result when adding a prop to the new schema."""

    def test_add_optional_prop_with_extra_props_banned(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    ADDED
        - Prop status:  OPTIONAL
        - Extra props:  BANNED in old schema
        - Release type: ADDITION
        """
        # arrange
        old = BASE_SCHEMA
        new = deepcopy(old)
        new["properties"]["cost"] = {"type": "number"}
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)

    def test_add_optional_prop_with_extra_props_allowed_implicitly(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    ADDED
        - Prop status:  OPTIONAL
        - Extra props:  ALLOWED (implicit) in old schema
        - Release type: REVISION
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        del old["additionalProperties"]
        new = deepcopy(old)
        new["properties"]["cost"] = {"type": "number"}
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.REVISION)

    def test_add_optional_prop_with_extra_props_allowed_explicitly(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    ADDED
        - Prop status:  OPTIONAL
        - Extra props:  ALLOWED (explicit) in old schema
        - Release type: REVISION
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        old["additionalProperties"] = True
        new = deepcopy(old)
        new["properties"]["cost"] = {"type": "number"}
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.REVISION)

    def test_add_required_prop_with_extra_props_banned(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    ADDED
        - Prop status:  OPTIONAL
        - Extra props:  BANNED in old schema
        - Release type: MODEL
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        new["properties"]["cost"] = {"type": "number"}
        new["required"].append("cost")
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.MODEL)

    def test_add_required_prop_with_extra_props_allowed_implicitly(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    ADDED
        - Prop status:  REQUIRED
        - Extra props:  ALLOWED (implicitly) in old schema
        - Release type: REVISION
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        del old["additionalProperties"]
        new = deepcopy(old)
        new["properties"]["cost"] = {"type": "number"}
        new["required"].append("cost")
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.REVISION)

    def test_add_required_prop_with_extra_props_allowed_explicitly(self):
        """
        Should result in a new REVISION.

        Scenario:
        - Prop diff:    ADDED
        - Prop status:  REQUIRED
        - Extra props:  ALLOWED (explicitly) in old schema
        - Release type: REVISION
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        old["additionalProperties"] = True
        new = deepcopy(old)
        new["properties"]["cost"] = {"type": "number"}
        new["required"].append("cost")
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.REVISION)

    def test_add_prop_to_nested_object(self):
        """Nested props should be accessed through recursion."""
        # arrange - add a nested object
        parent_prop = "parentObject"
        nested_prop = "nestedProp"
        old = deepcopy(BASE_SCHEMA)
        old["properties"][parent_prop] = {
            "type": "object",
            "properties": {nested_prop: {"type": "integer"}},
            "additionalProperties": False,
        }
        # arrange - remove nested property
        new_prop = "newProp"
        new = deepcopy(old)
        new["properties"][parent_prop]["properties"][new_prop] = {
            "type": "string",
            "description": "A new optional string in a nested object.",
        }
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)
        change = release.changelog.changes[0]
        assert new_prop in change.location
        assert parent_prop in change.location
        assert change.depth == 1

    def test_adding_multiple_props_results_in_multiple_changes(self):
        """The changelog should contain a change for every prop added."""
        # arrange - add a nested object
        old = deepcopy(BASE_SCHEMA)
        # arrange - remove nested property
        new = deepcopy(old)
        new["properties"]["cost"] = {"type": "number"}
        new["properties"]["quantity"] = {"type": "integer"}
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        changes = [change.attribute for change in release.changelog.changes]
        assert len(changes) == 2
        assert "cost" in changes
        assert "quantity" in changes


class TestRemovingProp:
    """Test result when removing a prop from the old schema."""

    def test_remove_optional_prop_with_extra_props_banned(self):
        """
        Should result in a new REVISION.

        Scenario:
        - Prop diff:    REMOVED
        - Prop status:  OPTIONAL
        - Extra props:  BANNED in new schema
        - Release type: REVISION
        """
        # arrange
        old = BASE_SCHEMA
        new = deepcopy(old)
        del new["properties"][PROP_ENUM]
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert_release_kind(release, wanted=ChangeLevel.REVISION)

    def test_remove_optional_prop_with_extra_props_allowed_implicitly(self):
        """
        Should result in a new ADDITION.

        Scenario:
        - Prop diff:    REMOVED
        - Prop status:  OPTIONAL
        - Extra props:  ALLOWED (implicit) in new schema
        - Release type: ADDITION
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        del new["properties"][PROP_ENUM]
        del new["additionalProperties"]
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)

    def test_remove_optional_prop_with_extra_props_allowed_explicitly(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    REMOVED
        - Prop status:  OPTIONAL
        - Extra props:  ALLOWED (explicit) in new schema
        - Release type: ADDITION
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        del new["properties"][PROP_ENUM]
        new["additionalProperties"] = True
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)

    def test_remove_required_prop_with_extra_props_banned(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    REMOVED
        - Prop status:  REQUIRED
        - Extra props:  BANNED in new schema
        - Release type: MODEL
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        del new["properties"][PROP_STRING]
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.MODEL)

    def test_remove_required_prop_with_extra_props_allowed_implicitly(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    REMOVED
        - Prop status:  REQUIRED
        - Extra props:  ALLOWED (implicitly) in new schema
        - Release type: ADDITION
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        del new["properties"][PROP_STRING]
        del new["additionalProperties"]
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)

    def test_remove_required_prop_with_extra_props_allowed_explicitly(self):
        """
        Should be an addition release.

        Scenario:
        - Prop diff:    ADDED
        - Prop status:  REQUIRED
        - Extra props:  ALLOWED (explicitly) in new schema
        - Release type: ADDITION
        """
        # arrange
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        del new["properties"][PROP_STRING]
        new["additionalProperties"] = True
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)

    def test_remove_prop_from_nested_object(self):
        """Nested props should be accessed through recursion."""
        # arrange - add a nested object
        parent_prop = "parentObject"
        nested_prop = "nestedProp"
        old = deepcopy(BASE_SCHEMA)
        old["properties"][parent_prop] = {
            "type": "object",
            "properties": {nested_prop: {"type": "integer"}},
            "additionalProperties": False,
        }
        # arrange - remove nested property
        new = deepcopy(old)
        del new["properties"][parent_prop]["properties"][nested_prop]
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.REVISION)
        change = release.changelog.changes[0]
        assert nested_prop in change.location
        assert parent_prop in change.location
        assert change.depth == 1

    def test_removing_multiple_props_results_in_multiple_changes(self):
        """The changelog should contain a change for every prop removed."""
        # arrange - add a nested object
        old = deepcopy(BASE_SCHEMA)
        # arrange - remove nested property
        new = deepcopy(old)
        del new["properties"][PROP_ENUM]
        del new["properties"][PROP_STRING]
        # act
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        changes = [change.attribute for change in release.changelog.changes]
        assert len(changes) == 2
        assert "productName" in changes
        assert PROP_ENUM in changes


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
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.REVISION)

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
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)


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
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)

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
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)

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
        release = compare_schemas(
            new_schema=new,
            previous_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_kind(got=release, wanted=ChangeLevel.ADDITION)
