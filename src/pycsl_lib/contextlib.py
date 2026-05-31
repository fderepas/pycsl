"""PyCSL mock for Python's contextlib module — Utilities for with-statement contexts."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def closing(thing: int) -> int:
    """Mock: Return a context manager that closes *thing* upon completion of the block.  This is basically equivalent to:: from conte..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def aclosing(thing: int) -> int:
    """Mock: Return an async context manager that calls the ``aclose()`` method of *thing* upon completion of the block.  This is bas..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nullcontext(enter_result: int) -> int:
    """Mock: Return a context manager that returns *enter_result* from :meth:`~object.__enter__`, but otherwise does nothing. It is i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def suppress() -> int:
    """Mock: Return a context manager that suppresses any of the specified exceptions if they occur in the body of a :keyword:`!with`..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def redirect_stdout(new_target: int) -> int:
    """Mock: Context manager for temporarily redirecting :data:`sys.stdout` to another :term:`file object`. This tool adds flexibilit..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def redirect_stderr(new_target: int) -> int:
    """Mock: Similar to :func:`~contextlib.redirect_stdout` but redirecting the global :data:`sys.stderr` to another :term:`file obje..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def chdir(path: int) -> int:
    """Mock: Non parallel-safe context manager to change the current working directory. As this changes a global state, the working d..."""
    return 0
