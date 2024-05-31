"""Inventory a list of changes associated with a release."""

from dataclasses import dataclass
from typing import Iterator

from schemaver.lookup import ChangeLevel


@dataclass
class SchemaChange:
    """Characterize an individual change made to a JSON schema."""

    kind: ChangeLevel
    description: str
    attribute: str
    depth: int = 0
    location: str = "root"


class Changelog:
    """Record and categorize a list of schema changes."""

    def __init__(self) -> None:
        """Initialize a Changelog."""
        self._changes: list[SchemaChange] = []

    def add(self, change: SchemaChange) -> None:
        """Add a change to the changelog."""
        self._changes.append(change)

    def summarize(self) -> str:
        """Format the list of changes as a string."""
        if not self._changes:
            return ""
        summary = "## Changes\n"
        summary += self._summarize_changes(ChangeLevel.MODEL)
        summary += self._summarize_changes(ChangeLevel.REVISION)
        summary += self._summarize_changes(ChangeLevel.ADDITION)
        return summary

    def _summarize_changes(self, level: ChangeLevel) -> str:
        """Summarize the list of changes as a string in the given format."""
        summary = ""
        changes = self.filter(level)
        if not changes:
            return summary
        summary += f"\n### {level.value.title()} level\n"
        for change in changes:
            summary += f"- {change.description}\n"
        return summary

    @property
    def highest_level(self) -> ChangeLevel:
        """Get the type of the highest-level change made in this changelog."""
        # Iterate through the levels starting with MODEL and
        # return the highest level with at least one change
        for level in ChangeLevel:
            if self.filter(level):
                return level
        return ChangeLevel.NONE

    @property
    def all(self) -> list[SchemaChange]:
        """Model-level schema changes."""
        return self._changes

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
        return [change for change in self._changes if change.kind == level]

    def __iter__(self) -> Iterator[SchemaChange]:
        """Iterate over the changes in the changelog."""
        return (change for change in self._changes)

    def __getitem__(self, index: int) -> SchemaChange:
        """Get an item from the changelog."""
        return self._changes[index]

    def __len__(self) -> int:
        """Get the size of the changelog."""
        return len(self._changes)
