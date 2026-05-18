"""Test 0257 — Python Reference 2.5.4.1: Ignored end of line (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_4_1_a(x: int) -> int:
    """Variation A for Ignored end of line."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_4_1_a(4) == 5
