"""PyCSL mock for Python's concurrent.interpreters module — Multiple interpreters in the same process."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def list_all() -> int:
    """Mock: Return a :class:`list` of :class:`Interpreter` objects, one for each existing interpreter."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_current() -> int:
    """Mock: Return an :class:`Interpreter` object for the currently running interpreter."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_main() -> int:
    """Mock: Return an :class:`Interpreter` object for the main interpreter. This is the interpreter the runtime created to run the :..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def create() -> int:
    """Mock: Initialize a new (idle) Python interpreter and return a :class:`Interpreter` object for it."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def create_queue() -> int:
    """Mock: Initialize a new cross-interpreter queue and return a :class:`Queue` object for it."""
    return 0
