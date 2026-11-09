output "telemetry_queue_url" {
  description = "The URL of the SQS queue receiving IoT telemetry events."
  value       = module.telemetry_queue.queue_url
}

output "alerts_table_name" {
  description = "The name of the DynamoDB table storing device anomaly alerts."
  value       = module.alerts_storage.table_name
}

output "archive_bucket_name" {
  description = "The name of the S3 bucket archiving raw telemetry data."
  value       = module.archive_storage.bucket_name
}

output "anomaly_detector_function_name" {
  description = "The name of the Lambda function processing telemetry for anomalies."
  value       = module.anomaly_detector.function_name
}
