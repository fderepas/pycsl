"""PyCSL mock for Python's stat module — Utilities for interpreting the results of os.stat(),."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def S_ISDIR(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISCHR(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a character special device file."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISBLK(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a block special device file."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISREG(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a regular file."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISFIFO(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a FIFO (named pipe)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISLNK(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a symbolic link."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISSOCK(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a socket."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISDOOR(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a door. .. versionadded:: 3.4"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISPORT(mode: int) -> int:
    """Mock: Return non-zero if the mode is from an event port. .. versionadded:: 3.4"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_ISWHT(mode: int) -> int:
    """Mock: Return non-zero if the mode is from a whiteout. .. versionadded:: 3.4"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_IMODE(mode: int) -> int:
    """Mock: Return the portion of the file's mode that can be set by :func:`os.chmod`\ ---that is, the file's permission bits, plus ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def S_IFMT(mode: int) -> int:
    """Mock: Return the portion of the file's mode that describes the file type (used by the :func:`!S_IS\*` functions above)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def filemode(mode: int) -> int:
    """Mock: Convert a file's mode to a string of the form '-rwxrwxrwx'. .. versionadded:: 3.3 .. versionchanged:: 3.4 The function s..."""
    return 0
