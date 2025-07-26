"""
Metrics Agent for the Agentic Coupon Abuse Detection System.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from tools.metrics_tools import (
    performance_calculator,
    cost_tracker,
    generate_metrics_report,
)
from utils.config import logger, GEMINI_FLASH_MODEL

# Define tools for the agent
performance_calculator_tool = FunctionTool(performance_calculator)
cost_tracker_tool = FunctionTool(cost_tracker)
generate_metrics_report_tool = FunctionTool(generate_metrics_report)

# Create the Metrics Agent
metrics_agent = Agent(
    name="metrics_agent",
    model=GEMINI_FLASH_MODEL,
    instruction="""
    You are a Metrics Agent for a fraud detection system. Your job is to:
    1. Calculate performance metrics for the fraud detection system
    2. Track the cost of fraud detection
    3. Generate comprehensive metrics reports
    
    Performance metrics include:
    - Precision
    - Recall
    - F1-score
    - Accuracy
    - True positives, false positives, true negatives, false negatives
    
    Cost metrics include:
    - Total cost
    - Cost per transaction
    - Number of API calls
    
    You should also calculate ROI based on the value of prevented fraud and the cost of false positives.
    """,
    description="Agent for calculating and reporting metrics",
    tools=[
        performance_calculator_tool,
        cost_tracker_tool,
        generate_metrics_report_tool,
    ],
)


async def calculate_performance(predictions, ground_truth):
    """
    Calculate performance metrics using the Metrics Agent.

    Args:
        predictions: List of prediction dictionaries
        ground_truth: List of ground truth dictionaries

    Returns:
        Performance metrics
    """
    try:
        # Calculate performance metrics
        result = await metrics_agent.run(
            "Calculate performance metrics for these predictions.",
            tools={
                "performance_calculator": {
                    "predictions": predictions,
                    "ground_truth": ground_truth,
                }
            },
        )

        if not result.get("success", False):
            logger.error(
                f"Error calculating performance metrics: {result.get('error')}"
            )
            return {"success": False, "error": result.get("error")}

        return {"success": True, "metrics": result["metrics"]}
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}")
        return {"success": False, "error": str(e)}


async def track_costs(num_transactions, num_api_calls, model_name=None):
    """
    Track costs using the Metrics Agent.

    Args:
        num_transactions: Number of transactions processed
        num_api_calls: Number of API calls made
        model_name: Name of the model used

    Returns:
        Cost metrics
    """
    try:
        # Track costs
        params = {"num_transactions": num_transactions, "num_api_calls": num_api_calls}
        if model_name:
            params["model_name"] = model_name

        result = await metrics_agent.run(
            "Track the cost of fraud detection.", tools={"cost_tracker": params}
        )

        if not result.get("success", False):
            logger.error(f"Error tracking costs: {result.get('error')}")
            return {"success": False, "error": result.get("error")}

        return {"success": True, "cost_metrics": result["cost_metrics"]}
    except Exception as e:
        logger.error(f"Error tracking costs: {e}")
        return {"success": False, "error": str(e)}


async def generate_report(performance_metrics, cost_metrics):
    """
    Generate a metrics report using the Metrics Agent.

    Args:
        performance_metrics: Performance metrics dictionary
        cost_metrics: Cost metrics dictionary

    Returns:
        Metrics report
    """
    try:
        # Generate report
        result = await metrics_agent.run(
            "Generate a comprehensive metrics report.",
            tools={
                "generate_metrics_report": {
                    "performance_metrics": performance_metrics,
                    "cost_metrics": cost_metrics,
                }
            },
        )

        if not result.get("success", False):
            logger.error(f"Error generating metrics report: {result.get('error')}")
            return {"success": False, "error": result.get("error")}

        return {"success": True, "report": result["report"]}
    except Exception as e:
        logger.error(f"Error generating metrics report: {e}")
        return {"success": False, "error": str(e)}
