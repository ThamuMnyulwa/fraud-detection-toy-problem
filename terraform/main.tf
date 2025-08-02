provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudfunctions.googleapis.com",
    "storage.googleapis.com",
    "monitoring.googleapis.com",
    "aiplatform.googleapis.com",
  ])
  
  service                    = each.value
  disable_dependent_services = false
}

resource "google_project_service" "secret_manager" {
  service                    = "secretmanager.googleapis.com"
  disable_dependent_services = false
}

resource "google_project_service" "kms" {
  service                    = "cloudkms.googleapis.com"
  disable_dependent_services = false
}

# Create KMS key for encrypting secrets
resource "google_kms_key_ring" "secrets_keyring" {
  name     = "${local.name_prefix}-keyring"
  location = var.gcp_region
  depends_on = [google_project_service.kms]
}

resource "google_kms_crypto_key" "secret_key" {
  name     = "${local.name_prefix}-key"
  key_ring = google_kms_key_ring.secrets_keyring.id
}

locals {
  # Environment-specific configurations
  env_config = {
    dev = {
      machine_type       = "e2-standard-2"
      storage_class      = "STANDARD"
      db_tier            = "db-f1-micro"  # Smallest instance for testing
      min_instances      = 1
      max_instances      = 2
      alerts_enabled     = false
    }
    prod = {
      machine_type       = "e2-standard-4"
      storage_class      = "STANDARD"
      db_tier            = "db-g1-small"  # Small but more reliable for production
      min_instances      = 2
      max_instances      = 5
      alerts_enabled     = true
    }
  }

  # Use the correct config based on environment
  config = local.env_config[var.environment]
  
  # Common resource naming
  name_prefix = "acads-${var.environment}"
}

# Storage bucket for data and models
resource "google_storage_bucket" "acads_storage" {
  name          = "${local.name_prefix}-storage-${random_id.bucket_suffix.hex}"
  location      = var.gcp_region
  storage_class = local.config.storage_class
  
  uniform_bucket_level_access = true
  force_destroy               = var.environment == "dev" ? true : false
}

# Random suffix for globally unique bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Cloud SQL instance (minimal size for testing)
resource "google_sql_database_instance" "acads_db" {
  name             = "${local.name_prefix}-db"
  database_version = "POSTGRES_13"
  region           = var.gcp_region
  
  settings {
    tier = local.config.db_tier
    
    backup_configuration {
      enabled = var.environment == "prod"
    }
  }

  deletion_protection = var.environment == "prod"
}

# Cloud SQL database
resource "google_sql_database" "acads_database" {
  name     = "acads_transactions"
  instance = google_sql_database_instance.acads_db.name
}

# Cloud SQL user
resource "google_sql_user" "acads_db_user" {
  name     = "acads_user"
  instance = google_sql_database_instance.acads_db.name
  password = random_password.db_password.result
}

# Generate random password for database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store database password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${local.name_prefix}-db-password"
  
  replication {
    auto {
      customer_managed {
        kms_key_name = google_kms_crypto_key.secret_key.id
      }
    }
  }

  depends_on = [google_project_service.secret_manager]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Grant the VM access to the secret
resource "google_secret_manager_secret_iam_member" "vm_secret_access" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_compute_instance.acads_vm.service_account[0].email}"
}

# Vertex AI endpoint for Gemini models
resource "google_vertex_ai_endpoint" "gemini_endpoint" {
  name         = "${local.name_prefix}-endpoint"
  display_name = "${local.name_prefix} Endpoint"
  region       = var.gcp_region
}

