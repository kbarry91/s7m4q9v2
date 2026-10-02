"""Application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routers import health, readings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Weather Sensor API",
    version="0.1.0",
    summary="Ingest and query weather sensor metrics.",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(readings.router)
