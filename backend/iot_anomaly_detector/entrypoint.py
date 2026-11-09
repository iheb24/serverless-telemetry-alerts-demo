"""Entrypoint for the iot_anomaly_detector workload (lambda_sqs)."""

import os
from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from iot_anomaly_detector.clients.alerts import AlertsClient
from iot_anomaly_detector.clients.archive import ArchiveClient
from iot_anomaly_detector.services.detector import AnomalyDetector
from iot_anomaly_detector.services.handler import TelemetryHandler

logger = Logger(service="iot_anomaly_detector")


def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda entrypoint wiring services and handling SQS event.

    Args:
        event: SQS event mapping.
        context: Lambda execution context.

    Returns:
        Standard Lambda response.
    """
    logger.set_correlation_id(context.aws_request_id)

    alerts_table = os.environ["ALERTS_TABLE_NAME"]
    archive_bucket = os.environ["ARCHIVE_BUCKET_NAME"]

    alerts_client = AlertsClient(table_name=alerts_table)
    archive_client = ArchiveClient(bucket_name=archive_bucket)
    detector = AnomalyDetector()

    telemetry_handler = TelemetryHandler(
        detector=detector,
        alerts_client=alerts_client,
        archive_client=archive_client,
    )

    records = event.get("Records", [])
    telemetry_handler.handle_records(records)

    return {"statusCode": 200, "message": f"Processed {len(records)} records"}
