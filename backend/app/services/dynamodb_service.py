from __future__ import annotations

from typing import Any, Dict, Protocol


class DynamoClientProtocol(Protocol):
    def put_item(self, *, TableName: str, Item: Dict[str, Any]) -> Any: ...

    def update_item(
        self,
        *,
        TableName: str,
        Key: Dict[str, Any],
        UpdateExpression: str,
        ExpressionAttributeNames: Dict[str, str],
        ExpressionAttributeValues: Dict[str, Any],
    ) -> Any: ...


class DynamoDBService:
    """
    Thin wrapper around a DynamoDB client.
    For tests we inject a fake that implements DynamoClientProtocol.
    """

    def __init__(self, table_name: str, client: DynamoClientProtocol | None = None) -> None:
        self.table_name = table_name
        self.client = client

    @classmethod
    def from_config(cls) -> "DynamoDBService | None":
        """
        Real boto3 DynamoDB client when AWS_ENDPOINT_URL is set (e.g. LocalStack).
        Returns None when not configured (in-memory / test mode without AWS).
        """
        from ..core.aws_clients import dynamodb_client
        from ..core.config import get_settings

        s = get_settings()
        if not s.aws_enabled:
            return None
        return cls(table_name=s.dynamodb_table_name, client=dynamodb_client(s))

    def put(self, item: Dict[str, Any]) -> None:
        if self.client is None:
            # In real deployment we will wire a boto3 client here.
            raise RuntimeError("DynamoDB client is not configured")
        self.client.put_item(TableName=self.table_name, Item=item)

    def update(self, key: Dict[str, Any], update_expression: str, names: Dict[str, str], values: Dict[str, Any]) -> None:
        if self.client is None:
            raise RuntimeError("DynamoDB client is not configured")
        self.client.update_item(
            TableName=self.table_name,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames={f"#{k}": v for k, v in names.items()},
            ExpressionAttributeValues={f":{k}": v for k, v in values.items()},
        )

