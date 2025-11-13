# Service Account for Cloud Scheduler
resource "google_service_account" "cloud_scheduler_sa" {
  account_id   = "isa-keywords-scheduler"
  display_name = "Service Account for ${var.service_name} Cloud Scheduler"
  project      = var.project_id
}

# Cloud Scheduler Job
resource "google_cloud_scheduler_job" "job" {
  name        = "${var.service_name}-trigger"
  description = "Triggers the ${var.service_name} Cloud Run service on schedule"
  schedule    = var.schedule
  time_zone   = "UTC"
  region      = var.region
  project     = var.project_id

  http_target {
    uri         = google_cloud_run_v2_service.main.uri
    http_method = "POST"

    oidc_token {
      service_account_email = google_service_account.cloud_scheduler_sa.email
    }
  }

  retry_config {
    retry_count = 3
    max_retry_duration = "0s"
    min_backoff_duration = "5s"
    max_backoff_duration = "3600s"
    max_doublings = 5
  }

  depends_on = [
    google_cloud_run_v2_service.main,
    google_service_account.cloud_scheduler_sa
  ]
}
