from typing import List, Optional

from core.utils import utcnow
from domain.search_query.model import SearchQuery
from domain.search_query.repository import SearchQueryRepository
from domain.search_query.schemas import (
    BulkDeleteRequest,
    PagedResponse,
    QueryCreate,
    QueryOut,
    QueryUpdate,
)


class SearchQueryService:
    def __init__(self, repo: SearchQueryRepository) -> None:
        self._repo = repo

    def list_queries(
        self,
        *,
        page: int,
        page_size: int,
        sort_by: str,
        sort_dir: str,
    ) -> PagedResponse:
        total = self._repo.count()
        items = self._repo.list_paginated(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        return PagedResponse(
            items       = items,
            total       = total,
            page        = page,
            page_size   = page_size,
            total_pages = max(1, (total + page_size - 1) // page_size),
        )

    def create_query(self, data: QueryCreate, *, owner: str) -> SearchQuery:
        entity = SearchQuery(
            name          = data.name,
            is_active     = data.is_active,
            deadline      = data.deadline,
            owner         = owner,
            results_count = 0,
        )
        return self._repo.add(entity)

    def update_query(self, query_id: int, data: QueryUpdate) -> Optional[SearchQuery]:
        entity = self._repo.get_by_id(query_id)
        if entity is None:
            return None

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(entity, field, value)
        entity.updated_at = utcnow()

        return self._repo.update(entity)

    def delete_query(self, query_id: int) -> bool:
        return self._repo.delete_by_id(query_id)

    def bulk_delete(self, body: BulkDeleteRequest) -> None:
        self._repo.delete_by_ids(body.ids)
