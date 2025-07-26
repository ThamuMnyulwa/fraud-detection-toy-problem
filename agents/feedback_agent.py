"""
Feedback Agent for the Agentic Coupon Abuse Detection System.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from utils.config import logger, GEMINI_PRO_MODEL, FRAUD_RULES
import pandas as pd
import numpy as np
from typing import Dict, List, Any


# Define custom tools for the feedback agent
def process_feedback(
    predictions: List[Dict[str, Any]], ground_truth: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Process feedback from ground truth labels.

    Args:
        predictions: List of prediction dictionaries
        ground_truth: List of ground truth dictionaries

    Returns:
        Dictionary with processed feedback
    """
    try:
        # Convert to DataFrames
        pred_df = pd.DataFrame(predictions)
        truth_df = pd.DataFrame(ground_truth)

        # Merge predictions with ground truth
        merged = pd.merge(
            pred_df[["transaction_id", "fraud_score", "triggered_rules"]],
            truth_df[["transaction_id", "abuse"]],
            on="transaction_id",
        )

        # Calculate errors
        merged["error"] = merged.apply(
            lambda x: abs((x["fraud_score"] >= 0.7) - x["abuse"]), axis=1
        )

        # Analyze rule effectiveness
        rule_effectiveness = {}
        for _, row in merged.iterrows():
            rules = (
                row["triggered_rules"]
                if isinstance(row["triggered_rules"], list)
                else []
            )
            is_correct = row["error"] == 0

            for rule in rules:
                if rule not in rule_effectiveness:
                    rule_effectiveness[rule] = {"correct": 0, "incorrect": 0}

                if is_correct:
                    rule_effectiveness[rule]["correct"] += 1
                else:
                    rule_effectiveness[rule]["incorrect"] += 1

        # Calculate rule accuracy
        for rule, counts in rule_effectiveness.items():
            total = counts["correct"] + counts["incorrect"]
            accuracy = counts["correct"] / total if total > 0 else 0
            rule_effectiveness[rule]["accuracy"] = accuracy

        # Find most common errors
        error_cases = merged[merged["error"] > 0]
        false_positives = error_cases[error_cases["abuse"] == 0]
        false_negatives = error_cases[error_cases["abuse"] == 1]

        return {
            "success": True,
            "rule_effectiveness": rule_effectiveness,
            "error_analysis": {
                "total_errors": len(error_cases),
                "false_positives": len(false_positives),
                "false_negatives": len(false_negatives),
            },
            "false_positive_examples": false_positives.to_dict(orient="records"),
            "false_negative_examples": false_negatives.to_dict(orient="records"),
        }
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        return {"success": False, "error": str(e)}


def update_rule_weights(
    rule_effectiveness: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Update rule weights based on effectiveness.

    Args:
        rule_effectiveness: Dictionary with rule effectiveness metrics

    Returns:
        Dictionary with updated rule weights
    """
    try:
        # Copy the current rules
        updated_rules = FRAUD_RULES.copy()

        # Update weights based on accuracy
        for rule_category, rule_info in updated_rules.items():
            patterns = rule_info["patterns"]
            new_weight = rule_info["weight"]

            # Calculate average accuracy for patterns in this category
            pattern_accuracies = []
            for pattern in patterns:
                if pattern in rule_effectiveness:
                    pattern_accuracies.append(rule_effectiveness[pattern]["accuracy"])

            # Update weight if we have accuracy data
            if pattern_accuracies:
                avg_accuracy = sum(pattern_accuracies) / len(pattern_accuracies)
                # Adjust weight (keep between 0.5 and 0.95)
                new_weight = max(0.5, min(0.95, avg_accuracy))
                updated_rules[rule_category]["weight"] = round(new_weight, 2)

        return {
            "success": True,
            "original_rules": FRAUD_RULES,
            "updated_rules": updated_rules,
        }
    except Exception as e:
        logger.error(f"Error updating rule weights: {e}")
        return {"success": False, "error": str(e)}


# Create tool objects
process_feedback_tool = FunctionTool(process_feedback)
update_rule_weights_tool = FunctionTool(update_rule_weights)

# Create the Feedback Agent
feedback_agent = Agent(
    name="feedback_agent",
    model=GEMINI_PRO_MODEL,
    instruction="""
    You are a Feedback Agent for a fraud detection system. Your job is to:
    1. Process feedback from ground truth labels
    2. Analyze the effectiveness of fraud detection rules
    3. Update rule weights based on performance
    
    You should identify which rules are most effective at detecting fraud and which ones
    generate the most false positives. Then, you should update the weights of the rules
    to improve overall performance.
    """,
    description="Agent for processing feedback and updating rules",
    tools=[process_feedback_tool, update_rule_weights_tool],
)


async def process_model_feedback(predictions, ground_truth):
    """
    Process feedback and update rules using the Feedback Agent.

    Args:
        predictions: List of prediction dictionaries
        ground_truth: List of ground truth dictionaries

    Returns:
        Feedback analysis and updated rules
    """
    try:
        # Process feedback
        feedback_result = await feedback_agent.run(
            "Process feedback from these predictions and ground truth labels.",
            tools={
                "process_feedback": {
                    "predictions": predictions,
                    "ground_truth": ground_truth,
                }
            },
        )

        if not feedback_result.get("success", False):
            logger.error(f"Error processing feedback: {feedback_result.get('error')}")
            return {"success": False, "error": feedback_result.get("error")}

        # Update rule weights
        rule_effectiveness = feedback_result["rule_effectiveness"]
        update_result = await feedback_agent.run(
            "Update rule weights based on this effectiveness data.",
            tools={"update_rule_weights": {"rule_effectiveness": rule_effectiveness}},
        )

        if not update_result.get("success", False):
            logger.error(f"Error updating rule weights: {update_result.get('error')}")
            return {"success": False, "error": update_result.get("error")}

        return {
            "success": True,
            "feedback_analysis": {
                "rule_effectiveness": rule_effectiveness,
                "error_analysis": feedback_result["error_analysis"],
            },
            "updated_rules": update_result["updated_rules"],
        }
    except Exception as e:
        logger.error(f"Error processing model feedback: {e}")
        return {"success": False, "error": str(e)}
