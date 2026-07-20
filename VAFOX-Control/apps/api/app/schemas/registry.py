from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import AnyHttpUrl, BaseModel, Field


class LifecycleStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"
    RETIRED = "retired"


class HealthStatus(StrEnum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ServerRegistration(BaseModel):
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,62}$")
    environment: str = Field(pattern=r"^(local|development|staging|production)$")
    region: str = Field(min_length=2, max_length=64)
    endpoint: AnyHttpUrl
    labels: dict[str, str] = Field(default_factory=dict)


class Server(ServerRegistration):
    id: UUID = Field(default_factory=uuid4)
    status: LifecycleStatus = LifecycleStatus.PENDING
    health_status: HealthStatus = HealthStatus.UNKNOWN
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ServiceRegistration(BaseModel):
    server_id: UUID
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{2,62}$")
    version: str = Field(min_length=1, max_length=128)
    endpoint: AnyHttpUrl
    capabilities: list[str] = Field(default_factory=list)


class Service(ServiceRegistration):
    id: UUID = Field(default_factory=uuid4)
    status: LifecycleStatus = LifecycleStatus.PENDING
    health_status: HealthStatus = HealthStatus.UNKNOWN
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeploymentRegistration(BaseModel):
    service_id: UUID
    version: str = Field(min_length=1, max_length=128)
    artifact_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    environment: str = Field(pattern=r"^(local|development|staging)$")
    change_reference: str = Field(min_length=3, max_length=128)


class Deployment(DeploymentRegistration):
    id: UUID = Field(default_factory=uuid4)
    status: LifecycleStatus = LifecycleStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealthCheck(BaseModel):
    status: HealthStatus
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: int | None = Field(default=None, ge=0)
    detail: str | None = Field(default=None, max_length=500)
