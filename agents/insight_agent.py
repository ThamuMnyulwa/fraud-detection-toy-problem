"""
Insight Agent for the Agentic Coupon Abuse Detection System.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from tools.insight_tools import generate_explanation, generate_batch_insights
from utils.config import logger, GEMINI_PRO_MODEL

# Define tools for the agent
generate_explanation_tool = FunctionTool(generate_explanation)
generate_batch_insights_tool = FunctionTool(generate_batch_insights)

# Create the Insight Agent
insight_agent = Agent(
    name="insight_agent",
    model=GEMINI_PRO_MODEL,
    instruction="""
    You are an Insight Agent for a fraud detection system. Your job is to:
    1. Generate human-readable explanations for fraud detection results
    2. Provide insights on patterns and trends in fraud detection
    3. Recommend actions to prevent fraud
    
    For individual transactions, you should explain why they were flagged and provide recommendations.
    For batch analysis, you should identify patterns and trends, and provide strategic recommendations.
    """,
    description="Agent for generating insights from fraud detection results",
    tools=[generate_explanation_tool, generate_batch_insights_tool],
)


async def explain_transaction(fraud_result, transaction):
    """
    Generate an explanation for a transaction using the Insight Agent.

    Args:
        fraud_result: Fraud detection result dictionary
        transaction: Original transaction data

    Returns:
        Explanation and recommendations
    """
    try:
        # Generate explanation
        result = await insight_agent.run(
            "Generate an explanation for this fraud detection result.",
            tools={
                "generate_explanation": {
                    "fraud_result": fraud_result,
                    "transaction": transaction,
                }
            },
        )

        if not result.get("success", False):
            logger.error(f"Error generating explanation: {result.get('error')}")
            return {"success": False, "error": result.get("error")}

        return {
            "success": True,
            "explanation": result["explanation"],
            "recommendations": result["recommendations"],
        }
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        return {"success": False, "error": str(e)}


async def analyze_batch(batch_results):
    """
    Generate insights for a batch of transactions using the Insight Agent.

    Args:
        batch_results: Results from batch rule evaluation

    Returns:
        Batch insights
    """
    try:
        # Generate batch insights
        result = await insight_agent.run(
            "Generate insights for this batch of fraud detection results.",
            tools={"generate_batch_insights": {"batch_results": batch_results}},
        )

        if not result.get("success", False):
            logger.error(f"Error generating batch insights: {result.get('error')}")
            return {"success": False, "error": result.get("error")}

        return {
            "success": True,
            "summary": result["summary"],
            "rule_frequency": result["rule_frequency"],
            "key_insights": result["key_insights"],
            "recommendations": result["recommendations"],
        }
    except Exception as e:
        logger.error(f"Error generating batch insights: {e}")
        return {"success": False, "error": str(e)}
