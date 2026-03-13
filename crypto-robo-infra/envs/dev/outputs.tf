output "deploy_role_arn" {
  value = module.github_oidc.deploy_role_arn
}

output "reports_bucket_name" {
  value = module.platform.reports_bucket_name
}
