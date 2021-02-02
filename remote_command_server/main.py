import os
import pathlib
from typing import Dict, Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from remote_command_server import crud, models, schemas, util
from remote_command_server.database import database_connection

app = FastAPI()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db() -> Session:  # pragma: no cover
    database_url = os.environ["SQL_ALCHEMY_DATABASE_URL"]
    LocalSession = database_connection(database_url).LocalSession
    return LocalSession()


def get_project(
    project_name: str, db: Session = Depends(get_db), token: str = Depends(oauth_scheme)
) -> models.Project:
    if not crud.verify_token(db=db, token=token, project_name=project_name):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    project: models.Project = (
        db.query(models.Project).filter(models.Project.name == project_name).first()
    )
    return project


@app.post("/run/{project_name}", responses={500: {"model": schemas.Message}})
async def run(
    project: models.Project = Depends(get_project),
) -> Union[Dict[str, bool], JSONResponse]:

    completed_process = util.run_command(
        directory=pathlib.Path(project.directory), command=project.command
    )
    if completed_process.returncode:
        return JSONResponse(
            content={"message": "Command returned with a non-zero return code."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return {"success": True}
