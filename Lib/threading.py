"""PyCSL mock for Python's threading module — Thread-based parallelism."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def active_count() -> int:
    """Mock: Return the number of :class:`Thread` objects currently alive.  The returned count is equal to the length of the list ret..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def current_thread() -> int:
    """Mock: Return the current :class:`Thread` object, corresponding to the caller's thread of control.  If the caller's thread of c..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def excepthook(args: int) -> int:
    """Mock: Handle uncaught exception raised by :func:`Thread.run`. The *args* argument has the following attributes: * *exc_type*: ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_ident() -> int:
    """Mock: Return the 'thread identifier' of the current thread.  This is a nonzero integer.  Its value has no direct meaning; it i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_native_id() -> int:
    """Mock: Return the native integral Thread ID of the current thread assigned by the kernel. This is a non-negative integer. Its v..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def enumerate() -> int:
    """Mock: Return a list of all :class:`Thread` objects currently active.  The list includes daemonic threads and dummy thread obje..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def main_thread() -> int:
    """Mock: Return the main :class:`Thread` object.  In normal conditions, the main thread is the thread from which the Python inter..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def settrace(func: int) -> int:
    """Mock: .. index:: single: trace function Set a trace function for all threads started from the :mod:`!threading` module. The *f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def settrace_all_threads(func: int) -> int:
    """Mock: Set a trace function for all threads started from the :mod:`!threading` module and all Python threads that are currently..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettrace() -> int:
    """Mock: .. index:: single: trace function single: debugger Get the trace function as set by :func:`settrace`. .. versionadded:: ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setprofile(func: int) -> int:
    """Mock: .. index:: single: profile function Set a profile function for all threads started from the :mod:`!threading` module. Th..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setprofile_all_threads(func: int) -> int:
    """Mock: Set a profile function for all threads started from the :mod:`!threading` module and all Python threads that are current..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getprofile() -> int:
    """Mock: .. index:: single: profile function Get the profiler function as set by :func:`setprofile`. .. versionadded:: 3.10"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def stack_size(size: int) -> int:
    """Mock: Return the thread stack size used when creating new threads.  The optional *size* argument specifies the stack size to b..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def synchronized_iterator(func: int) -> int:
    """Mock: Wrap an iterator-producing callable so that each iterator it returns is automatically passed through :class:`serialize_i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def concurrent_tee(iterable: int, n: int) -> int:
    """Mock: Return *n* independent iterators from a single input *iterable*, with guaranteed behavior when the derived iterators are..."""
    return 0
