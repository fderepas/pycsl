"""PyCSL mock for Python's zipapp module — Manage executable Python zip archives."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0 or \result == 1
def create_archive(source: int, target: int, interpreter: int, main: int, filter: int, compressed: int) -> int:
    """Mock: Create an application archive from *source*.  The source can be any of the following: * The name of a directory, or a :t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_interpreter(archive: int) -> int:
    """Mock: Return the interpreter specified in the ``#!`` line at the start of the archive.  If there is no ``#!`` line, return :co..."""
    return 0
