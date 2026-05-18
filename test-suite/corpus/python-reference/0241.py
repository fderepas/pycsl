"""Test 0241 — Python Reference 2.1.10: End marker (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_1_10_a(x: int) -> int:
    """Variation A for End marker."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_1_10_a(4) == 5
