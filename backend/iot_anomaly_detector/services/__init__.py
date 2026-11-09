"""Business logic for the iot_anomaly_detector workload.

Services receive client objects through dependency injection and never
import boto3, which keeps domain logic unit-testable without AWS.
"""
