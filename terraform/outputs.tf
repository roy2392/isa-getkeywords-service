output "cloud_run_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.main.uri
}

output "service_account_email" {
  description = "The email of the service account used by Cloud Run"
  value       = google_service_account.cloud_run_sa.email
}

output "scheduler_job_name" {
  description = "The name of the Cloud Scheduler job"
  value       = google_cloud_scheduler_job.job.name
}

output "bigquery_table" {
  description = "The BigQuery keywords table being used"
  value       = "pwcnext-sandbox01.telegram.keys (existing table)"
}
