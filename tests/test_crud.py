"""Tests for database operations."""
from sqlalchemy.orm import Session

from saao_deployment_server import models, schemas
from saao_deployment_server.crud import create_project
from saao_deployment_server.database import Base, database_connection


def test_create_project_adds_a_project(db: Session) -> None:
    """create_project adds a project to the database."""

    # there is no project to start with
    assert db.query(models.Project).count() == 0

    # create a project
    project = schemas.ProjectCreate(
        name="My Project", directory="/wherever", deploy_command="whatever"
    )
    create_project(db, project)

    # there is a project now...
    assert db.query(models.Project).count() == 1

    # ... and it has the correct content
    db_project = db.query(models.Project).first()
    assert db_project.id is not None
    assert db_project.deploy_command == project.deploy_command
    assert db_project.directory == project.directory
    assert db_project.name == project.name


def test_create_project_returns_added_project() -> None:
    """create_project adds a project to the database."""
    db_connection = database_connection("sqlite://")
    Base.metadata.create_all(bind=db_connection.engine)

    db = db_connection.LocalSession()

    # there is no project to start with
    print(type(Base))
    assert db.query(models.Project).count() == 0

    # create a project
    project = schemas.ProjectCreate(
        name="My Project", directory="/wherever", deploy_command="whatever"
    )
    created_project = create_project(db, project)

    # the return value and the database content are consistent
    db_project = db.query(models.Project).first()
    assert created_project.id == db_project.id
    assert created_project.deploy_command == project.deploy_command
    assert created_project.directory == project.directory
    assert db_project.name == project.name
