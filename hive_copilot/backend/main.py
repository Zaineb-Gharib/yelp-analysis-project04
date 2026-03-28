from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hive_copilot.backend.app.api.routes import router
from hive_copilot.backend.app.core.config import get_settings
from hive_copilot.backend.app.services.hive_execution_service import check_hive_connection
from hive_copilot.backend.app.services.hms_service import check_hms_connection


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="FastAPI backend for Hive Copilot.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def healthcheck() -> dict:
        hive_ok, hive_msg = check_hive_connection()
        hms_ok, hms_msg = check_hms_connection()
        return {
            "status": "ok" if hive_ok and hms_ok else "degraded",
            "mode": settings.frontend_mode,
            "database": settings.hive_database,
            "hive": {"ok": hive_ok, "message": hive_msg},
            "hms": {"ok": hms_ok, "message": hms_msg},
        }

    app.include_router(router, prefix=settings.api_prefix)
    return app


app = create_application()
