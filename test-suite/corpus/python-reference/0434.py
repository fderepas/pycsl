"""Test 0434 — Python Reference 6.2.3.2: String literal concatenation (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_2_3_2_b(x: int) -> int:
    """Variation B for String literal concatenation."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_2_3_2_b(3) == 6
