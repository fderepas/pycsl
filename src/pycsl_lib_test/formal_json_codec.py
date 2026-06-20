"""Formal test: pycsl_lib/json — detect_encoding, loads, dumps stubs.

Verifies structural properties of the json API through stubs.
detect_encoding is tested for all byte sequences, loads/dumps for
all symbolic inputs.
"""
from pycsl_lib.json._api import detect_encoding, loads, dumps


#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_detect_encoding(b) -> int:
    """detect_encoding never crashes for any byte input."""
    enc = detect_encoding(b)
    if enc < 0:
        return 1
    return 0


#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_loads(s) -> int:
    """loads returns a value or raises JSONDecodeError."""
    obj = loads(s)
    return 0


#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_dumps(obj) -> int:
    """dumps returns a value for any object."""
    result = dumps(obj)
    return 0
