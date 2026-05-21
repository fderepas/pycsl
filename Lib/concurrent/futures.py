"""PyCSL mock for Python's concurrent.futures module — Execute computations concurrently using threads or processes."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def wait(fs: int, timeout: int, return_when: int) -> int:
    """Mock: Wait for the :class:`Future` instances (possibly created by different :class:`Executor` instances) given by *fs* to comp..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def as_completed(fs: int, timeout: int) -> int:
    """Mock: Returns an iterator over the :class:`Future` instances (possibly created by different :class:`Executor` instances) given..."""
    return 0
