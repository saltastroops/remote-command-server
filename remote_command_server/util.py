"""Utility functions for the server."""

import pathlib
import subprocess  # nosec


def run_command(
    directory: pathlib.Path, command: str
) -> subprocess.CompletedProcess:  # type: ignore
    """
    Run a command in a directory.

    WARNING: The command is executed directly in a shell. This is potentially unsafe,
    so you should make sure that the command you pass is safe to execute.

    The directory must exist (and must be a directory).

    The function returns a CompletedProcess instance, with stdout and stderr captured.
    For example:

    r = run_command(directory="./tests", command="echo $(pwd)"
    if r.returncode:
        print("Oops. Something is wrong.")
        print(r.stderr)
    print(r.stdout)

    """

    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"Does not exist or is no directory: {directory}")

    return subprocess.run(
        command, shell=True, cwd=directory, capture_output=True  # nosec
    )
