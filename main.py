"""
Main entry point for the Agentic Coupon Abuse Detection System.
"""

import asyncio
import os
from google.adk import Runner
from google.adk.runners import RunConfig
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai.types import Content, Part
from agents.data_ingest_agent import data_ingest_agent
from agents.rule_engine_agent import rule_engine_agent
from agents.insight_agent import insight_agent
from agents.metrics_agent import metrics_agent
from agents.feedback_agent import feedback_agent
from utils.config import logger
from utils.helpers import load_data


async def process_test_dataset():
    """
    Process the test dataset and evaluate performance.
    """
    try:
        logger.info("Processing test dataset...")

        # Step 1: Load the test data
        test_file = "data/test_coupon_abuse_with_users.csv"
        test_data = load_data(test_file)
        test_transactions = test_data.to_dict(orient="records")

        # Step 2: Create runners for each agent
        session_service = InMemorySessionService()
        memory_service = InMemoryMemoryService()

        data_runner = Runner(
            app_name="data_ingest",
            agent=data_ingest_agent,
            session_service=session_service,
            memory_service=memory_service,
        )

        rule_runner = Runner(
            app_name="rule_engine",
            agent=rule_engine_agent,
            session_service=session_service,
            memory_service=memory_service,
        )

        insight_runner = Runner(
            app_name="insight",
            agent=insight_agent,
            session_service=session_service,
            memory_service=memory_service,
        )

        metrics_runner = Runner(
            app_name="metrics",
            agent=metrics_agent,
            session_service=session_service,
            memory_service=memory_service,
        )

        feedback_runner = Runner(
            app_name="feedback",
            agent=feedback_agent,
            session_service=session_service,
            memory_service=memory_service,
        )

        # Step 3: Process the test data
        user_id = "test_user"
        session_id = "test_session"

        # Data ingest
        data_message = Content(
            parts=[Part.from_text(f"Process this test data: {test_file}")]
        )

        async for event in data_runner.run_async(
            user_id=user_id, session_id=session_id, new_message=data_message
        ):
            if event.text:
                logger.info(f"Data Ingest: {event.text}")

        # Rule engine
        rule_message = Content(
            parts=[
                Part.from_text(
                    f"Evaluate these transactions for potential fraud: {len(test_transactions)} transactions"
                )
            ]
        )

        async for event in rule_runner.run_async(
            user_id=user_id, session_id=session_id, new_message=rule_message
        ):
            if event.text:
                logger.info(f"Rule Engine: {event.text}")

        # Insight generation
        insight_message = Content(
            parts=[Part.from_text("Generate insights for the fraud detection results")]
        )

        async for event in insight_runner.run_async(
            user_id=user_id, session_id=session_id, new_message=insight_message
        ):
            if event.text:
                logger.info(f"Insight: {event.text}")

        # Metrics calculation
        metrics_message = Content(
            parts=[
                Part.from_text(
                    "Calculate performance metrics for the fraud detection system"
                )
            ]
        )

        async for event in metrics_runner.run_async(
            user_id=user_id, session_id=session_id, new_message=metrics_message
        ):
            if event.text:
                logger.info(f"Metrics: {event.text}")

        # Feedback processing
        feedback_message = Content(
            parts=[
                Part.from_text("Process feedback and update rules based on performance")
            ]
        )

        async for event in feedback_runner.run_async(
            user_id=user_id, session_id=session_id, new_message=feedback_message
        ):
            if event.text:
                logger.info(f"Feedback: {event.text}")

        logger.info("Test dataset processed successfully!")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error processing test dataset: {e}")
        return {"success": False, "error": str(e)}


def main():
    """
    Main entry point.
    """
    logger.info("Starting Agentic Coupon Abuse Detection System...")

    # Run the async function
    result = asyncio.run(process_test_dataset())

    if result and result.get("success"):
        logger.info("Test dataset processed successfully!")
    else:
        logger.error("Failed to process test dataset.")

    logger.info("Done!")


if __name__ == "__main__":
    main()
