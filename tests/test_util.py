import pathlib

import pytest

from remote_command_server.util import run_command


def test_execute_command_directory_must_exist() -> None:
    """The directory passed to execute_command must exist."""
    with pytest.raises(ValueError) as excinfo:
        run_command(directory=pathlib.Path("i-am-missing"), command="echo")

    assert "exist" in str(excinfo) and "i-am-missing" in str(excinfo)


def test_execute_command_directory_must_be_directory(tmp_path: pathlib.Path) -> None:
    """The directory passed to execute_command must be a directory."""

    # create a new file
    file = tmp_path / "command.sh"
    file.write_text("")

    with pytest.raises(ValueError) as excinfo:
        run_command(directory=file, command="echo")

    assert "directory" in str(excinfo) and str(file) in str(excinfo)


def test_execute_command_makes_system_call_in_correct_directory(
    tmp_path: pathlib.Path,
) -> None:
    """
    The execute_command functions makes a system call in the specified directory.

    NOTE: This test requires that the system command pwd exists.
    """

    # pwd outputs the current directory, so it can bew used to check that the command is
    # executed in the correct directory
    directory = tmp_path / "some-directory"
    directory.mkdir()
    result = run_command(directory=directory, command="pwd")

    assert result.returncode == 0
    assert b"some-directory" in result.stdout
