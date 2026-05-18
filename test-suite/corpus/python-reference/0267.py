"""Test 0267 — Python Reference 2.5.4.6: Hexadecimal Unicode characters (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_4_6_a(x: int) -> int:
    """Variation A for Hexadecimal Unicode characters."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_4_6_a(4) == 5
