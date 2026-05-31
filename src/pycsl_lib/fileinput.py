"""PyCSL mock for Python's fileinput module — Loop over standard input or a list of files."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def input(files: int, inplace: int, backup: int, mode: int, openhook: int, encoding: int, errors: int) -> int:
    """Mock: Create an instance of the :class:`FileInput` class.  The instance will be used as global state for the functions of this..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def filename() -> int:
    """Mock: Return the name of the file currently being read.  Before the first line has been read, returns ``None``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fileno() -> int:
    """Mock: Return the integer 'file descriptor' for the current file. When no file is opened (before the first line and between fil..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lineno() -> int:
    """Mock: Return the cumulative line number of the line that has just been read.  Before the first line has been read, returns ``0..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def filelineno() -> int:
    """Mock: Return the line number in the current file.  Before the first line has been read, returns ``0``.  After the last line of..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isfirstline() -> int:
    """Mock: Return ``True`` if the line just read is the first line of its file, otherwise return ``False``."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isstdin() -> int:
    """Mock: Return ``True`` if the last line was read from ``sys.stdin``, otherwise return ``False``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nextfile() -> int:
    """Mock: Close the current file so that the next iteration will read the first line from the next file (if any); lines not read f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def close() -> int:
    """Mock: Close the sequence."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hook_compressed(filename: int, mode: int, encoding: int, errors: int) -> int:
    """Mock: Transparently opens files compressed with gzip and bzip2 (recognized by the extensions ``'.gz'`` and ``'.bz2'``) using t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hook_encoded(encoding: int, errors: int) -> int:
    """Mock: Returns a hook which opens each file with :func:`open`, using the given *encoding* and *errors* to read the file. Usage ..."""
    return 0
