import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config import get_settings
from core.auth.routes import router as auth_router
from core.flights.routes import router as flights_router
from core.health.routes import router as health_router
from core.logging_config import configure_logging, get_logger
from core.menus.routes import router as menus_router
from core.middleware.request_logging import RequestLoggingMiddleware
from dependencies import lifespan

# Register ORM models on Base.metadata
from core.flights import models as _flights_models  # noqa: F401
from core.menus import models as _menus_models  # noqa: F401

logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

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

    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(health_router, prefix=prefix)
    app.include_router(auth_router, prefix=prefix)
    app.include_router(flights_router, prefix=prefix)
    app.include_router(menus_router, prefix=prefix)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            method=request.method,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

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
