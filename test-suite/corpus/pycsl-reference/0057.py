"""Test 0057 — Multi-file: from mod import a, b (multiple names)"""
_ = 0  # anchor
from multi_file_lib.arith import double_int, triple_int

#@ ensures \result == 5 * x
def quintuple(x: int) -> int:
    """Adds double and triple."""
    return double_int(x) + triple_int(x)

if __name__ == "__main__":
    assert quintuple(4) == 20
    print("PASS")
