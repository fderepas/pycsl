"""Test 0099 — PyCSL Annotation Reference 3.1.13 (variation B)"""
_ = 0  # anchor
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def test_nothing_non_neg(a: int, b: int) -> int:
    """Nothing: pure function with non-negative result."""
    return a + b

if __name__ == "__main__":
    assert test_nothing_non_neg(5, 3) == 8
