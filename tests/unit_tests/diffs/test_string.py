"""Test the Property class for numeric instance types."""

from copy import deepcopy

import pytest

from schemaver.lookup import (
    ChangeLevel,
    InstanceType,
    StringField,
    ArrayField,
)
from schemaver.property import Property
from schemaver.changelog import Changelog

from tests.unit_tests.diffs.helpers import (
    assert_changes,
    arrange_add_attribute,
    arrange_change_attribute,
    arrange_remove_attribute,
)

BASE_SCHEMA = {"type": "string"}
VALIDATION_CHANGES = [
    (StringField.MAX_LENGTH.value, 10),
    (StringField.MIN_LENGTH.value, 10),
    (StringField.PATTERN.value, "[A-z]+"),
]


class TestDiffString:
    """Test adding, removing, or changing validation specific to numeric types."""

    def test_init_string(self):
        """Property class correctly initializes when type is 'integer'."""
        # act
        prop = Property(BASE_SCHEMA)
        # assert
        assert prop.kind == InstanceType.STRING

    @pytest.mark.parametrize(
        ("attr", "value"),
        [
            (ArrayField.MIN_ITEMS.value, 10),
            (ArrayField.MAX_CONTAINS.value, 10),
        ],
    )
    def test_ignore_validations_for_other_instance_types(
        self,
        attr: str,
        value: int,
    ):
        """Changes to non-numeric validations should be ignored."""
        # arrange - add validation to the new schema
        old: dict = deepcopy(BASE_SCHEMA)
        new: dict = deepcopy(old)
        new[attr] = value
        assert new != old
        # arrange - create properties and changelog
        changelog = Changelog()
        old_prop = Property(old)
        new_prop = Property(new)
        # act
        new_prop.diff(old_prop, changelog)
        # assert
        wanted = {
            ChangeLevel.ADDITION: 0,
            ChangeLevel.REVISION: 0,
            ChangeLevel.MODEL: 0,
        }
        assert_changes(got=changelog, wanted=wanted)

    @pytest.mark.parametrize(("attr", "value"), VALIDATION_CHANGES)
    def test_adding_validation_logs_a_revision(self, attr: str, value: int):
        """Adding validation should log a revision-level change to the changelog."""
        # arrange
        setup = arrange_add_attribute(BASE_SCHEMA, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    @pytest.mark.parametrize(("attr", "value"), VALIDATION_CHANGES)
    def test_removing_validation_logs_an_addition(self, attr: str, value: int):
        """Decreasing MAX should log a revision-level change to the changelog."""
        # arrange
        setup = arrange_remove_attribute(BASE_SCHEMA, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})

    def test_increasing_max_logs_an_addition(self):
        """Increasing MAX should log an addition-level change to the changelog."""
        # arrange
        value = 10
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=StringField.MAX_LENGTH.value,
            old_val=value,
            new_val=value + 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})

    def test_decreasing_max_logs_a_revision(self):
        """Decreasing MAX should log an revision-level change to the changelog."""
        # arrange
        value = 10
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=StringField.MAX_LENGTH.value,
            old_val=value,
            new_val=value - 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    def test_increasing_min_logs_a_revision(self):
        """Increasing MIN should log an revision-level change to the changelog."""
        value = 10
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=StringField.MIN_LENGTH.value,
            old_val=value,
            new_val=value + 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    def test_decreasing_min_logs_an_addition(self):
        """Decreasing MIN should log an addition-level change to the changelog."""
        # arrange
        value = 10
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=StringField.MIN_LENGTH.value,
            old_val=value,
            new_val=value - 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})
