"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deephold_api.config import get_settings
from deephold_api.routers import compare, dashboard, series

settings = get_settings()

app = FastAPI(
    title="deephold-app API",
    description="Backend API for the deephold financial data platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(series.router)
app.include_router(dashboard.router)
app.include_router(compare.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "deephold-api", "version": "0.1.0"}
