"""Test 0443 — Python Reference 6.3.2.2: Comma-separated subscripts (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_3_2_2_a(x: int) -> int:
    """Variation A for Comma-separated subscripts."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_3_2_2_a(4) == 5
