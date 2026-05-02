from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from domain.search_query.repository import SearchQueryRepository
from domain.search_query.schemas import (
    BulkDeleteRequest,
    PagedResponse,
    QueryCreate,
    QueryOut,
    QueryUpdate,
)
from domain.search_query.service import SearchQueryService

router = APIRouter(prefix="/api/queries", tags=["Search Queries"])

_CURRENT_USER = "current_user@corp.io"


def get_service(db: Session = Depends(get_db)) -> SearchQueryService:
    return SearchQueryService(SearchQueryRepository(db))


@router.get("", response_model=PagedResponse)
def list_queries(
    page:      int = Query(1,   ge=1),
    page_size: int = Query(50,  ge=10, le=200),
    sort_by:   str = Query("created_at"),
    sort_dir:  str = Query("desc"),
    svc: SearchQueryService = Depends(get_service),
):
    return svc.list_queries(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.post("", response_model=QueryOut, status_code=201)
def create_query(
    data: QueryCreate,
    svc: SearchQueryService = Depends(get_service),
):
    return svc.create_query(data, owner=_CURRENT_USER)


@router.put("/{query_id}", response_model=QueryOut)
def update_query(
    query_id: int,
    data: QueryUpdate,
    svc: SearchQueryService = Depends(get_service),
):
    result = svc.update_query(query_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.delete("/{query_id}", status_code=204)
def delete_query(
    query_id: int,
    svc: SearchQueryService = Depends(get_service),
):
    if not svc.delete_query(query_id):
        raise HTTPException(status_code=404, detail="Not found")


@router.delete("", status_code=204)
def bulk_delete(
    body: BulkDeleteRequest,
    svc: SearchQueryService = Depends(get_service),
):
    svc.bulk_delete(body)
