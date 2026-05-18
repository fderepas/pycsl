"""Test 0262 — Python Reference 2.5.4.3: Octal character (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_4_3_b(x: int) -> int:
    """Variation B for Octal character."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_4_3_b(3) == 6
