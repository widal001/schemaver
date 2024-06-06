"""Test recording the diff between array instance types."""

import pytest

from schemaver.changelog import ChangeLevel
from schemaver.diffs.string import StringField
from schemaver.diffs.numeric import NumericField
from schemaver.diffs.array import ArrayField
from schemaver.schema import InstanceType, Schema

from tests.unit_tests.diffs.helpers import (
    assert_changes,
    arrange_add_attribute,
    arrange_change_attribute,
    arrange_remove_attribute,
)

BASE_SCHEMA = {"type": "array"}
VALIDATION_CHANGES = [
    (ArrayField.MAX_ITEMS.value, 10),
    (ArrayField.MIN_ITEMS.value, 10),
    (ArrayField.MAX_CONTAINS.value, 10),
    (ArrayField.MIN_CONTAINS.value, 10),
    (ArrayField.ITEMS.value, {"type": "string"}),
    (ArrayField.CONTAINS.value, {"type": "string"}),
]


class TestDiffArray:
    """Test adding, removing, or changing validation specific to array types."""

    def test_init_string(self):
        """Property class correctly initializes when type is 'integer'."""
        # act
        prop = Schema(BASE_SCHEMA)
        # assert
        assert prop.kind == InstanceType.ARRAY

    @pytest.mark.parametrize(
        ("attr", "value"),
        [
            (NumericField.MIN.value, 10),
            (NumericField.MAX.value, 10),
            (StringField.MIN_LENGTH.value, 10),
            (StringField.MAX_LENGTH.value, 10),
        ],
    )
    def test_ignore_validations_for_other_instance_types(
        self,
        attr: str,
        value: int,
    ):
        """Changes to non-numeric validations should be ignored."""
        # arrange
        setup = arrange_add_attribute(BASE_SCHEMA, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        wanted = {
            ChangeLevel.ADDITION: 0,
            ChangeLevel.REVISION: 0,
            ChangeLevel.MODEL: 0,
        }
        assert_changes(got=setup.changelog, wanted=wanted)

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

    @pytest.mark.parametrize(
        ("attr", "value"),
        [
            (ArrayField.MAX_ITEMS.value, 10),
            (ArrayField.MAX_CONTAINS.value, 10),
        ],
    )
    def test_increasing_max_logs_an_addition(self, attr: str, value: int):
        """Increasing MAX should log an addition-level change to the changelog."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=attr,
            old_val=value,
            new_val=value + 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})

    @pytest.mark.parametrize(
        ("attr", "value"),
        [
            (ArrayField.MAX_ITEMS.value, 10),
            (ArrayField.MAX_CONTAINS.value, 10),
        ],
    )
    def test_decreasing_max_logs_a_revision(self, attr: str, value: int):
        """Decreasing MAX should log an revision-level change to the changelog."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=attr,
            old_val=value,
            new_val=value - 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    @pytest.mark.parametrize(
        ("attr", "value"),
        [
            (ArrayField.MIN_ITEMS.value, 10),
            (ArrayField.MIN_CONTAINS.value, 10),
        ],
    )
    def test_increasing_min_logs_a_revision(self, attr: str, value: int):
        """Increasing MIN should log an revision-level change to the changelog."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=attr,
            old_val=value,
            new_val=value + 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    @pytest.mark.parametrize(
        ("attr", "value"),
        [
            (ArrayField.MIN_ITEMS.value, 10),
            (ArrayField.MIN_CONTAINS.value, 10),
        ],
    )
    def test_decreasing_min_logs_an_addition(self, attr: str, value: int):
        """Decreasing MIN should log an addition-level change to the changelog."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=attr,
            old_val=value,
            new_val=value - 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})
