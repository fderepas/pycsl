"""PyCSL mock for Python's pickle module — Convert Python objects to streams of bytes and back."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def dump(obj: int, file: int, protocol: int, fix_imports: int, buffer_callback: int) -> int:
    """Mock: Write the pickled representation of the object *obj* to the open :term:`file object` *file*.  This is equivalent to ``Pi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dumps(obj: int, protocol: int, fix_imports: int, buffer_callback: int) -> int:
    """Mock: Return the pickled representation of the object *obj* as a :class:`bytes` object, instead of writing it to a file. Argum..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def load(file: int, fix_imports: int, encoding: int, errors: int, buffers: int) -> int:
    """Mock: Read the pickled representation of an object from the open :term:`file object` *file* and return the reconstituted objec..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def loads(data: int, fix_imports: int, encoding: int, errors: int, buffers: int) -> int:
    """Mock: Return the reconstituted object hierarchy of the pickled representation *data* of an object. *data* must be a :term:`byt..."""
    return 0
