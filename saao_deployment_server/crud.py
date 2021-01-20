import hashlib
import secrets

from sqlalchemy.orm import Session

from saao_deployment_server import models, schemas


def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    """Create a new project in the database."""
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def create_token(db: Session, project_name: str) -> models.Token:
    """Create a new token in the database."""

    # get the project
    project = (
        db.query(models.Project).filter(models.Project.name == project_name).first()
    )
    if project is None:
        raise ValueError("Project name not found in database")

    # create the token
    random_token_value = secrets.token_bytes()
    hashed_token_value = hashlib.sha256(random_token_value).hexdigest()
    db_token = models.Token(hashed_token=hashed_token_value)
    db_token.hashed_token = hashed_token_value
    db_token.project = project
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token
