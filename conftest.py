"""pytest configuration."""
import pathlib
from typing import Generator, Optional, Tuple

import pytest
from sqlalchemy.orm import Session

from remote_command_server.database import database_connection, Base


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """
    Fixture for creating a fresh test database in memory.

    All tables are created, but they have no entries.
    """

    db: Optional[Session] = None
    try:
        db_connection = database_connection('sqlite:///:memory:')
        Base.metadata.create_all(bind=db_connection.engine)
        db = db_connection.LocalSession()
        yield db
    finally:
        if db:
            db.close()


@pytest.fixture()
def file_based_db(tmp_path: pathlib.Path) -> Generator[Tuple[Session, pathlib.Path], None, None]:
    """
    Fixture for creating a fresh test database in a temporary file.

    All tables are created, but they have entries.
    """

    db: Optional[Session] = None
    try:
        db_file = tmp_path.absolute() / "test.sqlite3"
        db_connection = database_connection(f"sqlite:///{db_file}")
        Base.metadata.create_all(bind=db_connection.engine)
        db = db_connection.LocalSession()
        yield db, db_file
    finally:
        if db:
            db.close()
