from datetime import datetime, timezone
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from domain.search_query.model import SearchQuery
from main import app


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def make_query(db_session: Session):
    """Фабрика тестовых записей, доступна как фикстура в любом тесте."""
    def _make(
        *,
        name: str = "test_query",
        is_active: bool = True,
        owner: str = "owner@corp.io",
        deadline: datetime | None = None,
        results_count: int = 0,
    ) -> SearchQuery:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        q = SearchQuery(
            name=name,
            is_active=is_active,
            owner=owner,
            deadline=deadline,
            results_count=results_count,
            created_at=now,
            updated_at=now,
        )
        db_session.add(q)
        db_session.commit()
        db_session.refresh(q)
        return q
    return _make
