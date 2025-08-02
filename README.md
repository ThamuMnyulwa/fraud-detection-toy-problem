# Agentic Coupon Abuse Detection System

## Overview

This system uses a multi-agent architecture powered by Google ADK and Gemini to detect fraudulent coupon usage in e-commerce transactions.

## Fraud Detection Rules

The system detects fraud based on the following rules:

* **user\_name** and **phone\_number** (with duplicate detection)
* **vendor\_name** (including some intentionally fraudulent vendor names)
* Updated **abuse** label to flag any transaction where:
* the original fraud probability (`base_abuse`) was high
* the phone number is reused across transactions
* the user name appears multiple times
* the vendor name is known fraudulent

## Dataset

The dataset has 14 columns and is split into:

* **coupon\_abuse\_full\_with\_users.csv** (150 rows)
* **train\_coupon\_abuse\_with\_users.csv** (100 rows)
* **test\_coupon\_abuse\_with\_users.csv** (50 rows)

## Architecture

The system uses a multi-agent architecture with Google ADK:

1. **Data Ingest Agent**: Processes and validates transaction data
2. **Rule Engine Agent**: Evaluates transactions against fraud rules
3. **Insight Agent**: Generates explanations and recommendations
4. **Metrics Agent**: Tracks performance and costs
5. **Feedback Agent**: Learns from ground truth labels

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/fraud-detection-toy-problem.git
cd fraud-detection-toy-problem
```

2. Install dependencies:
```bash
uv init
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Google API key
```

## Usage

### Running the Backend

To run the backend system and evaluate the test dataset:

```bash
uv run python main.py
```

### Running the Streamlit Frontend

To run the Streamlit frontend:

```bash
cd frontend_streamlit_app
uv run python run_app.py
```

Or directly with Streamlit:

```bash
uv run streamlit run frontend_streamlit_app/app.py
```

## Features

- **Individual Transaction Check**: Analyze a single transaction for potential fraud
- **Batch Analysis**: Process multiple transactions at once
- **Metrics Dashboard**: View system performance metrics

