"""PyCSL mock for Python's copy module — Shallow and deep copy operations."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/copy.html#copy.copy
#@ ensures \result == obj
def copy(obj: int) -> int:
    """Mock: Return a shallow copy of *obj*."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/copy.html#copy.deepcopy
#@ ensures \result == obj
def deepcopy(obj: int, memo: int) -> int:
    """Mock: Return a deep copy of *obj*."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/copy.html#copy.replace
#@ ensures True
# cite:_note: full semantics (field-wise copy of obj with named fields replaced) exceed the expressible contract surface under the simplified int-typed mock; `ensures True` captures the success-path return
def replace(obj: int) -> int:
    """Mock: Creates a new object of the same type as *obj*, replacing fields with values from *changes*. .. versionadded:: 3.13"""
    return 0
