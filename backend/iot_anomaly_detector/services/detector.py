"""Domain service for detecting anomalies in telemetry data."""

from iot_anomaly_detector.models.telemetry import TelemetryAlert, TelemetryReading


class AnomalyDetector:
    """Logic for identifying breaches in temperature and voltage thresholds."""

    TEMP_THRESHOLD = 80.0
    VOLTAGE_THRESHOLD = 230.0

    def analyze(self, reading: TelemetryReading) -> list[TelemetryAlert]:
        """Check a reading for multiple types of anomalies.

        Args:
            reading: The telemetry reading to analyze.

        Returns:
            A list of detected alerts (empty if none).
        """
        alerts = []

        if reading.temperature > self.TEMP_THRESHOLD:
            alerts.append(
                TelemetryAlert(
                    device_id=reading.device_id,
                    timestamp=reading.timestamp,
                    alert_type="OVERHEAT",
                    value=reading.temperature,
                    pk=reading.device_id,
                    sk=f"{reading.timestamp}#OVERHEAT",
                )
            )

        if reading.voltage > self.VOLTAGE_THRESHOLD:
            alerts.append(
                TelemetryAlert(
                    device_id=reading.device_id,
                    timestamp=reading.timestamp,
                    alert_type="OVERVOLTAGE",
                    value=reading.voltage,
                    pk=reading.device_id,
                    sk=f"{reading.timestamp}#OVERVOLTAGE",
                )
            )

        return alerts
