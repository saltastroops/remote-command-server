import hashlib
import secrets
from typing import cast

from sqlalchemy.orm import Session

from remote_command_server import models, schemas


def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    """Create a new project in the database."""
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def create_token(db: Session, project_name: str) -> str:
    """
    Create a new token in the database.

    The unhashed token value is returned. There is no way to get this value from the
    database afterwards.
    """

    # get the project
    project = (
        db.query(models.Project).filter(models.Project.name == project_name).first()
    )
    if project is None:
        raise ValueError("Project name not found in database")

    # create the token
    random_token_value = secrets.token_urlsafe()
    hashed_token_value = hash_token(random_token_value)
    db_token = models.Token(hashed_token=hashed_token_value)
    db_token.hashed_token = hashed_token_value
    db_token.project = project
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return random_token_value


def verify_token(db: Session, token: str, project_name: str) -> bool:
    """
    Verify whether a token grants permission to execute a project.
    """

    # get the project
    project = (
        db.query(models.Project).filter(models.Project.name == project_name).first()
    )
    if project is None:
        return False

    # check the token
    hashed_token = hash_token(token)
    return cast(
        bool,
        db.query(models.Token)
        .filter(
            models.Token.hashed_token == hashed_token,
            models.Token.project_id == project.id,
        )
        .count()
        > 0,
    )


def hash_token(token: str) -> str:
    """Hash a token value."""

    return hashlib.sha256(token.encode("UTF-8")).hexdigest()
