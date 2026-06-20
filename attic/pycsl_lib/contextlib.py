"""PyCSL mock for Python's contextlib module — Utilities for with-statement contexts."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/contextlib.html#contextlib.closing
#@ ensures True
def closing(thing: int) -> int:
    """Mock: Return a context manager that closes *thing* upon completion of the block.  This is basically equivalent to:: from conte..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/contextlib.html#contextlib.aclosing
#@ ensures True
def aclosing(thing: int) -> int:
    """Mock: Return an async context manager that calls the ``aclose()`` method of *thing* upon completion of the block.  This is bas..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/contextlib.html#contextlib.nullcontext
#@ ensures \result == enter_result
def nullcontext(enter_result: int) -> int:
    """Mock: Return a context manager that returns *enter_result* from :meth:`~object.__enter__`, but otherwise does nothing. It is i..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/contextlib.html#contextlib.suppress
#@ ensures True
def suppress() -> int:
    """Mock: Return a context manager that suppresses any of the specified exceptions if they occur in the body of a :keyword:`!with`..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stdout
#@ ensures True
#@ assigns \nothing
def redirect_stdout(new_target: int) -> int:
    """Mock: Context manager for temporarily redirecting :data:`sys.stdout` to another :term:`file object`. This tool adds flexibilit..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stderr
#@ ensures True
#@ assigns \nothing
def redirect_stderr(new_target: int) -> int:
    """Mock: Similar to :func:`~contextlib.redirect_stdout` but redirecting the global :data:`sys.stderr` to another :term:`file obje..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/contextlib.html#contextlib.chdir
#@ ensures True
#@ assigns \nothing
def chdir(path: int) -> int:
    """Mock: Non parallel-safe context manager to change the current working directory. As this changes a global state, the working d..."""
    return 0
