"""Test 0288 — Python Reference 2.7: Operators and delimiters (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_7_b(x: int) -> int:
    """Variation B for Operators and delimiters."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_7_b(3) == 6
