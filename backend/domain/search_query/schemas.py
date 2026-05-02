from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field



class QueryCreate(BaseModel):
    name:      str                = Field(..., min_length=1, max_length=255)
    is_active: bool               = True
    deadline:  Optional[datetime] = None


class QueryUpdate(BaseModel):
    name:      Optional[str]      = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool]     = None
    deadline:  Optional[datetime] = None



class QueryOut(BaseModel):
    id:            int
    name:          str
    created_at:    datetime
    updated_at:    datetime
    is_active:     bool
    owner:         str
    deadline:      Optional[datetime]
    results_count: int

    model_config = {"from_attributes": True}


class PagedResponse(BaseModel):
    items:       List[QueryOut]
    total:       int
    page:        int
    page_size:   int
    total_pages: int



class BulkDeleteRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1)
