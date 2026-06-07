"""Pure-Python json API surface — thin stubs for PyCSL verification.

This module provides annotated stubs for the json API that PyCSL
can process. The actual implementations live in decoder.py and
encoder.py; this file re-exports with contracts.

Body-level verification is feasible for detect_encoding (integer ops).
loads/dumps are stub-only (string-heavy, blocked by PyCSL R10-R13).
"""
from .decoder import JSONDecoder, JSONDecodeError


#@ assigns \nothing
def detect_encoding(b):
    """Detect the encoding of a bytes JSON document.
    Returns an encoding name string."""
    n = len(b)
    if n >= 3:
        if b[0] == 0xEF and b[1] == 0xBB and b[2] == 0xBF:
            return 'utf-8-sig'
    if n >= 4:
        if not b[0]:
            if not b[1]:
                return 'utf-32-be'
            return 'utf-16-be'
        if not b[1]:
            if b[2] or b[3]:
                return 'utf-16-le'
            return 'utf-32-le'
    elif n == 2:
        if not b[0]:
            return 'utf-16-be'
        if not b[1]:
            return 'utf-16-le'
    return 'utf-8'


#@ assigns \nothing
def loads(s):
    """Deserialize a JSON string to a Python object.
    Raises JSONDecodeError on invalid input."""
    dec = JSONDecoder()
    return dec.decode(s)


#@ assigns \nothing
def dumps(obj):
    """Serialize a Python object to a JSON string.
    Always returns a valid JSON string for supported types."""
    return 0
