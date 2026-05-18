"""Test 0179 — PyCSL Annotation Reference 9.10 (variation B)"""
_ = 0  # anchor
from .multi_file_lib.arith import double_int

#@ ensures \result == 2 * x + 5
def rel_plus(x: int) -> int:
    return double_int(x) + 5

if __name__ == "__main__":
    print("PASS")
