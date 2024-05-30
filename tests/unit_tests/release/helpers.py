"""Helper constants and functions for testing the Release class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from schemaver.lookup import ChangeLevel

if TYPE_CHECKING:
    from schemaver.release import Release

# default props
PROP_INT = "productId"
PROP_STRING = "productName"
PROP_ENUM = "productType"
PROP_ARRAY = "tags"
PROP_OBJECT = "nestedObject"
PROP_ANY = "anyField"
# base version and schema
BASE_VERSION = "1-1-1"
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
VERSION_LOOKUP = {
    ChangeLevel.MODEL: "v2-0-0",
    ChangeLevel.REVISION: "v1-2-0",
    ChangeLevel.ADDITION: "v1-1-2",
    ChangeLevel.NONE: "v1-1-1",
}


def assert_release_level(got: Release, wanted: ChangeLevel):
    """Confirm the release matches expectations."""
    print(f"Got: {got.level} Wanted: {wanted}")
    assert got.level == wanted
    assert str(got.new_version) == VERSION_LOOKUP[wanted]
    assert len(got.changes.filter(wanted)) > 0
    for level in ChangeLevel:
        if level not in (wanted, ChangeLevel.NONE):
            assert not got.changes.filter(level)
