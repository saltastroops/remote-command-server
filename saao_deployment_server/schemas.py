"""Pydantic models (schemas)."""


from typing import List

from pydantic import BaseModel


class ProjectBase(BaseModel):
    """Base class for project models."""

    name: str
    directory: str
    deploy_command: str


class ProjectCreate(ProjectBase):
    """Model for creating a project."""

    pass


class Project(ProjectBase):
    """Model for a project."""

    id: int
    tokens: List["Token"] = []

    class Config:
        orm_mode = True


class TokenBase(BaseModel):
    """Base model for token models."""

    hashed_token: str


class TokenCreate(TokenBase):
    """Model for creating a token."""

    project_name: str


class Token(TokenBase):
    """Model for a token."""

    id: int

    class Config:
        orm_mode = True
