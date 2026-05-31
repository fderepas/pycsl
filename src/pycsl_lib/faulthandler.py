"""PyCSL mock for Python's faulthandler module — Dump the Python traceback."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def dump_traceback(file: int, all_threads: int, max_threads: int) -> int:
    """Mock: Dump the tracebacks of all threads into *file*. If *all_threads* is ``False``, dump only the current thread. *max_thread..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dump_c_stack(file: int) -> int:
    """Mock: Dump the C stack trace of the current thread into *file*. If the Python build does not support it or the operating syste..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def enable(file: int, all_threads: int, c_stack: int, max_threads: int) -> int:
    """Mock: Enable the fault handler: install handlers for the :const:`~signal.SIGSEGV`, :const:`~signal.SIGFPE`, :const:`~signal.SI..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def disable() -> int:
    """Mock: Disable the fault handler: uninstall the signal handlers installed by :func:`enable`."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_enabled() -> int:
    """Mock: Check if the fault handler is enabled."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dump_traceback_later(timeout: int, repeat: int, file: int, exit: int, max_threads: int) -> int:
    """Mock: Dump the tracebacks of all threads, after a timeout of *timeout* seconds, or every *timeout* seconds if *repeat* is ``Tr..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def cancel_dump_traceback_later() -> int:
    """Mock: Cancel the last call to :func:`dump_traceback_later`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register(signum: int, file: int, all_threads: int, chain: int, max_threads: int) -> int:
    """Mock: Register a user signal: install a handler for the *signum* signal to dump the traceback of all threads, or of the curren..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def unregister(signum: int) -> int:
    """Mock: Unregister a user signal: uninstall the handler of the *signum* signal installed by :func:`register`. Return ``True`` if..."""
    return 0
