"""PyCSL mock for Python's io module — Core tools for working with streams."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def open(file: int, mode: int, buffering: int, encoding: int, errors: int, newline: int, closefd: int) -> int:
    """Mock: This is an alias for the builtin :func:`open` function. .. audit-event:: open path,mode,flags io.open This function rais..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open_code(path: int) -> int:
    """Mock: Opens the provided file with mode ``'rb'``. This function should be used when the intent is to treat the contents as exe..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def text_encoding(encoding: int, stacklevel: int) -> int:
    """Mock: This is a helper function for callables that use :func:`open` or :class:`TextIOWrapper` and have an ``encoding=None`` pa..."""
    return 0
