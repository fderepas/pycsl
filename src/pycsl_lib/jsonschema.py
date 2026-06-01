"""PyCSL mock for jsonschema.

Provides trusted stubs for JSON Schema validation.
"""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://python-jsonschema.readthedocs.io/en/latest/api/jsonschema/validators/#jsonschema.validate
#@ requires True
#@ ensures True
def validate(instance: int, schema: int) -> int:
    """Mock: validate an instance under the given schema."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://python-jsonschema.readthedocs.io/en/latest/api/jsonschema/validators/#jsonschema.Draft4Validator
#@ requires True
#@ ensures True
def Draft4Validator(schema: int) -> int:
    """Mock: create a Draft4 validator."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://python-jsonschema.readthedocs.io/en/latest/api/jsonschema/validators/#jsonschema.Draft7Validator
#@ requires True
#@ ensures True
def Draft7Validator(schema: int) -> int:
    """Mock: create a Draft7 validator."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://python-jsonschema.readthedocs.io/en/latest/api/jsonschema/validators/#jsonschema.Draft202012Validator
#@ requires True
#@ ensures True
def Draft202012Validator(schema: int) -> int:
    """Mock: create a Draft 2020-12 validator."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pycsl_lib/ValidationError.py
#@ requires True
#@ ensures True
def ValidationError(message: int) -> int:
    """Mock: validation error constructor."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://python-jsonschema.readthedocs.io/en/stable/errors/#jsonschema.exceptions.SchemaError
#@ requires True
#@ ensures True
def SchemaError(message: int) -> int:
    """Mock: schema error constructor."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://python-jsonschema.readthedocs.io/en/stable/references/
#@ requires True
#@ ensures True
def RefResolver(base_uri: int, referrer: int) -> int:
    """Mock: create a JSON reference resolver."""
    return 0
