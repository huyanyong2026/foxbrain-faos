from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.registry import (Deployment, DeploymentRegistration, HealthCheck,
                                  LifecycleStatus, Server, ServerRegistration,
                                  Service, ServiceRegistration)
from app.store import deployments, servers, services

router = APIRouter(tags=["registries"])


def require(item, item_id: UUID):
    if item is None:
        raise HTTPException(status_code=404, detail=f"Registry item {item_id} was not found")
    return item


@router.post("/servers", response_model=Server, status_code=status.HTTP_201_CREATED)
def register_server(request: ServerRegistration) -> Server:
    return servers.create(Server(**request.model_dump()))


@router.get("/servers", response_model=list[Server])
def list_servers() -> list[Server]:
    return list(servers.list())


@router.post("/servers/{server_id}/health", response_model=Server)
def report_server_health(server_id: UUID, check: HealthCheck) -> Server:
    server = require(servers.get(server_id), server_id)
    # The V1 server record intentionally has no remote-probe capability.
    # Recording a report only confirms that a registered server remains active.
    return servers.replace(server.model_copy(update={"status": LifecycleStatus.ACTIVE}))


@router.post("/services", response_model=Service, status_code=status.HTTP_201_CREATED)
def register_service(request: ServiceRegistration) -> Service:
    require(servers.get(request.server_id), request.server_id)
    return services.create(Service(**request.model_dump()))


@router.get("/services", response_model=list[Service])
def list_services() -> list[Service]:
    return list(services.list())


@router.post("/services/{service_id}/health", response_model=Service)
def report_service_health(service_id: UUID, check: HealthCheck) -> Service:
    service = require(services.get(service_id), service_id)
    return services.replace(service.model_copy(update={"health_status": check.status}))


@router.post("/deployments", response_model=Deployment, status_code=status.HTTP_201_CREATED)
def register_deployment(request: DeploymentRegistration) -> Deployment:
    return deployments.create(Deployment(**request.model_dump()))


@router.get("/deployments", response_model=list[Deployment])
def list_deployments() -> list[Deployment]:
    return list(deployments.list())
