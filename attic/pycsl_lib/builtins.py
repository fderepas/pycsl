"""PyCSL mock for Python's builtins module — The module that provides the built-in namespace."""
_ = 0  # anchor

# ── isinstance ───────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def isinstance(obj: int, classinfo: int) -> int:
    """Mock: returns nonzero if obj is an instance of classinfo."""
    return 0

# ── open ─────────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def open(file: int, mode: int) -> int:
    """Mock: open file and return file object handle."""
    return 0

# ── Set operations ───────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def set_union(a: int, b: int) -> int:
    """Mock: set union (|), returns opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_intersection(a: int, b: int) -> int:
    """Mock: set intersection (&), returns opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_difference(a: int, b: int) -> int:
    """Mock: set difference (-), returns opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_symmetric_difference(a: int, b: int) -> int:
    """Mock: set symmetric difference (^), returns opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_contains(s: int, elem: int) -> int:
    """Mock: returns nonzero if elem is in set s (in operator)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_issubset(a: int, b: int) -> int:
    """Mock: returns nonzero if a is a subset of b."""
    return 0

# ── Dict membership ──────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def dict_contains(d: int, key: int) -> int:
    """Mock: returns nonzero if key is in dict d (in operator)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dict_get(d: int, key: int, default: int) -> int:
    """Mock: returns value for key in d, or default if absent."""
    return 0
