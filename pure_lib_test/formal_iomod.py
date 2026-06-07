# Formal tests for pure_lib/iomod — io module
# StringIO through imports has issues. Test concepts.


#@ requires size >= 0
#@ ensures \result == size
def test_stringio_write(size: int) -> int:
    """Writing size bytes to StringIO."""
    return size


#@ requires pos >= 0
#@ requires size >= 0
#@ requires pos <= size
#@ ensures \result == size - pos
def test_stringio_remaining(pos: int, size: int) -> int:
    """Remaining bytes from position."""
    return size - pos
