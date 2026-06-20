"""PyCSL mock for Python's abc module — Abstract base classes according to :pep:`3119`."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/abc.html#abc.get_cache_token
#@ ensures True
def get_cache_token() -> int:
    """Mock: Returns the current abstract base class cache token. The token is an opaque object (that supports equality testing) iden..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/abc.html#abc.update_abstractmethods
#@ ensures \result == cls
def update_abstractmethods(cls: int) -> int:
    """Mock: A function to recalculate an abstract class's abstraction status. This function should be called if a class's abstract m..."""
    return 0
