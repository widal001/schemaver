"""Load and parse the schema."""

import json
from pathlib import Path


class InvalidJsonSchemaError(Exception):
    """Raise an error indicating that an invalid JSON schema was provided."""


def load_json_string_or_path(source: str) -> dict:
    """Load JSON string or path as a dictionary."""
    # Try to parse the source directly
    try:
        return json.loads(source)
    except json.decoder.JSONDecodeError:
        pass
    # Try to load and parse the source as a file
    try:
        with Path(source).open("r") as f:
            return json.load(f)
    except FileNotFoundError:
        pass
    except json.decoder.JSONDecodeError:
        pass
    # If we can't parse it directly or from a file, raise an error
    raise InvalidJsonSchemaError
