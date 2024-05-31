"""Provide a command line interface (CLI) for schemaver."""

from typing import Annotated

import typer

from schemaver import release, schema

# instantiate the main CLI entrypoint
app = typer.Typer()


@app.callback()
def callback() -> None:
    """Manage JSON schema versions and migrations."""


@app.command(name="compare")
def compare_schemas(
    new: Annotated[
        str,
        typer.Option(help="Path or text with the new JSON schema"),
    ],
    old: Annotated[
        str,
        typer.Option(help="Path or text with the old JSON schema"),
    ],
    version: Annotated[
        str,
        typer.Option(help="Version number for the old JSON schema"),
    ],
) -> None:
    """Compare two JSON schemas and generate a release summary."""
    # Try to load the old schema
    try:
        old_schema = schema.load_json_string_or_path(old)
    except schema.InvalidJsonSchemaError:
        msg = "Value passed to --old is not valid JSON or path to valid JSON file."
        typer.echo(msg)
        raise typer.Exit(code=1) from None
    # Try to load the new schema
    try:
        new_schema = schema.load_json_string_or_path(new)
    except schema.InvalidJsonSchemaError:
        msg = "Value passed to --new is not valid JSON or path to valid JSON file."
        typer.echo(msg)
        raise typer.Exit(code=1) from None
    # Generate a new release migrating from the old to the new schema
    new_release = release.Release(
        new_schema=new_schema,
        old_schema=old_schema,
        old_version=version,
    )
    # Print the release summary to the console
    summary = new_release.summarize()
    typer.echo(summary)
