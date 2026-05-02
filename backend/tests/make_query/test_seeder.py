import pytest
from sqlalchemy.orm import Session

from domain.search_query.model import SearchQuery
from infrastructure.seeder import seed_db


class TestSeeder:
    def test_seeds_to_target(self, db_session: Session):
        seed_db(db_session, target=10)
        assert db_session.query(SearchQuery).count() == 10

    def test_is_idempotent(self, db_session: Session):
        seed_db(db_session, target=5)
        seed_db(db_session, target=5)
        assert db_session.query(SearchQuery).count() == 5

    def test_incremental_top_up(self, db_session: Session):
        seed_db(db_session, target=3)
        seed_db(db_session, target=7)
        assert db_session.query(SearchQuery).count() == 7

    def test_generated_rows_valid(self, db_session: Session):
        seed_db(db_session, target=5)
        for row in db_session.query(SearchQuery).all():
            assert row.name
            assert row.owner
            assert row.created_at is not None
            assert row.updated_at is not None
            assert isinstance(row.is_active, bool)
            assert row.results_count >= 0
