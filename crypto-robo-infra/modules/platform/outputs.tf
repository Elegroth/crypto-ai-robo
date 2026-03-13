output "state_table_name" {
  value = aws_dynamodb_table.state.name
}

output "reports_bucket_name" {
  value = aws_s3_bucket.reports.bucket
}

output "lambda_function_name" {
  value = aws_lambda_function.runtime.function_name
}

output "rebalance_state_machine_name" {
  value = aws_sfn_state_machine.rebalance.name
}
