"""Database connection."""

import dataclasses

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


@dataclasses.dataclass()
class DatabaseConnection:
    LocalSession: sessionmaker
    engine: Engine


def database_connection(database_url: str) -> DatabaseConnection:
    """Create a database connection."""
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    return DatabaseConnection(
        LocalSession=sessionmaker(autocommit=False, autoflush=False, bind=engine),
        engine=engine,
    )


Base = declarative_base()
