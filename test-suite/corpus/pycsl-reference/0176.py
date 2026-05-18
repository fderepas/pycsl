"""Test 0176 — PyCSL Annotation Reference 9.9 (variation A)"""
_ = 0  # anchor
from multi_file_lib.arith import triple_int as t3

#@ ensures \result == 3 * x
def call_aliased(x: int) -> int:
    return t3(x)

if __name__ == "__main__":
    print("PASS")
