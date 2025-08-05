import json
import re

from loguru import logger


def extract_and_parse_json(text: str) -> dict:
    """
    Finds and parses the first valid JSON object within a string,
    even if it's embedded in markdown code blocks or other text.

    Args:
        text: The string containing the JSON object.

    Returns:
        A dictionary parsed from the JSON object.

    Raises:
        ValueError: If no valid JSON object can be found.
    """
    logger.debug("Attempting to extract JSON from raw LLM output...")

    # Regex to find JSON wrapped in markdown code blocks (```json ... ```)
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)

    if match:
        json_str = match.group(1)
        logger.debug("Found JSON inside markdown block. Extracting content.")
    else:
        # If no markdown block, try to find the first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = text[start : end + 1]
            logger.debug("Found JSON by slicing from first '{' to last '}'.")
        else:
            logger.error("No JSON object found in the provided text.")
            raise ValueError("No valid JSON object found in the LLM output.")

    try:
        # Attempt to parse the extracted string
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Try to fix common JSON issues like trailing commas
        try:
            # Remove trailing commas before closing brackets/braces
            fixed_json = re.sub(r",(\s*[}\]])", r"\1", json_str)
            logger.debug("Attempting to fix trailing commas in JSON")
            return json.loads(fixed_json)
        except json.JSONDecodeError as e2:
            logger.error(f"Failed to parse extracted JSON string. Error: {e}")
            logger.debug(f"Invalid JSON string was: {json_str}")
            raise ValueError(f"Extracted text is not a valid JSON object: {e}")
