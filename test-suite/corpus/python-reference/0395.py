"""Test 0395 — Python Reference 5.3.1: The module cache (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_3_1_a(x: int) -> int:
    """Variation A for The module cache."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_3_1_a(4) == 5
