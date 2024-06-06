"""Compare two schemas and list the changes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from schemaver.changelog import Changelog
from schemaver.schema import Schema
from schemaver.version import Version

if TYPE_CHECKING:
    from schemaver.changelog import ChangeLevel


class Release:
    """Document the schema changes made when releasing a new SchemaVer."""

    new_version: Version
    old_version: Version
    new_schema: dict
    old_schema: dict
    level: ChangeLevel
    changes: Changelog

    def __init__(
        self,
        new_schema: dict,
        old_schema: dict,
        old_version: str,
    ) -> None:
        """Compare two schemas and create a release with the correct SchemaVer and Changelog."""
        self.new_schema = new_schema
        self.old_schema = old_schema
        schema_now = Schema(new_schema)
        schema_before = Schema(old_schema)
        self.changes = schema_now.diff(
            old=schema_before,
            changelog=Changelog(),
        )
        self.level = self.changes.highest_level
        self.old_version = Version(old_version)
        self.new_version = self.old_version.bump(self.level)

    def summarize(self) -> str:
        """Summarize the release details and changes."""
        summary = f"""
## Summary
- **New version**: `{self.new_version}`
- **Previous version**: `{self.old_version}`
- **Release level**: {self.level.value}
- **Total changes**: {len(self.changes)}\n
"""
        summary += self.changes.summarize()
        return summary.strip()
