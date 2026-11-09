
# iot_anomaly_detector

IoT telemetry anomaly detection stack: ingest sensor data via SQS, evaluate spikes in Python, store alerts in DynamoDB, and archive raw data to S3.

## Intent & Non-Goals

**Intent.** Implement the `lambda_sqs` workload on the standard
layering: thin `entrypoint.py` wiring, pure business logic in `services/`,
AWS SDK access isolated in `clients/`, typed payloads in `models/`, and
domain errors in `exceptions/`.

**Non-goals.** No boto3 outside `clients/` (AST-enforced). No inline
comments (tokenizer-enforced; docstrings carry intent). No business logic
in `entrypoint.py`.

## Architecture

```mermaid
flowchart TD
    H[entrypoint.py<br/>handler] --> S[services/<br/>business logic]
    S --> C[clients/<br/>BaseAwsClient subclasses]
    C --> AWS[(AWS services)]
    M[models/<br/>pydantic] --> S
    X[exceptions/<br/>IotAnomalyDetectorError · AwsClientError] --> C
    X --> S
```

<!-- BEGIN_HARNESS_DOCS -->
## Environment Contract

| Variable | Source | Value/Path | Description |
| --- | --- | --- | --- |
| ALERTS_TABLE_NAME | plain | `module.alerts_storage.table_name` | DynamoDB table for anomalous alerts. |
| ARCHIVE_BUCKET_NAME | plain | `module.archive_storage.bucket_name` | S3 bucket for archiving raw payloads. |

## Known Caveats & Next Steps

- No caveats recorded for this stack.
<!-- END_HARNESS_DOCS -->
