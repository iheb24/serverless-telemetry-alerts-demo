"""Unit tests for the entrypoint wiring."""

import os
from typing import Any
from unittest.mock import patch

from aws_lambda_powertools.utilities.typing import LambdaContext

from iot_anomaly_detector.entrypoint import handler


@patch("iot_anomaly_detector.services.handler.TelemetryHandler.handle_records")
def test_entrypoint_handler(mock_handle: Any) -> None:
    """Verify entrypoint wires correctly and calls service."""
    os.environ["ALERTS_TABLE_NAME"] = "test-table"
    os.environ["ARCHIVE_BUCKET_NAME"] = "test-bucket"

    context = LambdaContext()
    context._aws_request_id = "test-request"

    event = {"Records": [{"body": "{}"}]}

    response = handler(event, context)

    assert response["statusCode"] == 200
    assert mock_handle.called
