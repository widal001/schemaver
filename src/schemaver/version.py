"""Manage the logic behind a schema's version number."""

from __future__ import annotations

import re
from copy import deepcopy

from schemaver.lookup import ChangeLevel


class Version:
    """Manages changes to the version number."""

    model: int
    revision: int
    addition: int

    def __init__(self, version: str) -> None:
        """Initialize a version number."""
        version_pattern = re.compile(
            r"""
            v?                      # Optional leading v for version
            (?P<model>[0-9]+)-       # model number followed by a dash
            (?P<revision>[0-9]+)-    # revision number followed by a dash
            (?P<addition>[0-9]+)$    # addition number at the end of the string
            """,
            re.VERBOSE,
        )
        version_match = version_pattern.match(version.strip())
        if not version_match:
            raise ValueError
        self.model = int(version_match.group("model"))
        self.revision = int(version_match.group("revision"))
        self.addition = int(version_match.group("addition"))

    def bump(self, kind: ChangeLevel) -> Version:
        """Return a new version with an updated model, revision, and addition."""
        # make a copy of the current version
        new_version = deepcopy(self)
        match kind:
            case ChangeLevel.MODEL:
                # Increment model, reset others to 0
                new_version.model += 1
                new_version.revision = 0
                new_version.addition = 0
            case ChangeLevel.REVISION:
                # Increment revision, reset addition to 0
                new_version.revision += 1
                new_version.addition = 0
            case ChangeLevel.ADDITION:
                # Increment only the addition
                new_version.addition += 1
        return new_version

    def __str__(self) -> str:
        """Return a string representation of the version."""
        return f"v{self.model}-{self.revision}-{self.addition}"
