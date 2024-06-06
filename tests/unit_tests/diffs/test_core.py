"""Test recording the diff for core validation fields between any type."""

import pytest

from schemaver.changelog import ChangeLevel
from schemaver.diffs.core import CoreField
from schemaver.diffs.string import StringField
from schemaver.diffs.numeric import NumericField
from schemaver.property import InstanceType, Property

from tests.unit_tests.diffs.helpers import (
    assert_changes,
    arrange_add_attribute,
    arrange_change_attribute,
    arrange_remove_attribute,
)

# empty schema allows any type
BASE_SCHEMA = {}
EXAMPLES = [
    (CoreField.TYPE.value, "string"),
    (CoreField.ENUM.value, ["foo", "bar"]),
    (CoreField.FORMAT.value, "email"),
]


class TestDiffCore:
    """Test adding removing, or changing the validation fields shared by all types."""

    def test_init_string(self):
        """Property class correctly initializes when type is 'integer'."""
        # act
        prop = Property(BASE_SCHEMA)
        # assert
        assert prop.kind == InstanceType.ANY

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

    @pytest.mark.parametrize(("attr", "value"), EXAMPLES)
    def test_adding_validation_logs_a_revision(self, attr: str, value: int):
        """Adding validation should log a revision-level change to the changelog."""
        # arrange
        setup = arrange_add_attribute(BASE_SCHEMA, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    @pytest.mark.parametrize(("attr", "value"), EXAMPLES)
    def test_removing_validation_logs_an_addition(self, attr: str, value: int):
        """Decreasing MAX should log a revision-level change to the changelog."""
        # arrange
        setup = arrange_remove_attribute(BASE_SCHEMA, attr, value)
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.ADDITION: 1})

    def test_changing_types_logs_a_model_change(self):
        """Changing the type attribute logs a MODEL-level change."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=CoreField.TYPE.value,
            old_val="string",
            new_val="integer",
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.MODEL: 1})

    def test_changing_enum_logs_a_revision(self):
        """Changing the enum attribute results in a REVISION-level change."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=CoreField.ENUM.value,
            old_val=["foo", "bar"],
            new_val=["bar"],
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})

    def test_changing_format_logs_a_revision(self):
        """Changing the format attribute logs a REVISION-level change."""
        # arrange
        setup = arrange_change_attribute(
            base=BASE_SCHEMA,
            attr=CoreField.FORMAT.value,
            old_val="uuid",
            new_val="email",
        )
        # act
        setup.new_schema.diff(setup.old_schema, setup.changelog)
        # assert
        assert_changes(got=setup.changelog, wanted={ChangeLevel.REVISION: 1})
