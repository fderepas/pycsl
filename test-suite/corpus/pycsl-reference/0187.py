"""Test 0187 — PyCSL Annotation Reference 9.14 (variation B)"""
_ = 0  # anchor
# pycsl-flags: --deep
from multi_file_lib.circ_a import func_a

#@ ensures \result >= 0
#@ requires x >= 0
def circ_pos(x: int) -> int:
    return func_a(x)

if __name__ == "__main__":
    print("PASS")
