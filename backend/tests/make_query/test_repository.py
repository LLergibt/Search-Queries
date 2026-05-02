import pytest
from sqlalchemy.orm import Session

from domain.search_query.repository import SearchQueryRepository
from domain.search_query.model import SearchQuery


@pytest.fixture
def repo(db_session: Session) -> SearchQueryRepository:
    return SearchQueryRepository(db_session)


class TestSearchQueryRepository:
    def test_count_empty(self, repo: SearchQueryRepository):
        assert repo.count() == 0

    def test_count_after_insert(self, repo: SearchQueryRepository, db_session: Session, make_query):
        make_query(name="q1")
        make_query(name="q2")
        assert repo.count() == 2

    def test_get_by_id_found(self, repo: SearchQueryRepository, db_session: Session, make_query):
        q = make_query()
        found = repo.get_by_id(q.id)
        assert found is not None
        assert found.id == q.id

    def test_get_by_id_not_found(self, repo: SearchQueryRepository):
        assert repo.get_by_id(999999) is None

    def test_add(self, repo: SearchQueryRepository):
        from datetime import datetime, timezone
        entity = SearchQuery(
            name="new", owner="u@corp.io",
            is_active=True, results_count=0,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None), updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        saved = repo.add(entity)
        assert saved.id is not None

    def test_delete_by_id_existing(self, repo: SearchQueryRepository, db_session: Session, make_query):
        q = make_query()
        assert repo.delete_by_id(q.id) is True
        assert repo.get_by_id(q.id) is None

    def test_delete_by_id_missing(self, repo: SearchQueryRepository):
        assert repo.delete_by_id(999999) is False

    def test_delete_by_ids(self, repo: SearchQueryRepository, db_session: Session, make_query):
        q1 = make_query(name="a")
        q2 = make_query(name="b")
        q3 = make_query(name="c")
        repo.delete_by_ids([q1.id, q2.id])
        assert repo.count() == 1
        assert repo.get_by_id(q3.id) is not None

    def test_list_paginated_returns_correct_slice(
        self, repo: SearchQueryRepository, db_session: Session, make_query
    ):
        for i in range(15):
            make_query(name=f"q_{i:03d}")
        page1 = repo.list_paginated(page=1, page_size=10, sort_by="name", sort_dir="asc")
        page2 = repo.list_paginated(page=2, page_size=10, sort_by="name", sort_dir="asc")
        assert len(page1) == 10
        assert len(page2) == 5

    def test_list_paginated_sort_asc(
        self, repo: SearchQueryRepository, db_session: Session, make_query
    ):
        for name in ["banana", "apple", "cherry"]:
            make_query(name=name)
        items = repo.list_paginated(page=1, page_size=10, sort_by="name", sort_dir="asc")
        names = [i.name for i in items]
        assert names == sorted(names)

    def test_list_paginated_sort_desc(
        self, repo: SearchQueryRepository, db_session: Session, make_query
    ):
        for name in ["banana", "apple", "cherry"]:
            make_query(name=name)
        items = repo.list_paginated(page=1, page_size=10, sort_by="name", sort_dir="desc")
        names = [i.name for i in items]
        assert names == sorted(names, reverse=True)

    def test_list_paginated_unknown_sort_fallback(
        self, repo: SearchQueryRepository, db_session: Session, make_query
    ):
        make_query()
        # Не должно бросать исключение
        items = repo.list_paginated(
            page=1, page_size=10, sort_by="__nonexistent__", sort_dir="asc"
        )
        assert len(items) == 1
