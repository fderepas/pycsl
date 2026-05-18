"""Test 0169 — PyCSL Annotation Reference 9.5 (variation B)"""
_ = 0  # anchor
from multi_file_lib.arith import double_int

#@ ensures \result == 2 * x + 1
def double_plus(x: int) -> int:
    return double_int(x) + 1

if __name__ == "__main__":
    print("PASS")
