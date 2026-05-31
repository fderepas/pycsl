"""PyCSL mock for Python's bdb module — Debugger framework."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/bdb.html#bdb.checkfuncname
#@ ensures \result == 0 or \result == 1
def checkfuncname(b: int, frame: int) -> int:
    """Mock: Return ``True`` if we should break here, depending on the way the :class:`Breakpoint` *b* was set. If it was set via lin..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/bdb.html
#@ requires line >= 1
#@ ensures True
def effective(file: int, line: int, frame: int) -> int:
    """Mock: Return ``(active breakpoint, delete temporary flag)`` or ``(None, None)`` as the breakpoint to act upon. The *active bre..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/bdb.html#bdb.Bdb.set_trace
#@ ensures True
def set_trace() -> int:
    """Mock: Start debugging with a :class:`Bdb` instance from caller's frame."""
    return 0
