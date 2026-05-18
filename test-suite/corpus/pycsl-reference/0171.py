"""Test 0171 — PyCSL Annotation Reference 9.6 (variation B)"""
_ = 0  # anchor
from multi_file_lib.arith import double_int, triple_int

#@ ensures \result == 3 * x - 2 * x
def diff_ops(x: int) -> int:
    return triple_int(x) - double_int(x)

if __name__ == "__main__":
    print("PASS")
