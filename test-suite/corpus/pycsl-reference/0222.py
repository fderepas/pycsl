"""Test 0222 — PyCSL Annotation Reference 7.1 (assert without message)"""
_ = 0  # anchor
#@ requires x >= 0 and y >= 0
#@ ensures \result >= 0
def test_assert_no_msg(x: int, y: int) -> int:
    assert x >= 0
    assert y >= 0
    return x + y

if __name__ == "__main__":
    assert test_assert_no_msg(3, 4) == 7
    assert test_assert_no_msg(0, 0) == 0
