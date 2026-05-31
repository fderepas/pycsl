"""PyCSL mock for Python's dataclasses module.

Provides trusted stubs for data class utilities.
"""
_ = 0  # anchor

# ── Sentinel values ──

MISSING = 0
KW_ONLY = 0

# ── Decorator ──

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass
#@ ensures \result == cls
def dataclass(cls: int) -> int:
    """Mock: dataclass decorator — passthrough."""
    return cls

# ── Field creation ──

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dataclasses.html#dataclasses.field
#@ ensures True
def field(default: int, default_factory: int, init: int, repr: int, hash: int, compare: int, metadata: int, kw_only: int, doc: int) -> int:
    """Mock: field — returns an opaque Field descriptor."""
    return 0

# ── Introspection ──

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dataclasses.html#dataclasses.fields
#@ ensures \result >= 0
def fields(class_or_instance: int) -> int:
    """Mock: fields — returns tuple of Field objects for a dataclass."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dataclasses.html#dataclasses.is_dataclass
#@ ensures \result == 0 or \result == 1
def is_dataclass(obj: int) -> int:
    """Mock: is_dataclass — returns whether obj is a dataclass."""
    return 0

# ── Conversion ──

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict
# cite:_note: return type is dict (field_name → field_value); stub uses int mock — dict mapping semantics exceed expressible contract surface
#@ ensures True
def asdict(obj: int, dict_factory: int) -> int:
    """Mock: asdict — converts a dataclass instance to a dict."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dataclasses.html#dataclasses.astuple
#@ ensures True
#@ assigns \nothing
def astuple(obj: int, tuple_factory: int) -> int:
    """Mock: astuple — converts a dataclass instance to a tuple."""
    return 0

# ── Construction ──

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dataclasses.html#dataclasses.make_dataclass
# cite:_note: Returns a newly created class object; structural contracts on the
# cite:_note: returned type are inexpressible in the current Hoare model.
# cite:_note: L3 ceiling for this function.
#@ ensures True
def make_dataclass(cls_name: int, fields: int, bases: int, namespace: int, init: int, repr: int, eq: int, order: int, unsafe_hash: int, frozen: int, match_args: int, kw_only: int, slots: int, weakref_slot: int, dc_module: int, decorator: int) -> int:
    """Mock: make_dataclass — dynamically creates a new dataclass."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dataclasses.html#dataclasses.replace
#@ ensures True
# cite:_note: full semantics (field-wise copy of a dataclass instance with named fields replaced) exceed the expressible contract surface under the simplified int-typed mock; `ensures True` captures the success-path return
def replace(obj: int, changes: int) -> int:
    """Mock: replace — creates a copy of obj with fields replaced."""
    return 0

# ── Post-init ──

#@ \trusted
#@ ensures \result >= 0
def __post_init__() -> int:
    """Mock: __post_init__ — called by generated __init__ after init."""
    return 0
