import pytest

from src.main.db.engine import engine, SessionLocal


@pytest.fixture
def db_session():

    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

