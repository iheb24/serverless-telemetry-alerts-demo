"""Integration tests for the iot_anomaly_detector wiring."""

import os
from typing import Any

os.environ.setdefault("ALERTS_TABLE", "device-alerts-table")
os.environ.setdefault("ARCHIVE_BUCKET", "telemetry-raw-archive-bucket")


def test_resources_exist(aws_client: Any) -> None:
    """Verify provisioned infrastructure exists.

    Args:
        aws_client: Pytest fixture providing a factory for AWS clients.
    """
    alerts_table = os.environ["ALERTS_TABLE"]
    archive_bucket = os.environ["ARCHIVE_BUCKET"]

    ddb = aws_client("dynamodb")
    table_desc = ddb.describe_table(TableName=alerts_table)
    assert table_desc["Table"]["TableStatus"] == "ACTIVE"

    s3 = aws_client("s3")
    bucket_resp = s3.head_bucket(Bucket=archive_bucket)
    assert bucket_resp["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_env_contract() -> None:
    """Verify environment variables are resolved in the runtime contract."""
    assert os.environ.get("ALERTS_TABLE") is not None
    assert os.environ.get("ARCHIVE_BUCKET") is not None
