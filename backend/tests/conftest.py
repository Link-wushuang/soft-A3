import os

import pytest

os.environ["LLM_PROVIDER"] = "mock"

from fastapi.testclient import TestClient
from app.db.session import get_db, override_engine
from app.db.base import Base
from app.main import app
from app.models import *  # noqa: F401,F403

TEST_DB_URL = "sqlite:///:memory:"
override_engine(TEST_DB_URL)

import app.db.session as _sess


def _override_get_db():
    db = _sess.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=_sess.engine)
    session = _sess.SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=_sess.engine)


@pytest.fixture
def test_db():
    from app.db.init_data import init_demo_data

    Base.metadata.create_all(bind=_sess.engine)
    session = _sess.SessionLocal()
    init_demo_data(session)
    yield session
    session.close()
    Base.metadata.drop_all(bind=_sess.engine)


@pytest.fixture
def client(test_db):
    return TestClient(app)
