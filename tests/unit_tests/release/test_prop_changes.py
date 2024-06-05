"""Test Release class when a new schema adds or removes object properties."""

from copy import deepcopy

import pytest

from schemaver.release import Release
from schemaver.changelog import ChangeLevel
from schemaver.diffs.property import ExtraProps, Required

from tests.helpers import (
    BASE_SCHEMA,
    BASE_VERSION,
    PROP_ENUM,
    PROP_STRING,
    assert_release_level,
)


class TestAddingProp:
    """Test result when adding a prop to the new schema."""

    old_schema: dict
    new_schema: dict

    def arrange_schemas(
        self,
        new_prop_status: Required,
        extra_props_before: ExtraProps,
    ) -> None:
        """Arrange the old and new schemas for testing based on the input scenario."""
        # Arrange old schema
        self.old_schema = deepcopy(BASE_SCHEMA)
        if extra_props_before == ExtraProps.ALLOWED:
            self.old_schema["additionalProperties"] = True

        # Arrange new schema
        self.new_schema = deepcopy(self.old_schema)
        self.new_schema["properties"]["cost"] = {"type": "number"}
        if new_prop_status == Required.YES:
            self.new_schema["required"].append("cost")

    # fmt: off
    @pytest.mark.parametrize(
        ("new_prop_status", "extra_props_before", "release_level"),
        [
            (Required.NO,  ExtraProps.NOT_ALLOWED, ChangeLevel.ADDITION),
            (Required.NO,  ExtraProps.ALLOWED,     ChangeLevel.REVISION),
            (Required.YES, ExtraProps.NOT_ALLOWED, ChangeLevel.MODEL),
            (Required.YES, ExtraProps.ALLOWED,     ChangeLevel.REVISION),
        ],
    )
    # fmt: on
    def test_add_new_prop(
        self,
        new_prop_status: Required,
        extra_props_before: ExtraProps,
        release_level: ChangeLevel,
    ):
        """Test the various combinations of adding a new prop to a schema."""
        # arrange
        self.arrange_schemas(new_prop_status, extra_props_before)
        # act
        release = Release(
            new_schema=self.new_schema,
            old_schema=self.old_schema,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=release_level)

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
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=ChangeLevel.ADDITION)
        change = release.changes[0]
        assert new_prop == change.attribute
        assert parent_prop in change.location
        assert change.depth == 3

    def test_adding_multiple_props_results_in_multiple_changes(self):
        """The changelog should contain a change for every prop added."""
        # arrange - add a nested object
        old = deepcopy(BASE_SCHEMA)
        # arrange - remove nested property
        new = deepcopy(old)
        new["properties"]["cost"] = {"type": "number"}
        new["properties"]["quantity"] = {"type": "integer"}
        # act
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        changes = [change.attribute for change in release.changes]
        assert len(changes) == 2
        assert "cost" in changes
        assert "quantity" in changes


class TestRemovingProp:
    """Test result when removing a prop from the old schema."""

    old_schema: dict
    new_schema: dict

    def arrange_schemas(
        self,
        old_prop_status: Required,
        extra_props_now: ExtraProps,
    ) -> None:
        """Arrange the old and new schemas for testing based on the input scenario."""
        # Arrange new schema WITHOUT field
        self.new_schema = deepcopy(BASE_SCHEMA)
        if extra_props_now == ExtraProps.ALLOWED:
            self.new_schema["additionalProperties"] = True

        # Arrange old schema WITH field
        self.old_schema = deepcopy(BASE_SCHEMA)
        self.old_schema["properties"]["cost"] = {"type": "number"}
        if old_prop_status == Required.YES:
            self.old_schema["required"].append("cost")

    # fmt: off
    @pytest.mark.parametrize(
        ("old_prop_status", "extra_props_now", "release_level"),
        [
            (Required.NO,  ExtraProps.NOT_ALLOWED, ChangeLevel.REVISION),
            (Required.NO,  ExtraProps.ALLOWED,     ChangeLevel.ADDITION),
            (Required.YES, ExtraProps.NOT_ALLOWED, ChangeLevel.MODEL),
            (Required.YES, ExtraProps.ALLOWED,     ChangeLevel.ADDITION),
        ],
    )
    # fmt: on
    def test_remove_existing_prop(
        self,
        old_prop_status: Required,
        extra_props_now: ExtraProps,
        release_level: ChangeLevel,
    ):
        """Test the various combinations of removing an existing prop from a schema."""
        # arrange
        self.arrange_schemas(old_prop_status, extra_props_now)
        # act
        release = Release(
            new_schema=self.new_schema,
            old_schema=self.old_schema,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=release_level)

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
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        assert_release_level(got=release, wanted=ChangeLevel.REVISION)
        change = release.changes[0]
        assert nested_prop == change.attribute
        assert parent_prop in change.location
        assert change.depth == 3

    def test_removing_multiple_props_results_in_multiple_changes(self):
        """The changelog should contain a change for every prop removed."""
        # arrange - add a nested object
        old = deepcopy(BASE_SCHEMA)
        # arrange - remove nested property
        new = deepcopy(old)
        del new["properties"][PROP_ENUM]
        del new["properties"][PROP_STRING]
        # act
        release = Release(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        changes = [change.attribute for change in release.changes]
        assert len(changes) == 2
        assert "productName" in changes
        assert PROP_ENUM in changes
