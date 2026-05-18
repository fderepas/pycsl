"""Test 0263 — Python Reference 2.5.4.4: Hexadecimal character (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_4_4_a(x: int) -> int:
    """Variation A for Hexadecimal character."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_4_4_a(4) == 5
