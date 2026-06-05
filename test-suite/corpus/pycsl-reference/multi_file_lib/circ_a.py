"""multi_file_lib.circ_a — circular-import fixture (circ_a <-> circ_b)."""
_ = 0  # anchor
from multi_file_lib.circ_b import func_b


#@ ensures \result == x + 2
def func_a(x: int) -> int:
    return func_b(x) + 1
