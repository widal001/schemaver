"""Test the Version class."""

import pytest

from schemaver.changelog import ChangeLevel
from schemaver.version import Version

BASE_MODEL = 1
BASE_REVISION = 2
BASE_ADDITION = 3
BASE_VERSION = f"{BASE_MODEL}-{BASE_REVISION}-{BASE_ADDITION}"


class TestInit:
    """Test the Version.__init__() method."""

    def test_inits_successfully_without_leading_v(self):
        """Version should init successfully if version number has no leading v."""
        # act
        version = Version(BASE_VERSION)
        # assert
        assert version.model == BASE_MODEL
        assert version.revision == BASE_REVISION
        assert version.addition == BASE_ADDITION

    def test_inits_successfully_with_leading_v(self):
        """Version should init successfully if version number has no leading v."""
        # arrange
        version_number = "v" + BASE_VERSION
        # act
        version = Version(version_number)
        # assert
        assert version.model == BASE_MODEL
        assert version.revision == BASE_REVISION
        assert version.addition == BASE_ADDITION

    def test_stringify_returns_correctly_formatted_version(self):
        """Casting Version instance to string returns it with format v1-1-1."""
        # act
        version = Version(BASE_VERSION)
        # assert
        assert str(version) == "v" + BASE_VERSION

    def test_raise_error_if_version_number_is_not_valid_pattern(self):
        """Raise a ValueError if version number doesn't match the right pattern."""
        # arrange
        wanted = "Version number must match the pattern v1-1-0 or 1-1-0"
        # assert
        with pytest.raises(ValueError, match=wanted):
            Version(version="fake")


class TestBump:
    """Test the Version.bump() method."""

    def test_bumping_version_returns_a_modified_copy(self):
        """Bumping the version should return a copy and leave the original unchanged."""
        # arrange
        old = Version(BASE_VERSION)
        # act
        new = old.bump(ChangeLevel.MODEL)
        # assert
        assert old is not new
        assert old.model != new.model
        assert old.revision != new.revision
        assert old.addition != new.addition

    def test_bump_model(self):
        """Bumping the model increments model number and resets others to zero."""
        # arrange
        old = Version(BASE_VERSION)
        # act
        new = old.bump(ChangeLevel.MODEL)
        # arrange
        assert new.model == old.model + 1
        assert new.revision == 0
        assert new.addition == 0

    def test_bump_revision(self):
        """Bumping the model increments model number and resets others to zero."""
        # arrange
        old = Version(BASE_VERSION)
        # act
        new = old.bump(ChangeLevel.REVISION)
        # arrange
        assert new.model == old.model
        assert new.revision == old.revision + 1
        assert new.addition == 0

    def test_bump_addition(self):
        """Bumping the model increments model number and resets others to zero."""
        # arrange
        old = Version(BASE_VERSION)
        # act
        new = old.bump(ChangeLevel.ADDITION)
        # arrange
        assert new.model == old.model
        assert new.revision == old.revision
        assert new.addition == old.addition + 1

    def test_bump_no_change(self):
        """If there is no change, the bump should return a matching version."""
        # arrange
        old = Version(BASE_VERSION)
        # act
        new = old.bump(ChangeLevel.NONE)
        # arrange
        assert new == old


class TestComparisons:
    """Test comparing versions with one another."""

    def test_equal(self):
        """Test two versions are equal."""
        # arrange
        left = Version(BASE_VERSION)
        right = Version(BASE_VERSION)
        # assert
        assert left == right

    def test_not_equal_if_different_types(self):
        """Test a version doesn't equal an object of a different type."""
        # arrange
        version = Version(BASE_VERSION)
        string = "fake"
        # assert
        assert version != string

    def test_not_equal_if_different_versions(self):
        """Test two versions are not equal if they have different types."""
        # arrange
        version = Version(BASE_VERSION)
        string = BASE_VERSION
        # assert
        assert version != string
