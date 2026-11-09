"""DynamoDB client for writing detected anomalies."""

from typing import Any, cast

from iot_anomaly_detector.clients.base import BaseAwsClient
from iot_anomaly_detector.models.telemetry import TelemetryAlert


class AlertsClient(BaseAwsClient):
    """Client for interacting with the alerts DynamoDB table."""

    service_name = "dynamodb"

    def __init__(self, table_name: str, **kwargs: Any) -> None:
        """Initialize the client with a specific table name."""
        super().__init__(**kwargs)
        self._table_name = table_name

    def put_alert(self, alert: TelemetryAlert) -> None:
        """Store an anomaly alert in DynamoDB.

        Args:
            alert: The validated alert model.
        """
        item = {
            "pk": {"S": alert.pk},
            "sk": {"S": alert.sk},
            "device_id": {"S": alert.device_id},
            "timestamp": {"S": alert.timestamp},
            "alert_type": {"S": alert.alert_type},
            "value": {"N": str(alert.value)},
        }
        self.call("put_item", TableName=self._table_name, Item=item)

    def get_alert(self, pk: str, sk: str) -> dict[str, Any] | None:
        """Fetch an alert for testing purposes.

        Args:
            pk: Partition key.
            sk: Sort key.

        Returns:
            The raw DynamoDB item or None.
        """
        response = self.call(
            "get_item",
            TableName=self._table_name,
            Key={"pk": {"S": pk}, "sk": {"S": sk}},
        )
        return cast(dict[str, Any] | None, response.get("Item"))
