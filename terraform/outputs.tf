output "environment" {
  description = "Deployment environment"
  value       = var.environment
}

output "cloud_sql_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.acads_db.name
}

output "cloud_sql_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.acads_db.connection_name
}

output "storage_bucket_name" {
  description = "Storage bucket name"
  value       = google_storage_bucket.acads_storage.name
}

output "api_endpoint" {
  description = "API endpoint URL"
  value       = google_cloudfunctions_function.acads_api.https_trigger_url
}

output "vm_instance_name" {
  description = "Compute Engine VM instance name"
  value       = google_compute_instance.acads_vm.name
}

output "vm_instance_ip" {
  description = "Compute Engine VM instance external IP"
  value       = google_compute_instance.acads_vm.network_interface.0.access_config.0.nat_ip
}

output "database_connection_info" {
  description = "Database connection information"
  value = {
    instance = google_sql_database_instance.acads_db.connection_name
    database = google_sql_database.acads_database.name
    username = google_sql_user.acads_db_user.name
  }
  sensitive = false  # Not showing the password, just connection info
}

output "db_password_secret" {
  description = "Secret Manager secret for database password"
  value       = google_secret_manager_secret.db_password.name
}

output "service_account" {
  description = "Service account for ACADS components"
  value       = google_service_account.acads_sa.email
}