"""Test 0264 — Python Reference 2.5.4.4: Hexadecimal character (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_4_4_b(x: int) -> int:
    """Variation B for Hexadecimal character."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_4_4_b(3) == 6
