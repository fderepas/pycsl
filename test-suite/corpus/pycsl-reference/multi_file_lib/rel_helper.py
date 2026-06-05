"""multi_file_lib.rel_helper — fixture for relative-import tests."""
_ = 0  # anchor


#@ ensures \result == x + 1
def inc(x: int) -> int:
    return x + 1
