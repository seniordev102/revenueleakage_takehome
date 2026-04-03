from __future__ import annotations

from copy import deepcopy
from typing import Any


class InMemoryDynamoClient:
    def __init__(self) -> None:
        self.items: dict[tuple[str, str], dict[str, Any]] = {}
        self.put_calls: list[dict[str, Any]] = []
        self.update_calls: list[dict[str, Any]] = []

    def put_item(self, *, TableName: str, Item: dict[str, Any]) -> None:
        self.put_calls.append({"TableName": TableName, "Item": deepcopy(Item)})
        key = (Item["pk"]["S"], Item["sk"]["S"])
        self.items[key] = deepcopy(Item)

    def update_item(
        self,
        *,
        TableName: str,
        Key: dict[str, Any],
        UpdateExpression: str,
        ExpressionAttributeNames: dict[str, str],
        ExpressionAttributeValues: dict[str, Any],
    ) -> None:
        self.update_calls.append(
            {
                "TableName": TableName,
                "Key": deepcopy(Key),
                "UpdateExpression": UpdateExpression,
                "ExpressionAttributeNames": deepcopy(ExpressionAttributeNames),
                "ExpressionAttributeValues": deepcopy(ExpressionAttributeValues),
            }
        )
        key = (Key["pk"]["S"], Key["sk"]["S"])
        item = deepcopy(self.items.get(key, {**Key}))
        for placeholder, attribute in ExpressionAttributeNames.items():
            value_key = f":{placeholder.lstrip('#')}"
            if value_key in ExpressionAttributeValues:
                item[attribute] = deepcopy(ExpressionAttributeValues[value_key])
        self.items[key] = item


runtime_dynamo_client = InMemoryDynamoClient()
