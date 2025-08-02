# ACADS Terraform Deployment

This directory contains the Terraform configuration for deploying the Agentic Coupon Abuse Detection System (ACADS) on Google Cloud Platform.

## Architecture Overview

ACADS is deployed on Google Cloud Platform using a modular Terraform approach. The system leverages Google's Agent Development Kit (ADK) and Gemini models to provide real-time fraud detection with continuous learning capabilities.

```
GCP Infrastructure:
├── Compute Engine (Agent Processing)
├── Cloud Storage (Data & Model Storage)
├── Vertex AI (Gemini Model Hosting)
├── Cloud SQL (Transaction Database)
├── Cloud Functions (API Endpoints)
└── Cloud Monitoring (System Health & Metrics)
```

## Prerequisites

- Google Cloud Project with billing enabled
- Google Cloud SDK installed and configured
- Terraform v1.0+ installed
- Python 3.10+
- Google API Key or Vertex AI access configured

## Terraform Module Structure

The deployment is organized into modular components:

```
terraform/
├── main.tf             # Main configuration file
├── backend.tf          # State management configuration
├── variables.tf        # Input variables
├── outputs.tf          # Output values
└── modules/
    ├── infrastructure/ # Base GCP resources
    ├── database/       # Cloud SQL setup
    ├── agents/         # Vertex AI for Gemini models
    ├── frontend/       # Streamlit app deployment
    └── monitoring/     # Observability setup
```

## Deployment Steps

### 1. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
# For Vertex AI (preferred for production)
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=your_region

# OR for AI Studio API Key (for development)
# GOOGLE_GENAI_USE_VERTEXAI=FALSE
# GOOGLE_API_KEY=your_api_key
```

### 2. Initialize Terraform

```bash
cd terraform
terraform init
```

### 3. Create a `terraform.tfvars` file

Create a `terraform.tfvars` file with the following variables:

```hcl
gcp_project_id     = "your-gcp-project-id"
gcp_region         = "us-central1"
environment        = "dev" # or "prod"
gemini_pro_model   = "gemini-2.5-pro"
gemini_flash_model = "gemini-2.5-flash"
streamlit_image    = "gcr.io/your-project-id/acads-streamlit:latest"
alert_email        = "alerts@yourcompany.com"
```

### 4. Plan and Apply

```bash
terraform plan
terraform validate
terraform apply
```

## Agent Deployment

After infrastructure is deployed, deploy the ADK agents:

1. Configure the ADK CLI with appropriate credentials:

```bash
adk config set project your-gcp-project-id
adk config set location your-region
```

2. Deploy agents:

```bash
cd ..  # Return to project root
adk run  # For development testing
# OR
adk web  # For development UI
```

For production deployment:

```bash
python -m deploy_agent_engine.py
```

## Observability Setup

ACADS includes comprehensive monitoring through Cloud Trace and Weave:

1. Cloud Trace is automatically configured in the `monitoring` module
2. For Weave integration, ensure proper environment variables:

```
WANDB_API_KEY=your_wandb_api_key
WANDB_PROJECT=acads
WANDB_ENTITY=your_entity
```

## Monitoring and Troubleshooting

- Access the monitoring dashboard through the GCP Console
- Review agent logs in Cloud Logging
- Examine traces in Cloud Trace or Weave dashboard
- For deployment issues, check Terraform logs with `TF_LOG=DEBUG terraform apply`

## Terraform Resources

The deployment creates the following core resources:

1. **Compute Engine**: VM instances for agent processing
2. **Cloud Storage**: Buckets for model storage and data
3. **Vertex AI**: Gemini model endpoints for all five agents
4. **Cloud SQL**: PostgreSQL database for transaction storage
5. **Cloud Functions**: API endpoints for external integration
6. **Cloud Monitoring**: Alerting and metrics dashboard

## Security Considerations

- All agent communication uses secure service accounts
- Database access is restricted to the application subnet
- API endpoints use authentication
- Models are deployed in private endpoints where possible
- Monitoring includes security alerts for unusual access patterns