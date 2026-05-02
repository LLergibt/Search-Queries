from datetime import datetime

import pytest
from pydantic import ValidationError

from domain.search_query.schemas import (
    BulkDeleteRequest,
    QueryCreate,
    QueryUpdate,
)


class TestQueryCreate:
    def test_valid_minimal(self):
        q = QueryCreate(name="test")
        assert q.name == "test"
        assert q.is_active is True
        assert q.deadline is None

    def test_valid_full(self):
        dl = datetime(2099, 1, 1)
        q = QueryCreate(name="full", is_active=False, deadline=dl)
        assert q.is_active is False
        assert q.deadline == dl

    def test_name_empty_raises(self):
        with pytest.raises(ValidationError):
            QueryCreate(name="")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            QueryCreate(name="x" * 256)

    def test_name_max_length_ok(self):
        QueryCreate(name="x" * 255)

    def test_name_missing_raises(self):
        with pytest.raises(ValidationError):
            QueryCreate()


class TestQueryUpdate:
    def test_all_none_is_valid(self):
        q = QueryUpdate()
        assert q.name is None
        assert q.is_active is None
        assert q.deadline is None

    def test_name_empty_raises(self):
        with pytest.raises(ValidationError):
            QueryUpdate(name="")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            QueryUpdate(name="x" * 256)

    def test_partial_update_valid(self):
        q = QueryUpdate(is_active=False)
        assert q.is_active is False
        assert q.name is None


class TestBulkDeleteRequest:
    def test_valid(self):
        b = BulkDeleteRequest(ids=[1, 2, 3])
        assert b.ids == [1, 2, 3]

    def test_empty_list_raises(self):
        with pytest.raises(ValidationError):
            BulkDeleteRequest(ids=[])

    def test_missing_ids_raises(self):
        with pytest.raises(ValidationError):
            BulkDeleteRequest()
