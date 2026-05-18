"""Test 0185 — PyCSL Annotation Reference 9.13 (variation B)"""
_ = 0  # anchor
# pycsl-flags: --deep
from multi_file_lib.deep_mid import double_plus_one

#@ ensures \result >= 1
def deep_positive(x: int) -> int:
    return double_plus_one(x) + 1 - 2 * x

if __name__ == "__main__":
    print("PASS")
