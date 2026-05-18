"""Test 0022 — PyCSL Annotation Reference 3.2.2"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures x == 0 ==> \result == 0
#@ ensures x > 0 ==> \result == 1
def test_implication(x: int) -> int:
    """Implication (==>) and equivalence (<==>)."""
    if x == 0:
        return 0
    return 1

if __name__ == "__main__":
    assert test_implication(0) == 0
    assert test_implication(5) == 1
