"""PyCSL mock for Python's keyword module — Test whether a string is a keyword in Python."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/keyword.html#keyword.iskeyword
#@ ensures \result == 0 or \result == 1
def iskeyword(s: int) -> int:
    """Mock: Return ``True`` if *s* is a Python :ref:`keyword <keywords>`."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/keyword.html#keyword.issoftkeyword
#@ ensures \result == 0 or \result == 1
def issoftkeyword(s: int) -> int:
    """Mock: Return ``True`` if *s* is a Python :ref:`soft keyword <soft-keywords>`. .. versionadded:: 3.9"""
    return 0
