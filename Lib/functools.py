"""PyCSL mock for Python's functools module — Higher-order functions and operations on callable objects."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def cmp_to_key(func: int) -> int:
    """Mock: Transform an old-style comparison function to a :term:`key function`.  Used with tools that accept key functions (such a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def partial(func: int) -> int:
    """Mock: Return a new :ref:`partial object<partial-objects>` which when called will behave like *func* called with the positional..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def reduce(function_: int, iterable: int, initial: int) -> int:
    """Mock: Apply *function* of two arguments cumulatively to the items of *iterable*, from left to right, so as to reduce the itera..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def update_wrapper(wrapper: int, wrapped: int, assigned: int, updated: int) -> int:
    """Mock: Update a *wrapper* function to look like the *wrapped* function. The optional arguments are tuples to specify which attr..."""
    return 0
