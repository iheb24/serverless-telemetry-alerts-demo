"""Pydantic models for the iot_anomaly_detector workload."""

from pydantic import BaseModel, Field


class TelemetryReading(BaseModel):
    """Input schema for a single IoT telemetry reading."""

    device_id: str = Field(..., description="Unique identifier for the IoT device.")
    timestamp: str = Field(..., description="ISO8601 timestamp of the reading.")
    temperature: float = Field(..., description="Temperature in Celsius.")
    voltage: float = Field(..., description="Voltage reading.")


class TelemetryAlert(BaseModel):
    """Output schema for an anomaly alert record."""

    device_id: str = Field(..., description="Source device ID.")
    timestamp: str = Field(..., description="Timestamp of the reading.")
    alert_type: str = Field(
        ..., description="The nature of the anomaly (e.g., OVERHEAT)."
    )
    value: float = Field(..., description="The offending value.")
    pk: str = Field(..., description="Partition key for DynamoDB.")
    sk: str = Field(..., description="Sort key for DynamoDB.")
