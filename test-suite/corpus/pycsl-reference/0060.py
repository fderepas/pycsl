"""Test 0060 — Multi-file: from mod import name as alias"""
_ = 0  # anchor
from multi_file_lib.arith import double_int as di

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    """Calls double_int via alias di."""
    return di(x)

if __name__ == "__main__":
    print("PASS")
