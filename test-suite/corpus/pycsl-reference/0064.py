"""Test 0064 — Multi-file: --deep transitive import chain (A→B→C)"""
_ = 0  # anchor
# pycsl-flags: --deep
from multi_file_lib.deep_mid import double_plus_one

#@ ensures \result == 2 * x + 1
def call_deep(x: int) -> int:
    """Calls double_plus_one, which itself imports double_int from arith."""
    return double_plus_one(x)

if __name__ == "__main__":
    print("PASS")
