"""Test 0228 — PyCSL Annotation Reference 3.1.18 (boolean in ensures)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result >= 0 or False
def test_bool_ensures(x: int) -> int:
    return x

if __name__ == "__main__":
    assert test_bool_ensures(0) == 0
    assert test_bool_ensures(42) == 42
