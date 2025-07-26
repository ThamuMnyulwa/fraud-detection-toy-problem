# ACADS Agent Workflow Diagram

The diagram below illustrates the interaction between the five specialized agents in the Agentic Coupon Abuse Detection System (ACADS) and their connections to external systems and cloud infrastructure.

```mermaid
graph TD
    subgraph "ACADS Multi-Agent System"
        A[Data Ingest Agent] -->|Structured Data| B[Rule Engine Agent]
        B -->|Fraud Scores| C[Insight Agent]
        C -->|Explanations & Recommendations| D[Metrics Agent]
        D -->|Performance Metrics| E[Feedback Agent]
        E -->|Updated Rule Weights| B
    end
    
    subgraph "External Systems"
        F[Transaction Source] -->|Raw Data| A
        C -->|High Risk Cases| G[Alert System]
        D -->|Performance Reports| H[Dashboard]
        I[Human Reviewer] -->|Review Decisions| E
    end
    
    subgraph "Cloud Infrastructure"
        J[Compute Engine] --- K[Cloud Storage]
        K --- L[Vertex AI]
        L --- M[Cloud SQL]
        M --- N[Cloud Functions]
        N --- O[Cloud Monitoring]
    end
    
    A -.->|Stores Data| M
    B -.->|Retrieves History| M
    D -.->|Logs Metrics| O
    
    style A fill:#90CAF9,stroke:#0D47A1,stroke-width:2px
    style B fill:#FFE082,stroke:#FF6F00,stroke-width:2px
    style C fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px
    style D fill:#CE93D8,stroke:#4A148C,stroke-width:2px
    style E fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px
```

## Agent Workflow Explanation

1. **Data Flow Begins**: Transaction data enters the system from external sources (e-commerce platforms, APIs, batch uploads)

2. **Data Ingest Agent** (Blue):
   - Receives raw transaction data
   - Validates against schema requirements
   - Normalizes and preprocesses data
   - Stores structured data in Cloud SQL

3. **Rule Engine Agent** (Yellow):
   - Retrieves transaction data and historical patterns
   - Applies weighted fraud detection rules
   - Calculates fraud scores and confidence levels
   - Identifies triggered rules and risk levels

4. **Insight Agent** (Green):
   - Receives fraud analysis results
   - Generates human-readable explanations
   - Creates prevention recommendations
   - Routes high-risk cases to alert system

5. **Metrics Agent** (Purple):
   - Calculates performance metrics (precision, recall, F1)
   - Tracks API costs and processing times
   - Logs metrics to Cloud Monitoring
   - Generates reports for dashboards

6. **Feedback Agent** (Red):
   - Processes decisions from human reviewers
   - Updates rule weights based on feedback
   - Identifies new fraud patterns
   - Feeds improved rules back to Rule Engine Agent

7. **Continuous Improvement Loop**: The feedback loop between human reviewers, the Feedback Agent, and the Rule Engine Agent creates a reinforcement learning cycle that continuously improves detection accuracy.

The entire system is deployed on Google Cloud Platform, with each component leveraging specific cloud services for optimal performance, scalability, and reliability. 