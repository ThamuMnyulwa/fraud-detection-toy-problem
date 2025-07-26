# Agentic Coupon Abuse Detection System (ACADS)

## Executive Summary

The Agentic Coupon Abuse Detection System (ACADS) is a multi-agent AI solution designed to detect and prevent coupon fraud in e-commerce platforms. By leveraging Google's Agent Development Kit (ADK) and Gemini models, ACADS provides real-time fraud detection with continuous learning capabilities. The system identifies patterns such as account duplication, coupon sharing, and timing manipulation, significantly reducing revenue loss from coupon abuse.

## Architecture Overview

### Cloud Infrastructure (GCP)

ACADS is deployed on Google Cloud Platform using Infrastructure as Code (IaC) with Terraform. This approach ensures consistent, reproducible deployments and simplified scaling.

```
GCP Infrastructure:
├── Compute Engine (Agent Processing)
├── Cloud Storage (Data & Model Storage)
├── Vertex AI (Gemini Model Hosting)
├── Cloud SQL (Transaction Database)
├── Cloud Functions (API Endpoints)
└── Cloud Monitoring (System Health & Metrics)
```

### Multi-Agent System Architecture

ACADS employs a specialized multi-agent architecture where each agent performs distinct functions while communicating through a shared memory system:

1. **Data Ingest Agent**
   - **Model**: Gemini 1.5 Flash
   - **Agent Type**: Reactive Agent with Schema Validation Capabilities
   - **Purpose**: Processes raw transaction data, validates schema integrity, and normalizes inputs
   - **Key Functions**: 
     - Schema validation against predefined transaction models
     - Data normalization and preprocessing
     - Feature extraction (discount ratios, time-based features)
     - Duplicate detection and flagging
     - Data quality assessment and error handling
   - **Tools**: 
     - JSON/CSV parsers
     - Schema validators
     - Feature extractors
     - Data transformation utilities
   - **Memory**: Short-term processing buffer with schema registry
   - **Output**: Clean, structured transaction data ready for analysis
   - **Implementation**: Implemented using Google ADK's `FunctionTool` wrappers around core data processing functions

2. **Rule Engine Agent**
   - **Model**: Gemini 1.5 Pro
   - **Agent Type**: Knowledge-Based Reasoning Agent
   - **Purpose**: Applies weighted fraud detection rules to transactions
   - **Key Functions**:
     - Identity reuse detection (duplicate phone/email/username)
     - Vendor verification against known fraudulent entities
     - Discount ratio analysis (flagging suspiciously high discounts)
     - Pattern matching across transaction history
     - Rule prioritization and conflict resolution
     - Confidence scoring for each rule application
   - **Tools**:
     - Rule evaluator
     - Pattern matcher
     - Weighted scoring calculator
     - Historical data analyzer
   - **Memory**: Rule repository with weights and confidence scores
   - **Output**: Fraud scores (0.0-1.0) with triggered rules and confidence levels
   - **Implementation**: Uses a hybrid approach combining explicit rules with LLM reasoning capabilities

3. **Insight Agent**
   - **Model**: Gemini 1.5 Pro
   - **Agent Type**: Generative Reasoning Agent with NLG Capabilities
   - **Purpose**: Generates human-readable explanations and strategic recommendations
   - **Key Functions**:
     - Translating technical fraud signals into clear explanations
     - Generating contextual prevention recommendations
     - Prioritizing cases for manual review
     - Providing justification for automated decisions
     - Creating narrative summaries of complex fraud patterns
     - Generating risk mitigation strategies
   - **Tools**:
     - Explanation generator
     - Recommendation engine
     - Risk prioritizer
     - Content moderator
   - **Memory**: Case examples and explanation templates
   - **Output**: Detailed fraud analysis with actionable recommendations
   - **Implementation**: Leverages Gemini's advanced reasoning capabilities with few-shot examples

4. **Metrics Agent**
   - **Model**: Gemini 1.5 Flash
   - **Agent Type**: Analytical Agent with Statistical Capabilities
   - **Purpose**: Tracks system performance and calculates business impact
   - **Key Functions**:
     - Calculating precision, recall, F1-scores
     - Monitoring false positive/negative rates
     - Tracking API costs and processing latency
     - Generating ROI estimates based on prevented fraud
     - Trend analysis and anomaly detection
     - Performance visualization and reporting
   - **Tools**:
     - Performance calculator
     - Cost tracker
     - Statistical analyzer
     - Visualization generator
   - **Memory**: Historical metrics and performance benchmarks
   - **Output**: Performance dashboards and optimization recommendations
   - **Implementation**: Combines statistical functions with LLM-based interpretation

5. **Feedback Agent**
   - **Model**: Gemini 1.5 Pro
   - **Agent Type**: Learning Agent with Reinforcement Capabilities
   - **Purpose**: Enables continuous learning from human feedback
   - **Key Functions**:
     - Processing manual review outcomes
     - Updating rule weights based on confirmed fraud cases
     - Identifying emerging fraud patterns
     - Maintaining a case history for model refinement
     - Detecting concept drift in fraud patterns
     - Suggesting new rules based on feedback patterns
   - **Tools**:
     - Label processor
     - Weight updater
     - Pattern identifier
     - Rule generator
   - **Memory**: Feedback buffer with historical decisions
   - **Output**: Updated rule weights and confidence scores
   - **Implementation**: Implements a contextual bandit approach for continuous learning

