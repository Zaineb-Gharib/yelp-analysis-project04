import uvicorn

from hive_copilot.backend.app.core.config import get_settings


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "hive_copilot.backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
