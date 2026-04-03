from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def _backend_root() -> Path:
    # app/core/config.py -> parents[2] == backend/
    return Path(__file__).resolve().parents[2]


def load_env() -> None:
    """Load backend/.env if present (does not override existing env vars)."""
    env_file = _backend_root() / ".env"
    if env_file.is_file():
        load_dotenv(env_file, override=False)


@dataclass(frozen=True)
class Settings:
    """Runtime settings; LocalStack-friendly when AWS_ENDPOINT_URL is set."""

    aws_endpoint_url: str | None
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str
    s3_bucket_name: str
    dynamodb_table_name: str
    # e.g. anthropic.claude-3-haiku-20240307-v1:0 — when set, BedrockService uses bedrock-runtime
    bedrock_model_id: str | None

    @property
    def aws_enabled(self) -> bool:
        return bool(self.aws_endpoint_url)

    @property
    def bedrock_inference_enabled(self) -> bool:
        return bool(self.bedrock_model_id)


@lru_cache
def get_settings() -> Settings:
    load_env()
    endpoint = os.getenv("AWS_ENDPOINT_URL", "").strip() or None
    bedrock_mid = os.getenv("BEDROCK_MODEL_ID", "").strip() or None
    return Settings(
        aws_endpoint_url=endpoint,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        aws_default_region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        s3_bucket_name=os.getenv("S3_BUCKET_NAME", "revenue-leakage-uploads"),
        dynamodb_table_name=os.getenv("DYNAMODB_TABLE_NAME", "RevenueLeakage"),
        bedrock_model_id=bedrock_mid,
    )


def clear_settings_cache() -> None:
    """For tests that mutate environment between runs."""
    get_settings.cache_clear()
