import pytest
from sqlalchemy.orm import Session
from datetime import datetime


from domain.search_query.model import SearchQuery


class TestSearchQueryModel:
    def test_create_and_retrieve(self, db_session: Session, make_query):
        q = make_query(name="model_test")
        fetched = db_session.query(SearchQuery).filter_by(id=q.id).first()
        assert fetched is not None
        assert fetched.name == "model_test"

    def test_default_is_active_true(self, db_session: Session, make_query):
        q = make_query()
        assert q.is_active is True

    def test_default_results_count_zero(self, db_session: Session, make_query):
        q = make_query()
        assert q.results_count == 0

    def test_deadline_nullable(self, db_session: Session, make_query):
        q = make_query(deadline=None)
        assert q.deadline is None

    def test_deadline_stored(self, db_session: Session, make_query):
        dl = datetime(2099, 1, 1)
        q = make_query(deadline=dl)
        assert q.deadline == dl

    def test_update_name(self, db_session: Session, make_query):
        q = make_query(name="old_name")
        q.name = "new_name"
        db_session.commit()
        db_session.refresh(q)
        assert q.name == "new_name"

    def test_delete(self, db_session: Session, make_query):
        q = make_query()
        qid = q.id
        db_session.delete(q)
        db_session.commit()
        assert db_session.query(SearchQuery).filter_by(id=qid).first() is None

    def test_repr(self, db_session: Session, make_query):
        q = make_query(name="repr_test")
        assert "repr_test" in repr(q)
