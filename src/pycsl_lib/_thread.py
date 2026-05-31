"""PyCSL mock for Python's _thread module — Low-level threading API."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def start_new_thread(function_: int, args: int, kwargs: int) -> int:
    """Mock: Start a new thread and return its identifier.  The thread executes the function *function* with the argument list *args*..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def interrupt_main(signum: int) -> int:
    """Mock: Simulate the effect of a signal arriving in the main thread. A thread can use this function to interrupt the main thread..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exit() -> int:
    """Mock: Raise the :exc:`SystemExit` exception.  When not caught, this will cause the thread to exit silently."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def allocate_lock() -> int:
    """Mock: Return a new lock object.  Methods of locks are described below.  The lock is initially unlocked."""
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
def stack_size(size: int) -> int:
    """Mock: Return the thread stack size used when creating new threads.  The optional *size* argument specifies the stack size to b..."""
    return 0
