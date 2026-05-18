"""Test 0235 — Python Reference 2.1.7: Blank lines (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_1_7_a(x: int) -> int:
    """Variation A for Blank lines."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_1_7_a(4) == 5
