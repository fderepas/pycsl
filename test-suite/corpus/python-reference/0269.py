"""Test 0269 — Python Reference 2.5.4.7: Unrecognized escape sequences (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_4_7_a(x: int) -> int:
    """Variation A for Unrecognized escape sequences."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_4_7_a(4) == 5
