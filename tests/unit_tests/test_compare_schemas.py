"""Test the code in the compare_schemas module."""

from copy import deepcopy

from schemaver.compare_schemas import ChangeType, Release, compare_schemas

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


class TestCompareSchemas:
    """Test the core functionality of compare_schemas()."""

    def test_return_type_is_release(self):
        """compare_schemas() should return a new Release."""
        # arrange
        old = BASE_SCHEMA
        new = BASE_SCHEMA
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert
        isinstance(release, Release)


class TestModelChanges:
    """Test comparing two schemas that contain model-level changes."""

    def test_root_schema_type_changed(self):
        """Should return a model change if the root schema type changed."""
        # arrange
        old = {"type": "integer"}
        new = {"type": "string"}
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the changelog is correct
        changes = release.changes
        assert len(changes.model) == 1
        assert len(changes.revision) == 0
        assert len(changes.addition) == 0
        # assert - confirm the model change is structured correctly
        change = changes.model[0]
        assert change.location == "root"
        assert change.description == "Type was changed from integer to string"
        assert 1

    def test_nested_field_schema_type_changed(self):
        """Should return a model change if the root schema type changed."""
        # arrange
        old = BASE_SCHEMA
        new = deepcopy(old)
        new["properties"]["productId"]["type"] = "integer"
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        assert 1

    def test_new_required_field(self):
        """Should return a model change with a new required field."""
        # arrange
        old = BASE_SCHEMA
        new = deepcopy(old)
        new["properties"]["cost"] = {
            "type": "string",
            "description": "The cost of the product",
        }
        new["required"].append("cost")
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 1

    def test_removed_required_field_with_no_additional_props_allowed(self):
        """Should return a model change if a required field is removed."""
        # arrange
        old = BASE_SCHEMA
        new = deepcopy(old)
        del new["properties"]["productName"]
        del new["required"][1]
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 1


class TestRevisionChanges:
    """Test comparing two schemas that contain revision-level changes."""

    def test_add_optional_field_with_additional_properties_allowed(self):
        """Should return a model change with a new required field."""
        # arrange - allow additional properties in old schema
        old = deepcopy(BASE_SCHEMA)
        old["additionalProperties"] = True
        # arrange - add new optional field
        new = deepcopy(old)
        new["properties"]["cost"] = {
            "type": "string",
            "description": "The cost of the product",
        }
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 0

    def test_stop_allowing_additional_props(self):
        """Changing additionalProperties from True to False should be a revision."""
        # arrange - allow additional properties in old schema
        old = deepcopy(BASE_SCHEMA)
        old["additionalProperties"] = True
        # arrange - add new optional field
        new = deepcopy(old)
        new["properties"]["cost"] = {
            "type": "string",
            "description": "The cost of the product",
        }
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 1

    def test_remove_optional_field_with_no_additional_props_allowed(self):
        """Remove an optional field when additional props aren't allowed."""
        # arrange - make productName optional
        old = BASE_SCHEMA
        # arrange - remove productName
        new = deepcopy(old)
        del new["properties"]["productType"]
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 1


class TestAdditionChanges:
    """Test comparing two schemas that contain addition-level changes."""

    def test_new_optional_field_with_no_additional_props_allowed(self):
        """Adding a new optional field should be an addition."""
        # arrange - add new optional field
        old = BASE_SCHEMA
        new = deepcopy(old)
        new["properties"]["cost"] = {
            "type": "string",
            "description": "The cost of the product",
        }
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 0

    def test_remove_optional_field_if_additional_props_are_allowed(self):
        """Removing an optional field should be an addition if additional props are allowed."""
        # arrange - add new optional field
        old = deepcopy(BASE_SCHEMA)
        old["additionalProperties"] = True
        new = deepcopy(old)
        del new["properties"]["productType"]
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 0

    def test_allow_additional_props_explicit(self):
        """Changing additionalProperties from False to True should be an addition."""
        # arrange - add new optional field
        old = BASE_SCHEMA
        new = deepcopy(old)
        del new["additionalProperties"]
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 0

    def test_allow_additional_props_implicit(self):
        """Deleting additionalProperties that was False should be an addition."""
        # arrange - add new optional field
        old = BASE_SCHEMA
        new = deepcopy(old)
        new["additionalProperties"] = True
        # act
        release = compare_schemas(
            new_schema=new,
            old_schema=old,
            old_version=BASE_VERSION,
        )
        # assert - confirm the release has the right version
        assert release.new_version == "2-0-0"
        assert release.change_level == ChangeType.MODEL
        # assert - confirm the model change is structured correctly
        assert 0
