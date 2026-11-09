"""Unit tests for the TelemetryHandler and AnomalyDetector."""

import json
from unittest.mock import MagicMock

import pytest

from iot_anomaly_detector.clients.alerts import AlertsClient
from iot_anomaly_detector.clients.archive import ArchiveClient
from iot_anomaly_detector.services.detector import AnomalyDetector
from iot_anomaly_detector.services.handler import TelemetryHandler


@pytest.fixture
def mock_clients() -> tuple[MagicMock, MagicMock]:
    """Create mock clients for testing."""
    return MagicMock(spec=AlertsClient), MagicMock(spec=ArchiveClient)


def test_detector_thresholds() -> None:
    """Verify AnomalyDetector logic for thresholds."""
    detector = AnomalyDetector()
    from iot_anomaly_detector.models.telemetry import TelemetryReading

    # No anomaly
    reading1 = TelemetryReading(
        device_id="d1",
        timestamp="2023-01-01T00:00:00Z",
        temperature=20.0,
        voltage=220.0,
    )
    assert len(detector.analyze(reading1)) == 0

    # Overheat
    reading2 = TelemetryReading(
        device_id="d1",
        timestamp="2023-01-01T00:00:00Z",
        temperature=85.0,
        voltage=220.0,
    )
    alerts = detector.analyze(reading2)
    assert len(alerts) == 1
    assert alerts[0].alert_type == "OVERHEAT"

    # Both
    reading3 = TelemetryReading(
        device_id="d1",
        timestamp="2023-01-01T00:00:00Z",
        temperature=90.0,
        voltage=240.0,
    )
    assert len(detector.analyze(reading3)) == 2


def test_handler_valid_with_anomaly(mock_clients: tuple[MagicMock, MagicMock]) -> None:
    """Scenario: Valid batch with one anomaly stores alert and archives."""
    alerts_mock, archive_mock = mock_clients
    detector = AnomalyDetector()
    handler = TelemetryHandler(detector, alerts_mock, archive_mock)

    payload = {
        "device_id": "dev-123",
        "timestamp": "2023-10-27T10:00:00Z",
        "temperature": 100.0,
        "voltage": 220.0,
    }
    event_records = [{"body": json.dumps(payload)}]

    handler.handle_records(event_records)

    assert archive_mock.archive_payload.called
    assert alerts_mock.put_alert.called


def test_handler_no_anomaly(mock_clients: tuple[MagicMock, MagicMock]) -> None:
    """Scenario: Batch with no anomalies only archives raw data."""
    alerts_mock, archive_mock = mock_clients
    detector = AnomalyDetector()
    handler = TelemetryHandler(detector, alerts_mock, archive_mock)

    payload = {
        "device_id": "dev-123",
        "timestamp": "2023-10-27T10:00:00Z",
        "temperature": 25.0,
        "voltage": 220.0,
    }
    event_records = [{"body": json.dumps(payload)}]

    handler.handle_records(event_records)

    assert archive_mock.archive_payload.called
    assert not alerts_mock.put_alert.called


def test_handler_malformed_json(mock_clients: tuple[MagicMock, MagicMock]) -> None:
    """Scenario: Malformed JSON payload is handled without crashing."""
    alerts_mock, archive_mock = mock_clients
    detector = AnomalyDetector()
    handler = TelemetryHandler(detector, alerts_mock, archive_mock)

    event_records = [{"body": "not-json"}]

    # Should not raise exception
    handler.handle_records(event_records)

    assert not archive_mock.archive_payload.called
    assert not alerts_mock.put_alert.called


def test_handler_invalid_schema(mock_clients: tuple[MagicMock, MagicMock]) -> None:
    """Scenario: Valid JSON but missing required fields."""
    alerts_mock, archive_mock = mock_clients
    detector = AnomalyDetector()
    handler = TelemetryHandler(detector, alerts_mock, archive_mock)

    event_records = [{"body": json.dumps({"wrong": "field"})}]

    handler.handle_records(event_records)

    assert archive_mock.archive_payload.called
    assert not alerts_mock.put_alert.called
