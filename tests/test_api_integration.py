from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from backend.db.dependencies import get_db
from backend.main import app
from database.base import engine


@pytest.fixture
def client():
    """
    Run each API test inside an outer database transaction.

    Endpoint-level commits use savepoints, allowing the outer
    transaction to roll back all test changes afterward.
    """
    connection = engine.connect()
    transaction = connection.begin()

    TestSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)

        if transaction.is_active:
            transaction.rollback()

        connection.close()


def create_machine(client: TestClient) -> dict:
    """Create a machine with a unique name for the current test."""
    response = client.post(
        "/api/v1/machines",
        json={
            "machine_name": f"api-test-{uuid4().hex[:12]}",
            "cpu_capacity": 100,
            "memory_capacity": 64,
            "status": "active",
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_database_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health/database")

    assert response.status_code == 200


def test_create_and_retrieve_machine(client: TestClient):
    machine = create_machine(client)
    machine_id = machine["machine_id"]

    assert machine["status"] == "active"
    assert machine["machine_name"].startswith("api-test-")

    response = client.get(f"/api/v1/machines/{machine_id}")

    assert response.status_code == 200
    assert response.json()["machine_id"] == machine_id
    assert response.json()["machine_name"] == machine["machine_name"]


def test_list_machines(client: TestClient):
    machine = create_machine(client)

    response = client.get(
        "/api/v1/machines",
        params={"status": "active", "limit": 100},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        item["machine_id"] == machine["machine_id"]
        for item in response.json()
    )


def test_update_machine(client: TestClient):
    machine = create_machine(client)
    machine_id = machine["machine_id"]

    response = client.patch(
        f"/api/v1/machines/{machine_id}",
        json={"status": "maintenance"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "maintenance"


def test_machine_not_found(client: TestClient):
    response = client.get("/api/v1/machines/999999999")

    assert response.status_code == 404


def test_invalid_machine_input(client: TestClient):
    response = client.post(
        "/api/v1/machines",
        json={
            "machine_name": "",
            "cpu_capacity": -1,
            "memory_capacity": 64,
            "status": "unknown",
        },
    )

    assert response.status_code == 422


def test_create_and_list_workload(client: TestClient):
    machine = create_machine(client)

    start_time = datetime.now(timezone.utc).isoformat()

    response = client.post(
        "/api/v1/workloads",
        json={
            "machine_id": machine["machine_id"],
            "workload_type": "api_integration_test",
            "priority": "normal",
            "start_time": start_time,
            "active_tasks": 3,
        },
    )

    assert response.status_code == 201, response.text

    workload = response.json()

    assert workload["machine_id"] == machine["machine_id"]
    assert workload["workload_type"] == "api_integration_test"

    list_response = client.get(
        "/api/v1/workloads",
        params={"machine_id": machine["machine_id"]},
    )

    assert list_response.status_code == 200
    assert any(
        item["workload_id"] == workload["workload_id"]
        for item in list_response.json()
    )


def test_workload_rejects_end_time_before_start_time(
    client: TestClient,
):
    machine = create_machine(client)

    response = client.post(
        "/api/v1/workloads",
        json={
            "machine_id": machine["machine_id"],
            "workload_type": "invalid_time_test",
            "priority": "normal",
            "start_time": "2026-10-10T12:00:00+00:00",
            "end_time": "2026-10-10T11:00:00+00:00",
            "active_tasks": 1,
        },
    )

    assert response.status_code == 422


def create_workload(client: TestClient, machine_id: int) -> dict:
    response = client.post(
        "/api/v1/workloads",
        json={
            "machine_id": machine_id,
            "workload_type": "api_integration_test",
            "priority": "normal",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "active_tasks": 2,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_waste_event(
    client: TestClient,
    machine_id: int,
    workload_id: int,
) -> dict:
    response = client.post(
        "/api/v1/waste-events",
        json={
            "machine_id": machine_id,
            "workload_id": workload_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "waste_score": 82.5,
            "severity": "high",
            "waste_type": "excess_cpu",
            "confidence": 0.94,
            "persistent": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_measurement_creation_and_retrieval(client: TestClient):
    machine = create_machine(client)
    workload = create_workload(client, machine["machine_id"])

    response = client.post(
        "/api/v1/measurements",
        json={
            "machine_id": machine["machine_id"],
            "workload_id": workload["workload_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actual_cpu": 75,
            "actual_memory": 40,
            "actual_power": 120,
        },
    )

    assert response.status_code == 201, response.text
    measurement = response.json()

    assert measurement["machine_id"] == machine["machine_id"]
    assert measurement["workload_id"] == workload["workload_id"]

    fetched = client.get(
        f"/api/v1/measurements/{measurement['measurement_id']}"
    )
    assert fetched.status_code == 200
    assert fetched.json()["measurement_id"] == measurement["measurement_id"]


def test_waste_event_creation_and_filtering(client: TestClient):
    machine = create_machine(client)
    workload = create_workload(client, machine["machine_id"])
    waste = create_waste_event(
        client, machine["machine_id"], workload["workload_id"]
    )

    assert waste["severity"] == "high"
    assert waste["persistent"] is True

    response = client.get(
        "/api/v1/waste-events",
        params={
            "machine_id": machine["machine_id"],
            "severity": "high",
        },
    )

    assert response.status_code == 200
    assert any(
        item["waste_id"] == waste["waste_id"]
        for item in response.json()
    )


def test_alert_creation_and_status_lifecycle(client: TestClient):
    machine = create_machine(client)
    workload = create_workload(client, machine["machine_id"])
    waste = create_waste_event(
        client, machine["machine_id"], workload["workload_id"]
    )

    response = client.post(
        "/api/v1/alerts",
        json={
            "waste_id": waste["waste_id"],
            "severity": "high",
            "message": "Excessive CPU utilization detected.",
        },
    )

    assert response.status_code == 201, response.text
    alert = response.json()
    alert_id = alert["alert_id"]

    assert alert["status"] == "open"

    update = client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "acknowledged"},
    )
    assert update.status_code == 200, update.text
    assert update.json()["status"] == "acknowledged"

    resolve = client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "resolved"},
    )
    assert resolve.status_code == 200, resolve.text
    assert resolve.json()["status"] == "resolved"
    assert resolve.json()["resolved_at"] is not None


def test_saving_creation_and_duplicate_protection(client: TestClient):
    machine = create_machine(client)
    workload = create_workload(client, machine["machine_id"])
    waste = create_waste_event(
        client, machine["machine_id"], workload["workload_id"]
    )

    payload = {
        "waste_id": waste["waste_id"],
        "cpu_saving": 10,
        "memory_saving": 5,
        "power_saving": 15,
        "cost_saving": 25,
    }

    response = client.post("/api/v1/savings", json=payload)
    assert response.status_code == 201, response.text

    duplicate = client.post("/api/v1/savings", json=payload)
    assert duplicate.status_code == 409, duplicate.text


def test_replay_result_creation_and_duplicate_protection(
    client: TestClient,
):
    machine = create_machine(client)
    workload = create_workload(client, machine["machine_id"])
    waste = create_waste_event(
        client, machine["machine_id"], workload["workload_id"]
    )

    payload = {
        "waste_id": waste["waste_id"],
        "actual_cpu": 80,
        "expected_cpu": 50,
        "actual_power": 120,
        "expected_power": 80,
        "estimated_saving": 40,
    }

    response = client.post("/api/v1/replay-results", json=payload)
    assert response.status_code == 201, response.text

    duplicate = client.post("/api/v1/replay-results", json=payload)
    assert duplicate.status_code == 409, duplicate.text


def test_recommendation_creation_and_retrieval(client: TestClient):
    machine = create_machine(client)
    workload = create_workload(client, machine["machine_id"])
    waste = create_waste_event(
        client, machine["machine_id"], workload["workload_id"]
    )

    response = client.post(
        "/api/v1/recommendations",
        json={
            "waste_id": waste["waste_id"],
            "recommendation": "Reduce CPU allocation during idle periods.",
            "resource": "cpu",
            "current_value": 80,
            "suggested_value": 50,
            "estimated_benefit": 30,
        },
    )

    assert response.status_code == 201, response.text
    recommendation = response.json()

    fetched = client.get(
        f"/api/v1/recommendations/{recommendation['recommendation_id']}"
    )

    assert fetched.status_code == 200
    assert fetched.json()["recommendation_id"] == recommendation[
        "recommendation_id"
    ]
    assert fetched.json()["resource"] == "cpu"