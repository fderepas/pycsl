"""Test 0270 — Python Reference 2.5.4.7: Unrecognized escape sequences (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_4_7_b(x: int) -> int:
    """Variation B for Unrecognized escape sequences."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_4_7_b(3) == 6
