"""
Robust JSON parsing for LLM responses.
Handles common issues like trailing commas, unescaped newlines, markdown wrappers, etc.
"""

import json
import re
import logging

logger = logging.getLogger(__name__)


def parse_llm_json(text: str) -> dict:
    """
    Parse JSON from an LLM response with multiple fallback strategies.
    Raises ValueError if all strategies fail.
    """
    # Strategy 1: Extract JSON block and parse directly
    json_str = _extract_json(text)
    if json_str:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Repair common issues and retry
        repaired = _repair_json(json_str)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

    # Strategy 3: Try extracting from markdown code block
    code_block = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1).strip())
        except json.JSONDecodeError:
            repaired = _repair_json(code_block.group(1).strip())
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass

    raise ValueError(f"Failed to parse JSON from LLM response (length={len(text)})")


def _extract_json(text: str) -> str | None:
    """Extract the outermost JSON object from text by matching braces."""
    start = text.find('{')
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        c = text[i]

        if escape:
            escape = False
            continue

        if c == '\\' and in_string:
            escape = True
            continue

        if c == '"' and not escape:
            in_string = not in_string
            continue

        if in_string:
            continue

        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]

    # Fallback: use rfind approach
    end = text.rfind('}')
    if end > start:
        return text[start:end + 1]

    return None


def _repair_json(text: str) -> str:
    """Attempt to fix common JSON issues from LLM responses."""
    s = text

    # Remove trailing commas before } or ]
    s = re.sub(r',\s*([}\]])', r'\1', s)

    # Fix unescaped newlines inside string values
    # This is tricky - we process line by line within strings
    s = re.sub(r'(?<=": ")(.*?)(?="[,\s}])', _escape_newlines_in_value, s, flags=re.DOTALL)

    # Remove control characters (except \n, \r, \t which are valid in JSON strings when escaped)
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)

    # Fix single quotes used as JSON delimiters (only if no double quotes present)
    if "'" in s and '"' not in s:
        s = s.replace("'", '"')

    return s


def _escape_newlines_in_value(match):
    """Escape literal newlines inside a JSON string value."""
    return match.group(0).replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
