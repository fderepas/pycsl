"""multi_file_lib.deep_mid — transitive chain fixture (imports arith.double_int)."""
_ = 0  # anchor
from multi_file_lib.arith import double_int


#@ ensures \result == 2 * x + 1
def double_plus_one(x: int) -> int:
    return double_int(x) + 1
