import pytest

from db import Session, Base


@pytest.fixture(scope='session')
def test_engine():
    '''Session-wide test database'''
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///test.sqlite")
    return engine


@pytest.fixture()
def session():
    engine = test_engine()
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
