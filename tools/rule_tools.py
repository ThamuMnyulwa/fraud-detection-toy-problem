"""
Rule evaluation tools for the Agentic Coupon Abuse Detection System.
"""

import pandas as pd
from typing import Dict, List, Any, Union
from utils.config import logger, FRAUD_RULES, FRAUDULENT_VENDORS
from utils.helpers import calculate_fraud_score


def rule_evaluator(
    transaction: Dict[str, Any], all_transactions: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluate fraud rules for a single transaction.

    Args:
        transaction: Transaction data dictionary
        all_transactions: Optional list of all transactions for context

    Returns:
        Dictionary with fraud score and triggered rules
    """
    try:
        # Convert all_transactions to DataFrame if provided
        all_df = pd.DataFrame(all_transactions) if all_transactions else None

        # Calculate fraud score
        result = calculate_fraud_score(transaction, all_df)

        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error evaluating rules: {e}")
        return {"success": False, "error": str(e)}


def batch_rule_evaluator(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate fraud rules for a batch of transactions.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Dictionary with fraud scores and triggered rules
    """
    try:
        # Convert to DataFrame for efficient processing
        df = pd.DataFrame(transactions)

        results = []
        high_risk_count = 0
        flagged_count = 0

        for _, transaction in df.iterrows():
            # Calculate fraud score
            result = calculate_fraud_score(transaction.to_dict(), df)
            results.append(result)

            # Count high risk and flagged transactions
            if result["risk_level"] in ["HIGH", "CRITICAL"]:
                high_risk_count += 1
                flagged_count += 1
            elif result["risk_level"] == "MEDIUM":
                flagged_count += 1

        return {
            "success": True,
            "results": results,
            "summary": {
                "total_transactions": len(transactions),
                "flagged_transactions": flagged_count,
                "high_risk_transactions": high_risk_count,
                "flagged_percentage": round(flagged_count / len(transactions) * 100, 2),
                "high_risk_percentage": round(
                    high_risk_count / len(transactions) * 100, 2
                ),
            },
        }
    except Exception as e:
        logger.error(f"Error evaluating batch rules: {e}")
        return {"success": False, "error": str(e)}


def pattern_matcher(transaction: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    """
    Check if a transaction matches a specific fraud pattern.

    Args:
        transaction: Transaction data dictionary
        pattern: Pattern to match

    Returns:
        Dictionary with match result
    """
    try:
        result = False
        explanation = ""

        # Check for fraudulent vendor name
        if pattern == "fraudulent_vendor_name":
            result = transaction["vendor_name"] in FRAUDULENT_VENDORS
            explanation = f"Vendor '{transaction['vendor_name']}' is in the list of known fraudulent vendors"

        # Check for high discount ratio
        elif pattern == "high_discount_ratio":
            discount_ratio = (
                transaction["discount_amount"] / transaction["original_amount"]
            )
            result = discount_ratio > 0.5
            explanation = f"Discount ratio ({discount_ratio:.2f}) is suspiciously high"

        # Check for duplicate phone number
        elif (
            pattern == "same_phone_multiple_accounts"
            and "phone_number_count" in transaction
        ):
            result = transaction["phone_number_count"] > 1
            explanation = f"Phone number '{transaction['phone_number']}' is used in {transaction['phone_number_count']} transactions"

        # Check for duplicate user name
        elif (
            pattern == "same_user_name_multiple_accounts"
            and "user_name_count" in transaction
        ):
            result = transaction["user_name_count"] > 1
            explanation = f"User name '{transaction['user_name']}' appears in {transaction['user_name_count']} transactions"

        return {
            "success": True,
            "pattern": pattern,
            "match": result,
            "explanation": (
                explanation if result else f"No match for pattern '{pattern}'"
            ),
        }
    except Exception as e:
        logger.error(f"Error matching pattern {pattern}: {e}")
        return {"success": False, "error": str(e)}
