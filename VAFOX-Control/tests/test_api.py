from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoints_are_local_scaffold_only():
    assert client.get("/health/live").json() == {"status": "healthy"}
    assert client.get("/health/ready").json()["mode"] == "local-only"


def test_server_service_and_deployment_registry_flow():
    server = client.post("/api/servers", json={"hostname": "local-control-1", "ip": "127.0.0.1", "provider": "local", "role": "control-plane", "status": "active"})
    assert server.status_code == 201
    assert set(server.json()) >= {"hostname", "ip", "provider", "role", "status"}
    service = client.post("/api/services", json={"server_id": server.json()["id"], "service_name": "registry-api", "version": "0.1.0", "health_status": "healthy"})
    assert service.status_code == 201
    assert set(service.json()) >= {"service_name", "server_id", "version", "health_status"}
    deployment = client.post("/api/deployments", json={"version": "0.1.0", "deploy_time": "2026-07-20T12:00:00Z", "operator": "local-operator", "rollback_version": "0.0.9"})
    assert deployment.status_code == 201
    assert set(deployment.json()) >= {"version", "deploy_time", "operator", "rollback_version"}
    assert len(client.get("/api/servers").json()) >= 1
    assert len(client.get("/api/services").json()) >= 1
    assert len(client.get("/api/deployments").json()) >= 1


def test_unknown_server_is_rejected_for_service_registration():
    response = client.post("/api/services", json={"server_id": "00000000-0000-0000-0000-000000000001", "service_name": "registry-api", "version": "1"})
    assert response.status_code == 404


def test_result_submission_review_and_task_result_query():
    task_id = "00000000-0000-0000-0000-000000000010"
    submitted = client.post("/api/results", json={
        "task_id": task_id,
        "executor": "codex",
        "result_type": "delivery",
        "summary": "Implemented the reviewed change.",
        "artifact_url": "https://artifacts.example/result/10",
        "log_url": "https://logs.example/result/10",
        "test_result": "pytest: 12 passed",
        "risk_level": "medium",
    })
    assert submitted.status_code == 201
    result = submitted.json()
    assert result["approval_status"] == "review_pending"
    assert result["executor"] == "codex"

    task_results = client.get(f"/api/tasks/{task_id}/results")
    assert task_results.status_code == 200
    assert [item["id"] for item in task_results.json()] == [result["id"]]

    approved = client.post(f"/api/results/{result['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["approval_status"] == "cto_approved"


def test_result_submission_rejects_unapproved_executor():
    response = client.post("/api/results", json={
        "task_id": "00000000-0000-0000-0000-000000000011",
        "executor": "untrusted-agent",
        "result_type": "report",
        "summary": "This must not be accepted.",
    })
    assert response.status_code == 422
