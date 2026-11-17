from typing import Generator

import pytest
from sqlalchemy.orm import Session

from src.main.db.engine import engine, SessionLocal


# Сессия БД на один тест, после теста закрывается
@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

