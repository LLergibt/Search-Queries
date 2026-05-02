from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from domain.search_query.model import SearchQuery
from domain.search_query.repository import SearchQueryRepository
from domain.search_query.schemas import (
    BulkDeleteRequest,
    QueryCreate,
    QueryUpdate,
)
from domain.search_query.service import SearchQueryService


def _mock_repo(**kwargs) -> MagicMock:
    repo = MagicMock(spec=SearchQueryRepository)
    for k, v in kwargs.items():
        setattr(repo, k, MagicMock(return_value=v))
    return repo


def _entity(name="q", **kw) -> SearchQuery:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return SearchQuery(
        id=1, name=name, owner="u@corp.io",
        is_active=True, results_count=0,
        created_at=now, updated_at=now,
        **kw,
    )


class TestSearchQueryService:


    def test_list_total_pages_calculation(self):
        entities = [_entity(name=f"q{i}") for i in range(7)]
        repo = _mock_repo(count=7, list_paginated=entities)
        svc = SearchQueryService(repo)
        result = svc.list_queries(page=1, page_size=10, sort_by="name", sort_dir="asc")
        assert result.total == 7
        assert result.total_pages == 1

    def test_list_total_pages_multiple(self):
        repo = _mock_repo(count=25, list_paginated=[_entity() for _ in range(10)])
        svc = SearchQueryService(repo)
        result = svc.list_queries(page=1, page_size=10, sort_by="name", sort_dir="asc")
        assert result.total_pages == 3

    def test_list_empty_db_returns_one_page(self):
        repo = _mock_repo(count=0, list_paginated=[])
        svc = SearchQueryService(repo)
        result = svc.list_queries(page=1, page_size=10, sort_by="name", sort_dir="asc")
        assert result.total_pages == 1
        assert result.items == []

    def test_list_passes_params_to_repo(self):
        repo = _mock_repo(count=0, list_paginated=[])
        svc = SearchQueryService(repo)
        svc.list_queries(page=3, page_size=20, sort_by="owner", sort_dir="asc")
        repo.list_paginated.assert_called_once_with(
            page=3, page_size=20, sort_by="owner", sort_dir="asc"
        )


    def test_create_sets_owner(self):
        entity = _entity()
        repo = _mock_repo(add=entity)
        svc = SearchQueryService(repo)
        svc.create_query(QueryCreate(name="test"), owner="alice@corp.io")
        call_args = repo.add.call_args[0][0]
        assert call_args.owner == "alice@corp.io"

    def test_create_sets_results_count_zero(self):
        entity = _entity()
        repo = _mock_repo(add=entity)
        svc = SearchQueryService(repo)
        svc.create_query(QueryCreate(name="test"), owner="u@corp.io")
        call_args = repo.add.call_args[0][0]
        assert call_args.results_count == 0

    def test_create_passes_is_active(self):
        entity = _entity()
        repo = _mock_repo(add=entity)
        svc = SearchQueryService(repo)
        svc.create_query(QueryCreate(name="test", is_active=False), owner="u@corp.io")
        call_args = repo.add.call_args[0][0]
        assert call_args.is_active is False


    def test_update_returns_none_when_not_found(self):
        repo = _mock_repo(get_by_id=None)
        svc = SearchQueryService(repo)
        assert svc.update_query(999, QueryUpdate(name="x")) is None

    def test_update_applies_fields(self):
        entity = _entity(name="old")
        repo = _mock_repo(get_by_id=entity, update=entity)
        svc = SearchQueryService(repo)
        svc.update_query(1, QueryUpdate(name="new", is_active=False))
        assert entity.name == "new"
        assert entity.is_active is False

    def test_update_refreshes_updated_at(self):
        entity = _entity()
        old_ts = entity.updated_at
        repo = _mock_repo(get_by_id=entity, update=entity)
        svc = SearchQueryService(repo)
        with patch("domain.search_query.service.utcnow") as mock_now:
            mock_now.return_value = datetime(2099, 1, 1)
            svc.update_query(1, QueryUpdate(name="x"))
        assert entity.updated_at == datetime(2099, 1, 1)

    def test_update_empty_body_does_not_change_name(self):
        entity = _entity(name="original")
        repo = _mock_repo(get_by_id=entity, update=entity)
        svc = SearchQueryService(repo)
        svc.update_query(1, QueryUpdate())
        assert entity.name == "original"


    def test_delete_returns_true_when_found(self):
        repo = _mock_repo(delete_by_id=True)
        svc = SearchQueryService(repo)
        assert svc.delete_query(1) is True

    def test_delete_returns_false_when_not_found(self):
        repo = _mock_repo(delete_by_id=False)
        svc = SearchQueryService(repo)
        assert svc.delete_query(999) is False


    def test_bulk_delete_calls_repo(self):
        repo = _mock_repo(delete_by_ids=None)
        svc = SearchQueryService(repo)
        body = BulkDeleteRequest(ids=[1, 2, 3])
        svc.bulk_delete(body)
        repo.delete_by_ids.assert_called_once_with([1, 2, 3])
