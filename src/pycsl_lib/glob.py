"""PyCSL mock for Python's glob module — Unix shell style pathname pattern expansion."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def glob(pathname: int, root_dir: int, dir_fd: int, recursive: int, __include_hidden: int) -> int:
    """Mock: Return a possibly empty list of path names that match *pathname*, which must be a string containing a path specification..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iglob(pathname: int, root_dir: int, dir_fd: int, recursive: int, __include_hidden: int) -> int:
    """Mock: Return an :term:`iterator` which yields the same values as :func:`glob` without actually storing them all simultaneously..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def escape(pathname: int) -> int:
    """Mock: Escape all special characters (``'?'``, ``'*'`` and ``'['``). This is useful if you want to match an arbitrary literal s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def translate(pathname: int, recursive: int, include_hidden: int, seps: int) -> int:
    """Mock: Convert the given path specification to a regular expression for use with :func:`re.prefixmatch`. The path specification..."""
    return 0
