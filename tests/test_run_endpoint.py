import pathlib
from typing import Any, NamedTuple, cast

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

import remote_command_server
import remote_command_server.util
from remote_command_server import crud, schemas
from remote_command_server.main import app, get_db


class MockCompletedProcess(NamedTuple):
    """Mock for the CompletedProcess class."""

    returncode: int


client = TestClient(app)


def test_run_requires_a_valid_token(tmp_path: pathlib.Path, db: Session) -> None:
    """The deploy endpoint requires a valid token."""

    # set up the database content
    crud.create_project(
        db,
        schemas.ProjectCreate(
            name="shiny-project", directory=str(tmp_path), command="pwd"
        ),
    )
    crud.create_token(db, "shiny-project")

    # use the test database
    def override_get_db() -> Session:
        return db

    app.dependency_overrides[get_db] = override_get_db

    # call the run endpoint with an invalid token
    response = client.post(
        app.url_path_for("run", project_name="shiny-project"),
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 401

    # clean up
    app.dependency_overrides = {}


def test_run_executes_command(
    tmp_path: pathlib.Path, mocker: MockerFixture, db: Session
) -> None:
    """The run endpoint executes the stored command in the stored directory."""

    mocker.patch(
        "remote_command_server.util.run_command",
        return_value=MockCompletedProcess(returncode=0),
    )

    # set up the database content
    crud.create_project(
        db,
        schemas.ProjectCreate(
            name="shiny-project", directory=str(tmp_path), command="pwd"
        ),
    )
    token = crud.create_token(db, "shiny-project")

    # use the test database
    def override_get_db() -> Session:
        return db

    app.dependency_overrides[get_db] = override_get_db

    # make the server call
    response = client.post(
        app.url_path_for("run", project_name="shiny-project"),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    cast(Any, remote_command_server.util.run_command).assert_called_with(
        directory=tmp_path, command="pwd"
    )

    # clean up
    app.dependency_overrides = {}


def test_run_returns_500_if_command_fails(
    tmp_path: pathlib.Path, mocker: MockerFixture, db: Session
) -> None:
    """The run endpoint returns an internal serverc error if the command fails."""

    mocker.patch(
        "remote_command_server.util.run_command",
        return_value=MockCompletedProcess(returncode=1),
    )

    # set up the database content
    crud.create_project(
        db,
        schemas.ProjectCreate(
            name="shiny-project", directory=str(tmp_path), command="pwd"
        ),
    )
    token = crud.create_token(db, "shiny-project")

    # use the test database
    def override_get_db() -> Session:
        return db

    app.dependency_overrides[get_db] = override_get_db

    # make the server call
    response = client.post(
        app.url_path_for("run", project_name="shiny-project"),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 500
    cast(Any, remote_command_server.util.run_command).assert_called_with(
        directory=tmp_path, command="pwd"
    )

    # clean up
    app.dependency_overrides = {}
