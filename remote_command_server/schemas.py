"""Pydantic models (schemas)."""


from typing import List

from pydantic import BaseModel


class ProjectBase(BaseModel):
    """Base class for project models."""

    name: str
    directory: str
    command: str


class ProjectCreate(ProjectBase):
    """Model for creating a project."""

    pass


class Project(ProjectBase):
    """Model for a project."""

    id: int
    tokens: List["Token"] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    """Model for a token."""

    id: int
    hashed_token: str
    project: "Project"

    class Config:
        orm_mode = True
