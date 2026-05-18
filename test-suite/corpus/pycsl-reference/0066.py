"""Test 0066 — PyCSL Annotation Reference 2.1.1 (variation A)"""
_ = 0  # anchor
#@ requires x > 0
#@ requires x < 100
#@ ensures \result > 1
def test_multi_precondition(x: int) -> int:
    """Multiple preconditions conjuncted."""
    return x + 1

if __name__ == "__main__":
    assert test_multi_precondition(1) == 2
    assert test_multi_precondition(50) == 51
