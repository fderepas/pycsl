"""Test 0183 — PyCSL Annotation Reference 9.12 (variation B)"""
_ = 0  # anchor
from multi_file_lib.arith import *

#@ ensures \result == 3 * x
def just_triple(x: int) -> int:
    return triple_int(x)

if __name__ == "__main__":
    print("PASS")
