from __future__ import annotations

from typing import Any

import boto3
from botocore.client import BaseClient

from .config import Settings, get_settings


def _session_kwargs(settings: Settings) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "region_name": settings.aws_default_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return kwargs


def boto3_client(service_name: str, settings: Settings | None = None) -> BaseClient:
    """Build a boto3 client; uses single endpoint URL when talking to LocalStack."""
    s = settings or get_settings()
    return boto3.client(service_name, **_session_kwargs(s))


def dynamodb_client(settings: Settings | None = None) -> BaseClient:
    return boto3_client("dynamodb", settings)


def s3_client(settings: Settings | None = None) -> BaseClient:
    return boto3_client("s3", settings)


def bedrock_runtime_client(settings: Settings | None = None) -> BaseClient:
    """Invoke models (Claude, Titan, etc.). Same endpoint as LocalStack edge when configured."""
    return boto3_client("bedrock-runtime", settings)


def bedrock_control_client(settings: Settings | None = None) -> BaseClient:
    """List foundation models, etc. Used for health checks."""
    return boto3_client("bedrock", settings)
