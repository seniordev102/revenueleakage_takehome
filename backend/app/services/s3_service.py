from __future__ import annotations

import logging
from typing import Optional

from botocore.exceptions import ClientError

from ..core.aws_clients import s3_client
from ..core.config import Settings, get_settings

log = logging.getLogger(__name__)


def _ensure_bucket(client, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
        return
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code not in ("404", "NoSuchBucket", "403"):
            raise
    client.create_bucket(Bucket=bucket)


def upload_raw_file(
    upload_id: str,
    file_name: str,
    body: bytes,
    content_type: Optional[str],
    *,
    settings: Settings | None = None,
) -> Optional[str]:
    """
    Upload raw bytes to S3. Used with LocalStack or real AWS when AWS_ENDPOINT_URL is set.
    Returns the object key, or None if AWS is not configured.
    """
    s = settings or get_settings()
    if not s.aws_enabled:
        return None

    key = f"uploads/{upload_id}/{file_name}"
    client = s3_client(s)
    try:
        _ensure_bucket(client, s.s3_bucket_name)
        extra: dict = {}
        if content_type:
            extra["ContentType"] = content_type
        client.put_object(Bucket=s.s3_bucket_name, Key=key, Body=body, **extra)
        return key
    except ClientError:
        log.exception("S3 put_object failed (upload_id=%s key=%s)", upload_id, key)
        raise
