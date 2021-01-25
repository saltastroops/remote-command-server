import pathlib

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from remote_command_server import crud, schemas
from remote_command_server.main import get_project


def test_get_project_returns_correct_project(
    tmp_path: pathlib.Path, db: Session
) -> None:
    # set up the database
    dir = str(tmp_path.absolute())
    crud.create_project(
        db, schemas.ProjectCreate(name="shiny-project", directory=dir, command="echo")
    )
    token = crud.create_token(db, "shiny-project")

    # check the correct project is returned
    project = get_project("shiny-project", db, token)
    assert project.name == "shiny-project"
    assert project.directory == dir
    assert project.command == "echo"


def test_get_project_raises_error_for_invalid_token(
    tmp_path: pathlib.Path, db: Session
) -> None:
    # set up the database
    dir = str(tmp_path.absolute())
    crud.create_project(
        db, schemas.ProjectCreate(name="shiny-project", directory=dir, command="echo")
    )
    crud.create_token(db, "shiny-project")

    # check an exception is raised for an invalid token
    with pytest.raises(HTTPException) as excinfo:
        get_project("shiny-project", db, "invalid-token")
    assert "unauthorized" in str(excinfo).lower()
