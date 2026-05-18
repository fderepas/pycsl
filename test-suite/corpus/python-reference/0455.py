"""Test 0455 — Python Reference 6.10.1: Value comparisons (variation A)"""
_ = 0  # anchor
#@ ensures x > y ==> \result == x
#@ ensures x <= y ==> \result == y
def test_compare_a(x: int, y: int) -> int:
    """Comparison: max of two values."""
    if x > y:
        return x
    return y

if __name__ == "__main__":
    assert test_compare_a(3, 1) == 3
