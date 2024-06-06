"""Test recording the diff of object properties between schema versions."""

from copy import deepcopy
from pprint import pprint

import pytest

from schemaver.changelog import ChangeLevel, Changelog
from schemaver.diffs.property import ExtraProps, Required
from schemaver.schema import Schema

from tests.unit_tests.diffs.helpers import assert_changes

PROP_ID = "productId"
PROP_NAME = "productName"
PROP_COST = "cost"
PROP_OBJECT = "nestedObject"
BASE_SCHEMA = {
    "type": "object",
    "properties": {
        PROP_ID: {"type": "integer"},
        PROP_NAME: {"type": "string"},
        PROP_OBJECT: {"type": "object", "properties": {}},
    },
    "required": [PROP_ID, PROP_NAME],
    "additionalProperties": False,
}


class TestAddingProp:
    """Test result when adding a prop to the new schema."""

    old_schema: Schema
    new_schema: Schema
    changelog: Changelog

    def arrange_schemas(
        self,
        new_prop_status: Required,
        extra_props_before: ExtraProps,
        *,
        nested: bool = False,
    ) -> None:
        """Arrange the old and new schemas for testing based on the input scenario."""
        # Arrange old schema
        old = deepcopy(BASE_SCHEMA)
        if extra_props_before == ExtraProps.ALLOWED:
            old["additionalProperties"] = True
        # Arrange new schema
        new = deepcopy(old)
        if nested:
            new["properties"][PROP_OBJECT]["properties"] = {
                PROP_COST: {"type": "integer"},
            }
        else:
            new["properties"][PROP_COST] = {"type": "number"}
        if new_prop_status == Required.YES:
            new["required"].append(PROP_COST)
        # print the new and old schemas
        print("Old schema:")
        pprint(old)
        print("New schema:")
        pprint(new)
        # Set values for use in tests
        self.new_schema = Schema(new)
        self.old_schema = Schema(old)
        self.changelog = Changelog()

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
        self.new_schema.diff(self.old_schema, self.changelog)
        # assert
        assert_changes(got=self.changelog, wanted={release_level: 1})

    def test_add_prop_to_nested_object(self):
        """Nested props should be accessed through recursion."""
        # arrange - add a nested object
        self.arrange_schemas(Required.NO, ExtraProps.ALLOWED, nested=True)
        # act
        self.new_schema.diff(self.old_schema, self.changelog)
        # assert
        assert_changes(got=self.changelog, wanted={ChangeLevel.REVISION: 1})
        change = self.changelog[0]
        assert PROP_OBJECT in change.location
        assert change.depth == 3


class TestRemovingProp:
    """Test result when removing a prop from the old schema."""

    old_schema: Schema
    new_schema: Schema
    changelog: Changelog

    def arrange_schemas(
        self,
        old_prop_status: Required,
        extra_props_now: ExtraProps,
        *,
        nested: bool = False,
    ) -> None:
        """Arrange the old and new schemas for testing based on the input scenario."""
        # Arrange new schema WITHOUT field
        new = deepcopy(BASE_SCHEMA)
        if extra_props_now == ExtraProps.ALLOWED:
            new["additionalProperties"] = True
        # Arrange old schema WITH field
        old = deepcopy(BASE_SCHEMA)
        if nested:
            old["properties"][PROP_OBJECT]["properties"] = {
                PROP_COST: {"type": "integer"},
            }
        else:
            old["properties"][PROP_COST] = {"type": "number"}
        if old_prop_status == Required.YES:
            old["required"].append(PROP_COST)
        # print the new and old schemas
        print("Old schema:")
        pprint(old)
        print("New schema:")
        pprint(new)
        # Set values for use in tests
        self.new_schema = Schema(new)
        self.old_schema = Schema(old)
        self.changelog = Changelog()

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
        self.new_schema.diff(self.old_schema, self.changelog)
        # assert
        assert_changes(got=self.changelog, wanted={release_level: 1})

    def test_remove_prop_from_nested_object(self):
        """Nested props should be accessed through recursion."""
        # arrange - add a nested object
        self.arrange_schemas(Required.NO, ExtraProps.ALLOWED, nested=True)
        # act
        self.new_schema.diff(self.old_schema, self.changelog)
        # assert
        assert_changes(got=self.changelog, wanted={ChangeLevel.ADDITION: 1})
        change = self.changelog[0]
        assert PROP_OBJECT in change.location
        assert change.depth == 3


class TestChangingPropStatus:
    """Test switching a prop from required to optional or vice versa."""

    def test_making_prop_optional_logs_an_addition(self):
        """Making a required prop optional should log an addition-level change."""
        # arrange - make productId optional
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        del new["required"][0]
        assert PROP_ID not in new["required"]
        # arrange - init schemas
        old_schema = Schema(old)
        new_schema = Schema(new)
        changelog = Changelog()
        # act
        new_schema.diff(old_schema, changelog)
        # assert
        assert_changes(got=changelog, wanted={ChangeLevel.ADDITION: 1})
        assert changelog[0].attribute == PROP_ID

    def test_making_a_prop_required_logs_a_revision(self):
        """Making an optional prop required should log a revision-level change."""
        # arrange - make productId optional
        old = deepcopy(BASE_SCHEMA)
        new = deepcopy(old)
        new["required"].append(PROP_OBJECT)
        assert PROP_OBJECT in new["required"]
        assert PROP_OBJECT in new["properties"]
        # arrange - init schemas
        old_schema = Schema(old)
        new_schema = Schema(new)
        changelog = Changelog()
        # act
        new_schema.diff(old_schema, changelog)
        # assert
        assert_changes(got=changelog, wanted={ChangeLevel.REVISION: 1})
        assert changelog[0].attribute == PROP_OBJECT
