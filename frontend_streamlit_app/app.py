"""
Streamlit app for the Agentic Coupon Abuse Detection System.
"""

import streamlit as st
import pandas as pd
import sys
import os
import json
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Coupon Abuse Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state to track submissions
if "previous_submissions" not in st.session_state:
    st.session_state.previous_submissions = {
        "user_names": set(),
        "emails": set(),
        "phone_numbers": set(),
    }

# Initialize agent logs in session state
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []

# Sidebar
st.sidebar.title("🛡️ Coupon Abuse Detection")
st.sidebar.markdown("Detect fraudulent coupon usage with AI")

# Navigation
page = st.sidebar.radio(
    "Navigation", ["Home", "Transaction Check", "Batch Analysis", "Agent Monitoring"]
)

# Home page
if page == "Home":
    st.title("🛡️ Agentic Coupon Abuse Detection System")

    st.markdown(
        """
    ## Welcome to the Coupon Abuse Detection System
    
    This system uses a multi-agent architecture powered by Google ADK and Gemini to detect fraudulent coupon usage.
    
    ### Key Features
    
    - **Individual Transaction Check**: Analyze a single transaction for potential fraud
    - **Batch Analysis**: Process multiple transactions at once
    - **Agent Monitoring**: Visualize agent activity and performance
    
    ### How It Works
    
    1. **Data Ingest Agent** processes and validates transaction data
    2. **Rule Engine Agent** evaluates transactions against fraud rules
    3. **Insight Agent** generates explanations and recommendations
    4. **Metrics Agent** tracks performance and costs
    5. **Feedback Agent** learns from ground truth labels
    
    ### Getting Started
    
    Use the navigation menu on the left to explore the system.
    """
    )

    st.info(
        "This is a demonstration system. In a production environment, you would connect to a real-time transaction database."
    )

