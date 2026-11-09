"""Unit tests for the AWS clients."""

import json
import os

import boto3
from moto import mock_aws

from iot_anomaly_detector.clients.alerts import AlertsClient
from iot_anomaly_detector.clients.archive import ArchiveClient
from iot_anomaly_detector.models.telemetry import TelemetryAlert

os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_REGION"] = "us-east-1"


@mock_aws
def test_alerts_client_put_get() -> None:
    """Test DynamoDB put and get operations."""
    table_name = "test-table"
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )

    client = AlertsClient(table_name=table_name)
    alert = TelemetryAlert(
        device_id="d1",
        timestamp="2023-01-01T00:00:00Z",
        alert_type="TEST",
        value=10.5,
        pk="d1",
        sk="2023-01-01T00:00:00Z#TEST",
    )

    client.put_alert(alert)
    result = client.get_alert("d1", "2023-01-01T00:00:00Z#TEST")

    assert result is not None
    assert result["device_id"]["S"] == "d1"
    assert result["value"]["N"] == "10.5"


@mock_aws
def test_archive_client_put() -> None:
    """Test S3 put operation."""
    bucket_name = "test-bucket"
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket_name)

    client = ArchiveClient(bucket_name=bucket_name)
    client.archive_payload("test.json", {"key": "val"})

    response = s3.get_object(Bucket=bucket_name, Key="test.json")
    data = json.loads(response["Body"].read().decode("utf-8"))
    assert data["key"] == "val"
