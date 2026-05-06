from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db, get_queue_client
from app.db.base import Base
from app.main import create_app
from app.workers.queue import InMemoryQueueClient
import app.models  # noqa: F401


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def queue_client() -> InMemoryQueueClient:
    return InMemoryQueueClient()


@pytest.fixture
def client(db_session: Session, queue_client: InMemoryQueueClient) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_queue_client] = lambda: queue_client

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
