from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, IPvAnyAddress


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


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ServerRegistration(BaseModel):
    """A declared server record; registration never contacts the server."""

    hostname: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{0,252}$")
    ip: IPvAnyAddress
    provider: str = Field(min_length=1, max_length=128)
    role: str = Field(min_length=1, max_length=128)
    status: LifecycleStatus = LifecycleStatus.PENDING


class Server(ServerRegistration):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)


class ServiceRegistration(BaseModel):
    server_id: UUID
    service_name: str = Field(pattern=r"^[a-z][a-z0-9-]{2,62}$")
    version: str = Field(min_length=1, max_length=128)
    health_status: HealthStatus = HealthStatus.UNKNOWN


class Service(ServiceRegistration):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)


class DeploymentRegistration(BaseModel):
    version: str = Field(min_length=1, max_length=128)
    deploy_time: datetime = Field(default_factory=utc_now)
    operator: str = Field(min_length=1, max_length=128)
    rollback_version: str | None = Field(default=None, min_length=1, max_length=128)


class Deployment(DeploymentRegistration):
    id: UUID = Field(default_factory=uuid4)


class HealthCheck(BaseModel):
    status: HealthStatus
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: int | None = Field(default=None, ge=0)
    detail: str | None = Field(default=None, max_length=500)
