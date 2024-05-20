"""Lookup the results of a change based on standard inputs."""

from schemaver.compare_schemas import (
    ChangeType,
    ExtraPropsAllowed,
    PropDiffType,
    RequiredStatus,
)

TABLE = {
    PropDiffType.ADDED: {
        RequiredStatus.NEWLY_OPTIONAL: {
            ExtraPropsAllowed.ALWAYS: ChangeType.REVISION,
            ExtraPropsAllowed.NEVER: ChangeType.ADDITION,
            ExtraPropsAllowed.NO_TO_YES: ChangeType.ADDITION,
            ExtraPropsAllowed.YES_TO_NO: ChangeType.REVISION,
        },
        RequiredStatus.NEWLY_REQUIRED: {
            ExtraPropsAllowed.ALWAYS: ChangeType.REVISION,
            ExtraPropsAllowed.NEVER: ChangeType.MODEL,
            ExtraPropsAllowed.NO_TO_YES: ChangeType.MODEL,
            ExtraPropsAllowed.YES_TO_NO: ChangeType.REVISION,
        },
    },
    PropDiffType.REMOVED: {
        RequiredStatus.WAS_REQUIRED: {
            ExtraPropsAllowed.ALWAYS: ChangeType.REVISION,
            ExtraPropsAllowed.NEVER: ChangeType.MODEL,
            ExtraPropsAllowed.NO_TO_YES: ChangeType.MODEL,
            ExtraPropsAllowed.YES_TO_NO: ChangeType.REVISION,
        },
        RequiredStatus.WAS_OPTIONAL: {
            ExtraPropsAllowed.ALWAYS: ChangeType.ADDITION,
            ExtraPropsAllowed.NEVER: ChangeType.REVISION,
            ExtraPropsAllowed.NO_TO_YES: ChangeType.ADDITION,
            ExtraPropsAllowed.YES_TO_NO: ChangeType.REVISION,
        },
    },
    PropDiffType.CHANGED: {
        RequiredStatus.ALWAYS_REQUIRED: {},
        RequiredStatus.ALWAYS_OPTIONAL: {},
        RequiredStatus.NEWLY_OPTIONAL: {},
        RequiredStatus.NEWLY_REQUIRED: {},
    },
}
