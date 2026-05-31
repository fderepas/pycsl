"""PyCSL mock for Python's json module.

Provides trusted stubs for JSON encoding/decoding.
Top-level serialization/deserialization, plus JSONEncoder and
JSONDecoder methods flattened to module-level functions.
Side-effect functions ensure result == 0; data-returning functions
ensure result >= 0.
"""
_ = 0  # anchor

# ── Serialization ────────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.dump
#@ ensures True
#@ assigns \nothing
def dump(obj: int, fp: int, skipkeys: int, ensure_ascii: int, check_circular: int, allow_nan: int, cls: int, indent: int, separators: int, default: int, sort_keys: int) -> int:
    """Mock: serialize obj as JSON to a file-like object."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.dumps
#@ ensures True
#@ assigns \nothing
def dumps(obj: int, skipkeys: int, ensure_ascii: int, check_circular: int, allow_nan: int, cls: int, indent: int, separators: int, default: int, sort_keys: int) -> int:
    """Mock: serialize obj to a JSON-formatted string."""
    return 0

# ── Deserialization ──────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.load
#@ ensures True
#@ assigns \nothing
def load(fp: int, cls: int, object_hook: int, parse_float: int, parse_int: int, parse_constant: int, object_pairs_hook: int, array_hook: int) -> int:
    """Mock: deserialize a file-like object to a Python object."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.loads
#@ ensures True
def loads(s: int, cls: int, object_hook: int, parse_float: int, parse_int: int, parse_constant: int, object_pairs_hook: int, array_hook: int) -> int:
    """Mock: deserialize a JSON string to a Python object."""
    return 0

# ── JSONDecoder methods ──────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.JSONDecoder.decode
#@ requires True
#@ ensures True
def JSONDecoder_decode(s: int) -> int:
    """Mock: return Python representation of a JSON string."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.JSONDecoder.raw_decode
#@ requires True
#@ ensures True
def JSONDecoder_raw_decode(s: int) -> int:
    """Mock: decode JSON and return (object, end-index) tuple."""
    return 0

# ── JSONEncoder methods ──────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.JSONEncoder.default
#@ requires True
#@ ensures True
def JSONEncoder_default(o: int) -> int:
    """Mock: return a serializable object for o."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.JSONEncoder.encode
#@ requires True
#@ ensures True
def JSONEncoder_encode(o: int) -> int:
    """Mock: return a JSON string for a Python data structure."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/json.html#json.JSONEncoder.iterencode
#@ requires True
#@ ensures True
def JSONEncoder_iterencode(o: int) -> int:
    """Mock: encode object and yield string chunks."""
    return 0
