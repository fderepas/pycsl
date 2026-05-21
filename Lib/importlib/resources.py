"""PyCSL mock for Python's importlib.resources module — Package resource reading, opening, and access."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def files(anchor: int) -> int:
    """Mock: Returns a :class:`~importlib.resources.abc.Traversable` object representing the resource container (think directory) and..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def as_file(traversable: int) -> int:
    """Mock: Given a :class:`~importlib.resources.abc.Traversable` object representing a file or directory, typically from :func:`imp..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open_binary(anchor: int) -> int:
    """Mock: Open the named resource for binary reading. See :ref:`the introduction <importlib_resources_functional>` for details on ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open_text(anchor: int, encoding: int, errors: int) -> int:
    """Mock: Open the named resource for text reading. By default, the contents are read as strict UTF-8. See :ref:`the introduction ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def read_binary(anchor: int) -> int:
    """Mock: Read and return the contents of the named resource as :class:`bytes`. See :ref:`the introduction <importlib_resources_fu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def read_text(anchor: int, encoding: int, errors: int) -> int:
    """Mock: Read and return the contents of the named resource as :class:`str`. By default, the contents are read as strict UTF-8. S..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def path(anchor: int) -> int:
    """Mock: Provides the path to the *resource* as an actual file system path.  This function returns a context manager for use in a..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_resource(anchor: int) -> int:
    """Mock: Return ``True`` if the named resource exists, otherwise ``False``. This function does not consider directories to be res..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def contents(anchor: int) -> int:
    """Mock: Return an iterable over the named items within the package or path. The iterable returns names of resources (e.g. files)..."""
    return 0
