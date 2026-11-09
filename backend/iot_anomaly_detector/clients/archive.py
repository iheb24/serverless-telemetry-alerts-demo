"""S3 client for archiving raw telemetry payloads."""

import json
from typing import Any

from iot_anomaly_detector.clients.base import BaseAwsClient


class ArchiveClient(BaseAwsClient):
    """Client for storing raw data in S3."""

    service_name = "s3"

    def __init__(self, bucket_name: str, **kwargs: Any) -> None:
        """Initialize the client with a specific bucket name."""
        super().__init__(**kwargs)
        self._bucket_name = bucket_name

    def archive_payload(self, key: str, payload: dict[str, Any]) -> None:
        """Upload a raw JSON payload to the archive bucket.

        Args:
            key: S3 object key.
            payload: Dictionary to serialize and upload.
        """
        self.call(
            "put_object",
            Bucket=self._bucket_name,
            Key=key,
            Body=json.dumps(payload),
            ContentType="application/json",
        )
