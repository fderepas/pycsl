"""Test 0177 — PyCSL Annotation Reference 9.9 (variation B)"""
_ = 0  # anchor
from multi_file_lib.arith import double_int as d, triple_int as t

#@ ensures \result == 5 * x
def five_x(x: int) -> int:
    return d(x) + t(x)

if __name__ == "__main__":
    print("PASS")