# Transaction Check page
elif page == "Transaction Check":
    st.title("🔍 Transaction Check")
    st.markdown("Check an individual transaction for potential fraud.")

    # Input form
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)

        with col1:
            transaction_id = st.text_input("Transaction ID", "tx_0001")
            user_id = st.text_input("User ID", "user_001")
            user_name = st.text_input("User Name", "John Smith")
            email = st.text_input("Email", "john.smith@example.com")
            phone_number = st.text_input("Phone Number", "+27612345678")

        with col2:
            merchant = st.selectbox(
                "Merchant", ["StoreA", "StoreB", "StoreC", "StoreD", "StoreE"]
            )
            vendor_name = st.selectbox(
                "Vendor Name",
                [
                    "StoreA",
                    "StoreB",
                    "StoreC",
                    "StoreD",
                    "StoreE",
                    "FakeShop",
                    "ScamStore",
                    "FraudMart",
                ],
            )
            channel = st.selectbox("Channel", ["online", "in-store"])
            items_count = st.number_input("Items Count", min_value=1, value=3)
            coupon_code = st.selectbox(
                "Coupon Code", ["SAVE10", "SAVE20", "FREESHIP", "WELCOME", "HOLIDAY50"]
            )

        col1, col2, col3 = st.columns(3)
        with col1:
            original_amount = st.number_input(
                "Original Amount ($)", min_value=0.0, value=100.0
            )
        with col2:
            discount_amount = st.number_input(
                "Discount Amount ($)", min_value=0.0, value=20.0
            )
        with col3:
            final_amount = st.number_input(
                "Final Amount ($)", min_value=0.0, value=80.0
            )

        submit_button = st.form_submit_button("Check Transaction")

    # Process transaction when form is submitted
    if submit_button:
        transaction = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "user_name": user_name,
            "email": email,
            "phone_number": phone_number,
            "transaction_date": datetime.now().strftime("%Y-%m-%d"),
            "merchant": merchant,
            "vendor_name": vendor_name,
            "channel": channel,
            "items_count": items_count,
            "original_amount": original_amount,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "coupon_code": coupon_code,
        }

        with st.spinner("Analyzing transaction..."):
            # Log agent activity for visualization
            current_time = datetime.now()

            # Data Ingest Agent
            st.session_state.agent_logs.append(
                {
                    "agent": "DataIngestAgent",
                    "action": "Validating transaction data",
                    "timestamp": current_time.isoformat(),
                    "duration": 0.8,
                    "status": "completed",
                }
            )
            time.sleep(0.2)  # Simulate processing time

            # Rule Engine Agent
            # For demo purposes, we'll use a simple rule-based approach
            fraud_score = 0.0
            triggered_rules = []

            # Check for fraudulent vendor
            if vendor_name in ["FakeShop", "ScamStore", "FraudMart"]:
                fraud_score += 0.9
                triggered_rules.append("fraudulent_vendor_name")

            # Check for high discount ratio
            discount_ratio = discount_amount / original_amount
            if discount_ratio > 0.5:
                fraud_score += 0.75
                triggered_rules.append("high_discount_ratio")

            # Check for duplicate user name
            if user_name in st.session_state.previous_submissions["user_names"]:
                fraud_score += 0.85
                triggered_rules.append("same_user_name_multiple_accounts")

            # Check for duplicate email
            if email in st.session_state.previous_submissions["emails"]:
                fraud_score += 0.85
                triggered_rules.append("same_email_multiple_accounts")

            # Check for duplicate phone number
            if phone_number in st.session_state.previous_submissions["phone_numbers"]:
                fraud_score += 0.85
                triggered_rules.append("same_phone_multiple_accounts")

            # Add current submission to tracking
            st.session_state.previous_submissions["user_names"].add(user_name)
            st.session_state.previous_submissions["emails"].add(email)
            st.session_state.previous_submissions["phone_numbers"].add(phone_number)

            # Normalize fraud score
            fraud_score = min(fraud_score, 1.0)

            st.session_state.agent_logs.append(
                {
                    "agent": "RuleEngineAgent",
                    "action": "Evaluating fraud rules",
                    "timestamp": (current_time + timedelta(seconds=1)).isoformat(),
                    "duration": 1.2,
                    "status": "completed",
                    "details": f"Fraud score: {fraud_score:.2f}, Rules triggered: {', '.join(triggered_rules) if triggered_rules else 'None'}",
                }
            )
            time.sleep(0.3)  # Simulate processing time

            # Determine risk level
            if fraud_score >= 0.9:
                risk_level = "CRITICAL"
            elif fraud_score >= 0.7:
                risk_level = "HIGH"
            elif fraud_score >= 0.4:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            # Insight Agent
            # Generate explanation
            explanation = ""
            if "fraudulent_vendor_name" in triggered_rules:
                explanation += f"The vendor '{vendor_name}' is known to be associated with fraudulent activities. "
            if "high_discount_ratio" in triggered_rules:
                explanation += (
                    f"The discount ratio ({discount_ratio:.2f}) is suspiciously high. "
                )
            if "same_user_name_multiple_accounts" in triggered_rules:
                explanation += f"The user name '{user_name}' has been used in previous transactions. "
            if "same_email_multiple_accounts" in triggered_rules:
                explanation += (
                    f"The email '{email}' has been used in previous transactions. "
                )
            if "same_phone_multiple_accounts" in triggered_rules:
                explanation += f"The phone number '{phone_number}' has been used in previous transactions. "

            if not explanation:
                explanation = "No suspicious patterns detected in this transaction."

            # Generate recommendations
            if fraud_score > 0.0:
                recommendations = [
                    "Verify the customer's identity",
                    "Check for previous transactions from this user",
                    "Review the vendor's history",
                ]
                if (
                    "same_user_name_multiple_accounts" in triggered_rules
                    or "same_email_multiple_accounts" in triggered_rules
                    or "same_phone_multiple_accounts" in triggered_rules
                ):
                    recommendations.append(
                        "Investigate potential account sharing or duplicate accounts"
                    )
            else:
                recommendations = ["No specific recommendations needed."]

            st.session_state.agent_logs.append(
                {
                    "agent": "InsightAgent",
                    "action": "Generating insights and recommendations",
                    "timestamp": (current_time + timedelta(seconds=2.5)).isoformat(),
                    "duration": 1.5,
                    "status": "completed",
                    "details": f"Risk level: {risk_level}",
                }
            )
            time.sleep(0.4)  # Simulate processing time

            # Metrics Agent
            st.session_state.agent_logs.append(
                {
                    "agent": "MetricsAgent",
                    "action": "Calculating performance metrics",
                    "timestamp": (current_time + timedelta(seconds=4)).isoformat(),
                    "duration": 0.7,
                    "status": "completed",
                    "details": f"API cost: $0.002, Latency: 150ms",
                }
            )
            time.sleep(0.2)  # Simulate processing time

            # Display results
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Fraud Detection Result")

                # Risk level with appropriate color
                risk_color = {
                    "LOW": "green",
                    "MEDIUM": "orange",
                    "HIGH": "red",
                    "CRITICAL": "darkred",
                }

                st.markdown(
                    f"**Risk Level:** <span style='color:{risk_color[risk_level]}'>{risk_level}</span>",
                    unsafe_allow_html=True,
                )

                # Fraud score gauge
                st.markdown(f"**Fraud Score:** {fraud_score:.2f}")
                st.progress(fraud_score)

                # Triggered rules
                if triggered_rules:
                    st.markdown("**Triggered Rules:**")
                    for rule in triggered_rules:
                        st.markdown(f"- {rule}")
                else:
                    st.markdown("**No rules triggered**")

            with col2:
                st.subheader("Explanation & Recommendations")

                st.markdown("**Explanation:**")
                st.markdown(explanation)

                st.markdown("**Recommendations:**")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

                # Manual review flag
                if fraud_score >= 0.7:
                    st.warning("⚠️ This transaction requires manual review")
                else:
                    st.success("✅ No manual review required")

