"""Domain exceptions for the iot_anomaly_detector workload.

``clients/`` translates every botocore ``ClientError`` into ``AwsClientError``
so the rest of the package never depends on AWS SDK error shapes.
"""


class IotAnomalyDetectorError(Exception):
    """Base class for all iot_anomaly_detector domain errors."""


class AwsClientError(IotAnomalyDetectorError):
    """An AWS SDK call failed; carries service, operation, and AWS error code."""

    def __init__(self, *, service: str, operation: str, code: str, msg: str) -> None:
        """Store the AWS error context and build a readable message."""
        self.service = service
        self.operation = operation
        self.code = code
        super().__init__(f"{service}.{operation} failed with {code}: {msg}")
