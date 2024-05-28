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
            if self.filter(level):
                return level
        return ChangeLevel.NONE

    @property
    def model(self) -> list[SchemaChange]:
        """Model-level schema changes."""
        return self.filter(ChangeLevel.MODEL)

    @property
    def revision(self) -> list[SchemaChange]:
        """Revision-level schema changes."""
        return self.filter(ChangeLevel.REVISION)

    @property
    def addition(self) -> list[SchemaChange]:
        """Revision-level schema changes."""
        return self.filter(ChangeLevel.ADDITION)

    def filter(self, level: ChangeLevel) -> list[SchemaChange]:
        """Filter changelog by level."""
        return [change for change in self.changes if change.kind == level]
