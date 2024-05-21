"""Test the code in the compare_schemas module."""

from copy import deepcopy

from schemaver.compare_schemas import ChangeLevel, Release, compare_schemas

BASE_VERSION = "1-0-0"
BASE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/product.schema.json",
    "title": "Product",
    "description": "A product in the catalog",
    "type": "object",
    "properties": {
        "productId": {"type": "string"},
        "productName": {"type": "string"},
        "productType": {"type": "string", "enum": ["foo", "bar"]},
    },
    "required": ["productId", "productName"],
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
        del new["properties"]["productType"]
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
        del new["properties"]["productType"]
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
        del new["properties"]["productType"]
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
        del new["properties"]["productName"]
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
        del new["properties"]["productName"]
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
        del new["properties"]["productName"]
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
