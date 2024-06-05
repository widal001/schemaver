"""Test recording the diff between numeric instance types."""

import pytest

from schemaver.changelog import ChangeLevel

from schemaver.property import InstanceType, Property
from schemaver.diffs.object import ObjectField
from schemaver.diffs.string import StringField
from schemaver.diffs.array import ArrayField

from tests.unit_tests.diffs.helpers import (
    assert_changes,
    arrange_add_attribute,
    arrange_change_attribute,
    arrange_remove_attribute,
)

BASE_SCHEMA = {"type": "object"}
SCHEMA_WITH_PROPS = {
    **BASE_SCHEMA,
    "properties": {
        "foo": {},
        "bar": {},
    },
}
EXAMPLES = [
    (ObjectField.MAX_PROPS.value, 10, BASE_SCHEMA),
    (ObjectField.MIN_PROPS.value, 10, BASE_SCHEMA),
    (ObjectField.EXTRA_PROPS.value, False, SCHEMA_WITH_PROPS),
    (ObjectField.DEPENDENT_REQUIRED.value, 10, BASE_SCHEMA),
]


class TestDiffNumeric:
    """Test adding, removing, or changing validation specific to numeric types."""

    @pytest.mark.parametrize(
        ("schema", "kind"),
        [
            (BASE_SCHEMA, InstanceType.OBJECT),
            (SCHEMA_WITH_PROPS, InstanceType.OBJECT),
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

    @pytest.mark.parametrize(("attr", "value", "schema"), EXAMPLES)
    def test_adding_validation_logs_a_revision(
        self,
        schema: dict,
        attr: str,
        value: int,
    ):
        """Adding validation should log a revision-level change to the changelog."""
        # arrange
        setup = arrange_add_attribute(schema, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    @pytest.mark.parametrize(("attr", "value", "schema"), EXAMPLES)
    def test_removing_validation_logs_an_addition(
        self,
        schema: dict,
        attr: str,
        value: int,
    ):
        """Decreasing MAX should log a revision-level change to the changelog."""
        # arrange
        setup = arrange_remove_attribute(schema, attr, value)
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
            attr=ObjectField.MAX_PROPS.value,
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
            attr=ObjectField.MAX_PROPS.value,
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
            attr=ObjectField.MIN_PROPS.value,
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
            attr=ObjectField.MIN_PROPS.value,
            old_val=value,
            new_val=value - 5,
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})