# Compute Engine VM for agent processing
resource "google_compute_instance" "acads_vm" {
  name         = "${local.name_prefix}-vm"
  machine_type = local.config.machine_type
  zone         = "${var.gcp_region}-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  # Create a dedicated service account for the VM
  service_account {
    email  = google_service_account.acads_sa.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y python3-pip git
    pip install google-adk google-cloud-storage google-cloud-sql-postgres psycopg2-binary google-cloud-secret-manager
    
    # Set environment variables
    echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> /etc/environment
    echo "GOOGLE_CLOUD_PROJECT=${var.gcp_project_id}" >> /etc/environment
    echo "GOOGLE_CLOUD_LOCATION=${var.gcp_region}" >> /etc/environment
    
    # Add script to fetch DB password from Secret Manager
    cat > /usr/local/bin/fetch_db_password.py <<EOF
    import os
    from google.cloud import secretmanager
    
    def get_secret(project_id, secret_id):
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    
    if __name__ == "__main__":
        password = get_secret("${var.gcp_project_id}", "${local.name_prefix}-db-password")
        print(password)
    EOF
    
    chmod +x /usr/local/bin/fetch_db_password.py
  EOT

  depends_on = [
    google_sql_database_instance.acads_db,
    google_storage_bucket.acads_storage
  ]
}

# Service account for ACADS components
resource "google_service_account" "acads_sa" {
  account_id   = "${local.name_prefix}-sa"
  display_name = "ACADS Service Account"
  description  = "Service account for ACADS components"
}

# Grant roles to service account
resource "google_project_iam_member" "acads_sa_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/storage.objectAdmin",
    "roles/aiplatform.user",
    "roles/monitoring.metricWriter",
  ])
  
  project = var.gcp_project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.acads_sa.email}"
}

# Cloud Function for API endpoint
resource "google_cloudfunctions_function" "acads_api" {
  name        = "${local.name_prefix}-api"
  description = "ACADS API Endpoint"
  runtime     = "python310"
  
  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.acads_storage.name
  source_archive_object = google_storage_bucket_object.function_zip.name
  trigger_http          = true
  entry_point           = "api_handler"
  
  environment_variables = {
    DB_INSTANCE = google_sql_database_instance.acads_db.connection_name
    DB_NAME     = google_sql_database.acads_database.name
    DB_USER     = google_sql_user.acads_db_user.name
    DB_PASSWORD_SECRET = "${local.name_prefix}-db-password"
  }
  
  service_account_email = google_service_account.acads_sa.email
  
  # Grant the function access to the db password secret
  secret_environment_variables {
    key        = "DB_PASSWORD"
    project_id = var.gcp_project_id
    secret     = google_secret_manager_secret.db_password.secret_id
    version    = "latest"
  }
}

# Upload dummy function code (would be replaced by actual code in CI/CD)
resource "google_storage_bucket_object" "function_zip" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.acads_storage.name
  source = "/dev/null"  # Placeholder - would be a real zip file in production
}

# Cloud Monitoring alert policy for high fraud rates
resource "google_monitoring_alert_policy" "fraud_alert" {
  count = local.config.alerts_enabled ? 1 : 0
  
  display_name = "${local.name_prefix}-high-fraud-rate-alert"
  combiner     = "OR"
  
  conditions {
    display_name = "High Fraud Rate"
    
    condition_threshold {
      filter          = "metric.type=\"custom.googleapis.com/acads/fraud_rate\" resource.type=\"global\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.2
      
      trigger {
        count = 1
      }
    }
  }
  
  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].name] : []
}

# Email notification channel for alerts
resource "google_monitoring_notification_channel" "email" {
  count        = var.alert_email != "" ? 1 : 0
  display_name = "ACADS Alert Email"
  type         = "email"
  
  labels = {
    email_address = var.alert_email
  }
}

# Output the resources created
output "cloud_sql_connection" {
  value = google_sql_database_instance.acads_db.connection_name
}

output "storage_bucket" {
  value = google_storage_bucket.acads_storage.name
}

output "function_url" {
  value = google_cloudfunctions_function.acads_api.https_trigger_url
}

output "db_credentials_secret" {
  value     = "Database password stored in Secret Manager"
  sensitive = true
}
