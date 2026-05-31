"""PyCSL mock for Python's atexit module — Register and execute cleanup functions."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def register(func: int) -> int:
    """Mock: Register *func* as a function to be executed at termination.  Any optional arguments that are to be passed to *func* mus..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unregister(func: int) -> int:
    """Mock: Remove *func* from the list of functions to be run at interpreter shutdown. :func:`unregister` silently does nothing if ..."""
    return 0
