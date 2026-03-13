variable "aws_region" {
  type    = string
  default = "us-east-2"
}

variable "github_owner" {
  type = string
}

variable "github_repo" {
  type = string
}

variable "runtime_package_path" {
  type    = string
  default = ""
}

variable "runtime_package_s3_bucket" {
  type    = string
  default = "replace-me-artifacts"
}

variable "runtime_package_s3_key" {
  type    = string
  default = "runtime/dev/latest.zip"
}

variable "active_exchange" {
  type    = string
  default = "coinbase"
}