### Agent Communication and Orchestration

The agents communicate through a structured message passing system:

- **Message Format**: JSON-based with standardized fields for agent inputs/outputs
- **Orchestration**: Managed by the ADK Runner class that handles agent execution flow
- **Memory Services**: Shared memory system allowing agents to access relevant context
- **Session Management**: Persistent sessions for tracking transaction analysis lifecycle
- **Error Handling**: Graceful degradation with fallback mechanisms when agents encounter issues
- **Monitoring**: Telemetry collection across all agent interactions for performance analysis

## Workflow & Data Flow

1. **Transaction Ingestion**:
   - Transaction data arrives via API or batch upload
   - Data Ingest Agent validates and normalizes the data
   - Structured data is stored in Cloud SQL

2. **Fraud Detection**:
   - Rule Engine Agent evaluates transactions against fraud rules
   - Each transaction receives a fraud score (0.0-1.0)
   - Risk levels assigned (LOW, MEDIUM, HIGH, CRITICAL)

3. **Analysis & Explanation**:
   - Insight Agent generates human-readable explanations
   - Prevention recommendations are provided
   - High-risk transactions are flagged for manual review

4. **Performance Tracking**:
   - Metrics Agent calculates system performance
   - API costs and processing times are monitored
   - Business impact is quantified

5. **Feedback Loop**:
   - Human reviewers confirm/reject fraud flags
   - Feedback Agent processes these decisions
   - Rule weights are adjusted based on feedback
   - New patterns are incorporated into detection logic

## Reinforcement Learning Implementation

ACADS implements a reinforcement learning approach through its Feedback Agent, creating a continuous improvement cycle:

1. **State Representation**:
   - Transaction features (user data, discount ratios, timing)
   - Historical patterns across user accounts
   - Current rule weights and thresholds

2. **Action Space**:
   - Fraud classification decisions
   - Rule weight adjustments
   - Threshold modifications

3. **Reward Function**:
   - Positive rewards for correct fraud identification
   - Negative penalties for false positives/negatives
   - Weighted by financial impact of decisions

4. **Learning Algorithm**:
   - Contextual bandit approach for rule weight optimization
   - Bayesian updating of confidence scores
   - Periodic batch updates to maintain system stability

The system maintains a balance between exploration (testing rule variations) and exploitation (using proven rules) to continuously improve detection accuracy while adapting to new fraud patterns.

## Terraform Deployment Architecture

The deployment uses a modular Terraform approach:

```hcl
module "acads_infrastructure" {
  source = "./modules/infrastructure"
  
  project_id      = var.gcp_project_id
  region          = var.gcp_region
  environment     = var.environment
}

module "acads_database" {
  source = "./modules/database"
  
  instance_name   = "acads-transactions"
  database_version = "POSTGRES_13"
  tier            = "db-custom-2-4096"
  depends_on      = [module.acads_infrastructure]
}

module "acads_agents" {
  source = "./modules/agents"
  
  gemini_pro_model  = var.gemini_pro_model
  gemini_flash_model = var.gemini_flash_model
  api_key          = var.google_api_key
  depends_on       = [module.acads_database]
}

module "acads_frontend" {
  source = "./modules/frontend"
  
  app_name        = "acads-streamlit"
  container_image = var.streamlit_image
  depends_on      = [module.acads_agents]
}

module "acads_monitoring" {
  source = "./modules/monitoring"
  
  alert_email     = var.alert_email
  metrics_dashboard = true
  depends_on      = [module.acads_frontend]
}
```

## Performance Metrics & KPIs

ACADS is evaluated against the following key metrics:

1. **Fraud Detection Accuracy**:
   - Precision: >85% (correct fraud identifications)
   - Recall: >80% (proportion of actual fraud caught)
   - F1-Score: >82% (balanced measure of precision and recall)

2. **Operational Efficiency**:
   - False Positive Rate: <5% (minimizing legitimate transaction disruption)
   - Processing Latency: <30s per batch (real-time capability)
   - API Cost per Transaction: <$0.01 (cost efficiency)

3. **Business Impact**:
   - Revenue Protected: Estimated monthly savings from prevented fraud
   - Manual Review Reduction: Percentage decrease in human review time
   - Customer Experience: Minimal disruption to legitimate transactions

## Future Enhancements

1. **Advanced Pattern Recognition**:
   - Implement graph-based analysis for network fraud detection
   - Incorporate temporal sequence modeling for timing-based fraud

2. **Enhanced User Interface**:
   - Develop customizable dashboards for different stakeholder needs
   - Add interactive exploration of fraud patterns

3. **Integration Capabilities**:
   - Expand API connectors for major e-commerce platforms
   - Develop webhook system for real-time alerts

4. **Scalability Improvements**:
   - Implement distributed processing for high-volume scenarios
   - Develop multi-region deployment options for global businesses

## Conclusion

The Agentic Coupon Abuse Detection System represents a significant advancement in fraud prevention technology. By leveraging Google ADK's multi-agent architecture and reinforcement learning capabilities, ACADS provides a comprehensive solution that continuously improves over time. The system not only detects fraud but provides clear explanations and actionable insights, making it an invaluable tool for e-commerce businesses seeking to protect revenue while maintaining positive customer experiences. 