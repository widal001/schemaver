"""Test the Release.get_summary() method."""

from copy import deepcopy

import pytest

from schemaver.lookup import ChangeLevel
from schemaver.release import Release

from tests.helpers import BASE_SCHEMA, BASE_VERSION, PROP_ARRAY

PROP_COST = "cost"
PROP_FOO = "foo"


@pytest.fixture(name="release")
def mock_release() -> Release:
    """Generate a release fixture for use across tests in this module."""
    old = deepcopy(BASE_SCHEMA)
    new = deepcopy(old)
    # Addition-level change - adding an optional field
    new["properties"][PROP_COST] = {"type": "number"}
    # Revision-level change - removing an optional field with extra props not allowed
    del new["properties"][PROP_ARRAY]
    # Model-level change - adding a required field
    new["properties"][PROP_FOO] = {"type": "integer"}
    new["required"].append(PROP_FOO)
    release = Release(
        new_schema=new,
        old_schema=old,
        old_version=BASE_VERSION,
    )
    # check that it matches expectations
    assert release.level == ChangeLevel.MODEL
    assert len(release.changes) == 3
    # return the release
    return release


def test_format_summary_with_markdown(release: Release):
    """Release summary should be formatted with markdown."""
    # act
    summary: str = release.summarize()
    print(summary)
    # assert
    assert summary.startswith("## Summary")
    assert "### Model level" in summary
    assert "\n- " in summary


def test_include_all_changes_in_summary(release: Release):
    """All changes should be included in the summary."""
    # act
    summary: str = release.summarize()
    print(summary)
    # assert
    assert "Model level" in summary
    assert "Addition level" in summary
    assert "Revision level" in summary
    # assert
    assert PROP_COST in summary
    assert PROP_ARRAY in summary
    assert PROP_FOO in summary