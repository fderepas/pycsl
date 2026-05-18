"""Test 0106 — PyCSL Annotation Reference 3.2.4 (variation A)"""
_ = 0  # anchor
#@ requires x >= 0 and x <= 100
#@ ensures \result >= 1 and \result <= 101
def test_and_range(x: int) -> int:
    """And: bounded input → bounded output."""
    return x + 1

if __name__ == "__main__":
    assert test_and_range(0) == 1
    assert test_and_range(100) == 101
