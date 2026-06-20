"""PyCSL mock for Python's shelve module — Python object persistence."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def open(filename: int, flag: int, protocol: int, writeback: int, __serializer: int, deserializer: int) -> int:
    """Mock: Open a persistent dictionary.  The filename specified is the base filename for the underlying database.  As a side-effec..."""
    return 0
