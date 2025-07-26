"""
Metrics calculation tools for the Agentic Coupon Abuse Detection System.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union
from utils.config import logger
from utils.helpers import calculate_metrics


def performance_calculator(
    predictions: List[Dict[str, Any]], ground_truth: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate performance metrics for fraud detection.

    Args:
        predictions: List of prediction dictionaries
        ground_truth: List of ground truth dictionaries

    Returns:
        Dictionary with performance metrics
    """
    try:
        # Convert ground truth to DataFrame
        ground_truth_df = pd.DataFrame(ground_truth)

        # Calculate metrics
        metrics = calculate_metrics(predictions, ground_truth_df)

        return {"success": True, "metrics": metrics}
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}")
        return {"success": False, "error": str(e)}


def cost_tracker(
    num_transactions: int, num_api_calls: int, model_name: str = "gemini-1.5-pro"
) -> Dict[str, Any]:
    """
    Track the cost of fraud detection.

    Args:
        num_transactions: Number of transactions processed
        num_api_calls: Number of API calls made
        model_name: Name of the model used

    Returns:
        Dictionary with cost metrics
    """
    try:
        # Estimated costs per API call (in USD)
        cost_per_call = {
            "gemini-1.5-pro": 0.0025,
            "gemini-1.5-flash": 0.0010,
        }

        # Calculate costs
        model_cost = cost_per_call.get(model_name, 0.002)
        total_cost = num_api_calls * model_cost
        cost_per_transaction = (
            total_cost / num_transactions if num_transactions > 0 else 0
        )

        return {
            "success": True,
            "cost_metrics": {
                "total_cost_usd": round(total_cost, 4),
                "cost_per_transaction_usd": round(cost_per_transaction, 4),
                "num_transactions": num_transactions,
                "num_api_calls": num_api_calls,
                "model_name": model_name,
                "model_cost_per_call_usd": model_cost,
            },
        }
    except Exception as e:
        logger.error(f"Error tracking costs: {e}")
        return {"success": False, "error": str(e)}


def generate_metrics_report(
    performance_metrics: Dict[str, Any], cost_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a comprehensive metrics report.

    Args:
        performance_metrics: Performance metrics dictionary
        cost_metrics: Cost metrics dictionary

    Returns:
        Dictionary with comprehensive metrics report
    """
    try:
        # Combine metrics
        report = {
            "performance": performance_metrics,
            "cost": cost_metrics,
            "summary": {
                "accuracy": performance_metrics.get("accuracy", 0),
                "f1_score": performance_metrics.get("f1_score", 0),
                "total_cost_usd": cost_metrics.get("total_cost_usd", 0),
                "cost_per_transaction_usd": cost_metrics.get(
                    "cost_per_transaction_usd", 0
                ),
            },
        }

        # Calculate ROI (assuming each prevented fraud saves $50)
        true_positives = performance_metrics.get("true_positives", 0)
        false_positives = performance_metrics.get("false_positives", 0)
        total_cost = cost_metrics.get("total_cost_usd", 0)

        fraud_prevention_value = true_positives * 50  # $50 per prevented fraud
        false_positive_cost = (
            false_positives * 10
        )  # $10 per false positive (customer service cost)
        net_value = fraud_prevention_value - false_positive_cost - total_cost
        roi = (net_value / total_cost) * 100 if total_cost > 0 else 0

        report["roi"] = {
            "fraud_prevention_value_usd": round(fraud_prevention_value, 2),
            "false_positive_cost_usd": round(false_positive_cost, 2),
            "net_value_usd": round(net_value, 2),
            "roi_percentage": round(roi, 2),
        }

        return {"success": True, "report": report}
    except Exception as e:
        logger.error(f"Error generating metrics report: {e}")
        return {"success": False, "error": str(e)}
