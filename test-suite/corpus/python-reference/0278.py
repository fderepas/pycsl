"""Test 0278 — Python Reference 2.5.8: t-strings (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_8_b(x: int) -> int:
    """Variation B for t-strings."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_8_b(3) == 6
