"""Test 0284 — Python Reference 2.6.2: Floating-point literals (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_6_2_b(x: int) -> int:
    """Variation B for Floating-point literals."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_6_2_b(3) == 6
