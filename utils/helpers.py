"""
Helper functions for the Agentic Coupon Abuse Detection System.
"""

import pandas as pd
import json
from typing import Dict, List, Any, Union, Optional
from utils.config import logger, FRAUDULENT_VENDORS


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from CSV or JSON file.

    Args:
        file_path: Path to the data file

    Returns:
        DataFrame containing the data
    """
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".json"):
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise


def validate_transaction_schema(transaction: Dict[str, Any]) -> bool:
    """
    Validate that a transaction has all required fields.

    Args:
        transaction: Transaction data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "transaction_id",
        "user_id",
        "user_name",
        "email",
        "phone_number",
        "transaction_date",
        "merchant",
        "vendor_name",
        "channel",
        "items_count",
        "original_amount",
        "discount_amount",
        "final_amount",
        "coupon_code",
    ]

    return all(field in transaction for field in required_fields)


def calculate_fraud_score(
    transaction: Dict[str, Any], all_transactions: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Calculate fraud score for a transaction based on rules.

    Args:
        transaction: Transaction data dictionary
        all_transactions: Optional DataFrame with all transactions for context

    Returns:
        Dictionary with fraud score and triggered rules
    """
    fraud_score = 0.0
    triggered_rules = []
    rule_weights = {}

    # Check for fraudulent vendor
    if transaction["vendor_name"] in FRAUDULENT_VENDORS:
        fraud_score += 0.9
        triggered_rules.append("fraudulent_vendor_name")
        rule_weights["fraudulent_vendor_name"] = 0.9

    # Check for high discount ratio
    discount_ratio = transaction["discount_amount"] / transaction["original_amount"]
    if discount_ratio > 0.5:
        fraud_score += 0.75
        triggered_rules.append("high_discount_ratio")
        rule_weights["high_discount_ratio"] = 0.75

    # Check for duplicate phone number or username (if all_transactions is provided)
    if all_transactions is not None:
        # Check for duplicate phone number
        phone_count = all_transactions[
            all_transactions["phone_number"] == transaction["phone_number"]
        ].shape[0]
        if phone_count > 1:
            fraud_score += 0.85
            triggered_rules.append("same_phone_multiple_accounts")
            rule_weights["same_phone_multiple_accounts"] = 0.85

        # Check for duplicate username
        name_count = all_transactions[
            all_transactions["user_name"] == transaction["user_name"]
        ].shape[0]
        if name_count > 1:
            fraud_score += 0.85
            triggered_rules.append("same_user_name_multiple_accounts")
            rule_weights["same_user_name_multiple_accounts"] = 0.85

    # Normalize fraud score to be between 0 and 1
    fraud_score = min(fraud_score, 1.0)

    # Determine risk level
    if fraud_score >= 0.9:
        risk_level = "CRITICAL"
    elif fraud_score >= 0.7:
        risk_level = "HIGH"
    elif fraud_score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "transaction_id": transaction["transaction_id"],
        "fraud_score": fraud_score,
        "risk_level": risk_level,
        "triggered_rules": triggered_rules,
        "rule_weights": rule_weights,
        "manual_review_required": fraud_score >= 0.7,
    }


def calculate_metrics(
    predictions: List[Dict[str, Any]], ground_truth: pd.DataFrame
) -> Dict[str, float]:
    """
    Calculate performance metrics for fraud detection.

    Args:
        predictions: List of prediction dictionaries
        ground_truth: DataFrame with ground truth labels

    Returns:
        Dictionary with performance metrics
    """
    # Create a mapping of transaction_id to prediction
    pred_map = {p["transaction_id"]: p["fraud_score"] >= 0.7 for p in predictions}

    # Extract ground truth
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for _, row in ground_truth.iterrows():
        transaction_id = row["transaction_id"]
        if transaction_id in pred_map:
            is_fraud_pred = pred_map[transaction_id]
            is_fraud_true = row["abuse"] == 1

            if is_fraud_pred and is_fraud_true:
                true_positives += 1
            elif is_fraud_pred and not is_fraud_true:
                false_positives += 1
            elif not is_fraud_pred and not is_fraud_true:
                true_negatives += 1
            else:  # not is_fraud_pred and is_fraud_true
                false_negatives += 1

    # Calculate metrics
    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0
    )
    f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )
    accuracy = (true_positives + true_negatives) / (
        true_positives + true_negatives + false_positives + false_negatives
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "accuracy": accuracy,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
        "false_negatives": false_negatives,
    }
