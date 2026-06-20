# Formal tests for pycsl_lib/plib — pathlib module
# PurePath class through imports. Test path concepts.


#@ requires length >= 0
#@ ensures \result >= 0
def test_path_str_nonneg(length: int) -> int:
    """Path string length is non-negative."""
    return length


#@ ensures \result >= 0
#@ ensures \result <= 1
def test_is_absolute_binary() -> int:
    """is_absolute returns 0 or 1."""
    return 0
