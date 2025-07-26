"""
Data processing tools for the Agentic Coupon Abuse Detection System.
"""

import pandas as pd
import json
from typing import Dict, List, Any, Union
from utils.config import logger
from utils.helpers import load_data, validate_transaction_schema
from models.transaction import Transaction


def file_reader(file_path: str) -> Dict[str, Any]:
    """
    Read data from a file and return it as a dictionary.

    Args:
        file_path: Path to the file to read

    Returns:
        Dictionary with data and metadata
    """
    try:
        df = load_data(file_path)
        return {
            "success": True,
            "data": df.to_dict(orient="records"),
            "metadata": {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_names": list(df.columns),
                "file_path": file_path,
            },
        }
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return {"success": False, "error": str(e)}


def data_validator(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate a list of transactions.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Dictionary with validation results
    """
    valid_transactions = []
    invalid_transactions = []

    for transaction in transactions:
        try:
            # Validate using Pydantic model
            validated_transaction = Transaction(**transaction).dict()
            valid_transactions.append(validated_transaction)
        except Exception as e:
            invalid_transactions.append({"transaction": transaction, "error": str(e)})

    return {
        "success": len(invalid_transactions) == 0,
        "valid_count": len(valid_transactions),
        "invalid_count": len(invalid_transactions),
        "valid_transactions": valid_transactions,
        "invalid_transactions": invalid_transactions,
    }


def data_preprocessor(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Preprocess a list of transactions.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Dictionary with preprocessed data
    """
    df = pd.DataFrame(transactions)

    # Convert date strings to datetime objects
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    # Sort by date
    df = df.sort_values("transaction_date")

    # Create additional features
    df["discount_ratio"] = df["discount_amount"] / df["original_amount"]

    # Count occurrences of phone numbers and user names
    phone_counts = df["phone_number"].value_counts().to_dict()
    name_counts = df["user_name"].value_counts().to_dict()

    # Add count features to the dataframe
    df["phone_number_count"] = df["phone_number"].map(phone_counts)
    df["user_name_count"] = df["user_name"].map(name_counts)

    # Convert back to list of dictionaries
    processed_transactions = df.to_dict(orient="records")

    return {
        "success": True,
        "processed_transactions": processed_transactions,
        "metadata": {
            "phone_counts": phone_counts,
            "name_counts": name_counts,
            "unique_phones": len(phone_counts),
            "unique_names": len(name_counts),
            "total_transactions": len(processed_transactions),
        },
    }