# Batch Analysis page
elif page == "Batch Analysis":
    st.title("📊 Batch Analysis")
    st.markdown("Analyze multiple transactions at once.")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload transaction data (CSV or JSON)", type=["csv", "json"]
    )

    if uploaded_file:
        # Load the data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_json(uploaded_file)

        with st.spinner("Processing transactions..."):
            # Log agent activity for batch processing
            current_time = datetime.now()

            # Data Ingest Agent for batch
            st.session_state.agent_logs.append(
                {
                    "agent": "DataIngestAgent",
                    "action": f"Processing batch of {len(df)} transactions",
                    "timestamp": current_time.isoformat(),
                    "duration": 1.5,
                    "status": "completed",
                }
            )
            time.sleep(0.3)  # Simulate processing time

            # For demo purposes, we'll use a simple rule-based approach
            results = []
            flagged_count = 0
            high_risk_count = 0

            # Track duplicates within the batch
            batch_user_names = set()
            batch_emails = set()
            batch_phone_numbers = set()

            # Rule Engine Agent for batch
            for _, row in df.iterrows():
                transaction = row.to_dict()

                # Calculate fraud score
                fraud_score = 0.0
                triggered_rules = []

                # Check for fraudulent vendor
                if transaction["vendor_name"] in ["FakeShop", "ScamStore", "FraudMart"]:
                    fraud_score += 0.9
                    triggered_rules.append("fraudulent_vendor_name")

                # Check for high discount ratio
                discount_ratio = (
                    transaction["discount_amount"] / transaction["original_amount"]
                )
                if discount_ratio > 0.5:
                    fraud_score += 0.75
                    triggered_rules.append("high_discount_ratio")

                # Check for duplicate user name within batch and previous submissions
                user_name = transaction.get("user_name", "")
                if user_name:
                    if (
                        user_name in batch_user_names
                        or user_name
                        in st.session_state.previous_submissions["user_names"]
                    ):
                        fraud_score += 0.85
                        triggered_rules.append("same_user_name_multiple_accounts")
                    batch_user_names.add(user_name)
                    st.session_state.previous_submissions["user_names"].add(user_name)

                # Check for duplicate email within batch and previous submissions
                email = transaction.get("email", "")
                if email:
                    if (
                        email in batch_emails
                        or email in st.session_state.previous_submissions["emails"]
                    ):
                        fraud_score += 0.85
                        triggered_rules.append("same_email_multiple_accounts")
                    batch_emails.add(email)
                    st.session_state.previous_submissions["emails"].add(email)

                # Check for duplicate phone number within batch and previous submissions
                phone_number = transaction.get("phone_number", "")
                if phone_number:
                    if (
                        phone_number in batch_phone_numbers
                        or phone_number
                        in st.session_state.previous_submissions["phone_numbers"]
                    ):
                        fraud_score += 0.85
                        triggered_rules.append("same_phone_multiple_accounts")
                    batch_phone_numbers.add(phone_number)
                    st.session_state.previous_submissions["phone_numbers"].add(
                        phone_number
                    )

                # Normalize fraud score
                fraud_score = min(fraud_score, 1.0)

                # Determine risk level
                if fraud_score >= 0.9:
                    risk_level = "CRITICAL"
                    flagged_count += 1
                    high_risk_count += 1
                elif fraud_score >= 0.7:
                    risk_level = "HIGH"
                    flagged_count += 1
                    high_risk_count += 1
                elif fraud_score >= 0.4:
                    risk_level = "MEDIUM"
                    flagged_count += 1
                else:
                    risk_level = "LOW"

                # Add result
                results.append(
                    {
                        "transaction_id": transaction["transaction_id"],
                        "fraud_score": fraud_score,
                        "risk_level": risk_level,
                        "triggered_rules": triggered_rules,
                        "manual_review_required": fraud_score >= 0.7,
                    }
                )

            st.session_state.agent_logs.append(
                {
                    "agent": "RuleEngineAgent",
                    "action": "Evaluating batch fraud rules",
                    "timestamp": (current_time + timedelta(seconds=2)).isoformat(),
                    "duration": 2.5,
                    "status": "completed",
                    "details": f"Flagged: {flagged_count}/{len(df)} transactions",
                }
            )
            time.sleep(0.4)  # Simulate processing time

            # Insight Agent for batch
            st.session_state.agent_logs.append(
                {
                    "agent": "InsightAgent",
                    "action": "Generating batch insights",
                    "timestamp": (current_time + timedelta(seconds=5)).isoformat(),
                    "duration": 1.8,
                    "status": "completed",
                    "details": f"High risk: {high_risk_count}/{len(df)} transactions",
                }
            )
            time.sleep(0.3)  # Simulate processing time

            # Metrics Agent for batch
            st.session_state.agent_logs.append(
                {
                    "agent": "MetricsAgent",
                    "action": "Calculating batch performance metrics",
                    "timestamp": (current_time + timedelta(seconds=7)).isoformat(),
                    "duration": 1.2,
                    "status": "completed",
                    "details": f"API cost: ${0.0005 * len(df):.4f}, Avg latency: {120 + random.randint(0, 60)}ms",
                }
            )
            time.sleep(0.2)  # Simulate processing time

            # Display summary
            st.subheader("Batch Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Transactions", len(df))

            with col2:
                st.metric("Flagged Transactions", flagged_count)

            with col3:
                st.metric("High Risk Transactions", high_risk_count)

            # Display results table
            st.subheader("Transaction Results")

            results_df = pd.DataFrame(results)

            # Add color coding for risk level
            def color_risk(val):
                if val == "LOW":
                    return "background-color: green; color: white"
                elif val == "MEDIUM":
                    return "background-color: orange; color: white"
                elif val == "HIGH":
                    return "background-color: red; color: white"
                elif val == "CRITICAL":
                    return "background-color: darkred; color: white"
                return ""

            # Select columns to display
            display_cols = [
                "transaction_id",
                "fraud_score",
                "risk_level",
                "triggered_rules",
                "manual_review_required",
            ]
            styled_df = results_df[display_cols].style.applymap(
                color_risk, subset=["risk_level"]
            )

            st.dataframe(styled_df)

            # Download results
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="fraud_detection_results.csv",
                mime="text/csv",
            )

