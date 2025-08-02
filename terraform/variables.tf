variable "gcp_project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (dev or prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be either 'dev' or 'prod'."
  }
}

variable "gemini_pro_model" {
  description = "Gemini Pro model name"
  type        = string
  default     = "gemini-1.5-pro"
}

variable "gemini_flash_model" {
  description = "Gemini Flash model name"
  type        = string
  default     = "gemini-1.5-flash"
}

variable "google_api_key" {
  description = "Google API Key for Gemini models (if not using Vertex AI)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "streamlit_image" {
  description = "Container image for Streamlit frontend"
  type        = string
  default     = ""
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  default     = ""
}