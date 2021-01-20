from sqlalchemy.orm import Session

from saao_deployment_server import models, schemas


def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    """Create a new project in the database."""
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project
