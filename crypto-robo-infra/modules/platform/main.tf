locals {
  prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "reports" {
  bucket = "${local.prefix}-reports"
  tags   = local.common_tags
}

resource "aws_s3_bucket_versioning" "reports" {
  bucket = aws_s3_bucket.reports.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "state" {
  name         = "${local.prefix}-state"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "runtime" {
  name              = "/aws/lambda/${local.prefix}"
  retention_in_days = 30
  tags              = local.common_tags
}

resource "aws_iam_role" "lambda" {
  name = "${local.prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_runtime" {
  name = "${local.prefix}-lambda-runtime"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.state.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.reports.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "runtime" {
  function_name = local.prefix
  role          = aws_iam_role.lambda.arn
  handler       = "crypto_robo_runtime.orchestration.handlers.weekly_rebalance_handler"
  runtime       = "python3.12"
  memory_size   = 512
  timeout       = 900
  filename      = var.runtime_package_path != "" ? var.runtime_package_path : null
  source_code_hash = (
    var.runtime_package_path != ""
    ? filebase64sha256(var.runtime_package_path)
    : null
  )
  s3_bucket = var.runtime_package_path == "" ? var.runtime_package_s3_bucket : null
  s3_key    = var.runtime_package_path == "" ? var.runtime_package_s3_key : null

  environment {
    variables = {
      APP_ENV                  = var.environment
      AWS_REGION               = var.aws_region
      ACTIVE_EXCHANGE          = var.active_exchange
      STATE_TABLE_NAME         = aws_dynamodb_table.state.name
      REPORTS_BUCKET           = aws_s3_bucket.reports.bucket
      LIVE_TRADING             = tostring(var.environment == "prod")
      AI_DEFAULT_MULTIPLIER    = "0.85"
      DATA_FRESHNESS_HOURS     = "24"
      RESEARCH_FRESHNESS_HOURS = "24"
    }
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_event_rule" "daily_refresh" {
  name                = "${local.prefix}-daily-refresh"
  schedule_expression = var.schedule_daily_cron
  tags                = local.common_tags
}

resource "aws_cloudwatch_event_rule" "weekly_rebalance" {
  name                = "${local.prefix}-weekly-rebalance"
  schedule_expression = var.schedule_weekly_cron
  tags                = local.common_tags
}

resource "aws_cloudwatch_event_target" "daily_refresh" {
  rule      = aws_cloudwatch_event_rule.daily_refresh.name
  target_id = "daily-refresh"
  arn       = aws_lambda_function.runtime.arn
  input = jsonencode({
    job = "daily_refresh"
  })
}

resource "aws_iam_role" "step_functions" {
  name = "${local.prefix}-step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "step_functions" {
  name = "${local.prefix}-step-functions"
  role = aws_iam_role.step_functions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = aws_lambda_function.runtime.arn
      }
    ]
  })
}

resource "aws_sfn_state_machine" "rebalance" {
  name     = "${local.prefix}-rebalance"
  role_arn = aws_iam_role.step_functions.arn

  definition = jsonencode({
    Comment = "Weekly rebalance orchestration"
    StartAt = "RunWeeklyRebalance"
    States = {
      RunWeeklyRebalance = {
        Type = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        OutputPath = "$.Payload"
        Parameters = {
          FunctionName = aws_lambda_function.runtime.arn
          Payload = {
            job = "weekly_rebalance"
          }
        }
        End = true
      }
    }
  })

  tags = local.common_tags
}

resource "aws_iam_role" "eventbridge_step_functions" {
  name = "${local.prefix}-eventbridge-step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "eventbridge_step_functions" {
  name = "${local.prefix}-eventbridge-step-functions"
  role = aws_iam_role.eventbridge_step_functions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution"
        ]
        Resource = aws_sfn_state_machine.rebalance.arn
      }
    ]
  })
}

resource "aws_cloudwatch_event_target" "weekly_rebalance" {
  rule      = aws_cloudwatch_event_rule.weekly_rebalance.name
  target_id = "weekly-rebalance"
  arn       = aws_sfn_state_machine.rebalance.arn
  role_arn  = aws_iam_role.eventbridge_step_functions.arn
}

resource "aws_lambda_permission" "allow_eventbridge_daily" {
  statement_id  = "AllowExecutionFromEventBridgeDaily"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.runtime.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_refresh.arn
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.prefix}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Runtime lambda emitted errors"

  dimensions = {
    FunctionName = aws_lambda_function.runtime.function_name
  }

  tags = local.common_tags
}
