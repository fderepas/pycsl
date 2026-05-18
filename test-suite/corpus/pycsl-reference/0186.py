"""Test 0186 — PyCSL Annotation Reference 9.14 (variation A)"""
_ = 0  # anchor
# pycsl-flags: --deep
from multi_file_lib.circ_a import func_a

#@ ensures \result == x + 3
def circ_plus(x: int) -> int:
    return func_a(x) + 1

if __name__ == "__main__":
    print("PASS")
