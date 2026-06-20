"""PyCSL mock for Python's faulthandler module — Dump the Python traceback."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.dump_traceback
#@ ensures True
def dump_traceback(file: int, all_threads: int, max_threads: int) -> int:
    """Mock: Dump the tracebacks of all threads into *file*. If *all_threads* is ``False``, dump only the current thread. *max_thread..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.dump_traceback
#@ ensures True
#@ assigns \nothing
def dump_c_stack(file: int) -> int:
    """Mock: Dump the C stack trace of the current thread into *file*. If the Python build does not support it or the operating syste..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.enable
#@ ensures True
def enable(file: int, all_threads: int, c_stack: int, max_threads: int) -> int:
    """Mock: Enable the fault handler: install handlers for the :const:`~signal.SIGSEGV`, :const:`~signal.SIGFPE`, :const:`~signal.SI..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.disable
#@ ensures True
def disable() -> int:
    """Mock: Disable the fault handler: uninstall the signal handlers installed by :func:`enable`."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.is_enabled
#@ ensures \result == 0 or \result == 1
def is_enabled() -> int:
    """Mock: Check if the fault handler is enabled."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.dump_traceback_later
#@ requires timeout > 0
#@ ensures True
def dump_traceback_later(timeout: int, repeat: int, file: int, exit: int, max_threads: int) -> int:
    """Mock: Dump the tracebacks of all threads, after a timeout of *timeout* seconds, or every *timeout* seconds if *repeat* is ``Tr..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.cancel_dump_traceback_later
#@ ensures True
#@ assigns \nothing
def cancel_dump_traceback_later() -> int:
    """Mock: Cancel the last call to :func:`dump_traceback_later`."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.register
#@ requires signum > 0
#@ ensures True
def register(signum: int, file: int, all_threads: int, chain: int, max_threads: int) -> int:
    """Mock: Register a user signal: install a handler for the *signum* signal to dump the traceback of all threads, or of the curren..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/faulthandler.html#faulthandler.unregister
#@ requires signum > 0
#@ ensures \result == 0 or \result == 1
def unregister(signum: int) -> int:
    """Mock: Unregister a user signal: uninstall the handler of the *signum* signal installed by :func:`register`. Return ``True`` if..."""
    return 0
