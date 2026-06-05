"""multi_file_lib.circ_b — circular-import fixture (circ_a <-> circ_b)."""
_ = 0  # anchor
from multi_file_lib.circ_a import func_a  # noqa: F401 — establishes the cycle


#@ ensures \result == x + 1
def func_b(x: int) -> int:
    return x + 1
