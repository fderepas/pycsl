"""PyCSL mock for Python's multiprocessing module — Process-based parallelism."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def Pipe(duplex: int) -> int:
    """Mock: Returns a pair ``(conn1, conn2)`` of :class:`~multiprocessing.connection.Connection` objects representing the ends of a ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def active_children() -> int:
    """Mock: Return list of all live children of the current process. Calling this has the side effect of 'joining' any processes whi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cpu_count() -> int:
    """Mock: Return the number of CPUs in the system. This number is not equivalent to the number of CPUs the current process can use..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def current_process() -> int:
    """Mock: Return the :class:`Process` object corresponding to the current process. An analogue of :func:`threading.current_thread`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parent_process() -> int:
    """Mock: Return the :class:`Process` object corresponding to the parent process of the :func:`current_process`. For the main proc..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def freeze_support() -> int:
    """Mock: Add support for when a program which uses :mod:`!multiprocessing` has been frozen to produce an executable.  (Has been t..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_all_start_methods() -> int:
    """Mock: Returns a list of the supported start methods, the first of which is the default.  The possible start methods are ``'for..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_context(method: int) -> int:
    """Mock: Return a context object which has the same attributes as the :mod:`!multiprocessing` module. If *method* is ``None`` the..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_start_method(allow_none: int) -> int:
    """Mock: Return the name of start method used for starting processes. If the global start method is not set and *allow_none* is `..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_executable(executable: int) -> int:
    """Mock: Set the path of the Python interpreter to use when starting a child process. (By default :data:`sys.executable` is used)..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_forkserver_preload(module_names: int, on_error: int) -> int:
    """Mock: Set a list of module names for the forkserver main process to attempt to import so that their already imported state is ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_start_method(method: int, force: int) -> int:
    """Mock: Set the method which should be used to start child processes. The *method* argument can be ``'fork'``, ``'spawn'`` or ``..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Value(typecode_or_type: int, lock: int) -> int:
    """Mock: Return a :mod:`ctypes` object allocated from shared memory.  By default the return value is actually a synchronized wrap..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Array(typecode_or_type: int, size_or_initializer: int, lock: int) -> int:
    """Mock: Return a ctypes array allocated from shared memory.  By default the return value is actually a synchronized wrapper for ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def RawArray(typecode_or_type: int, size_or_initializer: int) -> int:
    """Mock: Return a ctypes array allocated from shared memory. *typecode_or_type* determines the type of the elements of the return..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def RawValue(typecode_or_type: int) -> int:
    """Mock: Return a ctypes object allocated from shared memory. *typecode_or_type* determines the type of the returned object: it i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy(obj: int) -> int:
    """Mock: Return a ctypes object allocated from shared memory which is a copy of the ctypes object *obj*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def synchronized(obj: int, lock: int, ctx: int) -> int:
    """Mock: Return a process-safe wrapper object for a ctypes object which uses *lock* to synchronize access.  If *lock* is ``None``..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def deliver_challenge(connection: int, authkey: int) -> int:
    """Mock: Send a randomly generated message to the other end of the connection and wait for a reply. If the reply matches the dige..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def answer_challenge(connection: int, authkey: int) -> int:
    """Mock: Receive a message, calculate the digest of the message using *authkey* as the key, and then send the digest back. If a w..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Client(address: int, family: int, authkey: int) -> int:
    """Mock: Attempt to set up a connection to the listener which is using address *address*, returning a :class:`~Connection`. The t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wait(object_list: int, timeout: int) -> int:
    """Mock: Wait till an object in *object_list* is ready.  Returns the list of those objects in *object_list* which are ready.  If ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_logger() -> int:
    """Mock: Returns the logger used by :mod:`!multiprocessing`.  If necessary, a new one will be created. When first created the log..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def log_to_stderr(level: int) -> int:
    """Mock: This function performs a call to :func:`get_logger` but in addition to returning the logger created by get_logger, it ad..."""
    return 0
