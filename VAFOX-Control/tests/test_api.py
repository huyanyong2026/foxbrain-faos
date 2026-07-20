from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoints_are_local_scaffold_only():
    assert client.get("/health/live").json() == {"status": "healthy"}
    assert client.get("/health/ready").json()["mode"] == "scaffold"


def test_server_service_and_deployment_registry_flow():
    server = client.post("/api/v1/servers", json={"name": "local-control-1", "environment": "local", "region": "lab", "endpoint": "https://localhost:8443"})
    assert server.status_code == 201
    service = client.post("/api/v1/services", json={"server_id": server.json()["id"], "name": "registry-api", "version": "0.1.0", "endpoint": "https://localhost:8080"})
    assert service.status_code == 201
    deployment = client.post("/api/v1/deployments", json={"service_id": service.json()["id"], "version": "0.1.0", "artifact_digest": "sha256:" + "a" * 64, "environment": "staging", "change_reference": "CHG-100"})
    assert deployment.status_code == 201


def test_production_deployment_is_rejected():
    response = client.post("/api/v1/deployments", json={"service_id": "00000000-0000-0000-0000-000000000001", "version": "1", "artifact_digest": "sha256:" + "a" * 64, "environment": "production", "change_reference": "CHG-101"})
    assert response.status_code == 422
