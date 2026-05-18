"""Test 0063 — Multi-file: from mod import * (wildcard import)"""
_ = 0  # anchor
from multi_file_lib.arith import *

#@ ensures \result == 5 * x
def quintuple(x: int) -> int:
    """Uses double_int and triple_int imported via wildcard."""
    return double_int(x) + triple_int(x)

if __name__ == "__main__":
    print("PASS")
