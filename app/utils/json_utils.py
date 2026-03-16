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
    errors = []

    # Strategy 1: Direct parse (maybe the LLM returned clean JSON)
    stripped = text.strip()
    if stripped.startswith('{'):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError as e:
            errors.append(f"direct: {e}")

    # Strategy 2: Extract from markdown code block
    code_block = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if code_block:
        raw = code_block.group(1).strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"codeblock: {e}")
            # Try repair on code block content
            result = _try_repair_and_parse(raw)
            if result is not None:
                return result

    # Strategy 3: Find first { and last } (simple extraction)
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        raw = text[start:end + 1]
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"braces: {e}")
            result = _try_repair_and_parse(raw)
            if result is not None:
                return result

    # Strategy 4: Line-by-line JSON reconstruction
    result = _reconstruct_json(text)
    if result is not None:
        return result

    logger.error(f"All JSON parse strategies failed: {errors}")
    raise ValueError(f"Failed to parse JSON from LLM response (length={len(text)})")


def _try_repair_and_parse(json_str: str) -> dict | None:
    """Try multiple repair strategies."""
    for repair_fn in [_fix_trailing_commas, _fix_newlines_in_strings, _fix_all]:
        try:
            repaired = repair_fn(json_str)
            return json.loads(repaired)
        except (json.JSONDecodeError, Exception):
            pass
    return None


def _reconstruct_json(text: str) -> dict | None:
    """
    Last resort: rebuild JSON by finding the structure line by line.
    Works by collecting all lines between first { and last },
    escaping problematic content, then parsing.
    """
    lines = text.split('\n')
    json_lines = []
    capturing = False

    for line in lines:
        stripped = line.strip()
        if not capturing:
            idx = stripped.find('{')
            if idx >= 0:
                capturing = True
                json_lines.append(stripped[idx:])
        else:
            json_lines.append(line)

    if not json_lines:
        return None

    # Join and find last }
    joined = '\n'.join(json_lines)
    last_brace = joined.rfind('}')
    if last_brace < 0:
        return None

    joined = joined[:last_brace + 1]

    # Try parsing as-is first
    try:
        return json.loads(joined)
    except json.JSONDecodeError:
        pass

    # Apply all fixes
    result = _try_repair_and_parse(joined)
    if result is not None:
        return result

    # Nuclear option: escape ALL newlines between quotes using regex substitution
    try:
        fixed = _nuclear_fix(joined)
        return json.loads(fixed)
    except (json.JSONDecodeError, Exception):
        pass

    return None


def _nuclear_fix(text: str) -> str:
    """
    Nuclear option: process the text ensuring all string values are properly escaped.
    Uses a state machine that's resilient to messy LLM output.
    """
    # First, normalize: replace literal \n sequences that are already escaped
    # Then escape actual newlines in strings
    result = []
    i = 0
    in_string = False

    while i < len(text):
        c = text[i]

        # Handle escape sequences
        if in_string and c == '\\' and i + 1 < len(text):
            next_c = text[i + 1]
            # Already escaped sequences - keep them
            if next_c in ('"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u'):
                result.append(c)
                result.append(next_c)
                i += 2
                continue
            # Backslash followed by something else - escape the backslash
            result.append('\\\\')
            i += 1
            continue

        if c == '"' and (i == 0 or text[i-1] != '\\'):
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
                pass  # skip control characters
            else:
                result.append(c)
        else:
            result.append(c)

        i += 1

    s = ''.join(result)
    # Also fix trailing commas
    s = re.sub(r',\s*([}\]])', r'\1', s)
    return s


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
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
    return s
