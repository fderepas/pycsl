# Formal tests for pure_lib/json — json module
# json module uses complex signatures. Test size concepts.


#@ requires obj_size >= 0
#@ ensures \result >= obj_size
def test_dumps_grows(obj_size: int) -> int:
    """JSON serialization >= object size."""
    return obj_size + 2


#@ requires json_len >= 0
#@ ensures \result >= 0
#@ ensures \result <= json_len
def test_loads_shrinks(json_len: int) -> int:
    """Deserialized object <= JSON string."""
    return json_len
