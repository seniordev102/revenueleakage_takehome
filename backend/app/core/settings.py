from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    environment: str
    log_level: str
    openai_api_key: str | None
    openai_model: str
    openai_timeout_seconds: int
    openai_base_url: str


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    load_dotenv()
    return AppSettings(
        app_name=os.getenv("APP_NAME", "Revenue Leakage Detection API"),
        environment=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_timeout_seconds=_get_int("OPENAI_TIMEOUT_SECONDS", 30),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions"),
    )
