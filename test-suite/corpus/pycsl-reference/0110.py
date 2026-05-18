"""Test 0110 — PyCSL Annotation Reference 3.2.6 (variation A)"""
_ = 0  # anchor
#@ requires x > 0
#@ ensures \result > x
def test_gt(x: int) -> int:
    """Greater-than comparison."""
    return x + 1

if __name__ == "__main__":
    assert test_gt(5) == 6
