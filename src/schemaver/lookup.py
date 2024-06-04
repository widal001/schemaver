"""Lookup the results of a change based on standard inputs."""

from dataclasses import dataclass
from enum import Enum

# ##################################
# Enums
# ##################################


class ChangeLevel(Enum):
    """
    Characterize a change using the SchemaVer hierarchy.

    This hierarchy is modeled after the Major.Minor.Patch hierarchy in SemVer.
    Additional information about each change type be found at:
    https://docs.snowplow.io/docs/pipeline-components-and-applications/iglu/common-architecture/schemaver/
    """

    MODEL = "model"
    REVISION = "revision"
    ADDITION = "addition"
    NONE = "no change"


class Required(Enum):
    """Indicate whether a property is required or optional."""

    YES = "required"
    NO = "optional"


class DiffType(Enum):
    """Indicate whether an attribute was added, removed, or modified."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


class ExtraProps(Enum):
    """Indicate whether additionalProps is allowed or not."""

    ALLOWED = "allowed"
    NOT_ALLOWED = "not allowed"
    VALIDATED = "validated"


class MetadataField(Enum):
    """List of supported metadata attributes."""

    TITLE = "title"
    DESCRIPTION = "description"
    DEFAULT = "default"
    DEPRECATED = "deprecated"
    READ_ONLY = "readOnly"
    WRITE_ONLY = "writeOnly"
    EXAMPLES = "examples"


class InstanceType(Enum):
    """The instance type for a property."""

    ARRAY = "array"
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    OBJECT = "object"
    ANY = None


class ValidationType(Enum):
    """Whether the validation represents a max, min, or some other format."""

    MAX = "maximum"
    MIN = "minimum"
    OTHER = "other"


@dataclass
class ValidationField:
    """A validation field."""

    name: str
    kind: ValidationType


class CoreField(Enum):
    """List of supported validation attributes."""

    # all instance types
    TYPE = "type"
    ENUM = "enum"
    FORMAT = "format"

    @property
    def kind(self) -> ValidationType:
        """The type of validation."""
        return ValidationType.OTHER


class ArrayField(Enum):
    """List of validations attributes for arrays."""

    # array types
    ITEMS = "items"
    MAX_ITEMS = "maxItems"
    MIN_ITEMS = "minItems"
    CONTAINS = "contains"
    UNIQUE_ITEMS = "uniqueItems"
    MAX_CONTAINS = "maxContains"
    MIN_CONTAINS = "minContains"

    @property
    def kind(self) -> ValidationType:
        """The type of validation."""
        lookup = {
            # other
            self.ITEMS: ValidationType.OTHER,
            self.CONTAINS: ValidationType.OTHER,
            self.UNIQUE_ITEMS: ValidationType.OTHER,
            # max
            self.MAX_ITEMS: ValidationType.MAX,
            self.MAX_CONTAINS: ValidationType.MAX,
            # min
            self.MIN_ITEMS: ValidationType.MIN,
            self.MIN_CONTAINS: ValidationType.MIN,
        }
        return lookup.get(self) or ValidationType.OTHER


class ObjectField(Enum):
    """List of validation attributes for objects."""

    # object types
    PROPS = "properties"
    MAX_PROPS = "maxProperties"
    MIN_PROPS = "minProperties"
    EXTRA_PROPS = "additionalProperties"
    DEPENDENT_REQUIRED = "dependentRequired"
    REQUIRED = "required"

    @property
    def kind(self) -> ValidationType:
        """The type of validation."""
        lookup: dict[ObjectField, ValidationType] = {
            # other
            self.PROPS: ValidationType.OTHER,
            self.EXTRA_PROPS: ValidationType.OTHER,
            self.DEPENDENT_REQUIRED: ValidationType.OTHER,
            self.REQUIRED: ValidationType.OTHER,
            # max
            self.MAX_PROPS: ValidationType.MAX,
            # min
            self.MIN_PROPS: ValidationType.MIN,
        }
        return lookup.get(self) or ValidationType.OTHER


class NumericField(Enum):
    """List of validation attributes for integers and numbers."""

    # numeric types
    MAX = "maximum"
    MIN = "minimum"
    EXCLUSIVE_MAX = "exclusiveMaximum"
    EXCLUSIVE_MIN = "exclusiveMinimum"
    MULTIPLE_OF = "multipleOf"

    @property
    def kind(self) -> ValidationType:
        """The type of validation."""
        lookup = {
            # other
            self.MULTIPLE_OF: ValidationType.OTHER,
            # max
            self.MAX: ValidationType.MAX,
            self.EXCLUSIVE_MAX: ValidationType.MAX,
            # min
            self.MIN: ValidationType.MIN,
            self.EXCLUSIVE_MIN: ValidationType.MIN,
        }
        return lookup.get(self) or ValidationType.OTHER


class StringField(Enum):
    """List of validation attributes for strings."""

    # string types
    MAX_LENGTH = "maxLength"
    MIN_LENGTH = "minLength"
    PATTERN = "pattern"

    @property
    def kind(self) -> ValidationType:
        """The type of validation."""
        lookup = {
            # other
            self.PATTERN: ValidationType.OTHER,
            # max
            self.MAX_LENGTH: ValidationType.MAX,
            # min
            self.MIN_LENGTH: ValidationType.MIN,
        }
        return lookup[self]


class ChangeDirection(Enum):
    """Whether the validation attribute increased or decreased, if applicable."""

    UP = "increased"
    DOWN = "decreased"
    NA = "not applicable"


METADATA_FIELDS = {option.value for option in MetadataField}
CORE_FIELDS = {option.value for option in CoreField}
VALIDATION_FIELDS: dict[InstanceType, set[str]] = {
    InstanceType.ARRAY: {option.value for option in ArrayField},
    InstanceType.INTEGER: {option.value for option in NumericField},
    InstanceType.NUMBER: {option.value for option in NumericField},
    InstanceType.STRING: {option.value for option in StringField},
    InstanceType.OBJECT: {option.value for option in ObjectField},
    InstanceType.ANY: CORE_FIELDS,
}


@dataclass
class SchemaContext:
    """Context about the current schema."""

    location: str = "root"
    curr_depth: int = 0
    required_before: bool = True
    required_now: bool = True
    extra_props_before: ExtraProps = ExtraProps.NOT_ALLOWED
    extra_props_now: ExtraProps = ExtraProps.NOT_ALLOWED


# ##################################
# Lookup tables
# ##################################


# Uses the following inputs to determine the appropriate change level
# - Diff type (i.e. property was ADDED vs REMOVED)
# - Required status (i.e. property was/is REQUIRED vs OPTIONAL)
# - Additional props (i.e. additional properties were/are ALLOWED vs BANNED)
PROP_LOOKUP: dict[
    DiffType,
    dict[Required, dict[ExtraProps, ChangeLevel]],
] = {
    # When a property is added to an object
    DiffType.ADDED: {
        # Newly added prop is required
        Required.YES: {
            # additionalProps were previously allowed
            ExtraProps.ALLOWED: ChangeLevel.REVISION,
            # additionalProps were previously banned
            ExtraProps.NOT_ALLOWED: ChangeLevel.MODEL,
        },
        # Newly added prop is optional
        Required.NO: {
            # additionalProps were previously allowed
            ExtraProps.ALLOWED: ChangeLevel.REVISION,
            # additionalProps were previously banned
            ExtraProps.NOT_ALLOWED: ChangeLevel.ADDITION,
        },
    },
    # When a property was removed from an object
    DiffType.REMOVED: {
        # Removed prop was required
        Required.YES: {
            # additionalProps are currently allowed
            ExtraProps.ALLOWED: ChangeLevel.ADDITION,
            # additional props are currently banned
            ExtraProps.NOT_ALLOWED: ChangeLevel.MODEL,
        },
        # Removed prop was optional
        Required.NO: {
            # additionalProps are currently allowed
            ExtraProps.ALLOWED: ChangeLevel.ADDITION,
            # additionalProps are currently banned
            ExtraProps.NOT_ALLOWED: ChangeLevel.REVISION,
        },
    },
}

# Maps the change in the validation type (i.e. max or min)
# and the validation direction (i.e. increase or decrease)
# to the level for that change (i.e. model, revision, or addition)
VALIDATION_CHANGE_LOOKUP: dict[
    ValidationType,
    dict[ChangeDirection, ChangeLevel],
] = {
    ValidationType.MAX: {
        # INCREASING the MAX is an ADDITION
        ChangeDirection.UP: ChangeLevel.ADDITION,
        # DECREASING the MAX is a REVISION
        ChangeDirection.DOWN: ChangeLevel.REVISION,
    },
    ValidationType.MIN: {
        # INCREASING the MIN is a REVISION
        ChangeDirection.UP: ChangeLevel.REVISION,
        # INCREASING the MAX is a REVISION
        ChangeDirection.DOWN: ChangeLevel.ADDITION,
    },
}
