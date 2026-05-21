"""PyCSL mock for Python's traceback module — Print or retrieve a stack traceback."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def print_tb(tb: int, limit: int, file: int) -> int:
    """Mock: Print up to *limit* stack trace entries from :ref:`traceback object <traceback-objects>` *tb* (starting from the caller'..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def print_exception(exc: int, value: int, tb: int, limit: int, __file: int, chain: int) -> int:
    """Mock: Print exception information and stack trace entries from :ref:`traceback object <traceback-objects>` *tb* to *file*. Thi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def print_exc(limit: int, file: int, chain: int) -> int:
    """Mock: This is a shorthand for ``print_exception(sys.exception(), limit=limit, file=file, chain=chain)``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def print_last(limit: int, file: int, chain: int) -> int:
    """Mock: This is a shorthand for ``print_exception(sys.last_exc, limit=limit, file=file, chain=chain)``.  In general it will work..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def print_stack(f: int, limit: int, file: int) -> int:
    """Mock: Print up to *limit* stack trace entries (starting from the invocation point) if *limit* is positive.  Otherwise, print t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def extract_tb(tb: int, limit: int) -> int:
    """Mock: Return a :class:`StackSummary` object representing a list of 'pre-processed' stack trace entries extracted from the :ref..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def extract_stack(f: int, limit: int) -> int:
    """Mock: Extract the raw traceback from the current :ref:`stack frame <frame-objects>`.  The return value has the same format as ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def print_list(extracted_list: int, file: int) -> int:
    """Mock: Print the list of tuples as returned by :func:`extract_tb` or :func:`extract_stack` as a formatted stack trace to the gi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def format_list(extracted_list: int) -> int:
    """Mock: Given a list of tuples or :class:`FrameSummary` objects as returned by :func:`extract_tb` or :func:`extract_stack`, retu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def format_exception_only(exc: int, value: int, show_group: int) -> int:
    """Mock: Format the exception part of a traceback using an exception value such as given by :data:`sys.last_value`.  The return v..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def format_exception(exc: int, value: int, tb: int, limit: int, chain: int) -> int:
    """Mock: Format a stack trace and the exception information.  The arguments  have the same meaning as the corresponding arguments..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def format_exc(limit: int, chain: int) -> int:
    """Mock: This is like ``print_exc(limit)`` but returns a string instead of printing to a file."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def format_tb(tb: int, limit: int) -> int:
    """Mock: A shorthand for ``format_list(extract_tb(tb, limit))``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def format_stack(f: int, limit: int) -> int:
    """Mock: A shorthand for ``format_list(extract_stack(f, limit))``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def clear_frames(tb: int) -> int:
    """Mock: Clears the local variables of all the stack frames in a :ref:`traceback <traceback-objects>` *tb* by calling the :meth:`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def walk_stack(f: int) -> int:
    """Mock: Walk a stack following :attr:`f.f_back <frame.f_back>` from the given frame, yielding the frame and line number for each..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def walk_tb(tb: int) -> int:
    """Mock: Walk a traceback following :attr:`~traceback.tb_next` yielding the frame and line number for each frame. This helper is ..."""
    return 0
