"""Service orchestrating the telemetry processing pipeline."""

import json
import uuid
from typing import Any

from aws_lambda_powertools import Logger
from pydantic import ValidationError

from iot_anomaly_detector.clients.alerts import AlertsClient
from iot_anomaly_detector.clients.archive import ArchiveClient
from iot_anomaly_detector.models.telemetry import TelemetryReading
from iot_anomaly_detector.services.detector import AnomalyDetector

logger = Logger(child=True)


class TelemetryHandler:
    """Handler for processing SQS batches of IoT telemetry."""

    def __init__(
        self,
        detector: AnomalyDetector,
        alerts_client: AlertsClient,
        archive_client: ArchiveClient,
    ) -> None:
        """Inject dependencies."""
        self.detector = detector
        self.alerts_client = alerts_client
        self.archive_client = archive_client

    def handle_records(self, records: list[dict[str, Any]]) -> None:
        """Process a batch of SQS records.

        Args:
            records: List of SQS message dictionaries.
        """
        for record in records:
            body_str = record.get("body", "{}")
            try:
                payload = json.loads(body_str)
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON payload", extra={"body": body_str})
                continue

            archive_key = f"raw/{uuid.uuid4()}.json"
            self.archive_client.archive_payload(archive_key, payload)

            try:
                reading = TelemetryReading(**payload)
            except (ValidationError, TypeError):
                logger.warning("Invalid telemetry schema", extra={"payload": payload})
                continue

            alerts = self.detector.analyze(reading)
            for alert in alerts:
                self.alerts_client.put_alert(alert)
                logger.info(
                    "Anomaly detected and stored",
                    extra={
                        "device_id": reading.device_id,
                        "type": alert.alert_type,
                    },
                )
