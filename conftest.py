"""pytest configuration."""
from typing import Generator

import pytest
from sqlalchemy.orm import Session

from saao_deployment_server.database import database_connection, Base


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """
    Fixture for creating a fresh test database in memory.

    All tables are created, but they have entries.
    """
    db_connection = database_connection('sqlite:///:memory:')
    Base.metadata.create_all(bind=db_connection.engine)

    yield db_connection.LocalSession()
