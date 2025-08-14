"""
# app/agent.py
# This module contains functions to interact with OpenAI's API for compliance checking and document modification.
# It includes functions to check the compliance of a text and modify it based on the compliance report.
# Created by Ratnesh Kumar on 2024-01-01.
"""
from app.utils import setup_logger
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL

ai_agent_logger = setup_logger()

client = OpenAI(api_key=OPENAI_API_KEY)


def check_compliance(text: str):
    """Check the compliance of the given text using OpenAI.

    Args:
        text (str): The text to check.

    Returns:
        list: A list of compliance issues.
    """
    ai_agent_logger.info("Checking compliance of the text.")
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"""Please check the following text for compliance with English guidelines.
Provide a detailed report specifying any violations of grammar, sentence structure, clarity, and writing rules.
ONLY return the JSON array. Do NOT include any other text, explanations, formatting, or code fences before or after the JSON.
The report should be in JSON format, as an array of objects. Each object should have the following keys:
- "type": (string) e.g., "grammar", "sentence_structure", "clarity", "writing_rule"
- "description": (string) A brief description of the violation.
- "original_text": (string) The exact text snippet that contains the violation.
- "suggestion": (string) A suggestion for correction.

Example JSON output:
[
    {{
        "type": "grammar",
        "description": "Subject-verb agreement error.",
        "original_text": "The dogs runs.",
        "suggestion": "The dogs run."
    }},
    {{
        "type": "clarity",
        "description": "Ambiguous pronoun reference.",
        "original_text": "John told Mike that he was wrong.",
        "suggestion": "John told Mike that Mike was wrong."
    }}
]

Text to check:
{text}"""}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        ai_agent_logger.error(f"Error checking compliance: {e}")
        return "[]"

def modify_document(text: str, compliance_report: list):
    """Modify the document to be compliant with English guidelines based on the compliance report.

    Args:
        text (str): The original text of the document.
        compliance_report (list): A list of compliance issues with suggestions.

    Returns:
        str: The modified text.
    """
    ai_agent_logger.info("Modifying the document to be compliant based on the report.")
    modified_text = text
    for item in compliance_report:
        original = item.get("original_text")
        suggestion = item.get("suggestion")
        if original and suggestion and original in modified_text:
            modified_text = modified_text.replace(original, suggestion, 1) # Replace only the first occurrence
    return modified_text