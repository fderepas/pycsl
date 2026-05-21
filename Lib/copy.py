"""PyCSL mock for Python's copy module — Shallow and deep copy operations."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def copy(obj: int) -> int:
    """Mock: Return a shallow copy of *obj*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def deepcopy(obj: int, memo: int) -> int:
    """Mock: Return a deep copy of *obj*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def replace(obj: int) -> int:
    """Mock: Creates a new object of the same type as *obj*, replacing fields with values from *changes*. .. versionadded:: 3.13"""
    return 0
