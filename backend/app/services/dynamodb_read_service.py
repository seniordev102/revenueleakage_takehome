"""Read billing records from DynamoDB (LocalStack / AWS)."""
from __future__ import annotations

from typing import Any, List, Optional

from ..schemas.common import BillingRecord
from ..services.dynamodb_service import DynamoDBService
from ..utils.dynamodb_deserialize import billing_record_from_ddb_item


def _scan_billing_items_paginated(client: Any, table_name: str) -> List[dict]:
    items: List[dict] = []
    kwargs: dict = {
        "TableName": table_name,
        "FilterExpression": "entity_type = :et",
        "ExpressionAttributeValues": {":et": {"S": "BILLING_RECORD"}},
    }
    while True:
        resp = client.scan(**kwargs)
        items.extend(resp.get("Items", []))
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
        kwargs["ExclusiveStartKey"] = lek
    return items


def fetch_all_billing_records(dynamo: DynamoDBService) -> List[BillingRecord]:
    if dynamo.client is None:
        return []
    raw_items = _scan_billing_items_paginated(dynamo.client, dynamo.table_name)
    return [billing_record_from_ddb_item(it) for it in raw_items]


def fetch_billing_record_by_id(dynamo: DynamoDBService, record_id: str) -> Optional[BillingRecord]:
    """Find a billing record by record_id (scan with filter; OK for small LocalStack datasets)."""
    if dynamo.client is None:
        return None
    kwargs: dict = {
        "TableName": dynamo.table_name,
        "FilterExpression": "entity_type = :et AND record_id = :rid",
        "ExpressionAttributeValues": {
            ":et": {"S": "BILLING_RECORD"},
            ":rid": {"S": record_id},
        },
    }
    while True:
        resp = dynamo.client.scan(**kwargs)
        items = resp.get("Items", [])
        if items:
            return billing_record_from_ddb_item(items[0])
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
        kwargs["ExclusiveStartKey"] = lek
    return None
