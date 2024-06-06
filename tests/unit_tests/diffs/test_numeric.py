"""Test recording the diff between numeric instance types."""

from copy import deepcopy

import pytest

from schemaver.changelog import ChangeLevel, Changelog
from schemaver.diffs.array import ArrayField
from schemaver.diffs.string import StringField
from schemaver.diffs.numeric import NumericField
from schemaver.schema import InstanceType, Property

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


def create_sub_schema(prop: str):
    """Create a schema with an integer sub-schema."""
    return {"type": "object", "properties": {prop: {**BASE_INTEGER}}}


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


class TestRecordNestedChanges:
    """Test recording changes to nested numeric types."""

    def test_adding_validation_to_sub_schema_logs_revision(self):
        """Adding validation attribute to a sub schema logs a revision-level change."""
        # arrange - create new and old schemas
        prop = "foo"
        attr = NumericField.MAX.value
        old = create_sub_schema(prop)
        new = deepcopy(old)
        new["properties"][prop][attr] = 10  # validation only on new schema
        # arrange - create schemas
        old_schema = Property(old)
        new_schema = Property(new)
        changelog = Changelog()
        # act
        new_schema.diff(old_schema, changelog)
        # assert
        change = changelog[0]
        assert change.level == ChangeLevel.REVISION
        assert change.attribute == attr
        assert prop in change.location
        assert change.depth > 1

    def test_removing_validation_from_sub_schema_logs_addition(self):
        """Removing validation attribute from a sub schema logs an addition-level change."""
        # arrange - create new and old schemas
        prop = "foo"
        attr = NumericField.MAX.value
        old = create_sub_schema(prop)
        new = deepcopy(old)
        old["properties"][prop][attr] = 5  # validation only on old schema
        # arrange - create schemas
        old_schema = Property(old)
        new_schema = Property(new)
        changelog = Changelog()
        # act
        new_schema.diff(old_schema, changelog)
        # assert
        change = changelog[0]
        assert change.level == ChangeLevel.ADDITION
        assert change.attribute == attr
        assert prop in change.location
        assert change.depth > 1

    def test_changing_multiple_attributes_in_a_sub_schema(self):
        """All of the changes in a sub-schema should be detected."""
        # arrange - create new and old schemas
        prop = "foo"
        old = create_sub_schema(prop)
        new = deepcopy(old)
        old_attr = NumericField.MIN.value
        new_attr = NumericField.MAX.value
        # arrange - add validations to the new and old schemas
        old["properties"][prop][old_attr] = 5  # only on old
        new["properties"][prop][new_attr] = 10  # only on new
        # arrange - create schemas
        new_schema = Property(old)
        old_schema = Property(new)
        changelog = Changelog()
        # act
        new_schema.diff(old_schema, changelog)
        # assert
        assert len(changelog) == 2
        assert {old_attr, new_attr} == {c.attribute for c in changelog}
