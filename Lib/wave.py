"""PyCSL mock for Python's wave module — Provide an interface to the WAV sound format."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def open(file: int, mode: int) -> int:
    """Mock: If *file* is a string, a :term:`path-like object` or a :term:`bytes-like object` open the file by that name, otherwise t..."""
    return 0
