"""Test 0111 — PyCSL Annotation Reference 3.2.6 (variation B)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result <= x
def test_le(x: int) -> int:
    """Less-or-equal comparison."""
    if x > 0:
        return x - 1
    return 0

if __name__ == "__main__":
    assert test_le(5) == 4
    assert test_le(0) == 0
