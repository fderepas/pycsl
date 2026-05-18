"""Test 0182 — PyCSL Annotation Reference 9.12 (variation A)"""
_ = 0  # anchor
from multi_file_lib.arith import *

#@ ensures \result == 2 * x
def just_double(x: int) -> int:
    return double_int(x)

if __name__ == "__main__":
    print("PASS")
