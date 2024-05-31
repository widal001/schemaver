"""Test the CLI entrypoints."""

import shlex

import pytest
from typer.testing import CliRunner

from schemaver.cli import app

runner = CliRunner()


class TestCompare:
    """Tests the schemaver compare command."""

    @pytest.mark.parametrize(("invalid_arg"), ["--old", "--new"])
    def test_exit_code_one_with_invalid_json_passed(self, invalid_arg: str):
        """CLI should return non-zero exit code with invalid JSON."""
        # arrange
        bad_json = r'{"foo"}'
        good_json = r'{"foo": 2}'
        cmd = "compare --new '{new}' --old '{old}' --version v1-1-1"
        if invalid_arg == "--new":
            cmd = cmd.format(new=bad_json, old=good_json)
        else:
            cmd = cmd.format(new=good_json, old=bad_json)
        # act
        result = runner.invoke(app, shlex.split(cmd))
        # assert
        assert result.exit_code == 1
        assert invalid_arg in result.stdout

    def test_valid_json_prints_summary_to_std_out(self):
        """Valid JSON results in printing the release summary to std out."""
        # arrange
        json = r'{"type": "integer"}'
        cmd = f"compare --new '{json}' --old '{json}' --version v1-1-1"
        # act
        result = runner.invoke(app, shlex.split(cmd))
        # assert
        assert result.exit_code == 0
        assert "Summary" in result.stdout
