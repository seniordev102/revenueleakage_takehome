from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.analysis import router as analysis_router
from .api.dashboard import router as dashboard_router
from .api.records import router as records_router
from .api.uploads import router as uploads_router
from .core.exceptions import AppError
from .core.logging import configure_logging, get_logger
from .core.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    app = FastAPI(title=settings.app_name)
    app.state.settings = settings

    app.include_router(uploads_router, prefix="/uploads", tags=["uploads"])
    app.include_router(records_router, prefix="/records", tags=["records"])
    app.include_router(analysis_router, tags=["analysis"])
    app.include_router(dashboard_router, tags=["dashboard"])

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.error_code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "Internal server error"}},
        )

    logger.info("Application initialized in %s environment", settings.environment)

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()

