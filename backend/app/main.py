from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_queue_client
from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.workers.queue import QueueClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="AlphaRadar Backend", version="0.1.0", lifespan=lifespan)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "alpharadar-backend"}

    @app.get("/ready", tags=["health"])
    def ready(
        db: Session = Depends(get_db),
        queue: QueueClient = Depends(get_queue_client),
    ) -> dict[str, dict[str, str] | str]:
        db.execute(text("SELECT 1"))
        queue.ping()
        return {"status": "ready", "checks": {"database": "ok", "queue": "ok"}}

    return app


app = create_app()
