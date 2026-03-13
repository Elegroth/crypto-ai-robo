variable "environment" {
  type = string
}

variable "project_name" {
  type    = string
  default = "crypto-robo"
}

variable "runtime_package_path" {
  type    = string
  default = ""
}

variable "runtime_package_s3_bucket" {
  type    = string
  default = ""
}

variable "runtime_package_s3_key" {
  type    = string
  default = ""
}

variable "active_exchange" {
  type = string
}

variable "schedule_daily_cron" {
  type    = string
  default = "cron(0 10 * * ? *)"
}

variable "schedule_weekly_cron" {
  type    = string
  default = "cron(0 13 ? * MON *)"
}
