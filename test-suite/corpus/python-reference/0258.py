"""Test 0258 — Python Reference 2.5.4.1: Ignored end of line (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_4_1_b(x: int) -> int:
    """Variation B for Ignored end of line."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_4_1_b(3) == 6
