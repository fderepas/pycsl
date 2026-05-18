"""Test 0001 — PyCSL Annotation Reference 2.1.1"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result >= 0
def test_precondition(x: int) -> int:
    """Precondition: requires must hold at function entry."""
    return x + 1

if __name__ == "__main__":
    assert test_precondition(0) == 1
    assert test_precondition(10) == 11
