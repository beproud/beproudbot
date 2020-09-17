import pytest

from tests.db import DatabaseManager


@pytest.fixture(scope='session')
def test_engine():
    """Session-wide test database"""
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///test.sqlite")
    return engine


@pytest.fixture()
def db(test_engine):
    db = DatabaseManager(test_engine)
    db.initialize()
    yield db
