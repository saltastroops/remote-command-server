"""Tests for the commabd line interface."""
import pathlib
from typing import List, Tuple

import pytest
from click.testing import CliRunner
from sqlalchemy.orm import Session

from remote_command_server import models, schemas
from remote_command_server.cli import cli
from remote_command_server.crud import create_project, create_token, hash_token
from remote_command_server.database import database_connection


def test_project_creates_project(
    tmp_path: pathlib.Path, file_based_db: Tuple[Session, pathlib.Path]
) -> None:
    """The project command creates a new project in the database."""

    # execute the CLI command
    db, db_file = file_based_db
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "--command",
            "some command",
            "--database",
            str(db_file),
            "--directory",
            str(tmp_path),
            "--name",
            "Test Project",
        ],
    )

    # check the result
    assert result.exit_code == 0
    project = db.query(models.Project).first()
    assert project.command == str("some command")
    assert project.directory == str(tmp_path)
    assert project.name == "Test Project"


def test_project_directory_must_exist(
    tmp_path: pathlib.Path, file_based_db: Tuple[Session, pathlib.Path]
) -> None:
    """The directory passed to the project command must exist."""

    # execute the CLI command
    missing_project_dir = tmp_path / "i_do_not_exist"
    _, db_file = file_based_db
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "--command",
            "some command",
            "--database",
            str(db_file),
            "--directory",
            str(missing_project_dir),
            "--name",
            "Test Project",
        ],
    )

    # check this has failed
    assert result.exit_code != 0
    assert "exist" in result.output


def test_project_directory_must_be_a_directory(
    tmp_path: pathlib.Path, file_based_db: Tuple[Session, pathlib.Path]
) -> None:
    """The directory passed to the project command must be a directory."""

    # execute the CLI command
    _, db_file = file_based_db
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "--command",
            "some command",
            "--database",
            str(db_file),
            "--directory",
            str(db_file),
            "--name",
            "Test Project",
        ],
    )

    # check this has failed
    assert result.exit_code != 0
    assert "directory" in result.output.lower()


def test_project_database_file_must_exist(tmp_path: pathlib.Path) -> None:
    """The database file passed to the project command must exist."""

    # execute the CLI command
    missing_db_file = tmp_path / "i_do_not_exist.sqlite"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "--command",
            "some command",
            "--database",
            str(tmp_path),
            "--directory",
            str(missing_db_file),
            "--name",
            "Test Project",
        ],
    )

    # check this has failed
    assert result.exit_code != 0
    assert "exist" in result.output.lower()


def test_project_database_file_must_be_a_file(tmp_path: pathlib.Path) -> None:
    """The database file passed to the project command must be a file."""

    # execute the CLI command
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "--command",
            "some command",
            "--database",
            str(tmp_path),
            "--directory",
            str(tmp_path),
            "--name",
            "Test Project",
        ],
    )

    # check this has failed
    assert result.exit_code != 0
    assert "file" in result.output.lower()


@pytest.mark.parametrize(
    "options",
    (
        [
            "--database",
            "some-file.sqlite",
            "--directory",
            "/tmp/some-directory",
            "--name",
            "Some Project",
        ],
        [
            "--command",
            "some command",
            "--directory",
            "/tmp/some-directory",
            "--name",
            "Some Project",
        ],
        [
            "--command",
            "some command",
            "--database",
            "some-file.sqlite",
            "--name",
            "Some Project",
        ],
        [
            "--command",
            "some command",
            "--database",
            "some-file.sqlite",
            "--directory",
            "/tmp/some-directory",
        ],
    ),
)
def test_all_project_options_must_be_present(options: List[str]) -> None:
    """All options for the project command must be present."""

    # Note: Some of these tests may fail because the database file or directory does
    #       not exist, rather than because not all options are present.

    # execute the CLI command
    command = ["project"]
    command.extend(options)
    runner = CliRunner()
    result = runner.invoke(cli, command)

    # check this has failed
    assert result.exit_code != 0
    assert "usage" in result.output.lower()


def test_token_creates_token(
    tmp_path: pathlib.Path, file_based_db: Tuple[Session, pathlib.Path]
) -> None:
    """The token command creates and outputs a token."""

    # create a project
    db, db_file = file_based_db
    create_project(
        db,
        schemas.ProjectCreate(
            name="Test Project", directory=str(tmp_path), command="some command"
        ),
    )

    # execute the CLI command
    runner = CliRunner()
    result = runner.invoke(
        cli, ["token", "--database", str(db_file), "--project", "Test Project"]
    )
    assert result.exit_code == 0

    # get the output token value
    output_token = result.output.split("\n")[0].split(": ")[1]

    # get the hashed token value from the database and check it is consistent with the
    # output token value
    db_token = db.query(models.Token).first()
    assert hash_token(output_token) == db_token.hashed_token


def test_token_database_file_must_exist(tmp_path: pathlib.Path) -> None:
    "The database file passed to the token command must exist."

    # execute the CLI command
    missing_db_file = tmp_path / "i_do_not_exist.sqlite"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["token", "--database", str(missing_db_file), "--project", "Test Project"]
    )

    # check this has failed
    assert result.exit_code != 0
    assert "exist" in result.output


def test_token_database_file_must_be_a_file(tmp_path: pathlib.Path) -> None:
    """The database file passed to the token command must be a file."""

    # execute the CLI command
    runner = CliRunner()
    result = runner.invoke(
        cli, ["token", "--database", str(tmp_path), "--project", "Test Project"]
    )

    # check this has failed
    assert result.exit_code != 0
    assert "file" in result.output


@pytest.mark.parametrize(
    "options", (["--database", "some-file.sqlite"], ["--project", "Some Project"])
)
def test_all_token_options_must_be_present(options: List[str]) -> None:
    """All options for the token command must be present."""

    # Note: Some of these tests may fail because the database file does not exist,
    #       rather than because not all options are present.

    # execute the CLI command
    command = ["token"]
    command.extend(options)
    runner = CliRunner()
    result = runner.invoke(cli, command)

    # check this has failed
    assert result.exit_code != 0
    assert "usage" in result.output.lower()


def test_initdb_creates_database_file(tmp_path: pathlib.Path) -> None:
    """The initdb command creates a new database file."""

    # execute the CLI command
    db_file = tmp_path / "test.sqlite"
    runner = CliRunner()
    result = runner.invoke(cli, ["initdb", str(db_file)])
    assert result.exit_code == 0

    # check that a project and token can be created in the new database file
    LocalSession = database_connection(f"sqlite:///{db_file.absolute()}").LocalSession
    db = LocalSession()
    assert db.query(models.Token).count() == 0
    create_project(
        db,
        schemas.ProjectCreate(
            name="New Project", directory=str(tmp_path), command="some command"
        ),
    )
    create_token(db, "New Project")
    assert db.query(models.Token).count() == 1


def test_initdb_argument_must_not_exist(tmp_path: pathlib.Path) -> None:
    """The argument of the initdb command must not be an existing file."""

    # create a file
    db_file = tmp_path / "test.sqlite"
    db_file.write_text("")
    assert db_file.exists()

    # execute the CLI command
    runner = CliRunner()
    result = runner.invoke(cli, ["initdb", str(db_file)])

    # check this has failed
    assert result.exit_code != 0
    assert "exists" in result.output.lower()


def test_initdb_argument_must_be_present() -> None:
    """The initdb command must be called with an argument."""

    # execute the CLI command
    runner = CliRunner()
    result = runner.invoke(cli, ["initdb"])

    # check this has failed
    assert result.exit_code != 0
    assert "usage" in result.output.lower()
