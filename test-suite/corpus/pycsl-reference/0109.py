"""Test 0109 — PyCSL Annotation Reference 3.2.5 (variation B)"""
_ = 0  # anchor
#@ requires x != 0
#@ ensures \result != 0
def test_neq(x: int) -> int:
    """Not-equal: nonzero input → nonzero output."""
    return x

if __name__ == "__main__":
    assert test_neq(5) == 5
