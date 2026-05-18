"""Test 0170 — PyCSL Annotation Reference 9.6 (variation A)"""
_ = 0  # anchor
from multi_file_lib.arith import double_int, triple_int

#@ ensures \result == 2 * x + 3 * x
def sum_ops(x: int) -> int:
    return double_int(x) + triple_int(x)

if __name__ == "__main__":
    print("PASS")
