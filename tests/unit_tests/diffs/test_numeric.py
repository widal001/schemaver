"""Test recording the diff between numeric instance types."""

import pytest

from schemaver.lookup import (
    ChangeLevel,
    InstanceType,
    NumericField,
    StringField,
    ArrayField,
)
from schemaver.property import Property

from tests.unit_tests.diffs.helpers import (
    assert_changes,
    arrange_add_attribute,
    arrange_change_attribute,
    arrange_remove_attribute,
)

BASE_INTEGER = {"type": "integer"}
BASE_NUMBER = {"type": "number"}
VALIDATION_CHANGES = [
    (NumericField.MAX.value, 10),
    (NumericField.MIN.value, 10),
    (NumericField.EXCLUSIVE_MAX.value, 10),
    (NumericField.EXCLUSIVE_MIN.value, 10),
    (NumericField.MULTIPLE_OF.value, 10),
]


class TestDiffNumeric:
    """Test adding, removing, or changing validation specific to numeric types."""

    @pytest.mark.parametrize(
        ("schema", "kind"),
        [
            (BASE_INTEGER, InstanceType.INTEGER),
            (BASE_NUMBER, InstanceType.NUMBER),
        ],
    )
    def test_init_schema(self, schema: dict, kind: InstanceType):
        """Property class correctly initializes when type is 'integer'."""
        # act
        parsed_schema = Property(schema)
        # assert
        assert parsed_schema.kind == kind

    @pytest.mark.parametrize(
        ("attr", "value"),
        [
            (StringField.MAX_LENGTH.value, 10),
            (StringField.MIN_LENGTH.value, 10),
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
        # arrange
        setup = arrange_add_attribute(BASE_INTEGER, attr, value)
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
        setup = arrange_add_attribute(BASE_INTEGER, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    @pytest.mark.parametrize(("attr", "value"), VALIDATION_CHANGES)
    def test_removing_validation_logs_an_addition(self, attr: str, value: int):
        """Decreasing MAX should log a revision-level change to the changelog."""
        # arrange
        setup = arrange_remove_attribute(BASE_INTEGER, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})

    @pytest.mark.parametrize(
        ("attr", "value"),
        [
            (NumericField.MAX.value, 10),
            (NumericField.EXCLUSIVE_MAX.value, 10),
        ],
    )
    def test_increasing_max_logs_an_addition(self, attr: str, value: int):
        """Increasing MAX should log an addition-level change to the changelog."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_INTEGER,
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
            (NumericField.MAX.value, 10),
            (NumericField.EXCLUSIVE_MAX.value, 10),
        ],
    )
    def test_decreasing_max_logs_a_revision(self, attr: str, value: int):
        """Decreasing MAX should log an revision-level change to the changelog."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_INTEGER,
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
            (NumericField.MIN.value, 10),
            (NumericField.EXCLUSIVE_MIN.value, 10),
        ],
    )
    def test_increasing_min_logs_a_revision(self, attr: str, value: int):
        """Increasing MIN should log an revision-level change to the changelog."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_INTEGER,
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
            (NumericField.MIN.value, 10),
            (NumericField.EXCLUSIVE_MIN.value, 10),
        ],
    )
    def test_decreasing_min_logs_an_addition(self, attr: str, value: int):
        """Decreasing MIN should log an addition-level change to the changelog."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_INTEGER,
            attr=attr,
            old_val=value,
            new_val=value - 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})
