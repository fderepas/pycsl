"""Test 0444 — Python Reference 6.3.2.2: Comma-separated subscripts (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_3_2_2_b(x: int) -> int:
    """Variation B for Comma-separated subscripts."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_3_2_2_b(3) == 6
