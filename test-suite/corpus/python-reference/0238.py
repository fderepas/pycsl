"""Test 0238 — Python Reference 2.1.8: Indentation (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_1_8_b(x: int) -> int:
    """Variation B for Indentation."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_1_8_b(3) == 6
