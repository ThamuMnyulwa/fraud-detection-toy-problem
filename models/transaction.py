"""
Transaction data models for the Agentic Coupon Abuse Detection System.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


class Transaction(BaseModel):
    """Transaction data model."""

    transaction_id: str
    user_id: str
    user_name: str
    email: str
    phone_number: str
    transaction_date: str
    merchant: str
    vendor_name: str
    channel: str
    items_count: int
    original_amount: float
    discount_amount: float
    final_amount: float
    coupon_code: str
    abuse: Optional[int] = None

    @validator("transaction_date")
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Invalid date format. Expected YYYY-MM-DD")

    @validator("original_amount", "discount_amount", "final_amount")
    def validate_amounts(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v

    @validator("items_count")
    def validate_items_count(cls, v):
        if v < 1:
            raise ValueError("Items count must be at least 1")
        return v


class FraudResult(BaseModel):
    """Fraud detection result model."""

    transaction_id: str
    fraud_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    triggered_rules: List[str] = []
    rule_weights: Dict[str, float] = {}
    explanation: Optional[str] = None
    prevention_recommendations: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    manual_review_required: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @validator("fraud_score")
    def validate_fraud_score(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Fraud score must be between 0 and 1")
        return v

    @validator("risk_level")
    def validate_risk_level(cls, v):
        valid_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"Risk level must be one of {valid_levels}")
        return v


class BatchAnalysisResult(BaseModel):
    """Batch analysis result model."""

    total_transactions: int
    flagged_transactions: int
    high_risk_transactions: int
    results: List[FraudResult]
    metrics: Optional[Dict[str, Any]] = None
