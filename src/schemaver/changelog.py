"""Inventory a list of changes associated with a release."""

from dataclasses import dataclass

from schemaver.lookup import ChangeLevel


@dataclass
class SchemaChange:
    """Characterize an individual change made to a JSON schema."""

    kind: ChangeLevel
    description: str
    attribute: str
    depth: int = 0
    location: str = "root"


@dataclass
class Changelog:
    """Record and categorize a list of schema changes."""

    changes: list[SchemaChange]

    @property
    def change_level(self) -> ChangeLevel:
        """Get the type of the highest-level change made in this changelog."""
        # Iterate through the levels starting with MODEL and
        # return the highest level with at least one change
        for level in ChangeLevel:
            if self.filter_changes(level):
                return level
        return ChangeLevel.NONE

    def filter_changes(self, level: ChangeLevel) -> list[SchemaChange]:
        """Filter changelog by level."""
        return [change for change in self.changes if change.kind == level]
