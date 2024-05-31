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


class ValidationField(Enum):
    """List of supported validation attributes."""

    # all instance types
    TYPE = "type"
    ENUM = "enum"
    FORMAT = "format"
    # array types
    ITEMS = "items"
    MAX_ITEMS = "maxItems"
    MIN_ITEMS = "minItems"
    CONTAINS = "contains"
    UNIQUE_ITEMS = "uniqueItems"
    MAX_CONTAINS = "maxContains"
    MIN_CONTAINS = "minContains"
    # object types
    PROPS = "properties"
    MAX_PROPS = "maxProperties"
    MIN_PROPS = "minProperties"
    EXTRA_PROPS = "additionalProperties"
    DEPENDENT_REQUIRED = "dependentRequired"
    REQUIRED = "required"
    # numeric types
    MULTIPLE_OF = "multipleOf"
    MAX = "maximum"
    EXCLUSIVE_MAX = "exclusiveMaximum"
    MIN = "minimum"
    EXCLUSIVE_MIN = "exclusiveMinimum"
    # string types
    MAX_LENGTH = "maxLength"
    MIN_LENGTH = "minLength"
    PATTERN = "pattern"


METADATA_FIELDS = {option.value for option in MetadataField}
VALIDATION_FIELDS = {option.value for option in ValidationField}


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

PROP_LOOKUP: dict[DiffType, dict[Required, dict[ExtraProps, ChangeLevel]]] = {
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
