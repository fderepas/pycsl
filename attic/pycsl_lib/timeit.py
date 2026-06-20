"""PyCSL mock for Python's timeit module — Measure the execution time of small code snippets."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def timeit(stmt: int, setup: int, timer: int, number: int, globals: int) -> int:
    """Mock: Create a :class:`Timer` instance with the given statement, *setup* code and *timer* function and run its :meth:`.timeit`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def repeat(stmt: int, setup: int, timer: int, repeat: int, number: int, globals: int) -> int:
    """Mock: Create a :class:`Timer` instance with the given statement, *setup* code and *timer* function and run its :meth:`.repeat`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def default_timer() -> int:
    """Mock: The default timer, which is always time.perf_counter(), returns float seconds. An alternative, time.perf_counter_ns, ret..."""
    return 0
