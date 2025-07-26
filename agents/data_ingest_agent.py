"""
Data Ingest Agent for the Agentic Coupon Abuse Detection System.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from tools.data_tools import file_reader, data_validator, data_preprocessor
from utils.config import logger, GEMINI_FLASH_MODEL

# Define tools for the agent
file_reader_tool = FunctionTool(file_reader)
data_validator_tool = FunctionTool(data_validator)
data_preprocessor_tool = FunctionTool(data_preprocessor)

# Create the Data Ingest Agent
data_ingest_agent = Agent(
    name="data_ingest_agent",
    model=GEMINI_FLASH_MODEL,
    instruction="""
    You are a Data Ingest Agent for a fraud detection system. Your job is to:
    1. Read data from files
    2. Validate that the data has the correct schema
    3. Preprocess the data for analysis
    
    The data should contain transaction information with the following fields:
    - transaction_id
    - user_id
    - user_name
    - email
    - phone_number
    - transaction_date
    - merchant
    - vendor_name
    - channel
    - items_count
    - original_amount
    - discount_amount
    - final_amount
    - coupon_code
    - abuse (optional)
    
    You should reject any data that doesn't match this schema.
    """,
    description="Agent for ingesting and preprocessing transaction data",
    tools=[file_reader_tool, data_validator_tool, data_preprocessor_tool],
)


async def process_data_file(file_path: str):
    """
    Process a data file using the Data Ingest Agent.

    Args:
        file_path: Path to the data file

    Returns:
        Processed data
    """
    try:
        # Read the file
        read_result = await data_ingest_agent.run(
            "Read the data file and return the contents.",
            tools={"file_reader": {"file_path": file_path}},
        )

        if not read_result.get("success", False):
            logger.error(f"Error reading file: {read_result.get('error')}")
            return {"success": False, "error": read_result.get("error")}

        # Validate the data
        transactions = read_result["data"]
        validate_result = await data_ingest_agent.run(
            "Validate the transactions to ensure they have the correct schema.",
            tools={"data_validator": {"transactions": transactions}},
        )

        if not validate_result.get("success", False):
            logger.error(f"Error validating data: {validate_result.get('error')}")
            return {"success": False, "error": validate_result.get("error")}

        # Preprocess the data
        valid_transactions = validate_result["valid_transactions"]
        preprocess_result = await data_ingest_agent.run(
            "Preprocess the transactions for analysis.",
            tools={"data_preprocessor": {"transactions": valid_transactions}},
        )

        if not preprocess_result.get("success", False):
            logger.error(f"Error preprocessing data: {preprocess_result.get('error')}")
            return {"success": False, "error": preprocess_result.get("error")}

        return {
            "success": True,
            "processed_data": preprocess_result["processed_transactions"],
            "metadata": {
                "original_count": len(transactions),
                "valid_count": len(valid_transactions),
                "invalid_count": validate_result["invalid_count"],
                "file_path": file_path,
            },
        }
    except Exception as e:
        logger.error(f"Error processing data file: {e}")
        return {"success": False, "error": str(e)}
