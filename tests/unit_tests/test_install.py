"""Test that the schemaver package was installed correctly."""

import schemaver


def test_package_installed_with_correct_name():
    """Confirm the package was installed and can be imported correctly."""
    # assert
    assert schemaver.__name__ == "schemaver"
