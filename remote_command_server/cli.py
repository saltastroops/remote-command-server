"""Command line interface for generating projects and tokens in the database."""

import os

import click

from remote_command_server import crud
from remote_command_server import database as _database
from remote_command_server import schemas
from remote_command_server.database import Base


@click.group()
def cli() -> None:
    pass


@click.command()
@click.option(
    "--command",
    "-c",
    type=str,
    required=True,
    help="Shell command to run.",
)
@click.option(
    "--database",
    "--db",
    type=click.Path(exists=True, file_okay=True, resolve_path=True),
    required=True,
    help="Database file. This must be a Sqlite 3 file, and it must have all the "
    "required tables and columns.",
)
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True),
    required=True,
    help="Directory in which to run the command. This directory must exist. "
    "Relative paths are converted into absolute paths, and symlinks are resolved. "
    "A tilde prefix is not resolved.",
)
@click.option("--name", "-n", type=str, required=True, help="Project name.")
def project(command: str, database: str, directory: str, name: str) -> None:
    """Create a new project in the database."""
    if not os.path.isfile(database):
        raise click.UsageError(message=f"Not a file: {database}")
    if not os.path.isdir(directory):
        raise click.UsageError(message=f"Not a directory: {directory}")

    database_connection = _database.database_connection(f"sqlite:///{database}")
    project = schemas.ProjectCreate(command=command, directory=directory, name=name)
    crud.create_project(database_connection.LocalSession(), project)


@click.option(
    "--database",
    "--db",
    type=click.Path(exists=True, file_okay=True, resolve_path=True),
    required=True,
    help="Database file. This must be a Sqlite 3 file, and it must have all the "
    "required tables and columns.",
)
@click.option(
    "--project",
    "-p",
    type=str,
    required=True,
    help="Project name. The name must exist in the database already.",
)
@click.command()
def token(database: str, project: str) -> None:
    """Create a new token in the database."""
    if not os.path.isfile(database):
        raise click.UsageError(message=f"Not a file: {database}")

    database_connection = _database.database_connection(f"sqlite:///{database}")
    token = crud.create_token(database_connection.LocalSession(), project)
    click.echo(f"Generated token: {token}")
    click.echo(
        click.style(
            "Please save the token as you will not be able to view it again later.",
            fg="yellow",
            bold=True,
        )
    )


@click.argument(
    "filename", type=click.Path(exists=False, file_okay=True, resolve_path=True)
)
@click.command()
def initdb(filename: str) -> None:
    """Create a new database with all tables but no entries in FILENAME."""
    if os.path.exists(filename):
        raise click.UsageError(f"File exists already: {filename}")

    database_connection = _database.database_connection(f"sqlite:///{filename}")
    Base.metadata.create_all(bind=database_connection.engine)


cli.add_command(project)
cli.add_command(token)
cli.add_command(initdb)
