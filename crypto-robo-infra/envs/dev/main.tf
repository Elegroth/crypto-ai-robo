module "platform" {
  source                    = "../../modules/platform"
  environment               = "dev"
  aws_region                = var.aws_region
  runtime_package_path      = var.runtime_package_path
  runtime_package_s3_bucket = var.runtime_package_s3_bucket
  runtime_package_s3_key    = var.runtime_package_s3_key
  active_exchange           = var.active_exchange
}

module "github_oidc" {
  source       = "../../modules/github_oidc"
  github_owner = var.github_owner
  github_repo  = var.github_repo
  branch_name  = "develop"
}
