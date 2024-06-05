"""Tests the Changelog class."""

import pytest

from schemaver.changelog import Changelog, SchemaChange
from schemaver.changelog import ChangeLevel

CHANGES = {
    ChangeLevel.MODEL: SchemaChange(
        level=ChangeLevel.MODEL,
        description="Added a required property",
        attribute="cost",
    ),
    ChangeLevel.REVISION: SchemaChange(
        level=ChangeLevel.REVISION,
        description="Added new validation",
        attribute="enum",
    ),
    ChangeLevel.ADDITION: SchemaChange(
        level=ChangeLevel.ADDITION,
        description="Added new metadata",
        attribute="description",
    ),
}


@pytest.fixture(name="changes")
def fixture_changelog():
    """Return a mock changelog for use in tests."""
    changelog = Changelog()
    for change in CHANGES.values():
        changelog.add(change)
    return changelog


class TestProperties:
    """Test the properties that return a filtered list of changes."""

    def test_all(self, changes: Changelog):
        """The Changelog.all property should return a list of all changes."""
        # act
        got = changes.all
        # assert
        assert len(got) == 3

    def test_model(self, changes: Changelog):
        """The Changelog.model property should filter for model-level changes."""
        # act
        got = changes.model
        # assert
        assert len(got) == 1
        assert got[0].level == ChangeLevel.MODEL

    def test_revision(self, changes: Changelog):
        """The Changelog.revision property should filter for revision-level changes."""
        # act
        got = changes.revision
        # assert
        assert len(got) == 1
        assert got[0].level == ChangeLevel.REVISION

    def test_addition(self, changes: Changelog):
        """The Changelog.addition property should filter for addition-level changes."""
        # act
        got = changes.addition
        # assert
        assert len(got) == 1
        assert got[0].level == ChangeLevel.ADDITION


class TestChangeLevel:
    """Test the Changelog.change_level property."""

    def test_return_model_with_at_least_one_model_level_change(
        self,
        changes: Changelog,
    ):
        """Change level should be MODEL if there's at least one model-level change."""
        # assert
        assert changes.highest_level == ChangeLevel.MODEL

    def test_return_revision_with_at_least_one_revision_level_change(self):
        """Change level should be REVISION if there's at least one revision-level change."""
        # arrange - Add revision and addition
        changes = Changelog()
        changes.add(CHANGES[ChangeLevel.REVISION])
        changes.add(CHANGES[ChangeLevel.ADDITION])
        # assert
        assert changes.highest_level == ChangeLevel.REVISION

    def test_return_addition_with_at_least_one_addition_level_change(self):
        """Change level should be REVISION if there's at least one revision-level change."""
        # arrange - Add addition
        changes = Changelog()
        changes.add(CHANGES[ChangeLevel.ADDITION])
        # assert
        assert changes.highest_level == ChangeLevel.ADDITION

    def test_return_none_if_no_changes(self):
        """Change level should be NONE if there are no changes."""
        # arrange
        changes = Changelog()
        # assert
        assert changes.highest_level == ChangeLevel.NONE
