"""Test 0287 — Python Reference 2.7: Operators and delimiters (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_7_a(x: int) -> int:
    """Variation A for Operators and delimiters."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_7_a(4) == 5
