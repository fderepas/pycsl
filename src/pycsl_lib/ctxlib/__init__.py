# pycsl_lib/ctxlib — pure-Python contextlib module model
# Named 'ctxlib' to avoid stdlib name clash.
#
# Contracts derived from library_reference/contextlib.rst.
# RST: "Utilities for with-statement contexts."
# RST: "contextmanager, closing, suppress, redirect_stdout, ExitStack"
#
# Model: context managers as enter/exit state tracking.


#@ requires func >= 0
#@ ensures \result == func
#@ assigns \nothing
def contextmanager(func: int) -> int:
    """RST: 'This function is a decorator that can be used to define a
    factory function for with statement context managers.' Returns func."""
    return func


#@ requires obj >= 0
#@ ensures \result == obj
#@ assigns \nothing
def closing(obj: int) -> int:
    """RST: 'Return a context manager that closes thing upon completion.'
    Returns the object (close called on exit)."""
    return obj


#@ requires val >= 0
#@ ensures \result == val
#@ assigns \nothing
def nullcontext(val: int) -> int:
    """RST: 'Return a context manager that returns enter_result from
    __enter__ but otherwise does nothing.' Identity."""
    return val


""  # pycsl
#@ class invariant self._depth >= 0
class ExitStack:
    """RST: 'A context manager that is designed to make it easy to
    programmatically combine other context managers and cleanup functions.'"""

    def __init__(self):
        self._depth = 0

    #@ ensures self._depth == \old(self._depth) + 1
    #@ assigns self._depth
    def enter_context(self, cm: int) -> None:
        """RST: 'Enters a new context manager and adds its __exit__ method.'"""
        self._depth = self._depth + 1

    #@ ensures self._depth == \old(self._depth) + 1
    #@ assigns self._depth
    def push(self, exit_func: int) -> None:
        """RST: 'Accepts an arbitrary callback function and arguments.'"""
        self._depth = self._depth + 1

    #@ ensures self._depth == 0
    #@ assigns self._depth
    def close(self) -> None:
        """RST: 'Immediately unwinds the callback stack.'"""
        self._depth = 0

    #@ ensures \result == self._depth
    #@ assigns \nothing
    def depth(self) -> int:
        """Number of registered exit callbacks."""
        return self._depth
