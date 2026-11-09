"""IoT telemetry anomaly detection stack.

Ingest sensor data via SQS, evaluate spikes in Python, store alerts in DynamoDB,
and archive raw data to S3.
"""
