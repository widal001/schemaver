"""Test the schema module."""

from pathlib import Path

import pytest

from schemaver.utils import InvalidJsonSchemaError, load_json_string_or_path


class TestLoadJsonStringOrPath:
    """Tests the load_json_string_or_path() function."""

    def test_load_valid_json_string_as_dict(self):
        """Successfully load valid JSON string as a dictionary."""
        # arrange
        source = r'{"type": "integer"}'
        # act
        got = load_json_string_or_path(source)
        # assert
        assert isinstance(got, dict)

    def test_load_valid_json_file_as_dict(self):
        """Successfully load valid JSON file as a dictionary."""
        # arrange
        source = "tests/data/valid_json_schema.json"
        assert Path(source).exists()
        # act
        got = load_json_string_or_path(source)
        # assert
        assert isinstance(got, dict)

    def test_raise_error_if_json_string_is_invalid(self):
        """Raise InvalidJsonSchemaError if JSON string is invalid."""
        # arrange
        source = r"{bad json}"
        # assert
        with pytest.raises(InvalidJsonSchemaError):
            load_json_string_or_path(source)

    def test_raise_error_if_json_file_does_not_exist(self):
        """Raise InvalidJsonSchemaError if file doesn't exist."""
        # arrange
        source = "fake-path.json"
        assert Path(source).exists() is False
        # assert
        with pytest.raises(InvalidJsonSchemaError):
            load_json_string_or_path(source)

    def test_raise_error_if_file_exists_but_not_valid_json(self):
        """Raise InvalidJsonSchemaError if file exist but isn't valid JSON."""
        # arrange
        source = "tests/data/fake_json_schema.txt"
        assert Path(source).exists()
        # assert
        with pytest.raises(InvalidJsonSchemaError):
            load_json_string_or_path(source)
