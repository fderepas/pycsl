"""Test 0221 — PyCSL Annotation Reference 7.1 (assert statement)"""
_ = 0  # anchor
#@ requires x > 0
#@ ensures \result > 0
def test_assert_basic(x: int) -> int:
    assert x > 0, "x must be positive"
    return x + 1

if __name__ == "__main__":
    assert test_assert_basic(5) == 6
    assert test_assert_basic(1) == 2
