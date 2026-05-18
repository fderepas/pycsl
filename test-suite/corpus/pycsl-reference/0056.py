"""Test 0056 — Multi-file: from mod import name (basic cross-file import)"""
_ = 0  # anchor
from multi_file_lib.arith import double_int

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    """Calls imported double_int."""
    return double_int(x)

if __name__ == "__main__":
    assert foobar(5) == 10
    print("PASS")
