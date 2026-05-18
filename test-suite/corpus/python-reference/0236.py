"""Test 0236 — Python Reference 2.1.7: Blank lines (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_1_7_b(x: int) -> int:
    """Variation B for Blank lines."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_1_7_b(3) == 6
