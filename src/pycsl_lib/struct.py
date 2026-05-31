"""PyCSL mock for Python's struct module — Interpret bytes as packed binary data."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def pack(format: int, v1: int, v2: int, ___: int) -> int:
    """Mock: Return a bytes object containing the values *v1*, *v2*, ... packed according to the format string *format*.  The argumen..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pack_into(format: int, buffer: int, offset: int, v1: int, v2: int, ___: int) -> int:
    """Mock: Pack the values *v1*, *v2*, ... according to the format string *format* and write the packed bytes into the writable buf..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unpack(format: int, buffer: int) -> int:
    """Mock: Unpack from the buffer *buffer* (presumably packed by ``pack(format, ...)``) according to the format string *format*.  T..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unpack_from(format: int, buffer: int, offset: int) -> int:
    """Mock: Unpack from *buffer* starting at position *offset*, according to the format string *format*.  The result is a tuple even..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iter_unpack(format: int, buffer: int) -> int:
    """Mock: Iteratively unpack from the buffer *buffer* according to the format string *format*.  This function returns an iterator ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def calcsize(format: int) -> int:
    """Mock: Return the size of the struct (and hence of the bytes object produced by ``pack(format, ...)``) corresponding to the for..."""
    return 0
