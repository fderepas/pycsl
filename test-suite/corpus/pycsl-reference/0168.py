"""Test 0168 — PyCSL Annotation Reference 9.5 (variation A)"""
_ = 0  # anchor
from multi_file_lib.arith import triple_int

#@ ensures \result == 3 * x
def call_triple(x: int) -> int:
    return triple_int(x)

if __name__ == "__main__":
    print("PASS")
