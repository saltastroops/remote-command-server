"""SQL Alchemy models."""


from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from remote_command_server.database import Base


class Project(Base):
    """A project to deploy."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    command = Column(String, nullable=False)
    directory = Column(String, nullable=False)
    name = Column(String, nullable=False, unique=True, index=True)

    tokens = relationship("Token", back_populates="project")


class Token(Base):
    """An authentication token."""

    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    hashed_token = Column(String, nullable=False, unique=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project = relationship("Project", back_populates="tokens")
