"""PyCSL mock for Python's marshal module — Convert Python objects to streams of bytes and back (with different."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def dump(value: int, file: int, version: int, allow_code: int) -> int:
    """Mock: Write the value on the open file.  The value must be a supported type.  The file must be a writeable :term:`binary file`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def load(file: int, allow_code: int) -> int:
    """Mock: Read one value from the open file and return it.  If no valid value is read (e.g. because the data has a different Pytho..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dumps(value: int, version: int, allow_code: int) -> int:
    """Mock: Return the bytes object that would be written to a file by ``dump(value, file)``.  The value must be a supported type.  ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def loads(bytes: int, allow_code: int) -> int:
    """Mock: Convert the :term:`bytes-like object` to a value.  If no valid value is found, raise :exc:`EOFError`, :exc:`ValueError` ..."""
    return 0
