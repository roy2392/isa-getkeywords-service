variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "The name of the Cloud Run service"
  type        = string
  default     = "isa-getkeywords-service"
}

variable "image_url" {
  description = "The Docker image URL for the Cloud Run service"
  type        = string
}

variable "schedule" {
  description = "Cron schedule for Cloud Scheduler (default: daily at 2 AM UTC)"
  type        = string
  default     = "0 2 * * *"
}
