"""
Insight generation tools for the Agentic Coupon Abuse Detection System.
"""

from typing import Dict, List, Any, Union
from utils.config import logger, FRAUDULENT_VENDORS
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_explanation(
    fraud_result: Dict[str, Any], transaction: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a human-readable explanation for a fraud detection result.

    Args:
        fraud_result: Fraud detection result dictionary
        transaction: Original transaction data

    Returns:
        Dictionary with explanation
    """
    try:
        # If no rules were triggered, provide a simple explanation
        if not fraud_result["triggered_rules"]:
            explanation = "No fraud patterns were detected in this transaction."
            recommendations = ["No specific recommendations needed."]
            return {
                "success": True,
                "explanation": explanation,
                "recommendations": recommendations,
            }

        # Prepare context for the LLM
        context = {
            "transaction": {
                "id": transaction["transaction_id"],
                "user_name": transaction["user_name"],
                "email": transaction["email"],
                "phone_number": transaction["phone_number"],
                "vendor_name": transaction["vendor_name"],
                "original_amount": transaction["original_amount"],
                "discount_amount": transaction["discount_amount"],
                "final_amount": transaction["final_amount"],
                "coupon_code": transaction["coupon_code"],
            },
            "fraud_result": {
                "fraud_score": fraud_result["fraud_score"],
                "risk_level": fraud_result["risk_level"],
                "triggered_rules": fraud_result["triggered_rules"],
            },
        }

        # Generate explanation using Gemini
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = f"""
        As a fraud detection expert, explain why the following transaction was flagged as potentially fraudulent.
        
        Transaction details:
        - Transaction ID: {context['transaction']['id']}
        - User Name: {context['transaction']['user_name']}
        - Email: {context['transaction']['email']}
        - Phone Number: {context['transaction']['phone_number']}
        - Vendor Name: {context['transaction']['vendor_name']}
        - Original Amount: ${context['transaction']['original_amount']:.2f}
        - Discount Amount: ${context['transaction']['discount_amount']:.2f}
        - Final Amount: ${context['transaction']['final_amount']:.2f}
        - Coupon Code: {context['transaction']['coupon_code']}
        
        Fraud detection results:
        - Fraud Score: {context['fraud_result']['fraud_score']:.2f}
        - Risk Level: {context['fraud_result']['risk_level']}
        - Triggered Rules: {', '.join(context['fraud_result']['triggered_rules'])}
        
        Provide a clear, concise explanation of why this transaction was flagged, focusing on the specific patterns that triggered the rules.
        Then provide 2-3 specific recommendations to prevent this type of fraud in the future.
        
        Format your response as JSON with the following structure:
        {{
            "explanation": "Your explanation here",
            "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
        }}
        """

        response = model.generate_content(prompt)
        response_text = response.text

        # Extract JSON from response (handle potential formatting issues)
        import json
        import re

        # Find JSON content in the response
        json_match = re.search(r"({[\s\S]*})", response_text)
        if json_match:
            json_str = json_match.group(1)
            try:
                result = json.loads(json_str)
                return {
                    "success": True,
                    "explanation": result.get(
                        "explanation", "No explanation provided."
                    ),
                    "recommendations": result.get(
                        "recommendations", ["No recommendations provided."]
                    ),
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                pass

        # Fallback explanation if parsing fails
        explanation = (
            f"This transaction was flagged with a fraud score of {fraud_result['fraud_score']:.2f} "
            f"(risk level: {fraud_result['risk_level']}) due to the following patterns: "
            f"{', '.join(fraud_result['triggered_rules'])}."
        )

        recommendations = [
            "Review vendor validation procedures.",
            "Implement stricter coupon usage policies.",
            "Monitor accounts with duplicate contact information.",
        ]

        return {
            "success": True,
            "explanation": explanation,
            "recommendations": recommendations,
        }
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        return {
            "success": False,
            "error": str(e),
            "explanation": "Unable to generate explanation due to an error.",
            "recommendations": ["Review transaction manually."],
        }


def generate_batch_insights(batch_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate insights for a batch of transactions.

    Args:
        batch_results: Results from batch rule evaluation

    Returns:
        Dictionary with batch insights
    """
    try:
        # Extract summary statistics
        summary = batch_results["summary"]
        results = batch_results["results"]

        # Count rule occurrences
        rule_counts = {}
        for result in results:
            for rule in result["triggered_rules"]:
                if rule in rule_counts:
                    rule_counts[rule] += 1
                else:
                    rule_counts[rule] = 1

        # Sort rules by frequency
        sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)

        # Generate insights using Gemini
        if sorted_rules:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            As a fraud detection expert, provide insights on the following batch analysis results:
            
            Summary:
            - Total Transactions: {summary['total_transactions']}
            - Flagged Transactions: {summary['flagged_transactions']} ({summary['flagged_percentage']}%)
            - High Risk Transactions: {summary['high_risk_transactions']} ({summary['high_risk_percentage']}%)
            
            Most Common Fraud Patterns:
            {'\n'.join([f"- {rule}: {count} occurrences" for rule, count in sorted_rules])}
            
            Provide 3-5 key insights about these results and 2-3 actionable recommendations.
            
            Format your response as JSON with the following structure:
            {{
                "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
                "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
            }}
            """

            response = model.generate_content(prompt)
            response_text = response.text

            # Extract JSON from response
            import json
            import re

            # Find JSON content in the response
            json_match = re.search(r"({[\s\S]*})", response_text)
            if json_match:
                json_str = json_match.group(1)
                try:
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "summary": summary,
                        "rule_frequency": dict(sorted_rules),
                        "key_insights": result.get("key_insights", []),
                        "recommendations": result.get("recommendations", []),
                    }
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    pass

        # Fallback insights if no rules triggered or parsing fails
        key_insights = [
            f"{summary['flagged_percentage']}% of transactions were flagged as potentially fraudulent.",
            f"{summary['high_risk_percentage']}% of transactions were classified as high risk.",
            "Review the most common fraud patterns to improve detection rules.",
        ]

        recommendations = [
            "Implement additional verification for high-risk transactions.",
            "Review coupon usage policies to prevent abuse.",
            "Monitor accounts with duplicate contact information.",
        ]

        return {
            "success": True,
            "summary": summary,
            "rule_frequency": dict(sorted_rules) if sorted_rules else {},
            "key_insights": key_insights,
            "recommendations": recommendations,
        }
    except Exception as e:
        logger.error(f"Error generating batch insights: {e}")
        return {"success": False, "error": str(e)}
