from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv


load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Hive Copilot")
    api_prefix: str = os.getenv("API_PREFIX", "/api")
    backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    streamlit_backend_url: str = os.getenv(
        "STREAMLIT_BACKEND_URL",
        "http://127.0.0.1:8000",
    )
    frontend_mode: str = os.getenv("FRONTEND_MODE", "mock").lower()

    hive_host: str = os.getenv("HIVE_HOST", "localhost")
    hive_port: int = int(os.getenv("HIVE_PORT", "10000"))
    hive_database: str = os.getenv("HIVE_DATABASE", "default")
    hive_username: str = os.getenv("HIVE_USERNAME", "")
    hive_password: str = os.getenv("HIVE_PASSWORD", "")
    hive_auth: str = os.getenv("HIVE_AUTH", "NONE").upper()
    hive_use_ssl: bool = _env_bool("HIVE_USE_SSL", False)
    hive_kerberos_service: str = os.getenv("HIVE_KERBEROS_SERVICE", "")

    hms_host: str = os.getenv("HMS_HOST", "localhost")
    hms_port: int = int(os.getenv("HMS_PORT", "9083"))
    hms_use_ssl: bool = _env_bool("HMS_USE_SSL", False)
    hms_auth: str = os.getenv("HMS_AUTH", "NONE").upper()
    hms_username: str = os.getenv("HMS_USERNAME", "")
    hms_password: str = os.getenv("HMS_PASSWORD", "")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def validate_runtime_settings(settings: Settings) -> None:
    if settings.frontend_mode not in {"mock", "api"}:
        raise ValueError("FRONTEND_MODE must be either 'mock' or 'api'")

    if settings.frontend_mode != "api":
        return

    if not settings.hive_host:
        raise ValueError("HIVE_HOST is required when FRONTEND_MODE=api")
    if not settings.hive_database:
        raise ValueError("HIVE_DATABASE is required when FRONTEND_MODE=api")
    if not settings.hms_host:
        raise ValueError("HMS_HOST is required when FRONTEND_MODE=api")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    validate_runtime_settings(settings)
    return settings
