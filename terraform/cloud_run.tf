# Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "isa-keywords-run"
  display_name = "Service Account for ${var.service_name}"
  project      = var.project_id
}

# IAM roles for Cloud Run service account
resource "google_project_iam_member" "cloud_run_bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "main" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = var.image_url

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }
    }

    timeout = "3600s" # 1 hour timeout for job execution
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_iam_member.cloud_run_bigquery_data_editor,
    google_project_iam_member.cloud_run_bigquery_job_user,
    google_project_iam_member.cloud_run_secret_accessor
  ]
}

# Allow Cloud Run to be invoked by Cloud Scheduler
resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  service  = google_cloud_run_v2_service.main.name
  location = google_cloud_run_v2_service.main.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloud_scheduler_sa.email}"
  project  = var.project_id
}
