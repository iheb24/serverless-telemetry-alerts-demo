module "telemetry_queue" {
  source = "./modules/event_choreography"

  name    = "telemetry-events-queue"
  pattern = "sqs_queue"

  tags = local.common_tags
}

module "alerts_storage" {
  source = "./modules/stateful_storage"

  name            = "device-alerts"
  enable_dynamodb = true

  dynamodb_partition_key = {
    name = "pk"
    type = "S"
  }

  tags = local.common_tags
}

module "archive_storage" {
  source = "./modules/stateful_storage"

  name             = "telemetry-raw-archive"
  enable_s3_bucket = true
  enable_dynamodb  = false

  tags = local.common_tags
}

module "anomaly_detector" {
  source = "./modules/serverless_compute"

  name             = "anomaly-detector"
  filename         = "${path.module}/../dist/iot_anomaly_detector.zip"
  source_code_hash = filebase64sha256("${path.module}/../dist/iot_anomaly_detector.zip")
  handler          = "iot_anomaly_detector.entrypoint.handler"
  runtime          = "python3.13"
  timeout          = 300

  triggers = {
    sqs = {
      queue_arn = module.telemetry_queue.queue_arn
    }
  }

  environment_variables = {
    ALERTS_TABLE   = module.alerts_storage.table_name
    ARCHIVE_BUCKET = module.archive_storage.bucket_name
  }

  policy_statements = [
    {
      actions   = ["dynamodb:PutItem", "dynamodb:UpdateItem"]
      resources = [module.alerts_storage.table_arn]
    },
    {
      actions   = ["s3:PutObject"]
      resources = ["${module.archive_storage.bucket_arn}/*"]
    }
  ]

  tags = local.common_tags
}
