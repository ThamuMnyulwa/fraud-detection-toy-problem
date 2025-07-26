"""
Rule Engine Agent for the Agentic Coupon Abuse Detection System.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from tools.rule_tools import rule_evaluator, batch_rule_evaluator, pattern_matcher
from utils.config import logger, GEMINI_PRO_MODEL

# Define tools for the agent
rule_evaluator_tool = FunctionTool(rule_evaluator)
batch_rule_evaluator_tool = FunctionTool(batch_rule_evaluator)
pattern_matcher_tool = FunctionTool(pattern_matcher)

# Create the Rule Engine Agent
rule_engine_agent = Agent(
    name="rule_engine_agent",
    model=GEMINI_PRO_MODEL,
    instruction="""
    You are a Rule Engine Agent for a fraud detection system. Your job is to:
    1. Evaluate transactions against fraud detection rules
    2. Identify potentially fraudulent transactions
    3. Provide fraud scores and explanations
    
    The main fraud patterns to look for are:
    - Fraudulent vendor names (FakeShop, ScamStore, FraudMart)
    - High discount ratio (discount_amount / original_amount > 0.5)
    - Same phone number used across multiple accounts
    - Same user name appearing in multiple transactions
    
    For each transaction, you should calculate a fraud score and identify which rules were triggered.
    """,
    description="Agent for evaluating fraud detection rules",
    tools=[rule_evaluator_tool, batch_rule_evaluator_tool, pattern_matcher_tool],
)


async def evaluate_transaction(transaction, all_transactions=None):
    """
    Evaluate a single transaction using the Rule Engine Agent.

    Args:
        transaction: Transaction data dictionary
        all_transactions: Optional list of all transactions for context

    Returns:
        Fraud detection result
    """
    try:
        # Evaluate the transaction
        result = await rule_engine_agent.run(
            "Evaluate this transaction for potential fraud.",
            tools={
                "rule_evaluator": {
                    "transaction": transaction,
                    "all_transactions": all_transactions,
                }
            },
        )

        if not result.get("success", False):
            logger.error(f"Error evaluating transaction: {result.get('error')}")
            return {"success": False, "error": result.get("error")}

        return {"success": True, "result": result["result"]}
    except Exception as e:
        logger.error(f"Error evaluating transaction: {e}")
        return {"success": False, "error": str(e)}


async def evaluate_batch(transactions):
    """
    Evaluate a batch of transactions using the Rule Engine Agent.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Batch evaluation results
    """
    try:
        # Evaluate the batch
        result = await rule_engine_agent.run(
            "Evaluate this batch of transactions for potential fraud.",
            tools={"batch_rule_evaluator": {"transactions": transactions}},
        )

        if not result.get("success", False):
            logger.error(f"Error evaluating batch: {result.get('error')}")
            return {"success": False, "error": result.get("error")}

        return {
            "success": True,
            "results": result["results"],
            "summary": result["summary"],
        }
    except Exception as e:
        logger.error(f"Error evaluating batch: {e}")
        return {"success": False, "error": str(e)}
