"""Utilities for parsing JSON."""

import json


def extract_json_from_text(text: str):
    """Extracts and parses the first valid JSON object found in the input text.

    Args:
        text (str): The input text to search for JSON.

    Returns:
        dict: The parsed JSON object or None if not found.
    """
    start = text.find("{")
    if start == -1:
        return None
    count = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            count += 1
        elif text[i] == "}":
            count -= 1
            if count == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None
