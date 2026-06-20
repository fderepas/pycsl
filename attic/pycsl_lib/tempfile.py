"""PyCSL mock for Python's tempfile module — Generate temporary files and directories."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def TemporaryFile(mode: int, buffering: int, encoding: int, newline: int, suffix: int, prefix: int, dir: int) -> int:
    """Mock: Return a :term:`file-like object` that can be used as a temporary storage area. The file is created securely, using the ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def NamedTemporaryFile(mode: int, buffering: int, encoding: int, newline: int, suffix: int, prefix: int, dir: int) -> int:
    """Mock: This function operates exactly as :func:`TemporaryFile` does, except the following differences: * This function returns ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mkstemp(suffix: int, prefix: int, dir: int, text: int) -> int:
    """Mock: Creates a temporary file in the most secure manner possible.  There are no race conditions in the file's creation, assum..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mkdtemp(suffix: int, prefix: int, dir: int) -> int:
    """Mock: Creates a temporary directory in the most secure manner possible. There are no race conditions in the directory's creati..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettempdir() -> int:
    """Mock: Return the name of the directory used for temporary files. This defines the default value for the *dir* argument to all ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettempdirb() -> int:
    """Mock: Same as :func:`gettempdir` but the return value is in bytes. .. versionadded:: 3.5"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettempprefix() -> int:
    """Mock: Return the filename prefix used to create temporary files.  This does not contain the directory component."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettempprefixb() -> int:
    """Mock: Same as :func:`gettempprefix` but the return value is in bytes. .. versionadded:: 3.5"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mktemp(suffix: int, prefix: int, dir: int) -> int:
    """Mock: .. deprecated:: 2.3 Use :func:`mkstemp` instead. Return an absolute pathname of a file that did not exist at the time th..."""
    return 0
