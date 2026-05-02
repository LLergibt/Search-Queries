from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from domain.search_query.model import SearchQuery


class TestCreateQuery:
    def test_minimal(self, client: TestClient, make_query):
        r = client.post("/api/queries", json={"name": "my_query"})
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == "my_query"
        assert body["is_active"] is True
        assert body["results_count"] == 0
        assert body["owner"] == "current_user@corp.io"

    def test_all_fields(self, client: TestClient, make_query):
        r = client.post("/api/queries", json={
            "name": "full", "is_active": False, "deadline": "2099-06-01T00:00:00"
        })
        assert r.status_code == 201
        body = r.json()
        assert body["is_active"] is False
        assert body["deadline"].startswith("2099-06-01")

    def test_assigns_id(self, client: TestClient, make_query):
        r = client.post("/api/queries", json={"name": "x"})
        assert r.json()["id"] > 0

    def test_name_empty_fails(self, client: TestClient, make_query):
        assert client.post("/api/queries", json={"name": ""}).status_code == 422

    def test_name_too_long_fails(self, client: TestClient, make_query):
        assert client.post("/api/queries", json={"name": "x" * 256}).status_code == 422

    def test_missing_name_fails(self, client: TestClient, make_query):
        assert client.post("/api/queries", json={}).status_code == 422

    def test_invalid_deadline_fails(self, client: TestClient, make_query):
        assert client.post("/api/queries", json={"name": "x", "deadline": "bad"}).status_code == 422

    def test_null_deadline_allowed(self, client: TestClient, make_query):
        r = client.post("/api/queries", json={"name": "x", "deadline": None})
        assert r.status_code == 201
        assert r.json()["deadline"] is None


class TestListQueries:
    def test_empty_db(self, client: TestClient, make_query):
        r = client.get("/api/queries")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 0
        assert body["items"] == []
        assert body["total_pages"] == 1

    def test_returns_inserted(self, client: TestClient, db_session: Session, make_query):
        make_query(name="q1")
        make_query(name="q2")
        assert client.get("/api/queries").json()["total"] == 2

    def test_defaults(self, client: TestClient, make_query):
        body = client.get("/api/queries").json()
        assert body["page"] == 1
        assert body["page_size"] == 50

    def test_pagination(self, client: TestClient, db_session: Session, make_query):
        for i in range(25):
            make_query(name=f"q_{i:03d}")
        body = client.get("/api/queries?page=1&page_size=10").json()
        assert len(body["items"]) == 10
        assert body["total_pages"] == 3

    def test_second_page(self, client: TestClient, db_session: Session, make_query):
        for i in range(25):
            make_query(name=f"q_{i:03d}")
        assert len(client.get("/api/queries?page=2&page_size=10").json()["items"]) == 10

    def test_last_page_partial(self, client: TestClient, db_session: Session, make_query):
        for i in range(25):
            make_query(name=f"q_{i:03d}")
        assert len(client.get("/api/queries?page=3&page_size=10").json()["items"]) == 5

    def test_page_size_below_min(self, client: TestClient, make_query):
        assert client.get("/api/queries?page_size=5").status_code == 422

    def test_page_size_above_max(self, client: TestClient, make_query):
        assert client.get("/api/queries?page_size=201").status_code == 422

    def test_page_zero_fails(self, client: TestClient, make_query):
        assert client.get("/api/queries?page=0").status_code == 422

    def test_sort_asc(self, client: TestClient, db_session: Session, make_query):
        for name in ["banana", "apple", "cherry"]:
            make_query(name=name)
        names = [i["name"] for i in client.get("/api/queries?sort_by=name&sort_dir=asc&page_size=10").json()["items"]]
        assert names == sorted(names)

    def test_sort_desc(self, client: TestClient, db_session: Session, make_query):
        for name in ["banana", "apple", "cherry"]:
            make_query(name=name)
        names = [i["name"] for i in client.get("/api/queries?sort_by=name&sort_dir=desc&page_size=10").json()["items"]]
        assert names == sorted(names, reverse=True)

    def test_unknown_sort_fallback(self, client: TestClient, make_query):
        assert client.get("/api/queries?sort_by=nonexistent").status_code == 200

    def test_response_schema(self, client: TestClient, db_session: Session, make_query):
        make_query()
        item = client.get("/api/queries?page_size=10").json()["items"][0]
        for field in ("id", "name", "created_at", "updated_at", "is_active",
                      "owner", "deadline", "results_count"):
            assert field in item


