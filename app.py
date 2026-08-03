import uvicorn
from fastapi import FastAPI

from config import get_settings
from core.flights.routes import router as flights_router
from core.health.routes import router as health_router
from core.menus.routes import router as menus_router
from dependencies import lifespan

# Register ORM models on Base.metadata
from core.flights import models as _flights_models  # noqa: F401
from core.menus import models as _menus_models  # noqa: F401


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="REST API for flight meal menu management.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    prefix = settings.api_prefix

    app.include_router(health_router, prefix=prefix)
    app.include_router(flights_router, prefix=prefix)
    app.include_router(menus_router, prefix=prefix)

    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.debug,
    )
