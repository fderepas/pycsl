"""PyCSL mock for Python's token module — Constants representing terminal nodes of the parse tree."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/token.html#token.ISTERMINAL
#@ requires True
#@ ensures \result == 0 or \result == 1
def ISTERMINAL(x: int) -> int:
    """Mock: Return ``True`` for terminal token values."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/token.py
#@ requires True
#@ ensures \result == 0 or \result == 1
def ISNONTERMINAL(x: int) -> int:
    """Mock: Return ``True`` for non-terminal token values."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/token.html#token.ISEOF
#@ requires True
#@ ensures True
def ISEOF(x: int) -> int:
    """Mock: Return ``True`` if *x* is the marker indicating the end of input."""
    return 0
