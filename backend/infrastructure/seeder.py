import random
import string
from datetime import timedelta

from sqlalchemy.orm import Session

from core.utils import utcnow
from domain.search_query.model import SearchQuery


_OWNERS  = [f"user_{i:03d}@corp.io" for i in range(1, 51)]
_DOMAINS = ["sales", "marketing", "tech", "hr", "finance", "ops", "legal", "it", "dev", "qa"]
_KINDS   = ["report", "audit", "scan", "monitor", "track", "watch", "check", "alert", "survey"]

_BATCH_SIZE = 2_000


def _rand(n: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def _make_row(now) -> SearchQuery:
    days_back = random.randint(0, 730)
    created   = now - timedelta(days=days_back, seconds=random.randint(0, 86_400))
    updated   = min(
        created + timedelta(seconds=random.randint(0, days_back * 3_600 + 1)),
        now,
    )
    r = random.random()
    if r < 0.30:
        deadline = now - timedelta(days=random.randint(1, 90))
    elif r < 0.90:
        deadline = now + timedelta(days=random.randint(1, 180))
    else:
        deadline = None

    return SearchQuery(
        name          = f"{random.choice(_DOMAINS)}_{random.choice(_KINDS)}_{_rand(6)}",
        created_at    = created,
        updated_at    = updated,
        is_active     = random.random() > 0.25,
        owner         = random.choice(_OWNERS),
        deadline      = deadline,
        results_count = random.randint(0, 1_000_000),
    )


def seed_db(db: Session, *, target: int) -> None:
    from sqlalchemy import func
    existing = db.query(func.count(SearchQuery.id)).scalar()
    if existing >= target:
        return

    now   = utcnow()
    batch: list[SearchQuery] = []

    for _ in range(target - existing):
        batch.append(_make_row(now))
        if len(batch) == _BATCH_SIZE:
            db.bulk_save_objects(batch)
            db.commit()
            batch = []

    if batch:
        db.bulk_save_objects(batch)
        db.commit()
