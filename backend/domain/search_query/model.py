from sqlalchemy import Boolean, Column, DateTime, Integer, String

from core.database import Base
from core.utils import utcnow


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(255), nullable=False, index=True)
    created_at    = Column(DateTime, default=utcnow, nullable=False)
    updated_at    = Column(DateTime, default=utcnow, nullable=False)
    is_active     = Column(Boolean, default=True,  nullable=False)
    owner         = Column(String(255), nullable=False)
    deadline      = Column(DateTime, nullable=True)
    results_count = Column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<SearchQuery id={self.id} name={self.name!r}>"
