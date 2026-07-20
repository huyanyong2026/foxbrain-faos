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


def test_result_management_and_cto_review_flow():
    result = client.post("/api/results", json={
        "task_id": "TASK-2026-001", "executor": "codex", "result_type": "codex_pr",
        "summary": "Adds the review dashboard.", "artifact_url": "https://github.com/vafox/control/pull/1",
        "log_url": "https://ci.vafox.example/logs/1", "test_result": "passed", "risk_level": "medium",
    })
    assert result.status_code == 201
    assert set(result.json()) >= {"task_id", "executor", "result_type", "summary", "artifact_url", "log_url", "test_result", "risk_level", "created_at"}

    reviews = client.get("/api/reviews")
    assert reviews.status_code == 200
    review = next(item for item in reviews.json() if item["id"] == result.json()["id"])
    assert review["status"] == "pending_review"

    approved = client.post(f"/api/reviews/{review['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["approval"] == "approved"
    assert client.post(f"/api/reviews/{review['id']}/approve").status_code == 409


def test_dispatcher_is_design_only():
    response = client.get("/api/dispatcher")
    assert response.status_code == 200
    assert [stage["name"] for stage in response.json()] == ["task", "executor", "result"]
    assert "no external agent is called" in response.json()[1]["phase_one_behavior"]
