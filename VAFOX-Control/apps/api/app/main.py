from fastapi import FastAPI

from app.routers.registries import router as registries_router
from app.schemas.registry import HealthStatus

app = FastAPI(title="VAFOX Control API", version="v1", openapi_url="/api/v1/openapi.json")
app.include_router(registries_router, prefix="/api")


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": HealthStatus.HEALTHY}


@app.get("/health/ready", tags=["health"])
def readiness() -> dict[str, str]:
    # Deliberately does not reach production systems in V1.
    return {"status": HealthStatus.HEALTHY, "mode": "local-only"}
