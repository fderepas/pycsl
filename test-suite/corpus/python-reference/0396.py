"""Test 0396 — Python Reference 5.3.1: The module cache (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_3_1_b(x: int) -> int:
    """Variation B for The module cache."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_3_1_b(3) == 6
