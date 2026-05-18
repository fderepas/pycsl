"""Test 0268 — Python Reference 2.5.4.6: Hexadecimal Unicode characters (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_4_6_b(x: int) -> int:
    """Variation B for Hexadecimal Unicode characters."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_4_6_b(3) == 6
