"""Smoke tests for the integrated WASTESENSE API."""
import asyncio
import httpx
from backend.main import app


def request(method: str, path: str, json: dict | None = None) -> httpx.Response:
    async def make_request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, json=json)
    return asyncio.run(make_request())


def test_root_endpoint():
    response = request("GET", "/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_endpoint():
    assert request("GET", "/api/v1/health").status_code == 200


def test_openapi_contains_live_routes():
    paths = app.openapi()["paths"]
    expected = {
        "/api/v1/overview", "/api/v1/machines", "/api/v1/machines/{item_id}",
        "/api/v1/workloads", "/api/v1/waste-events", "/api/v1/alerts",
        "/api/v1/trends", "/api/v1/savings", "/api/v1/replay-results",
        "/api/v1/recommendations", "/api/v1/waste/analyze",
    }
    assert expected.issubset(paths.keys())


def test_overview_is_integrated():
    response = request("GET", "/api/v1/overview")
    assert response.status_code == 200
    assert "total_machines" in response.json()


def test_analyze_rejects_missing_required_fields():
    assert request("POST", "/api/v1/waste/analyze", json={}).status_code == 422


def test_analyze_rejects_invalid_cpu_capacity():
    payload = {"machine_id":"M102", "timestamp":"2026-10-10T14:30:00", "active_tasks":5,
      "workload_type":"COMPUTE", "cpu_capacity":0, "memory_capacity":16,
      "actual_cpu":40, "actual_memory":8}
    assert request("POST", "/api/v1/waste/analyze", json=payload).status_code == 422


def test_ml_analysis_endpoint_runs_saved_models():
    payload = {
        "machine_id": "M102", "timestamp": "2026-10-15T14:30:00",
        "active_tasks": 25, "workload_type": "COMPUTE", "priority": 2,
        "workload_duration": 60, "cpu_capacity": 100, "memory_capacity": 256,
        "actual_cpu": 0.08, "actual_memory": 0.05,
    }
    response = request("POST", "/api/v1/waste/analyze", json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "prediction_completed"
    assert "resources" in response.json()
