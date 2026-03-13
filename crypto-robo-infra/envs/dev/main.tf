module "platform" {
  source                    = "../../modules/platform"
  environment               = "dev"
  runtime_package_path      = var.runtime_package_path
  runtime_package_s3_bucket = var.runtime_package_s3_bucket
  runtime_package_s3_key    = var.runtime_package_s3_key
  active_exchange           = var.active_exchange
}
