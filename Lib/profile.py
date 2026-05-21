"""PyCSL mock for Python's profile module — Pure Python profiler (deprecated)."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def run(command: int, filename: int, sort: int) -> int:
    """Mock: This function takes a single argument that can be passed to the :func:`exec` function, and an optional file name.  In al..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def runctx(command: int, globals: int, locals: int, filename: int, sort: int) -> int:
    """Mock: This function is similar to :func:`run`, with added arguments to supply the globals and locals mappings for the *command..."""
    return 0
