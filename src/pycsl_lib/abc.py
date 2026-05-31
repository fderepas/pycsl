"""PyCSL mock for Python's abc module — Abstract base classes according to :pep:`3119`."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def get_cache_token() -> int:
    """Mock: Returns the current abstract base class cache token. The token is an opaque object (that supports equality testing) iden..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def update_abstractmethods(cls: int) -> int:
    """Mock: A function to recalculate an abstract class's abstraction status. This function should be called if a class's abstract m..."""
    return 0
