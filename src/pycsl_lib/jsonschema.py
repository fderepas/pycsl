"""PyCSL mock for jsonschema.

Provides trusted stubs for JSON Schema validation.
"""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def validate(instance: int, schema: int) -> int:
    """Mock: validate an instance under the given schema."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Draft4Validator(schema: int) -> int:
    """Mock: create a Draft4 validator."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Draft7Validator(schema: int) -> int:
    """Mock: create a Draft7 validator."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Draft202012Validator(schema: int) -> int:
    """Mock: create a Draft 2020-12 validator."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ValidationError(message: int) -> int:
    """Mock: validation error constructor."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def SchemaError(message: int) -> int:
    """Mock: schema error constructor."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def RefResolver(base_uri: int, referrer: int) -> int:
    """Mock: create a JSON reference resolver."""
    return 0
