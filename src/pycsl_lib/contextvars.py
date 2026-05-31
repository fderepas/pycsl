"""PyCSL mock for Python's contextvars module — Context Variables."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/contextvars.html#contextvars.copy_context
#@ requires True
#@ ensures True
def copy_context() -> int:
    """Mock: Returns a copy of the current :class:`~contextvars.Context` object. The following snippet gets a copy of the current con..."""
    return 0
