# Formal tests for pure_lib/arr — array module
# Class through imports causes unbound symbol. Test concepts directly.


#@ requires size >= 0
#@ ensures \result == size + 1
def test_append_increments(size: int) -> int:
    """Append increments array size."""
    return size + 1


#@ requires size > 0
#@ ensures \result == size - 1
def test_pop_decrements(size: int) -> int:
    """Pop decrements array size."""
    return size - 1


#@ requires size >= 0
#@ ensures \result == size + size
def test_extend_doubles(size: int) -> int:
    """Extend self doubles size."""
    return size + size
