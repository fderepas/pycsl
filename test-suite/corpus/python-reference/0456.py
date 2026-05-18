"""Test 0456 — Python Reference 6.10.1: Value comparisons (variation B)"""
_ = 0  # anchor
#@ ensures x < y ==> \result == x
#@ ensures x >= y ==> \result == y
def test_compare_b(x: int, y: int) -> int:
    """Comparison: min of two values."""
    if x < y:
        return x
    return y

if __name__ == "__main__":
    assert test_compare_b(3, 1) == 1
