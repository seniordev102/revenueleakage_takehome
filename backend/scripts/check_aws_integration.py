#!/usr/bin/env python3
"""
Verify AWS / LocalStack integration using backend/.env (same logic as GET /health/aws).

Run with the backend virtualenv so boto3 is available:

  cd backend
  .\\.venv\\Scripts\\python.exe scripts\\check_aws_integration.py   # Windows
  # source .venv/bin/activate && python scripts/check_aws_integration.py   # Linux/macOS
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running as script: add backend root to path
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

try:
    import boto3
except ModuleNotFoundError:
    vpy = _BACKEND / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
    print(
        "boto3 is not installed for this Python interpreter.\n"
        "Use the backend venv (after: pip install -r requirements.txt), for example:\n"
        f"  {vpy} scripts\\check_aws_integration.py",
        file=sys.stderr,
    )
    sys.exit(1)
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError

from app.core.aws_clients import _session_kwargs
from app.core.config import clear_settings_cache, get_settings, load_env

# Fast failure when VM / LocalStack is down (default boto3 retries are slow).
_FAST = Config(connect_timeout=5, read_timeout=15, retries={"max_attempts": 2})


def _client(service: str, settings):
    kwargs = _session_kwargs(settings)
    kwargs["config"] = _FAST
    return boto3.client(service, **kwargs)


def main() -> int:
    load_env()
    clear_settings_cache()
    s = get_settings()

    if not s.aws_enabled and not s.bedrock_inference_enabled:
        print(json.dumps({"error": "Set AWS_ENDPOINT_URL and/or BEDROCK_MODEL_ID in backend/.env"}, indent=2))
        return 1

    out: dict = {
        "configured": True,
        "endpoint": s.aws_endpoint_url,
        "region": s.aws_default_region,
        "bedrock_model_id": s.bedrock_model_id,
        "checks": {},
    }

    if s.aws_enabled:
        for name, fn in (
            ("s3_bucket", lambda: _client("s3", s).head_bucket(Bucket=s.s3_bucket_name)),
            ("dynamodb_table", lambda: _client("dynamodb", s).describe_table(TableName=s.dynamodb_table_name)),
        ):
            try:
                fn()
                meta = {"ok": True}
                if name == "s3_bucket":
                    meta["bucket"] = s.s3_bucket_name
                else:
                    meta["table"] = s.dynamodb_table_name
                out["checks"][name] = meta
            except ClientError as e:
                out["checks"][name] = {
                    "ok": False,
                    "error": e.response.get("Error", {}).get("Code", str(e)),
                }
            except (OSError, EndpointConnectionError) as e:
                out["checks"][name] = {"ok": False, "error": str(e)}

    if s.bedrock_model_id:
        try:
            bc = _client("bedrock", s)
            lm = bc.list_foundation_models(maxResults=5)
            out["checks"]["bedrock"] = {
                "ok": True,
                "model_id": s.bedrock_model_id,
                "foundation_models_sample_count": len(lm.get("modelSummaries", [])),
            }
        except ClientError as e:
            out["checks"]["bedrock"] = {
                "ok": False,
                "error": e.response.get("Error", {}).get("Code", str(e)),
            }
        except (OSError, EndpointConnectionError) as e:
            out["checks"]["bedrock"] = {"ok": False, "error": str(e)}

    print(json.dumps(out, indent=2))

    checks = out.get("checks") or {}
    all_ok = all(isinstance(v, dict) and v.get("ok") for v in checks.values())
    if not checks:
        print("\nOVERALL: nothing to check")
        return 1
    print()
    if all_ok:
        print("OVERALL: SUCCESS - all checks passed.")
        return 0
    print("OVERALL: FAILED - at least one check failed (see errors above).")
    _print_failure_hints(checks, s)
    return 2


def _print_failure_hints(checks: dict, s) -> None:
    """Explain common cases: unreachable endpoint vs missing bucket/table."""
    any_conn = False
    for v in checks.values():
        if not isinstance(v, dict):
            continue
        err = str(v.get("error", ""))
        if "Could not connect" in err or "Connection refused" in err:
            any_conn = True
    if any_conn:
        print(
            "Hints (connectivity): Is the VM running LocalStack? Firewall open for port 4566? "
            "Listening on 0.0.0.0, not only 127.0.0.1?"
        )
        return

    s3 = checks.get("s3_bucket") or {}
    ddb = checks.get("dynamodb_table") or {}
    if (s3.get("error") in ("404", "NotFound", "NoSuchBucket")) or s3.get("error") == "404":
        print(
            f"Hints (S3): Bucket '{s.s3_bucket_name}' does not exist in LocalStack yet. Create it, e.g.:\n"
            f'  aws --endpoint-url={s.aws_endpoint_url} s3 mb s3://{s.s3_bucket_name}'
        )
    if ddb.get("error") == "ResourceNotFoundException":
        print(
            f"Hints (DynamoDB): Table '{s.dynamodb_table_name}' does not exist. Create a minimal table, e.g.:\n"
            f"  aws --endpoint-url={s.aws_endpoint_url} dynamodb create-table \\\n"
            f"    --table-name {s.dynamodb_table_name} \\\n"
            "    --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S \\\n"
            "    --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \\\n"
            "    --billing-mode PAY_PER_REQUEST\n"
            "(Adjust key schema to match your single-table design if you already documented GSIs.)"
        )


if __name__ == "__main__":
    raise SystemExit(main())
