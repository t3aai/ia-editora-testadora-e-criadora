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
    # Strategy 1: Try markdown code block first (most reliable when present)
    code_block = re.search(r'```(?:json)?\s*\n(.*?)\n\s*```', text, re.DOTALL)
    if code_block:
        raw = code_block.group(1).strip()
        result = _try_parse(raw)
        if result is not None:
            return result

    # Strategy 2: Extract JSON by brace matching and parse
    json_str = _extract_json(text)
    if json_str:
        result = _try_parse(json_str)
        if result is not None:
            return result

    # Strategy 3: Brute force - try rfind approach
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        raw = text[start:end + 1]
        result = _try_parse(raw)
        if result is not None:
            return result

    raise ValueError(f"Failed to parse JSON from LLM response (length={len(text)})")


def _try_parse(json_str: str) -> dict | None:
    """Try to parse JSON string, with repair fallbacks."""
    # Direct parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Repair and retry
    for repair_fn in [_fix_trailing_commas, _fix_newlines_in_strings, _fix_all]:
        try:
            repaired = repair_fn(json_str)
            return json.loads(repaired)
        except (json.JSONDecodeError, Exception):
            pass

    return None


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

    return None


def _fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before } or ]."""
    return re.sub(r',\s*([}\]])', r'\1', text)


def _fix_newlines_in_strings(text: str) -> str:
    """Fix unescaped newlines/tabs inside JSON string values character by character."""
    result = []
    i = 0
    in_string = False
    escape = False

    while i < len(text):
        c = text[i]

        if escape:
            result.append(c)
            escape = False
            i += 1
            continue

        if c == '\\' and in_string:
            result.append(c)
            escape = True
            i += 1
            continue

        if c == '"':
            in_string = not in_string
            result.append(c)
            i += 1
            continue

        if in_string:
            if c == '\n':
                result.append('\\n')
            elif c == '\r':
                result.append('\\r')
            elif c == '\t':
                result.append('\\t')
            elif ord(c) < 0x20:
                pass  # skip control chars
            else:
                result.append(c)
        else:
            result.append(c)

        i += 1

    return ''.join(result)


def _fix_all(text: str) -> str:
    """Apply all fixes."""
    s = _fix_newlines_in_strings(text)
    s = _fix_trailing_commas(s)
    # Remove control characters outside strings
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
    return s