class TestUpdateQuery:
    def test_update_name(self, client: TestClient, db_session: Session, make_query):
        q = make_query(name="original")
        r = client.put(f"/api/queries/{q.id}", json={"name": "updated"})
        assert r.status_code == 200
        assert r.json()["name"] == "updated"

    def test_update_is_active(self, client: TestClient, db_session: Session, make_query):
        q = make_query(is_active=True)
        assert client.put(f"/api/queries/{q.id}", json={"is_active": False}).json()["is_active"] is False

    def test_update_deadline(self, client: TestClient, db_session: Session, make_query):
        q = make_query()
        r = client.put(f"/api/queries/{q.id}", json={"deadline": "2099-12-31T00:00:00"})
        assert r.json()["deadline"].startswith("2099-12-31")

    def test_update_partial_leaves_other_fields(self, client: TestClient, db_session: Session, make_query):
        q = make_query(name="keep_me", is_active=True)
        client.put(f"/api/queries/{q.id}", json={"is_active": False})
        item = next(i for i in client.get("/api/queries?page_size=10").json()["items"] if i["id"] == q.id)
        assert item["name"] == "keep_me"
        assert item["is_active"] is False

    def test_update_empty_body_no_op(self, client: TestClient, db_session: Session, make_query):
        q = make_query(name="no_change")
        assert client.put(f"/api/queries/{q.id}", json={}).json()["name"] == "no_change"

    def test_update_not_found(self, client: TestClient, make_query):
        assert client.put("/api/queries/999999", json={"name": "x"}).status_code == 404

    def test_update_name_empty_fails(self, client: TestClient, db_session: Session, make_query):
        q = make_query()
        assert client.put(f"/api/queries/{q.id}", json={"name": ""}).status_code == 422

    def test_update_name_too_long_fails(self, client: TestClient, db_session: Session, make_query):
        q = make_query()
        assert client.put(f"/api/queries/{q.id}", json={"name": "x" * 256}).status_code == 422


class TestDeleteQuery:
    def test_delete_existing(self, client: TestClient, db_session: Session, make_query):
        q = make_query()
        assert client.delete(f"/api/queries/{q.id}").status_code == 204

    def test_delete_removes_from_db(self, client: TestClient, db_session: Session, make_query):
        q = make_query()
        qid = q.id
        client.delete(f"/api/queries/{qid}")
        assert db_session.query(SearchQuery).filter_by(id=qid).first() is None

    def test_delete_not_found(self, client: TestClient, make_query):
        assert client.delete("/api/queries/999999").status_code == 404

    def test_delete_does_not_affect_others(self, client: TestClient, db_session: Session, make_query):
        q1 = make_query(name="keep")
        q2 = make_query(name="remove")
        client.delete(f"/api/queries/{q2.id}")
        assert db_session.query(SearchQuery).filter_by(id=q1.id).first() is not None

    def test_double_delete_returns_404(self, client: TestClient, db_session: Session, make_query):
        q = make_query()
        client.delete(f"/api/queries/{q.id}")
        assert client.delete(f"/api/queries/{q.id}").status_code == 404


class TestBulkDelete:
    def test_multiple(self, client: TestClient, db_session: Session, make_query):
        qs = [make_query(name=f"b{i}") for i in range(5)]
        r = client.request("DELETE", "/api/queries", json={"ids": [q.id for q in qs[:3]]})
        assert r.status_code == 204
        assert db_session.query(SearchQuery).count() == 2

    def test_single(self, client: TestClient, db_session: Session, make_query):
        q = make_query()
        assert client.request("DELETE", "/api/queries", json={"ids": [q.id]}).status_code == 204

    def test_nonexistent_ids_silent(self, client: TestClient, make_query):
        assert client.request("DELETE", "/api/queries", json={"ids": [999888]}).status_code == 204

    def test_empty_ids_fails(self, client: TestClient, make_query):
        assert client.request("DELETE", "/api/queries", json={"ids": []}).status_code == 422

    def test_missing_ids_fails(self, client: TestClient, make_query):
        assert client.request("DELETE", "/api/queries", json={}).status_code == 422

    def test_partial_match(self, client: TestClient, db_session: Session, make_query):
        q1 = make_query(name="keep")
        q2 = make_query(name="gone")
        q1_id, q2_id = q1.id, q2.id
        client.request("DELETE", "/api/queries", json={"ids": [q2_id, 999999]})
        db_session.expire_all()
        assert db_session.query(SearchQuery).filter_by(id=q1_id).first() is not None
        assert db_session.query(SearchQuery).filter_by(id=q2_id).first() is None

    def test_all(self, client: TestClient, db_session: Session, make_query):
        qs = [make_query(name=f"x{i}") for i in range(4)]
        client.request("DELETE", "/api/queries", json={"ids": [q.id for q in qs]})
        assert db_session.query(SearchQuery).count() == 0


class TestIntegration:
    def test_create_then_list(self, client: TestClient, make_query):
        client.post("/api/queries", json={"name": "integration_q"})
        names = [i["name"] for i in client.get("/api/queries?page_size=10").json()["items"]]
        assert "integration_q" in names

    def test_create_update_list(self, client: TestClient, db_session: Session, make_query):
        q = make_query(name="before")
        client.put(f"/api/queries/{q.id}", json={"name": "after"})
        names = [i["name"] for i in client.get("/api/queries?page_size=10").json()["items"]]
        assert "after" in names
        assert "before" not in names

    def test_create_delete_list(self, client: TestClient, db_session: Session, make_query):
        q = make_query(name="ephemeral")
        client.delete(f"/api/queries/{q.id}")
        assert client.get("/api/queries?page_size=10").json()["total"] == 0

    def test_total_pages_overflow(self, client: TestClient, db_session: Session, make_query):
        for i in range(11):
            make_query(name=f"p_{i}")
        assert client.get("/api/queries?page_size=10").json()["total_pages"] == 2

    def test_total_pages_exact_fit(self, client: TestClient, db_session: Session, make_query):
        for i in range(10):
            make_query(name=f"e_{i}")
        assert client.get("/api/queries?page_size=10").json()["total_pages"] == 1
