"""Application entry point."""

from fastapi import FastAPI

from app.routers import health

app = FastAPI(
    title="Weather Sensor API",
    version="0.1.0",
    summary="Ingest and query weather sensor metrics.",
)

app.include_router(health.router)
