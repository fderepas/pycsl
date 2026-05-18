"""Test 0184 — PyCSL Annotation Reference 9.13 (variation A)"""
_ = 0  # anchor
# pycsl-flags: --deep
from multi_file_lib.deep_mid import double_plus_one

#@ ensures \result == 2 * x + 2
def deep_plus_two(x: int) -> int:
    return double_plus_one(x) + 1

if __name__ == "__main__":
    print("PASS")