# Agent Monitoring page
elif page == "Agent Monitoring":
    st.title("👁️ Agent Monitoring")
    st.markdown("Visualize agent activity and performance.")

    # Display agent logs in a timeline
    st.subheader("Agent Activity Timeline")

    if not st.session_state.agent_logs:
        st.info(
            "No agent activity recorded yet. Process a transaction to see agent activity."
        )
    else:
        # Create a DataFrame from logs
        logs_df = pd.DataFrame(st.session_state.agent_logs)

        # Sort by timestamp
        logs_df["timestamp"] = pd.to_datetime(logs_df["timestamp"])
        logs_df = logs_df.sort_values("timestamp")

        # Display timeline
        for i, log in logs_df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    timestamp = log["timestamp"].strftime("%H:%M:%S")
                    st.markdown(f"**{timestamp}**")

                    # Agent color coding
                    agent_colors = {
                        "DataIngestAgent": "blue",
                        "RuleEngineAgent": "orange",
                        "InsightAgent": "green",
                        "MetricsAgent": "purple",
                        "FeedbackAgent": "red",
                    }
                    color = agent_colors.get(log["agent"], "gray")

                    st.markdown(
                        f"<span style='color:{color};font-weight:bold'>{log['agent']}</span>",
                        unsafe_allow_html=True,
                    )

                with col2:
                    st.markdown(f"**Action:** {log['action']}")
                    if "details" in log and log["details"]:
                        st.markdown(f"**Details:** {log['details']}")
                    st.markdown(f"**Duration:** {log['duration']}s")
                    st.markdown(f"**Status:** {log['status'].capitalize()}")

                st.markdown("---")

        # Display agent performance metrics
        st.subheader("Agent Performance")

        # Group by agent and calculate metrics
        agent_metrics = (
            logs_df.groupby("agent")
            .agg(count=("action", "count"), avg_duration=("duration", "mean"))
            .reset_index()
        )

        # Display as bar chart
        st.bar_chart(agent_metrics.set_index("agent")["avg_duration"])

        # Display API usage
        st.subheader("API Usage")

        # Calculate total API cost from metrics agent logs
        metrics_logs = logs_df[logs_df["agent"] == "MetricsAgent"]
        total_cost = 0
        for _, log in metrics_logs.iterrows():
            if "details" in log and "API cost" in log["details"]:
                cost_str = log["details"].split("API cost: $")[1].split(",")[0]
                try:
                    total_cost += float(cost_str)
                except:
                    pass

        st.metric("Total API Cost", f"${total_cost:.4f}")

        # Add AgentOps link
        st.markdown("### Advanced Monitoring")
        st.markdown(
            "For more advanced monitoring, consider using a dedicated monitoring solution."
        )

        # Clear logs button
        if st.button("Clear Agent Logs"):
            st.session_state.agent_logs = []
            st.success("Agent logs cleared")
            st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2023 Agentic Coupon Abuse Detection System")
st.sidebar.markdown("Powered by Google ADK and Gemini")

# Add a reset button to clear previous submissions (for testing)
if st.sidebar.button("Reset Submission History"):
    st.session_state.previous_submissions = {
        "user_names": set(),
        "emails": set(),
        "phone_numbers": set(),
    }
    st.sidebar.success("Submission history has been reset")
