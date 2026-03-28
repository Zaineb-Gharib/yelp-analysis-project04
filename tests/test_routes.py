import os

os.environ["FRONTEND_MODE"] = "mock"

from fastapi.testclient import TestClient

from hive_copilot.backend.main import create_application


def _fake_plan(prompt, schema_context):
    return type(
        "QueryPlan",
        (),
        {
            "key": "query",
            "sql": "SELECT 1 AS value",
            "summary": "stub",
        },
    )()


def _fake_execute(plan_key, sql):
    return ([{"value": "1"}], {"has_chart": False})


def test_healthcheck():
    client = TestClient(create_application())
    resp = client.get("/health")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("status") == "ok"


def test_schema():
    client = TestClient(create_application())
    resp = client.get("/api/schema")
    assert resp.status_code == 200
    data = resp.json()
    assert "tables" in data and isinstance(data["tables"], list)


def test_query_uses_stubbed_services(monkeypatch):
    import hive_copilot.backend.app.api.routes as routes

    monkeypatch.setattr(routes, "generate_query_plan", _fake_plan)
    monkeypatch.setattr(routes, "execute_query_plan", _fake_execute)

    client = TestClient(create_application())
    resp = client.post("/api/query", json={"prompt": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == [{"value": "1"}]
    assert data["sql"] == "SELECT 1 AS value"
