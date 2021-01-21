"""Tests for database operations."""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from remote_command_server import models, schemas
from remote_command_server.crud import (
    create_project,
    create_token,
    hash_token,
    verify_token,
)


def test_create_project_adds_a_project(db: Session) -> None:
    """create_project adds a project to the database."""

    # there is no project to start with
    assert db.query(models.Project).count() == 0

    # create a project
    project = schemas.ProjectCreate(
        name="My Project", directory="/wherever", command="whatever"
    )
    create_project(db, project)

    # there is a project now...
    assert db.query(models.Project).count() == 1

    # ... and it has the correct content
    db_project = db.query(models.Project).first()
    assert db_project.id is not None
    assert db_project.command == project.command
    assert db_project.directory == project.directory
    assert db_project.name == project.name


def test_create_project_returns_added_project(db: Session) -> None:
    """create_project return the project added to the database."""

    # there is no project to start with
    assert db.query(models.Project).count() == 0

    # create a project
    project = schemas.ProjectCreate(
        name="My Project", directory="/wherever", command="whatever"
    )
    created_project = create_project(db, project)

    # the return value and the database content are consistent
    db_project = db.query(models.Project).first()
    assert created_project.id == db_project.id
    assert created_project.command == project.command
    assert created_project.directory == project.directory
    assert db_project.name == project.name


def test_no_duplicate_projects(db: Session) -> None:
    """A project name may exist only once."""

    # create a project
    create_project(
        db,
        schemas.ProjectCreate(
            name="My Project", directory="/wherever", command="whatever"
        ),
    )

    # try to create another project with the same name
    with pytest.raises(IntegrityError):
        create_project(
            db,
            schemas.ProjectCreate(
                name="My Project",
                directory="/somewhere_else",
                command="something_else",
            ),
        )


def test_create_token_adds_a_token(db: Session) -> None:
    """create_token adds a token to the database"""

    # create a project
    create_project(
        db,
        schemas.ProjectCreate(
            name="My Project", directory="/wherever", command="whatever"
        ),
    )

    # there is no token to start with
    assert db.query(models.Token).count() == 0

    # add a token
    created_token = create_token(db, project_name="My Project")

    # there is a token now...
    assert db.query(models.Token).count() == 1

    # ... and it has the correct content
    db_token = db.query(models.Token).first()
    assert db_token.id is not None
    assert db_token.hashed_token == hash_token(created_token)
    assert db_token.project.name == "My Project"


def test_create_token_returns_added_token(db: Session) -> None:
    """create_token returns the token added ton the database."""

    # create a project
    create_project(
        db,
        schemas.ProjectCreate(
            name="My Project", directory="/wherever", command="whatever"
        ),
    )

    # there is no token to start with
    assert db.query(models.Token).count() == 0

    # add a token
    created_token = create_token(db, project_name="My Project")

    # the return value and the database content are consistent
    db_token = db.query(models.Token).first()
    assert hash_token(created_token) == db_token.hashed_token


def tests_no_token_created_for_non_existing_project(db: Session) -> None:
    """No token is created for a project which does not exist."""

    # create a project
    create_project(
        db,
        schemas.ProjectCreate(
            name="My Project", directory="/wherever", command="whatever"
        ),
    )

    # try to add a token for another project
    with pytest.raises(ValueError) as excinfo:
        create_token(db, "Another Project")
    assert "project" in str(excinfo).lower()


def test_verify_token_with_valid_token(db: Session) -> None:
    """A valid token can be verified."""

    # create a project and a token
    create_project(
        db,
        schemas.ProjectCreate(
            name="Some Project", directory="/wherever", command="whatever"
        ),
    )
    token = create_token(db, project_name="Some Project")

    # verify the token
    assert verify_token(db, token=token, project_name="Some Project")


def test_verify_token_with_non_existing_token(db: Session) -> None:
    """A non-existing token cannot be verified."""

    # create a project and a token
    create_project(
        db,
        schemas.ProjectCreate(
            name="Some Project", directory="/wherever", command="whatever"
        ),
    )
    token = create_token(db, project_name="Some Project")

    # try to verify another token value
    assert not verify_token(db, token=token + "1234", project_name="Some Project")


def test_verify_token_with_non_existing_project(db: Session) -> None:
    """A token cannot be verified for a non-existing project."""

    # create a project and a token
    create_project(
        db,
        schemas.ProjectCreate(
            name="Some Project", directory="/wherever", command="whatever"
        ),
    )
    token = create_token(db, project_name="Some Project")

    # try to verify the token for another project
    assert not verify_token(db, token=token, project_name="Other Project")


def test_verify_token_for_wrong_project(db: Session) -> None:
    # create two projects and one token
    create_project(
        db,
        schemas.ProjectCreate(
            name="Some Project", directory="/wherever", command="whatever"
        ),
    )
    create_project(
        db,
        schemas.ProjectCreate(
            name="Other Project", directory="/wherever", command="whatever"
        ),
    )
    token = create_token(db, project_name="Some Project")

    # try to verify the token for the wrong project
    assert not verify_token(db, token=token, project_name="Other Project")
