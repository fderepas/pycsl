"""PyCSL mock for Python's contextvars module — Context Variables."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def copy_context() -> int:
    """Mock: Returns a copy of the current :class:`~contextvars.Context` object. The following snippet gets a copy of the current con..."""
    return 0
