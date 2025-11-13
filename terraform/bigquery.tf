# NOTE: This service uses an existing BigQuery table: pwcnext-sandbox01.telegram.keys
# The table is shared across ISA microservices and should not be created by this service
# The table has a column 'keys_group' which stores the keywords

# If you need to create the BigQuery infrastructure, uncomment the following:
#
# # BigQuery Dataset
# resource "google_bigquery_dataset" "telegram" {
#   dataset_id    = "telegram"
#   friendly_name = "Telegram Data"
#   description   = "Dataset for ISA microservices data"
#   location      = var.region
#   project       = var.project_id
#
#   labels = {
#     environment = "production"
#     service     = "isa-microservices"
#   }
# }
#
# # BigQuery Table for Keywords
# resource "google_bigquery_table" "keys" {
#   dataset_id = google_bigquery_dataset.telegram.dataset_id
#   table_id   = "keys"
#   project    = var.project_id
#
#   schema = jsonencode([
#     {
#       name        = "keys_group"
#       type        = "STRING"
#       mode        = "NULLABLE"
#       description = "Keyword for stocks and finance industry"
#     }
#     # Add other columns as needed
#   ])
#
#   labels = {
#     environment = "production"
#     service     = "isa-microservices"
#   }
# }
