"""PyCSL mock for Python's resource module — An interface to provide resource usage information on the current process."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def getrlimit(resource: int) -> int:
    """Mock: Returns a tuple ``(soft, hard)`` with the current soft and hard limits of *resource*. Raises :exc:`ValueError` if an inv..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setrlimit(resource: int, limits: int) -> int:
    """Mock: Sets new limits of consumption of *resource*. The *limits* argument must be a tuple ``(soft, hard)`` of two integers des..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prlimit(pid: int, resource: int, limits: int) -> int:
    """Mock: Combines :func:`setrlimit` and :func:`getrlimit` in one function and supports to get and set the resources limits of an ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getrusage(who: int) -> int:
    """Mock: This function returns an object that describes the resources consumed by either the current process or its children, as ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpagesize() -> int:
    """Mock: Returns the number of bytes in a system page. (This need not be the same as the hardware page size.)"""
    return 0
