"""Test 0103 — PyCSL Annotation Reference 3.2.2 (variation B)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures x == 0 <==> \result == 0
def test_iff(x: int) -> int:
    """Equivalence (iff): result is zero iff x is zero."""
    return x

if __name__ == "__main__":
    assert test_iff(0) == 0
    assert test_iff(5) == 5
