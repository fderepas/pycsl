"""Test 0024 — PyCSL Annotation Reference 3.2.4"""
_ = 0  # anchor
#@ requires x >= 0 and x <= 100
#@ ensures \result >= 0 and \result <= 100
def test_and_operator(x: int) -> int:
    """Logical and in contracts."""
    return x

if __name__ == "__main__":
    assert test_and_operator(50) == 50
