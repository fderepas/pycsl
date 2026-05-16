"""
Schema validator for inter-agent JSON contracts.

Validates Python dicts against JSON Schema files in config/schemas/.
Falls back to manual required-key checks if jsonschema is not installed.
"""

import json
import sys
from pathlib import Path
from typing import Optional

_SCHEMA_DIR: Optional[Path] = None

def _find_schema_dir() -> Path:
    """Locate config/schemas/ relative to the repository root."""
    global _SCHEMA_DIR
    if _SCHEMA_DIR is not None:
        return _SCHEMA_DIR
    # Walk up from this file to find the repo root (contains config/)
    here = Path(__file__).resolve().parent
    for ancestor in [here] + list(here.parents):
        candidate = ancestor / "config" / "schemas"
        if candidate.is_dir():
            _SCHEMA_DIR = candidate
            return _SCHEMA_DIR
    raise FileNotFoundError("Could not locate config/schemas/ directory")


def _load_schema(schema_name: str) -> dict:
    """Load a JSON Schema by name (without .schema.json suffix)."""
    schema_dir = _find_schema_dir()
    schema_path = schema_dir / f"{schema_name}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate(data: object, schema_name: str) -> list[str]:
    """Validate data against a named schema.

    Args:
        data: The Python object (dict or list) to validate.
        schema_name: Schema name, e.g. 'reconcile', 'monitor'.

    Returns:
        List of error messages. Empty list means valid.
    """
    schema = _load_schema(schema_name)

    # Try jsonschema library first
    try:
        import jsonschema
        validator = jsonschema.Draft7Validator(schema)
        return [e.message for e in validator.iter_errors(data)]
    except ImportError:
        pass

    # Fallback: manual required-key check
    return _manual_validate(data, schema)


def _manual_validate(data: object, schema: dict) -> list[str]:
    """Basic validation without jsonschema: check type and required keys."""
    errors: list[str] = []
    expected_type = schema.get("type")

    if expected_type == "object":
        if not isinstance(data, dict):
            return [f"Expected object, got {type(data).__name__}"]
        for key in schema.get("required", []):
            if key not in data:
                errors.append(f"Missing required key: '{key}'")
    elif expected_type == "array":
        if not isinstance(data, list):
            return [f"Expected array, got {type(data).__name__}"]
        item_schema = schema.get("items", {})
        for i, item in enumerate(data):
            for key in item_schema.get("required", []):
                if isinstance(item, dict) and key not in item:
                    errors.append(f"Item {i}: missing required key: '{key}'")

    return errors


def validate_or_warn(data: object, schema_name: str, logger=None) -> bool:
    """Validate and log warnings on failure. Returns True if valid.

    Args:
        data: The data to validate.
        schema_name: Schema name.
        logger: Optional callable(msg: str) for warnings. Defaults to stderr.

    Returns:
        True if validation passes, False otherwise.
    """
    try:
        errors = validate(data, schema_name)
    except FileNotFoundError as e:
        msg = f"[schema_validator] {e}"
        if logger:
            logger(msg)
        else:
            print(msg, file=sys.stderr)
        return True  # schema not found — don't block

    if errors:
        msg = f"[schema_validator] {schema_name}: {'; '.join(errors)}"
        if logger:
            logger(msg)
        else:
            print(msg, file=sys.stderr)
        return False
    return True
