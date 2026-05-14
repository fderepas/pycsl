"""PyCSL mock for Python's threading module."""
_ = 0  # anchor

# ---------------------------------------------------------------------------
# Module-level functions
# ---------------------------------------------------------------------------

#@ \trusted
#@ ensures \result >= 0
def active_count() -> int:
    """Mock: returns the number of Thread objects currently alive."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def current_thread() -> int:
    """Mock: returns the current Thread object."""
    return 0

#@ \trusted
#@ ensures \result == 0
def excepthook(args: int) -> int:
    """Mock: handles uncaught exception raised by Thread.run."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_ident() -> int:
    """Mock: returns thread identifier of the current thread."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_native_id() -> int:
    """Mock: returns native integral thread ID assigned by the kernel."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def enumerate() -> int:
    """Mock: returns list of all active Thread objects."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def main_thread() -> int:
    """Mock: returns the main Thread object."""
    return 0

#@ \trusted
#@ ensures \result == 0
def settrace(func: int) -> int:
    """Mock: sets a trace function for all threads."""
    return 0

#@ \trusted
#@ ensures \result == 0
def settrace_all_threads(func: int) -> int:
    """Mock: sets a trace function for all threads including running ones."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettrace() -> int:
    """Mock: returns the trace function set by settrace."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setprofile(func: int) -> int:
    """Mock: sets a profile function for all threads."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setprofile_all_threads(func: int) -> int:
    """Mock: sets a profile function for all threads including running ones."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getprofile() -> int:
    """Mock: returns the profile function set by setprofile."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def stack_size(size: int) -> int:
    """Mock: returns or sets the thread stack size."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def synchronized_iterator(func: int) -> int:
    """Mock: wraps an iterator-producing callable with serialize_iterator."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def concurrent_tee(iterable: int, n: int) -> int:
    """Mock: returns n independent thread-safe iterators from iterable."""
    return 0

# ---------------------------------------------------------------------------
# Classes (constructors returning opaque int >= 0)
# ---------------------------------------------------------------------------

#@ \trusted
#@ ensures \result >= 0
def local() -> int:
    """Mock: creates a thread-local data object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Thread(group: int, target: int, thread_name: int, args: int, kwargs: int, daemon: int, context: int) -> int:
    """Mock: creates a Thread object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Lock() -> int:
    """Mock: creates a primitive lock object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def RLock() -> int:
    """Mock: creates a reentrant lock object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Condition(lock: int) -> int:
    """Mock: creates a condition variable object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Semaphore(initial_value: int) -> int:
    """Mock: creates a semaphore object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def BoundedSemaphore(initial_value: int) -> int:
    """Mock: creates a bounded semaphore object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Event() -> int:
    """Mock: creates an event object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Timer(interval: int, function: int, args: int, kwargs: int) -> int:
    """Mock: creates a timer that runs function after interval seconds — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Barrier(parties: int, action: int, timeout: int) -> int:
    """Mock: creates a barrier for parties threads — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def serialize_iterator(iterable: int) -> int:
    """Mock: wraps an iterator with serialized concurrent access — opaque."""
    return 0
