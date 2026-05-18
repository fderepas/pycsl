"""Test 0105 — PyCSL Annotation Reference 3.2.3 (variation B)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result >= x or \result == 0
def test_or_ge(x: int) -> int:
    """Or: result >= x or zero."""
    return x

if __name__ == "__main__":
    assert test_or_ge(7) == 7
