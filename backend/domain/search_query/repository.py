from typing import List, Optional

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session

from domain.search_query.model import SearchQuery


_SORTABLE: dict[str, object] = {
    "name":          SearchQuery.name,
    "created_at":    SearchQuery.created_at,
    "updated_at":    SearchQuery.updated_at,
    "is_active":     SearchQuery.is_active,
    "owner":         SearchQuery.owner,
    "deadline":      SearchQuery.deadline,
    "results_count": SearchQuery.results_count,
}


class SearchQueryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db


    def count(self) -> int:
        return self._db.query(func.count(SearchQuery.id)).scalar()

    def get_by_id(self, query_id: int) -> Optional[SearchQuery]:
        return self._db.query(SearchQuery).filter(SearchQuery.id == query_id).first()

    def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        sort_by: str,
        sort_dir: str,
    ) -> List[SearchQuery]:
        col   = _SORTABLE.get(sort_by, SearchQuery.created_at)
        order = desc(col) if sort_dir == "desc" else asc(col)

        return (
            self._db.query(SearchQuery)
            .order_by(order)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )


    def add(self, entity: SearchQuery) -> SearchQuery:
        self._db.add(entity)
        self._db.commit()
        self._db.refresh(entity)
        return entity

    def update(self, entity: SearchQuery) -> SearchQuery:
        self._db.commit()
        self._db.refresh(entity)
        return entity

    def delete_by_id(self, query_id: int) -> bool:
        deleted = (
            self._db.query(SearchQuery)
            .filter(SearchQuery.id == query_id)
            .delete()
        )
        self._db.commit()
        return bool(deleted)

    def delete_by_ids(self, ids: List[int]) -> None:
        self._db.query(SearchQuery).filter(SearchQuery.id.in_(ids)).delete(
            synchronize_session=False
        )
        self._db.commit()
