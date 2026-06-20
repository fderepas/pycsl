"""PyCSL mock for Python's tracemalloc module — Trace memory allocations."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def clear_traces() -> int:
    """Mock: Clear traces of memory blocks allocated by Python. See also :func:`stop`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_object_traceback(obj: int) -> int:
    """Mock: Get the traceback where the Python object *obj* was allocated. Return a :class:`Traceback` instance, or ``None`` if the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_traceback_limit() -> int:
    """Mock: Get the maximum number of frames stored in the traceback of a trace. The :mod:`!tracemalloc` module must be tracing memo..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_traced_memory() -> int:
    """Mock: Get the current size and peak size of memory blocks traced by the :mod:`!tracemalloc` module as a tuple: ``(current: int..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def reset_peak() -> int:
    """Mock: Set the peak size of memory blocks traced by the :mod:`!tracemalloc` module to the current size. Do nothing if the :mod:..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_tracemalloc_memory() -> int:
    """Mock: Get the memory usage in bytes of the :mod:`!tracemalloc` module used to store traces of memory blocks. Return an :class:..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_tracing() -> int:
    """Mock: ``True`` if the :mod:`!tracemalloc` module is tracing Python memory allocations, ``False`` otherwise. See also :func:`st..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def start(nframe: int) -> int:
    """Mock: Start tracing Python memory allocations: install hooks on Python memory allocators. Collected tracebacks of traces will ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def stop() -> int:
    """Mock: Stop tracing Python memory allocations: uninstall hooks on Python memory allocators. Also clears all previously collecte..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def take_snapshot() -> int:
    """Mock: Take a snapshot of traces of memory blocks allocated by Python. Return a new :class:`Snapshot` instance. The snapshot do..."""
    return 0
