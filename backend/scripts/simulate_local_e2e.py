#!/usr/bin/env python3
"""
End-to-end local simulation: call the running FastAPI app (S3 + in-memory + DynamoDB when configured).

Prerequisites:
  1. LocalStack running; bucket + DynamoDB table created (see README).
  2. backend/.env with AWS_ENDPOINT_URL (and optional BEDROCK_MODEL_ID).
  3. API server:  uvicorn app.main:app --reload --port 8000

Usage (from backend/, venv active):
  python scripts/simulate_local_e2e.py
  python scripts/simulate_local_e2e.py --base-url http://127.0.0.1:8000 --sample path/to/sample_billing.json

Optional: after a successful upload, scans DynamoDB (same .env as the API) and prints item counts.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
_REPO_ROOT = _BACKEND.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


def main() -> int:
    try:
        import httpx
    except ModuleNotFoundError:
        print("Install backend deps: pip install -r requirements.txt", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(description="Local E2E: health, upload sample, records, dashboard")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API base URL")
    parser.add_argument(
        "--sample",
        type=Path,
        default=_REPO_ROOT / "sample_data" / "sample_billing.json",
        help="JSON billing file to upload",
    )
    args = parser.parse_args()

    if not args.sample.is_file():
        print(f"Sample file not found: {args.sample}", file=sys.stderr)
        return 1

    base = args.base_url.rstrip("/")

    with httpx.Client(timeout=60.0) as client:
        print("== GET /health")
        r = client.get(f"{base}/health")
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))

        print("\n== GET /health/aws")
        r = client.get(f"{base}/health/aws")
        print(json.dumps(r.json(), indent=2))

        print(f"\n== POST /uploads ({args.sample.name})")
        with args.sample.open("rb") as f:
            r = client.post(
                f"{base}/uploads",
                files={"file": (args.sample.name, f, "application/json")},
            )
        print(f"status={r.status_code}")
        try:
            body = r.json()
        except Exception:
            print(r.text)
            return 1
        print(json.dumps(body, indent=2))
        if r.status_code >= 400:
            return 1
        persisted = body.get("persisted_to_dynamodb")
        print(f"\n(persisted_to_dynamodb={persisted})")

        print("\n== GET /records?page_size=5")
        r = client.get(f"{base}/records", params={"page_size": 5})
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))

        print("\n== GET /dashboard/summary")
        r = client.get(f"{base}/dashboard/summary")
        r.raise_for_status()
        print(json.dumps(r.json(), indent=2))

    # Optional DynamoDB scan (same credentials as check_aws_integration)
    try:
        from app.core.config import clear_settings_cache, get_settings, load_env
        from app.core.aws_clients import dynamodb_client

        load_env()
        clear_settings_cache()
        s = get_settings()
        if s.aws_enabled:
            ddb = dynamodb_client(s)
            out = ddb.scan(TableName=s.dynamodb_table_name, Select="COUNT")
            print(f"\n== DynamoDB scan COUNT on {s.dynamodb_table_name}: {out.get('Count', 0)} items")
    except Exception as exc:
        print(f"\n(DynamoDB scan skipped: {exc})")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
